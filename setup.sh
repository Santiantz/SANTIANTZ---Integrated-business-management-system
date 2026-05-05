#!/bin/bash
# ============================================================
# CostControl — Script de configuración inicial
# ADMON SANTIANTZ
# ============================================================
echo "🚀 Iniciando configuración de CostControl..."
echo ""

# 1. Verificar firebase CLI
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI no encontrado. Instalando..."
    npm install -g firebase-tools
fi

echo "✅ Firebase CLI disponible"

# 2. Login
echo ""
echo "📋 Paso 1: Login con Firebase"
echo "Se abrirá el navegador para autenticarte con tu cuenta Google..."
firebase login

# 3. Inicializar proyecto
echo ""
echo "📋 Paso 2: Conectar con proyecto ADMON SANTIANTZ"
firebase use admon-santiantz

echo ""
echo "✅ Todo listo para desplegar!"
echo ""
echo "📋 Paso 3: Desplegar la app"
echo "Ejecuta: firebase deploy"
echo ""
echo "En 2 minutos tu app estará en:"
echo "🌐 https://admon-santiantz.web.app"
