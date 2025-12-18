#!/usr/bin/env bash
set -euo pipefail

# Script para baixar versões UMD locais de Ant Design e Recharts
# Coloca os arquivos em src/static/dist/balasis/vendor/

VENDOR_DIR="src/static/dist/balasis/vendor"
mkdir -p "$VENDOR_DIR"

echo "Baixando antd.min.css..."
curl -sS -L "https://unpkg.com/antd@5.11.0/dist/antd.min.css" -o "$VENDOR_DIR/antd.min.css"

echo "Baixando antd.min.js..."
curl -sS -L "https://unpkg.com/antd@5.11.0/dist/antd.min.js" -o "$VENDOR_DIR/antd.min.js"

echo "Baixando Recharts..."
curl -sS -L "https://unpkg.com/recharts/umd/Recharts.min.js" -o "$VENDOR_DIR/Recharts.min.js"

echo "Downloads concluídos. Verifique $VENDOR_DIR e comite os arquivos se desejar que fiquem no repo."