const { onCall, HttpsError } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Crea una nueva billetera Cashless para un usuario
 *
 * FASE 2: Implementará:
 * - Verificar que el usuario existe en users
 * - Crear documento en cashless_wallets con saldoCentavos=0
 * - Asignar QR único (UUID v4)
 * - Inicializar auditoría
 *
 * @param {Object} request - {tenantId, usuario_email}
 * @returns {Object} {ok: true, walletId: '...', qrCode: '...'}
 */
exports.crearWalletCashless = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    console.log('[crearWalletCashless] Invocacion por uid:', uid);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      walletId: 'TODO_GENERAR_ID',
      qrCode: 'TODO_GENERAR_QR'
    };
  }
);

/**
 * Consulta el saldo de una billetera por código QR
 *
 * FASE 2: Implementará:
 * - Buscar documento en cashless_wallets por qrCode
 * - Devolver saldoCentavos actual
 * - Registrar consulta en auditoría
 *
 * @param {Object} request - {qrCode}
 * @returns {Object} {ok: true, saldoCentavos: 0, usuario_email: '...'}
 */
exports.consultarWalletPorQR = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { qrCode } = request.data;
    console.log('[consultarWalletPorQR] Invocacion por uid:', uid, 'qrCode:', qrCode);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      saldoCentavos: 0,
      usuario_email: 'TODO@example.com'
    };
  }
);
