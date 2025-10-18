from flask import Flask, request, jsonify
import os
import PyPDF2
import openai

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Récupère la clé API OpenAI depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API de résumé de PDF 🚀"})

@app.route('/summarize_pdf', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du PDF: {str(e)}"}), 500

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant qui résume les documents PDF de manière claire et concise."},
                {"role": "user", "content": f"Résume ce texte:\n{text}"}
            ],
            max_tokens=500
        )
        summary = response.choices[0].message['content'].strip()
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Erreur IA: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
