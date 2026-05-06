const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { randomUUID } = require('crypto');
const admin = require('firebase-admin');
const { TENANT_ID } = require('./cashless_helpers');
const { escribirLedger } = require('./cashless_ledger');

if (!admin.apps.length) {
  admin.initializeApp();
}

const db = admin.firestore();

/**
 * Crea una nueva billetera Cashless para un cliente en un evento
 *
 * @param {Object} request - {personaId, eventoId, boletoId, negocioId, usuarioUid}
 * @returns {Object} {ok: true, walletId, qrCode, walletExpiraEn}
 */
exports.crearWalletCashless = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { personaId, eventoId, boletoId, negocioId, usuarioUid } = request.data;

    if (!personaId || !eventoId || !boletoId || !negocioId || !usuarioUid) {
      throw new HttpsError('invalid-argument', 'Faltan campos requeridos: personaId, eventoId, boletoId, negocioId, usuarioUid');
    }

    console.log('[crearWalletCashless] Invocacion por uid:', uid, 'personaId:', personaId, 'eventoId:', eventoId);

    try {
      // Leer persona y evento
      const personaSnap = await db.collection('personas_verificadas').doc(personaId).get();
      if (!personaSnap.exists) {
        throw new HttpsError('not-found', 'Persona no encontrada en personas_verificadas');
      }
      const persona = personaSnap.data();

      const eventoSnap = await db.collection('eventos').doc(eventoId).get();
      if (!eventoSnap.exists) {
        throw new HttpsError('not-found', 'Evento no encontrado');
      }
      const evento = eventoSnap.data();

      // Validar que evento está activo
      if (evento.estado !== 'activo') {
        throw new HttpsError('failed-precondition', `Evento no está activo. Estado: ${evento.estado}`);
      }

      // Validar que evento tiene campos requeridos
      if (!evento.fechaFin || typeof evento.diasGracia !== 'number') {
        throw new HttpsError('failed-precondition', 'Evento no tiene fechaFin o diasGracia configurados');
      }

      // Verificar que no existe wallet activa para esta persona y evento
      const walletExistente = await db.collection('cashless_wallets')
        .where('eventoId', '==', eventoId)
        .where('personaId', '==', personaId)
        .where('status', '==', 'activa')
        .limit(1)
        .get();

      if (!walletExistente.empty) {
        throw new HttpsError('failed-precondition', 'Ya existe una wallet activa para esta persona en este evento');
      }

      // Calcular fecha de expiración
      const fechaFinMs = evento.fechaFin.toMillis ? evento.fechaFin.toMillis() : evento.fechaFin;
      const walletExpiraEn = fechaFinMs + (evento.diasGracia * 86400000);

      // Generar IDs únicos
      const walletId = randomUUID();
      const qrCode = randomUUID();

      // Crear documento en cashless_wallets
      const walletRef = db.collection('cashless_wallets').doc(walletId);
      const walletData = {
        walletId,
        tenantId: TENANT_ID,
        eventoId,
        negocioId,
        personaId,
        boletoId,
        usuarioUid,
        personaNombre: persona.nombre || '',
        personaFotoURL: persona.fotoURL || null,
        qrCode,
        saldoCentavos: 0,
        totalRecargadoCentavos: 0,
        totalConsumidoCentavos: 0,
        status: 'activa',
        walletExpiraEn,
        fechaCreacion: admin.firestore.FieldValue.serverTimestamp(),
        fechaUltimoMovimiento: admin.firestore.FieldValue.serverTimestamp(),
        creadoPorUid: uid
      };

      // Usar transacción para crear wallet y escribir ledger atomicamente
      await db.runTransaction(async (transaction) => {
        transaction.set(walletRef, walletData);

        // Escribir entrada en ledger
        escribirLedger(transaction, {
          tipo: 'wallet_creada',
          walletId,
          montoCentavos: 0,
          saldoAntesCentavos: 0,
          saldoDespuesCentavos: 0,
          refDocId: walletId,
          refColeccion: 'cashless_wallets',
          actorUid: uid,
          metadata: { eventoId, personaId }
        });
      });

      console.log('[crearWalletCashless] Wallet creada:', walletId);

      return {
        ok: true,
        walletId,
        qrCode,
        walletExpiraEn
      };
    } catch (error) {
      console.error('[crearWalletCashless] Error:', error);
      if (error instanceof HttpsError) {
        throw error;
      }
      throw new HttpsError('internal', 'Error al crear wallet: ' + error.message);
    }
  }
);

/**
 * Consulta el saldo de una billetera por código QR
 *
 * @param {Object} request - {qrCode}
 * @returns {Object} {ok: true, walletId, saldoCentavos, status, personaNombre, personaFotoURL, walletExpiraEn}
 */
exports.consultarWalletPorQR = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 30 },
  async (request) => {
    const uid = request.auth?.uid;

    if (!uid) {
      throw new HttpsError('unauthenticated', 'Debes iniciar sesion para usar esta funcion.');
    }

    const { qrCode } = request.data;

    if (!qrCode) {
      throw new HttpsError('invalid-argument', 'El qrCode es requerido');
    }

    console.log('[consultarWalletPorQR] Invocacion por uid:', uid, 'qrCode:', qrCode);

    try {
      // Buscar wallet por QR
      const walletSnap = await db.collection('cashless_wallets')
        .where('qrCode', '==', qrCode)
        .limit(1)
        .get();

      if (walletSnap.empty) {
        throw new HttpsError('not-found', 'Wallet no encontrada');
      }

      const walletDoc = walletSnap.docs[0];
      const wallet = walletDoc.data();

      // Verificar expiración: si está vencida y activa, marcar como expirada
      const ahora = Date.now();
      if (wallet.status === 'activa' && ahora > wallet.walletExpiraEn) {
        await walletDoc.ref.update({
          status: 'expirada'
        });
        wallet.status = 'expirada';
      }

      return {
        ok: true,
        walletId: wallet.walletId,
        saldoCentavos: wallet.status === 'expirada' ? 0 : wallet.saldoCentavos,
        status: wallet.status,
        personaNombre: wallet.personaNombre,
        personaFotoURL: wallet.personaFotoURL,
        walletExpiraEn: wallet.walletExpiraEn
      };
    } catch (error) {
      console.error('[consultarWalletPorQR] Error:', error);
      if (error instanceof HttpsError) {
        throw error;
      }
      throw new HttpsError('internal', 'Error al consultar wallet: ' + error.message);
    }
  }
);
