# app.py
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from utils.data_processor import DataProcessor
from utils.statistics import StatisticalAnalyzer
from utils.report_generator import ReportGenerator
import traceback

app = Flask(__name__)
CORS(app)

# Configurações
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Criar pastas se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

def clean_json_data(data):
    """
    Limpa dados para garantir que sejam serializáveis em JSON.
    """
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json_data(v) for v in data]
    elif isinstance(data, (np.integer, np.floating)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif pd.isna(data) or data == np.inf or data == -np.inf:
        return None
    else:
        return data

@app.route('/')
def index():
    """Renderiza a página principal."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa o upload de arquivo."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({'error': 'Formato de arquivo não suportado. Use CSV ou XLSX'}), 400
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processar arquivo
        processor = DataProcessor(filepath, sigma_threshold=2)
        df = processor.load_data()
        
        if df is None:
            return jsonify({'error': 'Erro ao processar arquivo'}), 500
        
        # Obter informações básicas
        categories = processor.get_categories()
        
        response_data = {
            'status': 'success',
            'message': 'Arquivo carregado com sucesso',
            'filename': filename,
            'filepath': filepath,
            'data': {
                'total_categories': len(categories),
                'categories': categories[:10] if len(categories) > 10 else categories,
                'total_months': len(df.columns) - 1,
                'shape': list(df.shape)
            }
        }
        
        # Limpar dados para JSON
        response_data = clean_json_data(response_data)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """Analisa os dados e calcula sazonalidade."""
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify({'error': 'Filepath não fornecido'}), 400
        
        filepath = data['filepath']
        sigma_threshold = float(data.get('sigma_threshold', 2))
        
        # Verificar se arquivo existe
        if not os.path.exists(filepath):
            return jsonify({'error': f'Arquivo não encontrado: {filepath}'}), 404
        
        # Processar dados
        processor = DataProcessor(filepath, sigma_threshold)
        df = processor.load_data()
        
        if df is None:
            return jsonify({'error': 'Erro ao carregar dados'}), 500
        
        # Analisar estatísticas
        analyzer = StatisticalAnalyzer(df, sigma_threshold)
        results = analyzer.process_all_categories()
        
        # Preparar resposta
        response_data = {
            'status': 'success',
            'message': 'Análise concluída',
            'results': {
                'summary': results.get('summary', {}),
                'total_processed': len(results.get('categories', [])),
                'categories': results.get('categories', [])[:10],  # Primeiras 10 para preview
                'has_more': len(results.get('categories', [])) > 10
            }
        }
        
        # Limpar dados para JSON
        response_data = clean_json_data(response_data)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Erro na análise: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Gera relatório completo em Excel."""
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify({'error': 'Filepath não fornecido'}), 400
        
        filepath = data['filepath']
        sigma_threshold = float(data.get('sigma_threshold', 2))
        
        # Verificar se arquivo existe
        if not os.path.exists(filepath):
            return jsonify({'error': f'Arquivo não encontrado: {filepath}'}), 404
        
        print(f"Gerando relatório para: {filepath}")
        
        # Processar dados
        processor = DataProcessor(filepath, sigma_threshold)
        df = processor.load_data()
        
        if df is None:
            return jsonify({'error': 'Erro ao carregar dados'}), 500
        
        # Analisar estatísticas
        analyzer = StatisticalAnalyzer(df, sigma_threshold)
        results = analyzer.process_all_categories()
        
        # Gerar relatório
        report_gen = ReportGenerator(results)
        report_path = report_gen.generate_excel_report(app.config['REPORTS_FOLDER'])
        
        if report_path and os.path.exists(report_path):
            response_data = {
                'status': 'success',
                'message': 'Relatório gerado com sucesso',
                'report_path': report_path,
                'report_name': os.path.basename(report_path),
                'summary': {
                    'total_categories': results['summary'].get('processed', 0),
                    'errors': results['summary'].get('errors', 0)
                }
            }
            
            # Limpar dados para JSON
            response_data = clean_json_data(response_data)
            
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Erro ao gerar relatório'}), 500
            
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download-report/<filename>')
def download_report(filename):
    """Faz download do relatório gerado."""
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Erro no download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a aplicação está funcionando."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handler para erros 404."""
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handler para erros 500."""
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Reports folder: {app.config['REPORTS_FOLDER']}")
    print("Servidor rodando em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
