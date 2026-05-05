/**
 * BOLETERA SANTIANTZ EVENTS - Cloud Functions
 *
 * Punto de entrada que importa y exporta los 6 endpoints:
 *   - healthcheck         (HTTP publico)
 *   - verificarRostro     (Callable)
 *   - crearPreferencia    (Callable)
 *   - webhookMP           (HTTP publico, recibe MercadoPago)
 *   - generarBoleto       (Callable interna)
 *   - enviarEmail         (Callable interna)
 *
 * Inicializa firebase-admin una sola vez para que todos los modulos
 * compartan la misma conexion a Firestore y Storage.
 */

const { onRequest } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');

// Inicializa firebase-admin una sola vez
if (!admin.apps.length) {
  admin.initializeApp();
}

// ============================================================
// HEALTHCHECK - Endpoint publico para verificar que el deploy vive
// ============================================================
exports.healthcheck = onRequest(
  { region: 'us-east1', cors: true, memory: '256MiB' },
  (req, res) => {
    res.status(200).json({
      ok: true,
      project: 'Boletera Santiantz Events',
      phase: '2 - Codigo real',
      timestamp: new Date().toISOString(),
      message: 'Cloud Functions activas con codigo real implementado.',
      endpoints: [
        'verificarRostro (callable)',
        'crearPreferencia (callable)',
        'webhookMP (https)',
        'generarBoleto (callable)',
        'enviarEmail (callable)'
      ]
    });
  }
);

// ============================================================
// MODULOS DE NEGOCIO - Cada uno en su propio archivo
// ============================================================
exports.verificarRostro = require('./verificarRostro').verificarRostro;
exports.crearPreferencia = require('./crearPreferencia').crearPreferencia;
exports.webhookMP = require('./webhookMP').webhookMP;
exports.generarBoleto = require('./generarBoleto').generarBoleto;
exports.enviarEmail = require('./enviarEmail').enviarEmail;
