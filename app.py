# app.py
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json
from datetime import datetime
from utils.statistics import StatisticsCalculator
from utils.report_generator import ReportGenerator
from utils.data_processor import DataProcessor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

# Criar pastas necessárias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Se não houver template, retornar JSON
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "message": "SazIA - Sistema de Análise de Sazonalidade",
            "status": "running",
            "endpoints": ["/", "/analyze", "/export/excel", "/health"]
        })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "SazIA"})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint para análise de sazonalidade"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Processar
            processor = DataProcessor()
            data = processor.load_data(filepath)
            
            # Calcular
            calculator = StatisticsCalculator()
            results = calculator.calculate_seasonality(data)
            
            # Limpar arquivo temporário
            os.remove(filepath)
            
            return jsonify(results)
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/excel', methods=['GET', 'POST'])
def export_excel():
    """Endpoint para exportar relatório Excel"""
    try:
        if request.method == 'POST':
            data = request.json
        else:
            data_str = request.args.get('data')
            data = json.loads(data_str) if data_str else {}
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        generator = ReportGenerator()
        filepath = generator.generate_excel_report(data)
        
        return send_file(filepath, as_attachment=True, 
                        download_name=f'analise_sazonalidade_{datetime.now().strftime("%Y%m%d")}.xlsx')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
