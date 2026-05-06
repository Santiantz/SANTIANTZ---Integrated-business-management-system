const { randomUUID } = require('crypto');
const admin = require('firebase-admin');
const { TENANT_ID } = require('./cashless_helpers');

// Tipos válidos de ledger
const TIPOS_LEDGER_VALIDOS = [
  'wallet_creada',
  'recarga_efectivo',
  'consumo',
  'consumo_cancelado'
];

/**
 * Escribe una entrada en el ledger de cashless (append-only, inmutable)
 * Debe ejecutarse dentro de una transacción para garantizar atomicidad
 *
 * @param {Transaction} transaction - Transacción de Firestore
 * @param {Object} datos - Datos de la entrada del ledger:
 *   - tipo: string (wallet_creada, recarga_efectivo, consumo, consumo_cancelado)
 *   - walletId: string
 *   - montoCentavos: number (cantidad movida, puede ser 0 para wallet_creada)
 *   - saldoAntesCentavos: number (saldo antes de la operación)
 *   - saldoDespuesCentavos: number (saldo después de la operación)
 *   - refDocId: string (ID del documento que causó este registro: recargaId, consumoId, etc.)
 *   - refColeccion: string (colección del documento: cashless_recargas, cashless_consumos, etc.)
 *   - actorUid: string (UID del usuario que ejecutó la operación)
 *   - metadata: Object|null (datos adicionales específicos de la operación)
 * @returns {string} ledgerId del registro creado
 */
function escribirLedger(transaction, datos) {
  const {
    tipo,
    walletId,
    montoCentavos,
    saldoAntesCentavos,
    saldoDespuesCentavos,
    refDocId,
    refColeccion,
    actorUid,
    metadata
  } = datos;

  // Validaciones básicas
  if (!TIPOS_LEDGER_VALIDOS.includes(tipo)) {
    throw new Error(`Tipo de ledger inválido: ${tipo}. Válidos: ${TIPOS_LEDGER_VALIDOS.join(', ')}`);
  }

  if (!walletId || !refDocId || !refColeccion || !actorUid) {
    throw new Error('Faltan campos requeridos en datos del ledger');
  }

  // Generar ID único para el ledger
  const ledgerId = randomUUID();

  // Crear documento en cashless_ledger
  const ledgerRef = admin.firestore().collection('cashless_ledger').doc(ledgerId);

  const entradaLedger = {
    ledgerId,
    tenantId: TENANT_ID,
    tipo,
    walletId,
    montoCentavos,
    saldoAntesCentavos,
    saldoDespuesCentavos,
    refDocId,
    refColeccion,
    actorUid,
    metadata: metadata || null,
    timestamp: admin.firestore.FieldValue.serverTimestamp()
  };

  // Escribir dentro de la transacción para garantizar atomicidad
  transaction.set(ledgerRef, entradaLedger);

  return ledgerId;
}

module.exports = {
  escribirLedger,
  TIPOS_LEDGER_VALIDOS
};
