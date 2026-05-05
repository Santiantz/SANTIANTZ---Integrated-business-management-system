const { onCall, HttpsError, onRequest } = require('firebase-functions/v2/https');
const { onSchedule } = require('firebase-functions/v2/scheduler');
const admin = require('firebase-admin');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Inicia una recarga de billetera en efectivo
 *
 * FASE 2: Implementará:
 * - Validar monto en centavos (mínimo 1000 centavos = $10.00 MXN)
 * - Crear documento en cashless_recargas con estado='pendiente_pago'
 * - Generar referencia único para taquilla
 * - Devolver referencia y código de confirmación
 *
 * @param {Object} request - {walletId, montoMxn, tenantId}
 * @returns {Object} {ok: true, recargaId: '...', referencia: '...', estado: 'pendiente_pago'}
 */
exports.iniciarRecargaEfectivo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoMxn } = request.data;
    console.log('[iniciarRecargaEfectivo] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoMxn);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      recargaId: 'TODO_GENERAR_ID',
      referencia: 'TODO_GENERAR_REFERENCIA',
      estado: 'pendiente_pago'
    };
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
