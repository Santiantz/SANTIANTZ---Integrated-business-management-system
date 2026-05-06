const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { randomUUID } = require('crypto');
const admin = require('firebase-admin');
const {
  TENANT_ID,
  CONSUMO_MIN_CENTAVOS,
  CONSUMO_MAX_CENTAVOS,
  VENTANA_CANCELACION_MS,
  validarMontoEntero,
  validarWalletActivaNoExpirada,
  obtenerRolUsuario
} = require('./cashless_helpers');
const { escribirLedger } = require('./cashless_ledger');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Registra un consumo (venta) en la billetera del cliente
 *
 * @param {Object} request - {walletId, montoCentavos, concepto, productosJSON?}
 * @returns {Object} {ok: true, consumoId, saldoNuevoCentavos}
 */
exports.registrarConsumo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { walletId, montoCentavos, concepto, productosJSON } = request.data;

    if (!walletId || typeof montoCentavos !== 'number' || !concepto) {
      throw new HttpsError('invalid-argument', 'Faltan campos requeridos: walletId, montoCentavos, concepto');
    }

    console.log('[registrarConsumo] Invocacion por uid:', uid, 'walletId:', walletId, 'monto:', montoCentavos);

    try {
      // Validar monto
      validarMontoEntero(montoCentavos, CONSUMO_MIN_CENTAVOS, CONSUMO_MAX_CENTAVOS);

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

        // Validar saldo suficiente
        if (wallet.saldoCentavos < montoCentavos) {
          throw new HttpsError('failed-precondition', 'Saldo insuficiente para realizar este consumo');
        }

        // Calcular nuevo saldo
        const saldoAntes = wallet.saldoCentavos;
        const saldoDespues = saldoAntes - montoCentavos;

        // Generar ID para el consumo
        const consumoId = randomUUID();

        // Crear documento en cashless_consumos
        const consumoRef = db.collection('cashless_consumos').doc(consumoId);
        const consumoData = {
          consumoId,
          tenantId: TENANT_ID,
          walletId,
          eventoId: wallet.eventoId,
          negocioId: wallet.negocioId,
          personaId: wallet.personaId,
          montoCentavos,
          concepto,
          productosJSON: productosJSON || null,
          saldoAntesCentavos: saldoAntes,
          saldoDespuesCentavos: saldoDespues,
          bartenderUid: uid,
          timestamp: admin.firestore.FieldValue.serverTimestamp(),
          cancelado: false,
          canceladoPor: null,
          canceladoEn: null,
          motivoCancelacion: null
        };

        transaction.set(consumoRef, consumoData);

        // Actualizar wallet
        transaction.update(walletRef, {
          saldoCentavos: saldoDespues,
          totalConsumidoCentavos: wallet.totalConsumidoCentavos + montoCentavos,
          fechaUltimoMovimiento: admin.firestore.FieldValue.serverTimestamp()
        });

        // Escribir ledger
        escribirLedger(transaction, {
          tipo: 'consumo',
          walletId,
          montoCentavos,
          saldoAntesCentavos: saldoAntes,
          saldoDespuesCentavos: saldoDespues,
          refDocId: consumoId,
          refColeccion: 'cashless_consumos',
          actorUid: uid,
          metadata: { concepto }
        });

        return {
          consumoId,
          saldoNuevoCentavos: saldoDespues
        };
      });

      console.log('[registrarConsumo] Consumo creado:', resultado.consumoId);

      return {
        ok: true,
        consumoId: resultado.consumoId,
        saldoNuevoCentavos: resultado.saldoNuevoCentavos
      };
    } catch (error) {
      console.error('[registrarConsumo] Error:', error);
      if (error instanceof HttpsError) {
        throw error;
      }
      throw new HttpsError('internal', 'Error al registrar consumo: ' + error.message);
    }
  }
);

/**
 * Cancela un consumo (solo propietario o admin_negocio, dentro de 10 minutos)
 *
 * @param {Object} request - {consumoId, motivo}
 * @returns {Object} {ok: true, consumoId, saldoNuevoCentavos}
 */
exports.cancelarConsumo = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { consumoId, motivo } = request.data;

    if (!consumoId || !motivo) {
      throw new HttpsError('invalid-argument', 'Faltan campos requeridos: consumoId, motivo');
    }

    console.log('[cancelarConsumo] Invocacion por uid:', uid, 'consumoId:', consumoId);

    try {
      // Verificar rol del usuario
      const rol = await obtenerRolUsuario(db, uid);
      if (rol !== 'propietario' && rol !== 'admin_negocio') {
        throw new HttpsError('permission-denied', 'Solo propietario o admin_negocio pueden cancelar consumos');
      }

      // Leer consumo
      const consumoSnap = await db.collection('cashless_consumos').doc(consumoId).get();
      if (!consumoSnap.exists) {
        throw new HttpsError('not-found', 'Consumo no encontrado');
      }

      const consumo = consumoSnap.data();

      // Validar que no está ya cancelado
      if (consumo.cancelado === true) {
        throw new HttpsError('failed-precondition', 'Este consumo ya está cancelado');
      }

      // Validar ventana de cancelación (10 minutos)
      const timestampMs = consumo.timestamp.toMillis ? consumo.timestamp.toMillis() : consumo.timestamp;
      const tiempoTranscurrido = Date.now() - timestampMs;

      if (tiempoTranscurrido > VENTANA_CANCELACION_MS) {
        throw new HttpsError('failed-precondition', 'La ventana de cancelación (10 minutos) ha expirado');
      }

      // Usar transacción para atomicidad
      const resultado = await db.runTransaction(async (transaction) => {
        // Leer wallet
        const walletRef = db.collection('cashless_wallets').doc(consumo.walletId);
        const walletSnap = await transaction.get(walletRef);

        if (!walletSnap.exists) {
          throw new HttpsError('not-found', 'Wallet no encontrada');
        }

        const wallet = walletSnap.data();

        // Calcular devolución
        const saldoAntes = wallet.saldoCentavos;
        const saldoDespues = saldoAntes + consumo.montoCentavos;

        // Actualizar wallet (devolver dinero)
        transaction.update(walletRef, {
          saldoCentavos: saldoDespues,
          totalConsumidoCentavos: wallet.totalConsumidoCentavos - consumo.montoCentavos
        });

        // Actualizar consumo (marcar como cancelado)
        const consumoRef = db.collection('cashless_consumos').doc(consumoId);
        transaction.update(consumoRef, {
          cancelado: true,
          canceladoPor: uid,
          canceladoEn: admin.firestore.FieldValue.serverTimestamp(),
          motivoCancelacion: motivo
        });

        // Escribir ledger
        escribirLedger(transaction, {
          tipo: 'consumo_cancelado',
          walletId: consumo.walletId,
          montoCentavos: consumo.montoCentavos,
          saldoAntesCentavos: saldoAntes,
          saldoDespuesCentavos: saldoDespues,
          refDocId: consumoId,
          refColeccion: 'cashless_consumos',
          actorUid: uid,
          metadata: { motivoCancelacion: motivo }
        });

        return {
          consumoId,
          saldoNuevoCentavos: saldoDespues
        };
      });

      console.log('[cancelarConsumo] Consumo cancelado:', resultado.consumoId);

      return {
        ok: true,
        consumoId: resultado.consumoId,
        saldoNuevoCentavos: resultado.saldoNuevoCentavos
      };
    } catch (error) {
      console.error('[cancelarConsumo] Error:', error);
      if (error instanceof HttpsError) {
        throw error;
      }
      throw new HttpsError('internal', 'Error al cancelar consumo: ' + error.message);
    }
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
