const { onCall, HttpsError } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Registra un consumo (venta) en la billetera del cliente
 *
 * FASE 2: Implementará:
 * - Validar que wallet existe y tiene saldo suficiente
 * - Usar runTransaction para:
 *   a) Restar saldoCentavos de la wallet
 *   b) Crear documento en cashless_consumos con estado='completado'
 *   c) Crear entrada en ledger inmutable
 *   d) Registrar en auditoría
 * - Devolver confirmación y nuevo saldo
 *
 * @param {Object} request - {walletId, montoCentavos, descripcion, tenantId}
 * @returns {Object} {ok: true, consumoId: '...', saldoNuevo: 0, timestamp: ISO}
 */
exports.registrarConsumo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoCentavos, descripcion } = request.data;
    console.log('[registrarConsumo] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoCentavos);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      consumoId: 'TODO_GENERAR_ID',
      saldoNuevo: 0,
      timestamp: new Date().toISOString()
    };
  }
);

/**
 * Cancela un consumo (solo admin, dentro de 10 minutos)
 *
 * FASE 2: Implementará:
 * - Verificar que uid tiene rol 'admin_negocio' o 'propietario'
 * - Buscar consumo en cashless_consumos por consumoId
 * - Validar que transcurrieron menos de 10 minutos
 * - Usar runTransaction para:
 *   a) Sumar saldoCentavos nuevamente a la wallet
 *   b) Actualizar consumo a estado='cancelado'
 *   c) Crear documento en cashless_reembolsos
 *   d) Registrar en auditoría
 *
 * @param {Object} request - {consumoId, motivo, tenantId}
 * @returns {Object} {ok: true, saldoRestituido: 0}
 */
exports.cancelarConsumo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { consumoId, motivo } = request.data;
    console.log('[cancelarConsumo] Invocacion por uid:', uid, 'consumoId:', consumoId);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      saldoRestituido: 0
    };
  }
);

/**
 * Inicia un reembolso parcial/total de la billetera (cliente)
 *
 * FASE 2: Implementará:
 * - Validar monto en centavos (máximo saldo actual)
 * - Crear documento en cashless_reembolsos con estado='solicitado'
 * - Notificar a admin para revisión
 * - Devolver confirmación
 *
 * @param {Object} request - {walletId, montoCentavos, motivo, tenantId}
 * @returns {Object} {ok: true, reembolsoId: '...', estado: 'solicitado'}
 */
exports.solicitarReembolso = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoCentavos, motivo } = request.data;
    console.log('[solicitarReembolso] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoCentavos);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      reembolsoId: 'TODO_GENERAR_ID',
      estado: 'solicitado'
    };
  }
);

/**
 * Procesa un reembolso aprobado (solo admin)
 *
 * FASE 2: Implementará:
 * - Verificar que uid tiene rol 'admin_negocio' o 'propietario'
 * - Buscar reembolso en cashless_reembolsos
 * - Usar runTransaction para:
 *   a) Restar saldoCentavos de la wallet
 *   b) Actualizar reembolso a estado='completado' o 'rechazado'
 *   c) Registrar transferencia en colección cashless_reembolsos (registro inmutable)
 *   d) Registrar en auditoría
 * - Notificar al cliente
 *
 * @param {Object} request - {reembolsoId, aprobado: boolean, razonRechazo?: string, tenantId}
 * @returns {Object} {ok: true, estado: 'completado' | 'rechazado'}
 */
exports.procesarReembolso = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { reembolsoId, aprobado, razonRechazo } = request.data;
    console.log('[procesarReembolso] Invocacion por uid:', uid, 'reembolsoId:', reembolsoId, 'aprobado:', aprobado);

    // FASE 2: Lógica real aquí
    return {
      ok: true,
      estado: aprobado ? 'completado' : 'rechazado'
    };
  }
);
