from flask import Flask, render_template, request, send_file, jsonify
import subprocess
import tempfile
import asyncio
import edge_tts

app = Flask(__name__)

VOICES = {
    'denise': {'id': 'fr-FR-DeniseNeural', 'name': 'Denise (Femme)', 'style': 'Naturelle'},
    'henri': {'id': 'fr-FR-HenriNeural', 'name': 'Henri (Homme)', 'style': 'Naturel'},
    'eloise': {'id': 'fr-FR-EloiseNeural', 'name': 'Éloïse (Femme)', 'style': 'Douce'},
    'brigitte': {'id': 'fr-BE-CharlineNeural', 'name': 'Charline (Femme BE)', 'style': 'Belge'},
    'gerard': {'id': 'fr-BE-GerardNeural', 'name': 'Gérard (Homme BE)', 'style': 'Belge'},
    'ariane': {'id': 'fr-CH-ArianeNeural', 'name': 'Ariane (Femme CH)', 'style': 'Suisse'},
    'fabrice': {'id': 'fr-CH-FabriceNeural', 'name': 'Fabrice (Homme CH)', 'style': 'Suisse'},
    'sylvie': {'id': 'fr-CA-SylvieNeural', 'name': 'Sylvie (Femme CA)', 'style': 'Québécois'},
    'antoine': {'id': 'fr-CA-AntoineNeural', 'name': 'Antoine (Homme CA)', 'style': 'Québécois'},
}

async def generate_audio(text, voice_id, output_path):
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(output_path)

@app.route('/')
def index():
    return render_template('index.html', voices=VOICES)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.json.get('text', '')
    voice_key = request.json.get('voice', 'denise')
    if not text:
        return jsonify({'error': 'Texte vide'}), 400
    
    voice_id = VOICES.get(voice_key, VOICES['denise'])['id']
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        output_path = f.name
    
    try:
        asyncio.run(generate_audio(text, voice_id, output_path))
        return send_file(output_path, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    text = request.json.get('text', '')
    voice_key = request.json.get('voice', 'denise')
    if not text:
        return jsonify({'error': 'Texte vide'}), 400
    
    voice_id = VOICES.get(voice_key, VOICES['denise'])['id']
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        output_path = f.name
    
    try:
        asyncio.run(generate_audio(text, voice_id, output_path))
        response = send_file(output_path, mimetype='application/octet-stream', 
                        as_attachment=True, download_name='audio.mp3')
        response.headers['Content-Disposition'] = 'attachment; filename="audio.mp3"'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
