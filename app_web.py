from flask import Flask, render_template, request, jsonify, url_for
import os
import pandas as pd
import datetime
from werkzeug.utils import secure_filename
from GraphsGenerator import generate_network_graph

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            xl = pd.ExcelFile(file_path)
            sheets = xl.sheet_names
            return jsonify({'filename': filename, 'sheets': sheets})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    filename = data.get('filename')
    sheet_name = data.get('sheet_name')
    
    if not filename or not sheet_name:
        return jsonify({'error': 'Missing filename or sheet_name'}), 400
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Graph_ICMI_{timestamp}.png"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        generate_network_graph(file_path, output_path, sheet_name=sheet_name)
        # Return URL to the generated image
        image_url = url_for('static', filename=f'outputs/{output_filename}')
        return jsonify({'image_url': image_url, 'image_name': output_filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
