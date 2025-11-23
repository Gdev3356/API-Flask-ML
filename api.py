from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import re
from collections import Counter

app = Flask(__name__)
CORS(app)

FEATURES = ['PONTOS_XP', 'COMP_MEDIDA_ONTEM', 'MED_ESTRESSE_3_DIAS', 'SETOR_TI', 'SETOR_RH', 'SETOR_FINANCEIRO', 'SETOR_VENDAS']

# === DICIONÁRIOS DE ANÁLISE DE SENTIMENTO ===
PALAVRAS_SAUDE_MENTAL = {
    # Emoções Positivas (alto impacto)
    'feliz': 10, 'alegre': 9, 'animado': 9, 'empolgado': 9, 'motivado': 10,
    'confiante': 10, 'otimista': 9, 'esperançoso': 9, 'grato': 10, 'aliviado': 8,
    'tranquilo': 9, 'calmo': 9, 'relaxado': 8, 'sereno': 9, 'paz': 9,
    
    # Estados Positivos (médio impacto)
    'bem': 6, 'melhor': 7, 'ótimo': 9, 'excelente': 10, 'maravilhoso': 10,
    'produtivo': 8, 'focado': 7, 'concentrado': 7, 'energizado': 8, 'descansado': 8,
    'equilibrado': 9, 'controlado': 7, 'organizado': 6, 'realizado': 9,
    
    # Conquistas (reforço positivo)
    'consegui': 8, 'alcancei': 9, 'superei': 10, 'venci': 10, 'realizei': 8,
    'completei': 7, 'terminei': 7, 'avancei': 8, 'progredi': 9, 'melhorei': 9,
    
    # Emoções Negativas (alto impacto negativo)
    'triste': -10, 'deprimido': -10, 'angustiado': -10, 'desesperado': -10,
    'ansioso': -10, 'estressado': -10, 'sobrecarregado': -10, 'pânico': -10,
    'exausto': -9, 'esgotado': -10, 'burnout': -10, 'colapso': -10,
    
    # Estados Negativos (médio impacto negativo)
    'cansado': -7, 'irritado': -8, 'frustrado': -9, 'preocupado': -8,
    'nervoso': -8, 'tenso': -8, 'inquieto': -7, 'inseguro': -8,
    'desmotivado': -9, 'desanimado': -8, 'perdido': -7, 'confuso': -6,
    
    # Sintomas Físicos
    'insônia': -8, 'dor': -7, 'mal': -7, 'doente': -6, 'péssimo': -9,
    'horrível': -9, 'terrível': -9, 'difícil': -5, 'duro': -5,
    
    # Modificadores (intensificadores)
    'muito': 1.5, 'super': 1.5, 'extremamente': 1.8, 'totalmente': 1.3,
    'pouco': 0.5, 'levemente': 0.6, 'razoavelmente': 0.7
}

# Padrões de negação (invertem sentimento)
NEGACOES = {'não', 'nao', 'nunca', 'jamais', 'sem', 'nenhum', 'nada'}

# === CARREGAR MODELOS ===
try:
    classifier = joblib.load('model_stress_classifier.joblib')
    scaler_stress = joblib.load('scaler_stress.joblib')
    regressor = joblib.load('model_mood_regressor.joblib')
    scaler_mood = joblib.load('scaler_mood.joblib')
    print("Modelos carregados com sucesso!")
except Exception as e:
    print(f"ERRO ao carregar modelos: {e}")
    classifier = None
    regressor = None

# === FUNÇÕES DE ANÁLISE DE SENTIMENTO ===
def analisar_sentimento(texto):
    """
    Analisa sentimento usando dicionário de palavras-chave + contexto de negação
    Retorna: pontuação, palavras detectadas, bônus de pontos
    """
    texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
    palavras = texto_limpo.split()
    
    pontuacao = 0
    palavras_detectadas = []
    modificador_atual = 1.0
    negacao_ativa = False
    
    for i, palavra in enumerate(palavras):
        # Detecta negação (afeta próxima palavra)
        if palavra in NEGACOES:
            negacao_ativa = True
            continue
        
        # Detecta modificadores de intensidade
        if palavra in PALAVRAS_SAUDE_MENTAL and isinstance(PALAVRAS_SAUDE_MENTAL[palavra], float):
            modificador_atual = PALAVRAS_SAUDE_MENTAL[palavra]
            continue
        
        # Analisa palavra com sentimento
        if palavra in PALAVRAS_SAUDE_MENTAL and isinstance(PALAVRAS_SAUDE_MENTAL[palavra], int):
            valor_base = PALAVRAS_SAUDE_MENTAL[palavra]
            
            # Aplica modificador
            valor_final = valor_base * modificador_atual
            
            # Inverte se houver negação
            if negacao_ativa:
                valor_final = -valor_final
                palavras_detectadas.append((palavra, 'negação aplicada', valor_final))
            else:
                tipo = 'positiva' if valor_final > 0 else 'negativa'
                palavras_detectadas.append((palavra, tipo, valor_final))
            
            pontuacao += valor_final
            
            # Reset modificadores
            modificador_atual = 1.0
            negacao_ativa = False
    
    # Calcula bônus de pontos (escala de -50 a +50)
    bonus_pontos = int(max(-50, min(50, pontuacao)))
    
    # Classifica sentimento geral
    if pontuacao > 20:
        categoria = 'muito_positivo'
        emoji = '😄'
    elif pontuacao > 5:
        categoria = 'positivo'
        emoji = '🙂'
    elif pontuacao > -5:
        categoria = 'neutro'
        emoji = '😐'
    elif pontuacao > -20:
        categoria = 'negativo'
        emoji = '😟'
    else:
        categoria = 'muito_negativo'
        emoji = '😢'
    
    return {
        'pontuacao': round(pontuacao, 2),
        'bonus_pontos': bonus_pontos,
        'categoria': categoria,
        'emoji': emoji,
        'palavras_detectadas': palavras_detectadas[:10],  # Top 10
        'num_palavras_positivas': len([p for p in palavras_detectadas if p[2] > 0]),
        'num_palavras_negativas': len([p for p in palavras_detectadas if p[2] < 0])
    }

# === ENDPOINT: ANÁLISE DE TEXTO ===
@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json(force=True)
        texto = data.get('texto', '')
        
        if not texto or len(texto.strip()) < 5:
            return jsonify({
                'error': 'Texto muito curto. Escreva pelo menos 5 caracteres.'
            }), 400
        
        resultado = analisar_sentimento(texto)
        
        # Gera recomendação baseada no sentimento
        recomendacoes = {
            'muito_negativo': 'Considere conversar com alguém de confiança. Você não está sozinho.',
            'negativo': 'Tente fazer uma pausa ativa ou uma respiração profunda.',
            'neutro': 'Continue monitorando seu bem-estar. Pequenas ações fazem diferença!',
            'positivo': 'Ótimo! Continue assim. Você está no caminho certo!',
            'muito_positivo': 'Excelente! Seu autocuidado está funcionando muito bem!'
        }
        
        resultado['recomendacao'] = recomendacoes.get(resultado['categoria'], '')
        resultado['status'] = 'success'
        
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Erro ao analisar texto.'}), 400

# === ENDPOINT: PREDICT STRESS (Original) ===
@app.route('/predict_stress', methods=['POST'])
def predict_stress():
    if classifier is None:
        return jsonify({"error": "Modelo de Classificação não carregado."}), 500
    try:
        data = request.get_json(force=True)
        input_data = np.array([[data.get(f, 0) for f in FEATURES]])
        input_scaled = scaler_stress.transform(input_data)
        prediction_proba = classifier.predict_proba(input_scaled)[0][1]
        
        return jsonify({
            'status': 'success',
            'risco_estresse_alto_proba': f"{prediction_proba:.4f}",
            'mensagem': 'Intervenção Proativa Recomendada' if prediction_proba > 0.5 else 'Risco Baixo'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# === ENDPOINT: PREDICT MOOD (Original) ===
@app.route('/predict_mood', methods=['POST'])
def predict_mood():
    if regressor is None:
        return jsonify({"error": "Modelo de Regressão não carregado."}), 500
    try:
        data = request.get_json(force=True)
        input_data = np.array([[data.get(f, 0) for f in FEATURES]])
        input_scaled = scaler_mood.transform(input_data)
        predicted_mood = regressor.predict(input_scaled)[0]
        predicted_mood_safe = int(np.clip(round(predicted_mood), 1, 5))
        
        return jsonify({
            'status': 'success',
            'humor_predito_dia_seguinte': predicted_mood_safe,
            'mensagem': 'Predição de humor concluída.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)