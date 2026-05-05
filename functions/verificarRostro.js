/**
 * VERIFICAR ROSTRO - AWS Rekognition CompareFaces
 *
 * Recibe dos imagenes en base64 (foto INE y selfie) y las compara
 * usando AWS Rekognition. Si la similitud es >= scoreMinimo,
 * confirma que es la misma persona.
 *
 * Score minimo default: 80 (configurable por evento).
 *
 * Costo aproximado: $0.001 USD por comparacion.
 */

const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const {
  RekognitionClient,
  CompareFacesCommand
} = require('@aws-sdk/client-rekognition');

// Secrets de AWS configurados en Firebase Secret Manager
const AWS_ACCESS_KEY_ID = defineSecret('AWS_ACCESS_KEY_ID');
const AWS_SECRET_ACCESS_KEY = defineSecret('AWS_SECRET_ACCESS_KEY');
const AWS_REGION = defineSecret('AWS_REGION');

exports.verificarRostro = onCall(
  {
    region: 'us-east1',
    memory: '512MiB',
    timeoutSeconds: 60,
    secrets: [AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]
  },
  async (request) => {
    // Validar que el cliente este autenticado (Firebase Auth anonimo o con login)
    if (!request.auth) {
      console.warn('Llamada sin autenticacion');
      throw new HttpsError(
        'unauthenticated',
        'Debes iniciar sesion para usar esta funcion.'
      );
    }
    console.log('Invocacion de verificarRostro por uid:', request.auth.uid);

    const { fotoReferenciaBase64, fotoIntentoBase64, scoreMinimo } = request.data || {};

    // Log de tamanos para depurar
    const sizeRef = fotoReferenciaBase64 ? fotoReferenciaBase64.length : 0;
    const sizeInt = fotoIntentoBase64 ? fotoIntentoBase64.length : 0;
    console.log('Tamano referencia (chars base64):', sizeRef, 'Tamano intento:', sizeInt);

    // Validacion de entrada
    if (!fotoReferenciaBase64 || !fotoIntentoBase64) {
      throw new HttpsError(
        'invalid-argument',
        'Faltan parametros: fotoReferenciaBase64 y fotoIntentoBase64 son requeridos.'
      );
    }

    const minimo = typeof scoreMinimo === 'number' ? scoreMinimo : 80;

    // Limpia el prefijo data:image/...;base64, si viene incluido
    const limpiarBase64 = (b64) => {
      if (typeof b64 !== 'string') return b64;
      const idx = b64.indexOf(',');
      return idx > -1 ? b64.substring(idx + 1) : b64;
    };

    try {
      // Convierte base64 a Buffer (AWS SDK acepta Buffer directamente)
      const sourceBuffer = Buffer.from(limpiarBase64(fotoReferenciaBase64), 'base64');
      const targetBuffer = Buffer.from(limpiarBase64(fotoIntentoBase64), 'base64');

      // Configura el cliente AWS Rekognition con las credenciales del secret
      const cliente = new RekognitionClient({
        region: AWS_REGION.value() || 'us-east-1',
        credentials: {
          accessKeyId: AWS_ACCESS_KEY_ID.value(),
          secretAccessKey: AWS_SECRET_ACCESS_KEY.value()
        }
      });

      // Comando CompareFaces
      const comando = new CompareFacesCommand({
        SourceImage: { Bytes: sourceBuffer },
        TargetImage: { Bytes: targetBuffer },
        SimilarityThreshold: minimo,
        QualityFilter: 'AUTO'
      });

      const respuesta = await cliente.send(comando);

      // Si encontro al menos un rostro coincidente
      if (respuesta.FaceMatches && respuesta.FaceMatches.length > 0) {
        const mejor = respuesta.FaceMatches[0];
        const similitud = Math.round((mejor.Similarity || 0) * 100) / 100;

        return {
          match: true,
          similitud,
          scoreMinimo: minimo,
          mensaje: `Coincidencia confirmada con ${similitud}% de similitud.`
        };
      }

      // Si no hay match, calculamos el score mas alto encontrado (si lo hay)
      const sinMatch = respuesta.UnmatchedFaces && respuesta.UnmatchedFaces.length > 0;
      return {
        match: false,
        similitud: 0,
        scoreMinimo: minimo,
        rostroDetectado: sinMatch,
        mensaje: sinMatch
          ? 'Se detecto un rostro pero no coincide con la referencia.'
          : 'No se detecto un rostro claro en la imagen objetivo.'
      };
    } catch (error) {
      console.error('Error AWS Rekognition - name:', error.name);
      console.error('Error AWS Rekognition - message:', error.message);
      console.error('Error AWS Rekognition - code:', error.code);
      console.error('Error AWS Rekognition - completo:', JSON.stringify(error, Object.getOwnPropertyNames(error)));

      if (error.name === 'InvalidParameterException') {
        throw new HttpsError(
          'invalid-argument',
          'Las imagenes no son validas. Asegurate de subir fotos claras con un rostro visible.',
          { awsError: error.name, awsMessage: error.message }
        );
      }
      if (error.name === 'ImageTooLargeException') {
        throw new HttpsError(
          'invalid-argument',
          'Las imagenes son demasiado grandes. Maximo 5MB por imagen.',
          { awsError: error.name, awsMessage: error.message }
        );
      }
      if (error.name === 'InvalidImageFormatException') {
        throw new HttpsError(
          'invalid-argument',
          'Formato de imagen no valido. Solo se aceptan JPEG y PNG.',
          { awsError: error.name, awsMessage: error.message }
        );
      }

      throw new HttpsError(
        'internal',
        'Error al verificar rostro: ' + (error.message || error.name || 'desconocido'),
        { awsError: error.name, awsMessage: error.message, awsCode: error.code }
      );
    }
  }
);
