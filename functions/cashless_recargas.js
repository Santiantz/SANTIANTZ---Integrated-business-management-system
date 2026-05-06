const { onCall, HttpsError, onRequest } = require('firebase-functions/v2/https');
const { onSchedule } = require('firebase-functions/v2/scheduler');
const { randomUUID } = require('crypto');
const admin = require('firebase-admin');
const {
  TENANT_ID,
  RECARGA_MIN_CENTAVOS,
  RECARGA_MAX_CENTAVOS,
  validarMontoEntero,
  validarWalletActivaNoExpirada
} = require('./cashless_helpers');
const { escribirLedger } = require('./cashless_ledger');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Inicia una recarga de billetera en efectivo
 *
 * @param {Object} request - {walletId, montoCentavos, notas?}
 * @returns {Object} {ok: true, recargaId, saldoNuevoCentavos}
 */
exports.iniciarRecargaEfectivo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoCentavos, notas } = request.data;

    if (!walletId || typeof montoCentavos !== 'number') {
      throw new HttpsError('invalid-argument', 'Faltan campos requeridos: walletId, montoCentavos');
    }

    console.log('[iniciarRecargaEfectivo] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoCentavos);

    try {
      // Validar monto
      validarMontoEntero(montoCentavos, RECARGA_MIN_CENTAVOS, RECARGA_MAX_CENTAVOS);

      // Usar transacción para atomicidad
      const resultado = await db.runTransaction(async (transaction) => {
        // Leer wallet
        const walletRef = db.collection('cashless_wallets').doc(walletId);
        const walletSnap = await transaction.get(walletRef);

        if (!walletSnap.exists) {
          throw new HttpsError('not-found', 'Wallet no encontrada');
        }

        const wallet = walletSnap.data();

        // Validar que wallet está activa y no expirada
        validarWalletActivaNoExpirada(wallet);

        // Calcular nuevo saldo
        const saldoAntes = wallet.saldoCentavos;
        const saldoDespues = saldoAntes + montoCentavos;

        // Generar ID para la recarga
        const recargaId = randomUUID();

        // Crear documento en cashless_recargas
        const recargaRef = db.collection('cashless_recargas').doc(recargaId);
        const recargaData = {
          recargaId,
          tenantId: TENANT_ID,
          walletId,
          eventoId: wallet.eventoId,
          negocioId: wallet.negocioId,
          personaId: wallet.personaId,
          montoCentavos,
          metodoPago: 'efectivo',
          saldoAntesCentavos: saldoAntes,
          saldoDespuesCentavos: saldoDespues,
          cajeroUid: uid,
          notas: notas || null,
          timestamp: admin.firestore.FieldValue.serverTimestamp(),
          cancelada: false
        };

        transaction.set(recargaRef, recargaData);

        // Actualizar wallet
        transaction.update(walletRef, {
          saldoCentavos: saldoDespues,
          totalRecargadoCentavos: wallet.totalRecargadoCentavos + montoCentavos,
          fechaUltimoMovimiento: admin.firestore.FieldValue.serverTimestamp()
        });

        // Escribir ledger
        escribirLedger(transaction, {
          tipo: 'recarga_efectivo',
          walletId,
          montoCentavos,
          saldoAntesCentavos: saldoAntes,
          saldoDespuesCentavos: saldoDespues,
          refDocId: recargaId,
          refColeccion: 'cashless_recargas',
          actorUid: uid,
          metadata: { metodoPago: 'efectivo' }
        });

        return {
          recargaId,
          saldoNuevoCentavos: saldoDespues
        };
      });

      console.log('[iniciarRecargaEfectivo] Recarga creada:', resultado.recargaId);

      return {
        ok: true,
        recargaId: resultado.recargaId,
        saldoNuevoCentavos: resultado.saldoNuevoCentavos
      };
    } catch (error) {
      console.error('[iniciarRecargaEfectivo] Error:', error);
      if (error instanceof HttpsError) {
        throw error;
      }
      throw new HttpsError('internal', 'Error al procesar recarga: ' + error.message);
    }
  }
);

/**
 * Inicia una recarga de billetera vía MercadoPago online
 *
 * FASE 2: Implementará:
 * - Validar monto en centavos
 * - Crear documento en cashless_recargas con estado='pendiente_mp'
 * - Llamar a MercadoPago Checkout Pro API (patrón como crearPreferencia.js)
 * - Devolver initPoint para que cliente abra en navegador
 *
 * @param {Object} request - {walletId, montoMxn, usuario_email, tenantId}
 * @returns {Object} {ok: true, recargaId: '...', initPoint: 'https://mercadopago.com/...'}
 */
exports.iniciarRecargaOnlineMP = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoMxn, usuario_email } = request.data;
    console.log('[iniciarRecargaOnlineMP] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoMxn);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      recargaId: 'TODO_GENERAR_ID',
      initPoint: 'https://mercadopago.com/TODO'
    };
  }
);

/**
 * Webhook para recibir notificaciones de MercadoPago sobre recargas
 *
 * FASE 2: Implementará:
 * - Recibir payload de MP (payment.id, status, external_reference)
 * - Validar firma de MP
 * - Si status='approved': actualizar cashless_recargas a estado='completado' y sumar saldo en wallet
 * - Si status='rejected': actualizar a estado='rechazado'
 * - Registrar en auditoría
 *
 * @param {Object} req - HTTP request con payload de MP
 * @param {Object} res - HTTP response
 */
exports.webhookRecargaMP = onRequest(
  { region: 'us-east1' },
  async (req, res) => {
    console.log('[webhookRecargaMP] Iniciado');

    if (req.method !== 'POST') {
      return res.status(405).send('Metodo no permitido');
    }

    // FASE 2: Lógica real aquí
    return res.status(200).json({ ok: true, mensaje: 'Webhook stub' });
  }
);

/**
 * Función programada: Verifica billeteras expiradas cada 3am (hora México)
 *
 * FASE 2: Implementará:
 * - Buscar billeteras con status='inactiva' por más de 30 días
 * - Transferir fondos al negocio (NO reembolso)
 * - Actualizar estado a 'expirada'
 * - Registrar en auditoría
 *
 * Cron: 0 3 * * * (3am diarios, zona horaria América/Mexico_City)
 */
exports.verificarExpiracionWallets = onSchedule(
  { schedule: '0 3 * * *', timeZone: 'America/Mexico_City', region: 'us-east1' },
  async (event) => {
    console.log('[verificarExpiracionWallets] Iniciado');

    // FASE 2: Lógica real aquí
    return { ok: true, procesadas: 0 };
  }
);
