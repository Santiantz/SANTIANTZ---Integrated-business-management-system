/**
 * WEBHOOK MERCADOPAGO
 *
 * Endpoint publico que recibe notificaciones de MercadoPago cuando
 * cambia el estado de un pago. Si el pago fue aprobado:
 *   1. Actualiza los boletos a status 'pagado'
 *   2. Genera QR unico (UUID v4) por boleto
 *   3. Llama generarBoleto para crear el PDF
 *   4. Llama enviarEmail para mandarlo al comprador
 *   5. Decrementa la capacidad disponible del tipo de entrada
 *
 * MercadoPago puede llamar este webhook varias veces. La logica
 * es idempotente: solo procesa si el boleto sigue en pendiente.
 */

const { onRequest } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const admin = require('firebase-admin');
const { MercadoPagoConfig, Payment } = require('mercadopago');
const { v4: uuidv4 } = require('uuid');

const MP_ACCESS_TOKEN = defineSecret('MP_ACCESS_TOKEN_TEST');

exports.webhookMP = onRequest(
  {
    region: 'us-east1',
    memory: '512MiB',
    timeoutSeconds: 60,
    cors: false,
    secrets: [MP_ACCESS_TOKEN]
  },
  async (req, res) => {
    try {
      // MercadoPago manda POST con JSON o queryParams (depende del tipo de notificacion)
      const tipo = req.body?.type || req.query?.type || req.body?.topic;
      const dataId = req.body?.data?.id || req.query?.id || req.query?.['data.id'];

      console.log('Webhook MP recibido:', { tipo, dataId, body: req.body, query: req.query });

      // Solo procesamos notificaciones de tipo payment
      if (tipo !== 'payment' || !dataId) {
        // Respondemos 200 igual para que MP no reintente eternamente
        res.status(200).send('OK - tipo no procesable');
        return;
      }

      // Consulta el pago a MP
      const mp = new MercadoPagoConfig({ accessToken: MP_ACCESS_TOKEN.value() });
      const pagoApi = new Payment(mp);
      const pago = await pagoApi.get({ id: dataId });

      if (!pago) {
        console.warn('Pago no encontrado en MP:', dataId);
        res.status(200).send('OK - pago no encontrado');
        return;
      }

      console.log('Pago MP:', {
        id: pago.id,
        status: pago.status,
        externalReference: pago.external_reference
      });

      const db = admin.firestore();
      const boletoIds = (pago.external_reference || '').split(',').filter(Boolean);

      if (boletoIds.length === 0) {
        console.warn('Sin external_reference, no se puede asociar a boletos');
        res.status(200).send('OK - sin referencia');
        return;
      }

      // Si el pago no esta aprobado, solo registramos el estado
      if (pago.status !== 'approved') {
        const lote = db.batch();
        boletoIds.forEach(id => {
          lote.update(db.collection('boletos').doc(id), {
            mercadopagoPaymentId: String(pago.id),
            mercadopagoStatus: pago.status,
            mercadopagoData: {
              status_detail: pago.status_detail,
              payment_method_id: pago.payment_method_id,
              transaction_amount: pago.transaction_amount
            }
          });
        });
        await lote.commit();
        res.status(200).send(`OK - status ${pago.status} registrado`);
        return;
      }

      // Pago aprobado: activamos los boletos
      const promesas = [];
      for (const boletoId of boletoIds) {
        promesas.push(activarBoleto(db, boletoId, pago));
      }
      await Promise.all(promesas);

      res.status(200).send('OK - boletos activados');
    } catch (error) {
      console.error('Error en webhookMP:', error);
      // Respondemos 500 para que MP reintente
      res.status(500).send('Error: ' + (error.message || 'desconocido'));
    }
  }
);

/**
 * Activa un boleto individual de manera idempotente.
 * Si ya esta pagado, no hace nada.
 */
async function activarBoleto(db, boletoId, pago) {
  const boletoRef = db.collection('boletos').doc(boletoId);

  // Transaccion atomica para prevenir doble activacion
  const resultado = await db.runTransaction(async (tx) => {
    const snap = await tx.get(boletoRef);
    if (!snap.exists) {
      return { ok: false, motivo: 'boleto-no-existe' };
    }

    const boleto = snap.data();
    if (boleto.status === 'pagado' || boleto.status === 'usado') {
      return { ok: false, motivo: 'ya-procesado' };
    }

    // Genera QR unico
    const qrCode = uuidv4();

    tx.update(boletoRef, {
      qrCode,
      status: 'pagado',
      mercadopagoPaymentId: String(pago.id),
      mercadopagoStatus: pago.status,
      mercadopagoData: {
        status_detail: pago.status_detail,
        payment_method_id: pago.payment_method_id,
        transaction_amount: pago.transaction_amount
      },
      fechaPago: admin.firestore.FieldValue.serverTimestamp()
    });

    return { ok: true, boleto, qrCode };
  });

  if (!resultado.ok) {
    console.log(`Boleto ${boletoId}: ${resultado.motivo}`);
    return;
  }

  // Decrementa capacidad disponible del tipo de entrada
  try {
    const eventoRef = db.collection('eventos').doc(resultado.boleto.eventoId);
    await db.runTransaction(async (tx) => {
      const evSnap = await tx.get(eventoRef);
      if (!evSnap.exists) return;
      const ev = evSnap.data();
      const tipos = (ev.tiposEntrada || []).map(t => {
        if (t.id === resultado.boleto.tipoEntradaId) {
          return { ...t, vendidos: (t.vendidos || 0) + 1 };
        }
        return t;
      });
      tx.update(eventoRef, { tiposEntrada: tipos });
    });
  } catch (e) {
    console.warn('No se pudo decrementar capacidad:', e.message);
  }

  // Genera PDF y envia email (en paralelo, no bloqueante)
  const generarBoleto = require('./generarBoleto').generarBoletoInternal;
  const enviarEmail = require('./enviarEmail').enviarEmailInternal;

  try {
    await generarBoleto(boletoId);
    await enviarEmail(boletoId);
  } catch (e) {
    console.error('Error al generar PDF o enviar email:', e);
    // No lanzamos error porque el boleto ya esta activado.
    // El cliente puede descargar el PDF desde la pagina de exito.
  }
}
