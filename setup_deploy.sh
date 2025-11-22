#!/bin/bash

# Script de Setup para Deploy da API Flask no Render
# Uso: bash setup_deploy.sh

echo "🚀 Configurando projeto para deploy no Render..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Criar requirements.txt
echo -e "${BLUE}📦 Criando requirements.txt...${NC}"
cat > requirements.txt << EOF
flask==3.0.0
flask-cors==4.0.0
joblib==1.3.2
numpy==1.24.3
scikit-learn==1.3.2
gunicorn==21.2.0
EOF

echo -e "${GREEN}✅ requirements.txt criado!${NC}"

# 2. Criar .gitignore
echo -e "${BLUE}📝 Criando .gitignore...${NC}"
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv
pip-log.txt
pip-delete-this-directory.txt
.DS_Store
*.log
EOF

echo -e "${GREEN}✅ .gitignore criado!${NC}"

# 3. Criar Procfile (para Railway/Heroku)
echo -e "${BLUE}📄 Criando Procfile...${NC}"
echo "web: gunicorn api:app" > Procfile
echo -e "${GREEN}✅ Procfile criado!${NC}"

# 4. Criar render.yaml (opcional para Render)
echo -e "${BLUE}⚙️ Criando render.yaml...${NC}"
cat > render.yaml << EOF
services:
  - type: web
    name: ai-ml-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn api:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
EOF

echo -e "${GREEN}✅ render.yaml criado!${NC}"

# 5. Verificar se os modelos existem
echo -e "${BLUE}🔍 Verificando modelos ML...${NC}"
if [ -f "model_stress_classifier.joblib" ] && [ -f "model_mood_regressor.joblib" ]; then
    echo -e "${GREEN}✅ Modelos encontrados!${NC}"
else
    echo -e "${YELLOW}⚠️  ATENÇÃO: Modelos .joblib não encontrados!${NC}"
    echo "Certifique-se de ter os arquivos:"
    echo "  - model_stress_classifier.joblib"
    echo "  - scaler_stress.joblib"
    echo "  - model_mood_regressor.joblib"
    echo "  - scaler_mood.joblib"
fi

# 6. Verificar se api.py existe
if [ -f "api.py" ]; then
    echo -e "${GREEN}✅ api.py encontrado!${NC}"
else
    echo -e "${YELLOW}⚠️  api.py não encontrado!${NC}"
fi

# 7. Instruções finais
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup completo!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 Próximos passos para deploy no Render:${NC}"
echo ""
echo "1. Crie um repositório no GitHub (se não tiver)"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Setup API Flask ML'"
echo "   git remote add origin https://github.com/seu-usuario/seu-repo.git"
echo "   git push -u origin main"
echo ""
echo "2. Acesse https://render.com e faça login"
echo "3. Clique em 'New +' → 'Web Service'"
echo "4. Conecte seu repositório GitHub"
echo "5. Configure:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn api:app"
echo "6. Clique em 'Create Web Service'"
echo ""
echo -e "${YELLOW}⏰ O deploy leva ~5 minutos${NC}"
echo -e "${GREEN}🌐 Sua URL será: https://seu-app.onrender.com${NC}"
echo ""
echo -e "${BLUE}📱 Não esqueça de atualizar aiService.ts com a nova URL!${NC}"
echo ""