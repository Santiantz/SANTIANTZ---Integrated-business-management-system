# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Resumen del Proyecto

**SANTIANTZ** es un sistema integrado de gestión empresarial (ERP) basado en Firebase, diseñado para negocios de eventos y servicios. Proporciona:
- Gestión de múltiples negocios con separación por inquilino
- Sistema de control de ventas, gastos e inventario
- Gestión de nóminas y empleados
- Generación de reportes financieros
- Control de eventos
- Arquitectura sin servidor con Cloud Functions

## Estructura del Proyecto

```
SANTIANTZ/
├── public/                  # Frontend SPA (Single Page Application)
│   ├── index.html          # Aplicación principal (montada en Firebase Hosting)
│   └── firebase-config.js  # Configuración de Firebase para el cliente
├── functions/              # Cloud Functions (Node.js 20)
│   ├── src/
│   │   └── index.js       # Funciones callable y triggers de Firestore
│   ├── package.json       # Dependencias y scripts
│   └── .eslintrc.js       # Configuración de linting
├── firestore.rules        # Reglas de seguridad de Firestore (Access Control)
├── firestore.indexes.json # Índices compuestos de Firestore
├── storage.rules          # Reglas de seguridad de Cloud Storage
├── firebase.json          # Configuración de Firebase (hosting, functions, firestore)
└── .github/workflows/     # CI/CD con GitHub Actions
```

## Arquitectura de Datos (Firestore)

### Colecciones Principales

**usuarios/{userId}** - Perfiles de usuarios
- Campos clave: `uid`, `email`, `nombre`, `rol`, `negocioId`, `activo`, `creadoEn`, `ultimoAcceso`
- Roles: `superadmin`, `admin`, `gerente`, `empleado`
- Cada usuario pertenece a un negocio (excepto superadmin)

**negocios/{negocioId}** - Empresas/negocios
- Planes: `basico`, `profesional`, `enterprise`
- Contiene estadísticas agregadas: `ventasTotales`, `ingresosTotales`, `egresosTotales`
- Cada negocio tiene subcol acciones heredadas para acceso

**ventas/{ventaId}** - Registro de transacciones de ventas
- Estados: `pendiente`, `completada`, `cancelada`
- Trigger automático: actualiza estadísticas del negocio

**gastos/{gastoId}** - Registro de egresos
- Trigger automático: actualiza estadísticas del negocio

**empleados/{empleadoId}** - Nómina de personal

**nominas/{nominaId}** - Registros de nómina por periodo

**inventario/{itemId}** - Control de stock

**eventos/{eventoId}** - Gestión de eventos
- Tipos: `boda`, `quinceañera`, `corporativo`, `otro`

**reportes/{reporteId}** - Reportes generados

### Modelo de Control de Acceso

Implementado en `firestore.rules` con funciones helper:
- **isAuth()** - Usuario autenticado
- **belongsToBusiness(negocioId)** - Usuario pertenece al negocio
- **isAdmin() / isSuperAdmin()** - Nivel de rol
- **isManagerOrAbove()** - Gerente o superior
- **isOwner(resource)** - Es propietario del documento

**Patrón de acceso:**
```
- Lectura: Requerida autenticación + pertenencia al negocio
- Crear: Validación de campos + autorización de rol
- Actualizar: No cambiar campos críticos (negocioId, creadoPor, uid)
- Eliminar: Generalmente solo admin/superadmin
```

## Cloud Functions (functions/src/index.js)

### Funciones Callable (HTTP)

Todas requieren autenticación y validan permisos del usuario.

**calcularResumenFinanciero(negocioId, fechaInicio, fechaFin)**
- Agrega ventas completadas y gastos en un rango de fechas
- Devuelve: ingresos, egresos, utilidad, conteos
- Validación: usuario pertenece al negocio

**crearUsuario(email, nombre, rol, negocioId)**
- Solo admin/superadmin
- Crea cuenta en Firebase Auth + documento en Firestore
- Admin no puede crear usuarios en otros negocios
- Roles permitidos: `empleado`, `gerente`, `admin`

**validarStock(negocioId, items[])**
- Verifica disponibilidad antes de crear venta
- Devuelve stock disponible por item y motivos de falta

### Triggers de Firestore

**onUserCreated** - Al crear usuario
- Inicializa: `creadoEn`, `activo`, `ultimoAcceso`

**onVentaCreada** - Al crear venta
- Incrementa `estadisticas.ventasTotales` y `ingresosTotales` del negocio

**onGastoCreado** - Al crear gasto
- Incrementa `estadisticas.gastosTotales` y `egresosTotales` del negocio

### Patrones de Desarrollo

```javascript
// Validación de campos requeridos
validateRequiredFields(data, ['campo1', 'campo2']);

// Validación de números positivos
validatePositiveNumber(value, 'nombreCampo');

// Incrementos con FieldValue
'estadisticas.total': FieldValue.increment(valor)

// Timestamps del servidor
'creadoEn': FieldValue.serverTimestamp()
```

## Flujos de Autenticación y Autorización

1. **Login**: Usuario se autentica en Frontend → Firebase Auth
2. **Consultas**: Frontend incluye token en request
3. **Firestore Security Rules**: Valida token + permisos en colección
4. **Cloud Functions**: Verifican `request.auth.uid` + acceso a negocio

## Desarrollo y Deployment

### Comandos Principales

```bash
# Cloud Functions
cd functions
npm install
npm run lint              # ESLint (Google config)
npm run serve             # Emuladores locales (Firestore + Functions)
npm run deploy            # Deploy a Firebase
npm run logs              # Ver logs de funciones

# Verificar configuración
firebase --version
firebase projects:list
```

### CI/CD (GitHub Actions)

**deploy.yml** - Deployment automático a Firebase
- Trigger: Push a rama `main` (con filter de archivos relevantes)
- Deploy: Firestore rules, Cloud Storage rules, Cloud Functions
- Requisitos: Variables de entorno `FIREBASE_TOKEN`

**main.yml** - Workflow manual
- Trigger: `workflow_dispatch` (manual desde UI)
- Mismo comportamiento que deploy.yml

### Reglas Importantes

- **No pushear a main directamente** - Usar ramas feature y PRs
- **Probar security rules localmente** antes de deploy:
  ```bash
  firebase emulators:start --only firestore
  # En otra terminal: firebase functions:shell
  ```
- **Todas las funciones callable validan autenticación** - No confiar en cliente
- **Firestore es fuente de verdad** - Las estadísticas se calculan desde triggers, no desde cliente

## Patrones de Búsqueda Comunes

### Obtener datos de negocio actual
```javascript
const userDoc = await db.collection('usuarios').doc(request.auth.uid).get();
const negocioId = userDoc.data().negocioId;
```

### Filtrar por rango de fechas
```javascript
.where('fecha', '>=', new Date(fechaInicio))
.where('fecha', '<=', new Date(fechaFin))
```

### Queries paralelos
```javascript
const [ventasSnap, gastosSnap] = await Promise.all([
  db.collection('ventas').where(...).get(),
  db.collection('gastos').where(...).get(),
]);
```

## Consideraciones de Seguridad

1. **Firestore Rules es la capa de seguridad principal** - No confiar en validaciones del cliente
2. **notChanging() helper** - Previene cambios no autorizados de campos críticos
3. **Validación de rol antes de acciones** - `isManagerOrAbove()`, `isSuperAdmin()`
4. **Auditoria de cambios** - Registrar `creadoPor` y `creadoEn` en operaciones críticas
5. **Tokens de autenticación** - Generados por Firebase Auth, no hardcodear credentials

## Notas de Mantenimiento

- **Índices compuestos**: Firestore requiere índices para queries con múltiples campos - se actualizan en `firestore.indexes.json`
- **FieldValue helpers**: Usar `FieldValue.increment()` para contadores atómicos
- **Transacciones**: Para operaciones multi-documento, considerar batch writes
- **Rate limiting**: Cloud Functions tienen límites según plan Firebase

## Cuando Necesites...

### Agregar nueva colección
1. Definir estructura en Firestore rules
2. Implementar helper functions de acceso
3. Escribir validaciones específicas
4. Agregar reglas read/write/delete
5. Crear índices en `firestore.indexes.json` si es necesario

### Agregar nueva función Cloud
1. Crear función `onCall` o `onDocument` en `functions/src/index.js`
2. Validar autenticación y permisos
3. Implementar lógica de negocio
4. Retornar error con `HttpsError` para fallos
5. Test localmente con emuladores

### Debuggear reglas de Firestore
1. Usar emuladores locales: `firebase emulators:start --only firestore`
2. Ver logs: `firebase functions:shell` (para testing de rules)
3. Verificar `request.auth`, `resource.data` en context

## Referencias de Estilo de Código

- **ESLint**: Google config (functions/.eslintrc.js)
- **Nombres**: camelCase para variables/funciones, PascalCase para clases
- **Idioma**: Comentarios y nombres de variables en español (convención del proyecto)
- **Funciones helpers**: Definir al inicio de archivo para reutilizar
