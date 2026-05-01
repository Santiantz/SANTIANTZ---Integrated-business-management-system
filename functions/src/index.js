const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { onDocumentCreated, onDocumentUpdated } = require('firebase-functions/v2/firestore');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');
const { getAuth } = require('firebase-admin/auth');

initializeApp();
const db = getFirestore();

// ── Validaciones compartidas ─────────────────────────────────────────────────
function validateRequiredFields(data, fields) {
  const missing = fields.filter(f => data[f] === undefined || data[f] === null);
  if (missing.length > 0) {
    throw new HttpsError('invalid-argument', `Campos requeridos: ${missing.join(', ')}`);
  }
}

function validatePositiveNumber(value, fieldName) {
  if (typeof value !== 'number' || value < 0) {
    throw new HttpsError('invalid-argument', `${fieldName} debe ser un número positivo`);
  }
}

// ── Trigger: Nuevo usuario → crear perfil en Firestore ───────────────────────
exports.onUserCreated = onDocumentCreated('usuarios/{userId}', async (event) => {
  const userId = event.params.userId;
  const data = event.data.data();

  await db.collection('usuarios').doc(userId).update({
    creadoEn: FieldValue.serverTimestamp(),
    activo: true,
    ultimoAcceso: FieldValue.serverTimestamp(),
  });

  console.log(`Perfil inicializado para usuario: ${userId}`);
});

// ── Trigger: Nueva venta → actualizar totales del negocio ───────────────────
exports.onVentaCreada = onDocumentCreated('ventas/{ventaId}', async (event) => {
  const venta = event.data.data();
  const { negocioId, total } = venta;

  if (!negocioId || typeof total !== 'number') return;

  await db.collection('negocios').doc(negocioId).update({
    'estadisticas.ventasTotales': FieldValue.increment(1),
    'estadisticas.ingresosTotales': FieldValue.increment(total),
    'estadisticas.ultimaActualizacion': FieldValue.serverTimestamp(),
  });

  console.log(`Venta ${event.params.ventaId} registrada: $${total} en negocio ${negocioId}`);
});

// ── Trigger: Gasto creado → actualizar acumulado del negocio ─────────────────
exports.onGastoCreado = onDocumentCreated('gastos/{gastoId}', async (event) => {
  const gasto = event.data.data();
  const { negocioId, monto } = gasto;

  if (!negocioId || typeof monto !== 'number') return;

  await db.collection('negocios').doc(negocioId).update({
    'estadisticas.gastosTotales': FieldValue.increment(1),
    'estadisticas.egresosTotales': FieldValue.increment(monto),
    'estadisticas.ultimaActualizacion': FieldValue.serverTimestamp(),
  });
});

// ── Callable: Calcular resumen financiero de un periodo ──────────────────────
exports.calcularResumenFinanciero = onCall({ region: 'us-central1' }, async (request) => {
  if (!request.auth) {
    throw new HttpsError('unauthenticated', 'Se requiere autenticación');
  }

  const { negocioId, fechaInicio, fechaFin } = request.data;
  validateRequiredFields(request.data, ['negocioId', 'fechaInicio', 'fechaFin']);

  const userDoc = await db.collection('usuarios').doc(request.auth.uid).get();
  if (!userDoc.exists || userDoc.data().negocioId !== negocioId) {
    throw new HttpsError('permission-denied', 'Sin acceso a este negocio');
  }

  const inicio = new Date(fechaInicio);
  const fin = new Date(fechaFin);

  const [ventasSnap, gastosSnap] = await Promise.all([
    db.collection('ventas')
      .where('negocioId', '==', negocioId)
      .where('fecha', '>=', inicio)
      .where('fecha', '<=', fin)
      .where('estado', '==', 'completada')
      .get(),
    db.collection('gastos')
      .where('negocioId', '==', negocioId)
      .where('fecha', '>=', inicio)
      .where('fecha', '<=', fin)
      .get(),
  ]);

  const ingresos = ventasSnap.docs.reduce((acc, d) => acc + (d.data().total || 0), 0);
  const egresos = gastosSnap.docs.reduce((acc, d) => acc + (d.data().monto || 0), 0);

  return {
    periodo: { inicio: fechaInicio, fin: fechaFin },
    ingresos,
    egresos,
    utilidad: ingresos - egresos,
    totalVentas: ventasSnap.size,
    totalGastos: gastosSnap.size,
    generadoEn: new Date().toISOString(),
  };
});

// ── Callable: Validar y crear usuario con rol ─────────────────────────────────
exports.crearUsuario = onCall({ region: 'us-central1' }, async (request) => {
  if (!request.auth) {
    throw new HttpsError('unauthenticated', 'Se requiere autenticación');
  }

  const callerDoc = await db.collection('usuarios').doc(request.auth.uid).get();
  const callerData = callerDoc.data() || {};

  if (!['admin', 'superadmin'].includes(callerData.rol)) {
    throw new HttpsError('permission-denied', 'Solo admins pueden crear usuarios');
  }

  const { email, nombre, rol, negocioId } = request.data;
  validateRequiredFields(request.data, ['email', 'nombre', 'rol', 'negocioId']);

  const rolesPermitidos = ['empleado', 'gerente', 'admin'];
  if (!rolesPermitidos.includes(rol)) {
    throw new HttpsError('invalid-argument', `Rol inválido. Permitidos: ${rolesPermitidos.join(', ')}`);
  }

  if (callerData.rol === 'admin' && callerData.negocioId !== negocioId) {
    throw new HttpsError('permission-denied', 'No puedes crear usuarios en otro negocio');
  }

  const auth = getAuth();
  const userRecord = await auth.createUser({ email, displayName: nombre });

  await db.collection('usuarios').doc(userRecord.uid).set({
    uid: userRecord.uid,
    email,
    nombre,
    rol,
    negocioId,
    activo: true,
    creadoEn: FieldValue.serverTimestamp(),
    creadoPor: request.auth.uid,
  });

  return { uid: userRecord.uid, mensaje: 'Usuario creado exitosamente' };
});

// ── Callable: Validar stock antes de venta ────────────────────────────────────
exports.validarStock = onCall({ region: 'us-central1' }, async (request) => {
  if (!request.auth) {
    throw new HttpsError('unauthenticated', 'Se requiere autenticación');
  }

  const { negocioId, items } = request.data;
  validateRequiredFields(request.data, ['negocioId', 'items']);

  if (!Array.isArray(items) || items.length === 0) {
    throw new HttpsError('invalid-argument', 'items debe ser un array no vacío');
  }

  const resultados = await Promise.all(
    items.map(async (item) => {
      const inventarioRef = db.collection('inventario').doc(item.inventarioId);
      const doc = await inventarioRef.get();

      if (!doc.exists || doc.data().negocioId !== negocioId) {
        return { inventarioId: item.inventarioId, disponible: false, motivo: 'Producto no encontrado' };
      }

      const stockActual = doc.data().cantidad || 0;
      const disponible = stockActual >= item.cantidad;

      return {
        inventarioId: item.inventarioId,
        nombre: doc.data().nombre,
        stockActual,
        solicitado: item.cantidad,
        disponible,
        motivo: disponible ? null : `Stock insuficiente (disponible: ${stockActual})`,
      };
    })
  );

  const todoDisponible = resultados.every(r => r.disponible);
  return { valido: todoDisponible, items: resultados };
});
