/**
 * ENVIAR EMAIL - Nodemailer + Gmail SMTP
 *
 * Envia el boleto al email del comprador con:
 *   - HTML branded de Santiantz Events
 *   - PDF del boleto adjunto
 *   - Link para descargar/ver el boleto en linea
 *
 * Si la persona no tiene email registrado, retorna error.
 * Marca emailEnviado=true para no duplicar.
 */

const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const admin = require('firebase-admin');
const nodemailer = require('nodemailer');
const https = require('https');

const GMAIL_USER = defineSecret('GMAIL_USER');
const GMAIL_APP_PASSWORD = defineSecret('GMAIL_APP_PASSWORD');
const GMAIL_FROM_NAME = defineSecret('GMAIL_FROM_NAME');

// ============================================================
// FUNCION INTERNA - reutilizable desde el webhook
// ============================================================
async function enviarEmailInternal(boletoId) {
  if (!boletoId) throw new Error('boletoId es requerido');

  const db = admin.firestore();

  // 1. Lee boleto
  const boletoRef = db.collection('boletos').doc(boletoId);
  const boletoSnap = await boletoRef.get();
  if (!boletoSnap.exists) throw new Error('Boleto no encontrado');
  const boleto = boletoSnap.data();

  if (boleto.emailEnviado) {
    return { ok: true, mensaje: 'Email ya enviado previamente' };
  }

  if (!boleto.pdfURL) {
    throw new Error('El PDF no ha sido generado aun');
  }

  // 2. Lee persona y evento
  const [personaSnap, eventoSnap] = await Promise.all([
    db.collection('personas_verificadas').doc(boleto.personaId).get(),
    db.collection('eventos').doc(boleto.eventoId).get()
  ]);

  const persona = personaSnap.exists ? personaSnap.data() : {};
  const evento = eventoSnap.exists ? eventoSnap.data() : {};

  if (!persona.email) {
    throw new Error('La persona no tiene email registrado');
  }

  // 3. Descarga el PDF como buffer (lo adjuntamos directo)
  const pdfBuffer = await descargarBuffer(boleto.pdfURL);

  // 4. Configura transporter Gmail
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      user: GMAIL_USER.value(),
      pass: GMAIL_APP_PASSWORD.value()
    }
  });

  // 5. Construye HTML del email
  const fechaEvento = formatearFecha(evento.fecha);
  const html = construirHTMLEmail({
    nombrePersona: boleto.personaNombre,
    nombreEvento: evento.nombre || 'Evento',
    fechaEvento,
    horaApertura: evento.horaApertura,
    tipoEntrada: boleto.tipoEntradaNombre,
    precio: boleto.precio,
    qrCode: boleto.qrCode,
    pdfURL: boleto.pdfURL
  });

  // 6. Envia
  const fromName = GMAIL_FROM_NAME.value() || 'Santiantz Events';
  const fromEmail = GMAIL_USER.value();

  const info = await transporter.sendMail({
    from: `"${fromName}" <${fromEmail}>`,
    to: persona.email,
    subject: `Tu boleto para ${evento.nombre || 'tu evento'} - Santiantz Events`,
    html,
    attachments: [{
      filename: `Boleto-${boletoId}.pdf`,
      content: pdfBuffer,
      contentType: 'application/pdf'
    }]
  });

  // 7. Marca como enviado
  await boletoRef.update({
    emailEnviado: true,
    emailEnviadoEn: admin.firestore.FieldValue.serverTimestamp(),
    emailMessageId: info.messageId || null
  });

  return { ok: true, messageId: info.messageId, destinatario: persona.email };
}

/**
 * HTML branded del email
 */
function construirHTMLEmail(p) {
  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Tu boleto - Santiantz Events</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;color:#ffffff;">
  <div style="max-width:600px;margin:0 auto;background:#1a1a1a;">
    <div style="background:#0a0a0a;padding:40px 30px;text-align:center;border-bottom:3px solid #d4af37;">
      <h1 style="margin:0;color:#d4af37;font-size:32px;letter-spacing:2px;">SANTIANTZ EVENTS</h1>
      <p style="margin:8px 0 0;color:#aaaaaa;font-size:13px;">Tu boleto esta listo</p>
    </div>

    <div style="padding:40px 30px;">
      <h2 style="margin:0 0 8px;color:#ffffff;">Hola ${escapar(p.nombrePersona)},</h2>
      <p style="color:#cccccc;line-height:1.6;">Tu compra fue confirmada. Aqui estan los detalles de tu boleto.</p>

      <div style="margin:30px 0;padding:24px;background:#0a0a0a;border:1px solid #d4af37;border-radius:8px;">
        <h3 style="margin:0 0 16px;color:#d4af37;font-size:22px;">${escapar(p.nombreEvento)}</h3>
        <p style="margin:6px 0;color:#cccccc;"><strong style="color:#ffffff;">Fecha:</strong> ${escapar(p.fechaEvento)}</p>
        ${p.horaApertura ? `<p style="margin:6px 0;color:#cccccc;"><strong style="color:#ffffff;">Apertura:</strong> ${escapar(p.horaApertura)}</p>` : ''}
        <p style="margin:6px 0;color:#cccccc;"><strong style="color:#ffffff;">Entrada:</strong> ${escapar(p.tipoEntrada)}</p>
        <p style="margin:6px 0;color:#cccccc;"><strong style="color:#ffffff;">Precio:</strong> $${Number(p.precio || 0).toLocaleString('es-MX')} MXN</p>
      </div>

      <div style="text-align:center;margin:30px 0;">
        <a href="${escapar(p.pdfURL)}" style="display:inline-block;padding:14px 32px;background:#d4af37;color:#000000;text-decoration:none;border-radius:6px;font-weight:bold;font-size:14px;letter-spacing:1px;">DESCARGAR BOLETO PDF</a>
      </div>

      <div style="margin:30px 0;padding:16px;background:#221c0a;border-left:3px solid #d4af37;border-radius:4px;">
        <p style="margin:0;color:#ffbb33;font-size:13px;line-height:1.6;">
          <strong>IMPORTANTE:</strong><br>
          - Llega con tu identificacion oficial (la misma que registraste).<br>
          - Tu boleto incluye un codigo QR unico. Es personal e intransferible.<br>
          - Se puede solicitar verificacion facial en la entrada.
        </p>
      </div>

      <p style="color:#666666;font-size:12px;margin:30px 0 0;">
        Codigo QR: <code style="color:#d4af37;">${escapar(p.qrCode)}</code>
      </p>
    </div>

    <div style="background:#0a0a0a;padding:20px 30px;text-align:center;border-top:1px solid #333333;">
      <p style="margin:0;color:#666666;font-size:11px;">
        Santiantz Events - SE ARMO LA MACHAKA SAPI de CV<br>
        Este email fue enviado a la direccion registrada en tu compra.
      </p>
    </div>
  </div>
</body>
</html>`;
}

/**
 * Escapa caracteres HTML para prevenir XSS en el email.
 */
function escapar(texto) {
  if (texto === null || texto === undefined) return '';
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Formatea fecha YYYY-MM-DD a texto legible en espanol.
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

/**
 * Descarga el contenido de una URL como Buffer.
 */
function descargarBuffer(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode} al descargar ${url}`));
        return;
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    }).on('error', reject);
  });
}

// ============================================================
// EXPOSICION COMO CALLABLE
// ============================================================
exports.enviarEmail = onCall(
  {
    region: 'us-east1',
    memory: '512MiB',
    timeoutSeconds: 60,
    secrets: [GMAIL_USER, GMAIL_APP_PASSWORD, GMAIL_FROM_NAME]
  },
  async (request) => {
    const { boletoId } = request.data || {};
    if (!boletoId) {
      throw new HttpsError('invalid-argument', 'boletoId es requerido.');
    }
    try {
      return await enviarEmailInternal(boletoId);
    } catch (error) {
      console.error('Error enviando email:', error);
      throw new HttpsError('internal', error.message || 'Error al enviar email');
    }
  }
);

exports.enviarEmailInternal = enviarEmailInternal;
