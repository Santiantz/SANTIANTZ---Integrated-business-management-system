/**
 * CREAR PREFERENCIA - MercadoPago Checkout Pro
 *
 * Recibe los datos de compra, valida edad, crea registros en Firestore
 * (persona_verificada + boleto en estado pendiente) y genera la
 * preferencia de pago en MercadoPago.
 *
 * Retorna la URL initPoint para redirigir al cliente al checkout.
 */

const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const admin = require('firebase-admin');
const { MercadoPagoConfig, Preference } = require('mercadopago');

const MP_ACCESS_TOKEN = defineSecret('MP_ACCESS_TOKEN_TEST');

exports.crearPreferencia = onCall(
  {
    region: 'us-east1',
    memory: '512MiB',
    timeoutSeconds: 30,
    secrets: [MP_ACCESS_TOKEN]
  },
  async (request) => {
    // Validar que el cliente este autenticado (Firebase Auth anonimo o con login)
    if (!request.auth) {
      console.warn('Llamada a crearPreferencia sin autenticacion');
      throw new HttpsError(
        'unauthenticated',
        'Debes iniciar sesion para usar esta funcion.'
      );
    }
    console.log('Invocacion de crearPreferencia por uid:', request.auth.uid);

    const data = request.data || {};
    console.log('Datos recibidos: eventoId=', data.eventoId, 'tipoEntradaId=', data.tipoEntradaId, 'cantidad=', data.cantidad);

    const {
      eventoId,
      tipoEntradaId,
      cantidad,
      personaData,
      // URLs a las que MP va a redirigir despues del pago
      successUrl,
      failureUrl,
      pendingUrl
    } = data;

    // Validacion basica
    if (!eventoId || !tipoEntradaId || !cantidad || !personaData) {
      throw new HttpsError(
        'invalid-argument',
        'Faltan parametros requeridos: eventoId, tipoEntradaId, cantidad, personaData.'
      );
    }

    if (cantidad < 1 || cantidad > 10) {
      throw new HttpsError(
        'invalid-argument',
        'La cantidad debe estar entre 1 y 10 boletos por compra.'
      );
    }

    const db = admin.firestore();

    try {
      // 1. Lee el evento
      const eventoRef = db.collection('eventos').doc(eventoId);
      const eventoSnap = await eventoRef.get();

      if (!eventoSnap.exists) {
        throw new HttpsError('not-found', 'El evento no existe.');
      }

      const evento = eventoSnap.data();

      if (evento.status !== 'activo') {
        throw new HttpsError(
          'failed-precondition',
          'Este evento no esta activo en este momento.'
        );
      }

      // 2. Encuentra el tipo de entrada
      const tipoEntrada = (evento.tiposEntrada || []).find(t => t.id === tipoEntradaId);
      if (!tipoEntrada) {
        throw new HttpsError('not-found', 'Tipo de entrada no encontrado.');
      }

      // 3. Verifica capacidad disponible
      const vendidos = tipoEntrada.vendidos || 0;
      const disponibles = (tipoEntrada.capacidad || 0) - vendidos;
      if (disponibles < cantidad) {
        throw new HttpsError(
          'resource-exhausted',
          `Solo quedan ${disponibles} boletos disponibles de este tipo.`
        );
      }

      // 4. Validacion de edad minima
      const edadMinima = evento.edadMinima || 0;
      if (edadMinima > 0 && personaData.fechaNacimiento) {
        const edad = calcularEdad(personaData.fechaNacimiento);
        if (edad < edadMinima) {
          throw new HttpsError(
            'failed-precondition',
            `Este evento requiere edad minima de ${edadMinima} anios. La persona tiene ${edad}.`
          );
        }
      }

      // 5. Crea o actualiza persona_verificada
      const personaPayload = {
        ...personaData,
        edad: personaData.fechaNacimiento ? calcularEdad(personaData.fechaNacimiento) : null,
        verificadoFacialmente: !!personaData.awsRekognitionScore,
        fechaRegistro: admin.firestore.FieldValue.serverTimestamp(),
        ultimaActualizacion: admin.firestore.FieldValue.serverTimestamp()
      };

      let personaId;
      // Si tiene CURP, intentamos buscar primero por CURP para no duplicar
      if (personaData.curp) {
        const existente = await db
          .collection('personas_verificadas')
          .where('curp', '==', personaData.curp)
          .limit(1)
          .get();

        if (!existente.empty) {
          personaId = existente.docs[0].id;
          await db.collection('personas_verificadas').doc(personaId).update(personaPayload);
        }
      }
      if (!personaId) {
        const personaRef = await db.collection('personas_verificadas').add(personaPayload);
        personaId = personaRef.id;
      }

      // 6. Crea N boletos en estado pendiente
      const boletoIds = [];
      const lote = db.batch();

      for (let i = 0; i < cantidad; i++) {
        const boletoRef = db.collection('boletos').doc();
        lote.set(boletoRef, {
          eventoId,
          eventoNombre: evento.nombre,
          eventoFecha: evento.fecha,
          negocioId: evento.negocioId,
          sucursalId: evento.sucursalId || null,
          personaId,
          personaNombre: personaData.nombre || personaData.nombreCompleto || '',
          personaFotoURL: personaData.fotoSelfieURL || null,
          tipoEntradaId,
          tipoEntradaNombre: tipoEntrada.nombre,
          precio: tipoEntrada.precio,
          qrCode: null, // Se genera al confirmar pago
          status: 'pendiente',
          mercadopagoPaymentId: null,
          mercadopagoStatus: null,
          fechaCompra: admin.firestore.FieldValue.serverTimestamp(),
          fechaPago: null,
          fechaUso: null,
          emailEnviado: false
        });
        boletoIds.push(boletoRef.id);
      }

      await lote.commit();

      // 7. Crea preferencia MercadoPago
      const mp = new MercadoPagoConfig({ accessToken: MP_ACCESS_TOKEN.value() });
      const preference = new Preference(mp);

      const itemsMP = [{
        id: tipoEntradaId,
        title: `${evento.nombre} - ${tipoEntrada.nombre}`,
        description: `${cantidad} boleto(s) para ${evento.nombre}`,
        quantity: cantidad,
        unit_price: Number(tipoEntrada.precio),
        currency_id: 'MXN'
      }];

      const baseUrl = data.baseUrl || 'https://admon-santiantz.web.app';

      const cuerpoPreferencia = {
        items: itemsMP,
        payer: {
          name: personaData.nombre || '',
          surname: personaData.apellidoPaterno || '',
          email: personaData.email || undefined
        },
        external_reference: boletoIds.join(','),
        metadata: {
          evento_id: eventoId,
          persona_id: personaId,
          boleto_ids: boletoIds.join(',')
        },
        back_urls: {
          success: successUrl || `${baseUrl}/eventos.html?evento=${eventoId}&estado=success`,
          failure: failureUrl || `${baseUrl}/eventos.html?evento=${eventoId}&estado=failure`,
          pending: pendingUrl || `${baseUrl}/eventos.html?evento=${eventoId}&estado=pending`
        },
        auto_return: 'approved',
        notification_url: `https://us-east1-admon-santiantz.cloudfunctions.net/webhookMP`,
        statement_descriptor: 'SANTIANTZ EVENTS'
      };

      const prefResultado = await preference.create({ body: cuerpoPreferencia });

      // 8. Guarda referencia de la preferencia en cada boleto
      const lote2 = db.batch();
      boletoIds.forEach(id => {
        lote2.update(db.collection('boletos').doc(id), {
          mercadopagoPreferenceId: prefResultado.id
        });
      });
      await lote2.commit();

      return {
        ok: true,
        preferenceId: prefResultado.id,
        initPoint: prefResultado.init_point,
        sandboxInitPoint: prefResultado.sandbox_init_point,
        boletoIds,
        personaId
      };
    } catch (error) {
      console.error('Error creando preferencia - name:', error.name);
      console.error('Error creando preferencia - message:', error.message);
      console.error('Error creando preferencia - code:', error.code);
      console.error('Error creando preferencia - stack:', error.stack);
      console.error('Error creando preferencia - completo:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
      if (error instanceof HttpsError) throw error;
      throw new HttpsError(
        'internal',
        'Error al crear preferencia: ' + (error.message || error.name || 'desconocido'),
        { errorName: error.name, errorMessage: error.message, errorCode: error.code }
      );
    }
  }
);

/**
 * Calcula edad en anios completos a partir de fecha YYYY-MM-DD.
 */
function calcularEdad(fechaNacimientoISO) {
  const hoy = new Date();
  const nacimiento = new Date(fechaNacimientoISO);
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mesActual = hoy.getMonth();
  const mesNacimiento = nacimiento.getMonth();
  if (mesActual < mesNacimiento || (mesActual === mesNacimiento && hoy.getDate() < nacimiento.getDate())) {
    edad--;
  }
  return edad;
}
