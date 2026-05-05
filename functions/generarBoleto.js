/**
 * GENERAR BOLETO - PDF con QR
 *
 * Crea un PDF profesional con la informacion del boleto y un QR
 * unico embebido. Sube el PDF a Firebase Storage y guarda la URL
 * publica en el documento del boleto.
 *
 * Se expone como:
 *   - generarBoleto (Callable) para llamada manual desde el frontend
 *   - generarBoletoInternal (funcion plana) para uso del webhook
 */

const { onCall, HttpsError } = require('firebase-functions/v2/https');
const admin = require('firebase-admin');
const PDFDocument = require('pdfkit');
const QRCode = require('qrcode');

// ============================================================
// FUNCION INTERNA - reutilizable desde el webhook
// ============================================================
async function generarBoletoInternal(boletoId) {
  if (!boletoId) throw new Error('boletoId es requerido');

  const db = admin.firestore();
  const bucket = admin.storage().bucket();

  // 1. Lee boleto
  const boletoRef = db.collection('boletos').doc(boletoId);
  const boletoSnap = await boletoRef.get();
  if (!boletoSnap.exists) throw new Error('Boleto no encontrado');
  const boleto = boletoSnap.data();

  if (!boleto.qrCode) throw new Error('Boleto no tiene QR generado aun');

  // 2. Lee evento y persona
  const [eventoSnap, personaSnap] = await Promise.all([
    db.collection('eventos').doc(boleto.eventoId).get(),
    db.collection('personas_verificadas').doc(boleto.personaId).get()
  ]);

  const evento = eventoSnap.exists ? eventoSnap.data() : {};
  const persona = personaSnap.exists ? personaSnap.data() : {};

  // 3. Genera QR como buffer PNG
  const qrBuffer = await QRCode.toBuffer(boleto.qrCode, {
    errorCorrectionLevel: 'H',
    type: 'png',
    margin: 2,
    width: 400,
    color: { dark: '#000000', light: '#FFFFFF' }
  });

  // 4. Crea el PDF
  const pdfBuffer = await new Promise((resolve, reject) => {
    const doc = new PDFDocument({ size: 'A4', margin: 50 });
    const chunks = [];
    doc.on('data', c => chunks.push(c));
    doc.on('end', () => resolve(Buffer.concat(chunks)));
    doc.on('error', reject);

    // ENCABEZADO
    doc.rect(0, 0, doc.page.width, 120).fill('#0a0a0a');
    doc.fillColor('#d4af37')
       .fontSize(28)
       .font('Helvetica-Bold')
       .text('SANTIANTZ EVENTS', 50, 40);
    doc.fillColor('#ffffff')
       .fontSize(12)
       .font('Helvetica')
       .text('Boleto Oficial', 50, 80);

    doc.fillColor('#000000');
    doc.moveDown(5);

    // NOMBRE DEL EVENTO
    doc.fillColor('#0a0a0a')
       .fontSize(22)
       .font('Helvetica-Bold')
       .text(evento.nombre || 'Evento', 50, 160);

    if (evento.descripcion) {
      doc.fillColor('#666666')
         .fontSize(10)
         .font('Helvetica')
         .text(evento.descripcion, 50, 195, { width: 500 });
    }

    // FECHA Y HORA
    const fechaTexto = formatearFecha(evento.fecha);
    doc.fillColor('#0a0a0a')
       .fontSize(13)
       .font('Helvetica-Bold')
       .text('Fecha:', 50, 240);
    doc.font('Helvetica').text(fechaTexto, 110, 240);

    if (evento.horaApertura) {
      doc.font('Helvetica-Bold').text('Apertura:', 250, 240);
      doc.font('Helvetica').text(evento.horaApertura, 320, 240);
    }

    // TIPO DE ENTRADA
    doc.fillColor('#d4af37')
       .fontSize(16)
       .font('Helvetica-Bold')
       .text(boleto.tipoEntradaNombre || 'Entrada', 50, 280);
    doc.fillColor('#0a0a0a')
       .fontSize(12)
       .font('Helvetica')
       .text(`$${Number(boleto.precio || 0).toLocaleString('es-MX')} MXN`, 50, 305);

    // TITULAR
    doc.fillColor('#666666').fontSize(10).text('TITULAR', 50, 350);
    doc.fillColor('#0a0a0a')
       .fontSize(14)
       .font('Helvetica-Bold')
       .text(boleto.personaNombre || 'Sin nombre', 50, 365);

    if (persona.curp) {
      doc.fillColor('#666666').fontSize(9).font('Helvetica').text(`CURP: ${persona.curp}`, 50, 388);
    }

    // QR GRANDE
    doc.image(qrBuffer, 50, 430, { width: 200, height: 200 });

    // INSTRUCCIONES
    doc.fillColor('#0a0a0a')
       .fontSize(11)
       .font('Helvetica-Bold')
       .text('Instrucciones de acceso:', 270, 430);
    doc.fontSize(9).font('Helvetica').fillColor('#333333').text(
      '1. Presenta este QR en la entrada del evento.\n' +
      '2. Lleva tu identificacion oficial (la misma que registraste).\n' +
      '3. El boleto es personal e intransferible.\n' +
      '4. Solo se permite un acceso por boleto.\n' +
      '5. La verificacion facial puede ser requerida.',
      270, 455,
      { width: 280, lineGap: 4 }
    );

    // FOOTER CON ID
    doc.fillColor('#999999').fontSize(8).font('Helvetica')
       .text(`ID Boleto: ${boletoId}`, 50, 700)
       .text(`Codigo QR: ${boleto.qrCode}`, 50, 712)
       .text(`SE ARMO LA MACHAKA SAPI de CV`, 50, 730)
       .text(`Generado: ${new Date().toLocaleString('es-MX')}`, 50, 742);

    doc.end();
  });

  // 5. Sube a Storage
  const archivoPath = `boletos/${boleto.eventoId}/${boletoId}.pdf`;
  const file = bucket.file(archivoPath);

  await file.save(pdfBuffer, {
    contentType: 'application/pdf',
    metadata: {
      cacheControl: 'public, max-age=31536000',
      metadata: { boletoId, eventoId: boleto.eventoId }
    }
  });

  // Hace el archivo accesible via URL firmada (valida 90 dias)
  const [signedUrl] = await file.getSignedUrl({
    action: 'read',
    expires: Date.now() + 90 * 24 * 60 * 60 * 1000
  });

  // 6. Actualiza boleto con la URL del PDF
  await boletoRef.update({
    pdfURL: signedUrl,
    pdfPath: archivoPath,
    pdfGeneradoEn: admin.firestore.FieldValue.serverTimestamp()
  });

  return { ok: true, pdfURL: signedUrl, pdfPath: archivoPath };
}

/**
 * Formatea una fecha YYYY-MM-DD a texto legible en espanol.
 */
function formatearFecha(fechaISO) {
  if (!fechaISO) return 'Fecha por confirmar';
  try {
    const f = new Date(fechaISO);
    const opciones = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    return f.toLocaleDateString('es-MX', opciones);
  } catch (e) {
    return fechaISO;
  }
}

// ============================================================
// EXPOSICION COMO CALLABLE
// ============================================================
exports.generarBoleto = onCall(
  { region: 'us-east1', memory: '512MiB', timeoutSeconds: 60 },
  async (request) => {
    const { boletoId } = request.data || {};
    if (!boletoId) {
      throw new HttpsError('invalid-argument', 'boletoId es requerido.');
    }
    try {
      return await generarBoletoInternal(boletoId);
    } catch (error) {
      console.error('Error generando boleto:', error);
      throw new HttpsError('internal', error.message || 'Error al generar PDF');
    }
  }
);

exports.generarBoletoInternal = generarBoletoInternal;
