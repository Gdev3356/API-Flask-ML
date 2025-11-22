#!/bin/bash

# Script para corrigir erro de deploy no Render
# Uso: bash fix_deploy.sh [opcao]
# Opção 1: atualizar dependências
# Opção 2: forçar Python 3.11

echo "🔧 Correção de Deploy - Render.com"
echo ""
echo "Escolha uma solução:"
echo "1) Atualizar dependências para Python 3.13 (RECOMENDADO)"
echo "2) Forçar Python 3.11 (mantém setup atual)"
echo ""
read -p "Digite sua escolha (1 ou 2): " choice

case $choice in
  1)
    echo ""
    echo "✅ Opção 1: Atualizando requirements.txt..."
    
    cat > requirements.txt << 'EOF'
flask==3.0.0
flask-cors==4.0.0
joblib==1.4.2
numpy==1.26.4
scikit-learn==1.4.2
gunicorn==21.2.0
EOF
    
    echo "✅ requirements.txt atualizado!"
    echo ""
    echo "⚠️  IMPORTANTE: Teste localmente antes de fazer push!"
    echo "Execute: python -c \"import joblib; joblib.load('model_stress_classifier.joblib')\""
    echo ""
    read -p "Testar e fazer commit? (s/n): " confirm
    
    if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
      git add requirements.txt
      git commit -m "Fix: Atualizar dependências para compatibilidade Python 3.13"
      echo ""
      echo "✅ Commit realizado!"
      echo ""
      read -p "Fazer push para o GitHub? (s/n): " push_confirm
      
      if [ "$push_confirm" = "s" ] || [ "$push_confirm" = "S" ]; then
        git push
        echo ""
        echo "🚀 Push realizado! O Render vai rebuildar automaticamente."
        echo "⏰ Aguarde 5-10 minutos."
        echo "🔗 Acompanhe em: https://dashboard.render.com"
      fi
    fi
    ;;
    
  2)
    echo ""
    echo "✅ Opção 2: Forçando Python 3.11..."
    
    echo "3.11.0" > .python-version
    
    echo "✅ Arquivo .python-version criado!"
    echo ""
    
    git add .python-version
    git commit -m "Fix: Forçar Python 3.11 para compatibilidade"
    echo ""
    echo "✅ Commit realizado!"
    echo ""
    read -p "Fazer push para o GitHub? (s/n): " push_confirm
    
    if [ "$push_confirm" = "s" ] || [ "$push_confirm" = "S" ]; then
      git push
      echo ""
      echo "🚀 Push realizado! O Render vai rebuildar automaticamente."
      echo "⏰ Aguarde 5-10 minutos."
      echo "🔗 Acompanhe em: https://dashboard.render.com"
    fi
    ;;
    
  *)
    echo ""
    echo "❌ Opção inválida. Execute novamente."
    exit 1
    ;;
esac

echo ""
echo "============================================"
echo "✅ Correção aplicada com sucesso!"
echo "============================================"
echo ""
echo "📋 Próximos passos:"
echo "1. Aguarde o rebuild no Render (5-10 min)"
echo "2. Teste sua API: https://seu-app.onrender.com/health"
echo "3. Atualize o frontend com a nova URL"
echo ""