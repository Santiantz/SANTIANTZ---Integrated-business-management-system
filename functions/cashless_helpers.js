const { HttpsError } = require('firebase-functions/v2/https');

// ============================================================
// CONSTANTES GLOBALES CASHLESS
// ============================================================
const TENANT_ID = 'machaka';
const RECARGA_MIN_CENTAVOS = 5000;       // $50 MXN
const RECARGA_MAX_CENTAVOS = 50000000;   // $500,000 MXN
const CONSUMO_MIN_CENTAVOS = 100;        // $1 MXN
const CONSUMO_MAX_CENTAVOS = 50000000;   // $500,000 MXN
const VENTANA_CANCELACION_MS = 10 * 60 * 1000;  // 10 minutos

// ============================================================
// VALIDACIONES COMPARTIDAS
// ============================================================

/**
 * Valida que un monto esté en centavos y dentro de los límites
 * @param {number} monto - Valor en centavos
 * @param {number} min - Mínimo permitido en centavos
 * @param {number} max - Máximo permitido en centavos
 * @throws {HttpsError} Si el monto no es válido
 */
function validarMontoEntero(monto, min, max) {
  if (!Number.isInteger(monto)) {
    throw new HttpsError('invalid-argument', 'El monto debe ser un número entero en centavos.');
  }
  if (monto < min || monto > max) {
    throw new HttpsError('invalid-argument', `El monto debe estar entre ${min} y ${max} centavos.`);
  }
}

/**
 * Valida que una wallet esté activa y no expirada
 * @param {Object} walletData - Documento de wallet de Firestore
 * @throws {HttpsError} Si la wallet no está activa o está expirada
 */
function validarWalletActivaNoExpirada(walletData) {
  if (walletData.status !== 'activa') {
    throw new HttpsError('failed-precondition', `Wallet no está activa. Estado: ${walletData.status}`);
  }

  const ahora = Date.now();
  if (ahora > walletData.walletExpiraEn) {
    throw new HttpsError('failed-precondition', 'Wallet expirada. No se permiten operaciones.');
  }
}

/**
 * Obtiene el rol de un usuario desde la colección users
 * @param {Object} db - Instancia de Firestore
 * @param {string} uid - UID del usuario en Firebase Auth
 * @returns {Promise<string|null>} El rol del usuario o null si no existe
 */
async function obtenerRolUsuario(db, uid) {
  try {
    const docRef = db.collection('users').doc(uid);
    const docSnap = await docRef.get();
    if (!docSnap.exists) {
      return null;
    }
    return docSnap.data().rol || null;
  } catch (error) {
    console.error('[obtenerRolUsuario] Error:', error);
    return null;
  }
}

// ============================================================
// EXPORTACIONES
// ============================================================
module.exports = {
  TENANT_ID,
  RECARGA_MIN_CENTAVOS,
  RECARGA_MAX_CENTAVOS,
  CONSUMO_MIN_CENTAVOS,
  CONSUMO_MAX_CENTAVOS,
  VENTANA_CANCELACION_MS,
  validarMontoEntero,
  validarWalletActivaNoExpirada,
  obtenerRolUsuario
};
