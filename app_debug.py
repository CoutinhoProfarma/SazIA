# app_debug.py
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json
import traceback
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from utils.statistics import StatisticsCalculator
    from utils.report_generator import ReportGenerator
    from utils.data_processor import DataProcessor
    logger.info("✅ Imports dos utils realizados com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao importar utils: {str(e)}")
    logger.error(traceback.format_exc())

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

# Criar pastas necessárias
for folder in ['uploads', 'reports', 'templates', 'static/js', 'static/css']:
    os.makedirs(folder, exist_ok=True)
    logger.info(f"📁 Pasta {folder} verificada/criada")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.warning(f"⚠️ Template index.html não encontrado: {e}")
        return jsonify({
            "message": "SazIA - Sistema de Análise de Sazonalidade",
            "status": "running",
            "info": "Template HTML não encontrado. Use /test para testar o processamento"
        })

@app.route('/test')
def test_endpoint():
    """Endpoint para teste rápido"""
    try:
        # Criar dados de teste
        import numpy as np
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'sku': ['SKU001'] * 12 + ['SKU002'] * 12,
            'sales': list(np.random.normal(100, 30, 12)) + list(np.random.normal(200, 10, 12)),
            'date': pd.date_range('2023-01-01', periods=24, freq='M'),
            'description': ['Produto 1'] * 12 + ['Produto 2'] * 12,
            'category': ['Cat A'] * 12 + ['Cat B'] * 12
        })
        
        logger.info("✅ Dados de teste criados")
        
        # Processar
        processor = DataProcessor()
        processed = processor.preprocess_data(test_data)
        logger.info("✅ Dados processados")
        
        # Calcular
        calculator = StatisticsCalculator()
        results = calculator.calculate_seasonality(processed)
        logger.info("✅ Estatísticas calculadas")
        
        return jsonify({
            "status": "success",
            "message": "Teste concluído com sucesso",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint para análise de sazonalidade com debug detalhado"""
    logger.info("🔍 === INICIANDO ANÁLISE ===")
    
    try:
        # Verificar arquivo
        if 'file' not in request.files:
            logger.error("❌ Nenhum arquivo no request")
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        logger.info(f"📎 Arquivo recebido: {file.filename}")
        
        if file.filename == '':
            logger.error("❌ Nome do arquivo vazio")
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"❌ Tipo de arquivo não permitido: {file.filename}")
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"💾 Salvando arquivo em: {filepath}")
        file.save(filepath)
        logger.info("✅ Arquivo salvo com sucesso")
        
        # Verificar se arquivo existe e tem conteúdo
        if not os.path.exists(filepath):
            logger.error(f"❌ Arquivo não encontrado após salvar: {filepath}")
            return jsonify({'error': 'Erro ao salvar arquivo'}), 500
        
        file_size = os.path.getsize(filepath)
        logger.info(f"📊 Tamanho do arquivo: {file_size} bytes")
        
        # Processar dados
        logger.info("🔄 Iniciando processamento de dados")
        processor = DataProcessor()
        
        try:
            data = processor.load_data(filepath)
            logger.info(f"✅ Dados carregados - Shape: {data.shape}")
            logger.info(f"📋 Colunas: {list(data.columns)}")
            logger.info(f"👀 Primeiras linhas:\n{data.head()}")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {str(e)}")
            logger.error(traceback.format_exc())
            os.remove(filepath)
            return jsonify({
                'error': f'Erro ao carregar arquivo: {str(e)}',
                'details': traceback.format_exc()
            }), 500
        
        # Validar dados
        is_valid, errors = processor.validate_data(data)
        if not is_valid:
            logger.error(f"❌ Dados inválidos: {errors}")
            os.remove(filepath)
            return jsonify({
                'error': 'Dados inválidos',
                'validation_errors': errors
            }), 400
        
        # Calcular estatísticas
        logger.info("📈 Iniciando cálculo de estatísticas")
        calculator = StatisticsCalculator()
        
        try:
            results = calculator.calculate_seasonality(data)
            logger.info("✅ Estatísticas calculadas com sucesso")
            logger.info(f"📊 Resultados: Total SKUs={results.get('total_skus')}, "
                       f"Sazonais={results.get('seasonal_skus')}, "
                       f"%={results.get('seasonality_percentage', 0):.2f}")
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {str(e)}")
            logger.error(traceback.format_exc())
            os.remove(filepath)
            return jsonify({
                'error': f'Erro ao calcular estatísticas: {str(e)}',
                'details': traceback.format_exc()
            }), 500
        
        # Limpar arquivo temporário
        try:
            os.remove(filepath)
            logger.info("🗑️ Arquivo temporário removido")
        except:
            logger.warning("⚠️ Não foi possível remover arquivo temporário")
        
        logger.info("✅ === ANÁLISE CONCLUÍDA COM SUCESSO ===")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Erro geral na análise: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Tentar limpar arquivo se existir
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"❌ Erro não tratado: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'error': str(e),
        'type': type(e).__name__,
        'traceback': traceback.format_exc()
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando aplicação SazIA em modo DEBUG")
    app.run(debug=True, port=5000)
