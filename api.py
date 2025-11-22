
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)
# A lista de features deve ser idêntica à usada no treinamento
FEATURES = ['PONTOS_XP', 'COMP_MEDIDA_ONTEM', 'MED_ESTRESSE_3_DIAS', 'SETOR_TI', 'SETOR_RH', 'SETOR_FINANCEIRO', 'SETOR_VENDAS']

# --- CARREGAR MODELOS PRÉ-TREINADOS ---
try:
    classifier = joblib.load('model_stress_classifier.joblib')
    scaler_stress = joblib.load('scaler_stress.joblib')
    regressor = joblib.load('model_mood_regressor.joblib')
    scaler_mood = joblib.load('scaler_mood.joblib')
    print("Modelos carregados com sucesso!")
except Exception as e:
    print(f"ERRO ao carregar modelos: {e}. Execute as Etapas 3 e 4.")
    classifier = None
    regressor = None

# --- ENDPOINT 1: CLASSIFICAÇÃO DE RISCO DE ESTRESSE ---
@app.route('/predict_stress', methods=['POST'])
def predict_stress():
    if classifier is None: return jsonify({"error": "Modelo de Classificação não carregado."}), 500
    try:
        data = request.get_json(force=True)

        # 1. Converte JSON para array de features
        input_data = np.array([[data.get(f, 0) for f in FEATURES]])

        # 2. Padroniza (CRUCIAL!)
        input_scaled = scaler_stress.transform(input_data)

        # 3. Prediz a probabilidade de Risco Alto (classe 1)
        prediction_proba = classifier.predict_proba(input_scaled)[0][1]

        return jsonify({
            'status': 'success',
            'risco_estresse_alto_proba': f"{prediction_proba:.4f}",
            'mensagem': 'Intervenção Proativa Recomendada' if prediction_proba > 0.5 else 'Risco Baixo'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Erro ao processar dados de classificação.'}), 400


# --- ENDPOINT 2: REGRESSÃO DO NÍVEL DE HUMOR ---
@app.route('/predict_mood', methods=['POST'])
def predict_mood():
    if regressor is None: return jsonify({"error": "Modelo de Regressão não carregado."}), 500
    try:
        data = request.get_json(force=True)

        # 1. Converte JSON para array de features
        input_data = np.array([[data.get(f, 0) for f in FEATURES]])

        # 2. Padroniza (CRUCIAL!)
        input_scaled = scaler_mood.transform(input_data)

        # 3. Prediz e limita entre 1 e 5
        predicted_mood = regressor.predict(input_scaled)[0]
        predicted_mood_safe = int(np.clip(round(predicted_mood), 1, 5))

        return jsonify({
            'status': 'success',
            'humor_predito_dia_seguinte': predicted_mood_safe,
            'mensagem': 'Predição de humor concluída para personalização.'
        })

    except Exception as e:
        return jsonify({'error': str(e), 'message': 'Erro ao processar dados de regressão.'}), 400

if __name__ == '__main__':
    # Flask usa a porta 5000 por padrão
    app.run(host='0.0.0.0', port=5000, debug=False)
