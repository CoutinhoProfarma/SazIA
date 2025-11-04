# test_excel.py
import pandas as pd
import sys
import os

# Adicionar o diretório ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor
from utils.statistics import StatisticalAnalyzer

def test_excel_processing():
    """Testa o processamento do arquivo Excel."""
    
    print("=" * 60)
    print("TESTE DE PROCESSAMENTO DO EXCEL")
    print("=" * 60)
    
    # Caminho do arquivo (ajuste conforme necessário)
    filepath = "uploads/teste.xlsx"  # Coloque seu arquivo aqui
    
    if not os.path.exists(filepath):
        print(f"Arquivo não encontrado: {filepath}")
        print("Por favor, coloque o arquivo Excel na pasta 'uploads'")
        return
    
    print(f"\n1. Carregando arquivo: {filepath}")
    
    try:
        # Testar carregamento direto com pandas
        df = pd.read_excel(filepath)
        print(f"   ✓ Arquivo carregado com pandas: {df.shape}")
        print(f"   Primeiras colunas: {list(df.columns[:5])}")
        print(f"   Primeiras linhas:")
        print(df.head(3))
        
    except Exception as e:
        print(f"   ✗ Erro ao carregar com pandas: {e}")
        return
    
    print("\n2. Testando DataProcessor")
    
    try:
        processor = DataProcessor(filepath, sigma_threshold=2)
        df_processed = processor.load_data()
        
        if df_processed is not None:
            print(f"   ✓ Dados processados com sucesso")
            print(f"   Shape: {df_processed.shape}")
            print(f"   Categorias: {processor.get_categories()[:5]}...")
        else:
            print("   ✗ Erro no processamento dos dados")
            
    except Exception as e:
        print(f"   ✗ Erro no DataProcessor: {e}")
        import traceback
        print(traceback.format_exc())
        return
    
    print("\n3. Testando StatisticalAnalyzer")
    
    try:
        if df_processed is not None:
            analyzer = StatisticalAnalyzer(df_processed, sigma_threshold=2)
            
            # Testar com uma categoria
            categories = processor.get_categories()
            if categories:
                test_category = categories[0]
                print(f"   Testando com categoria: {test_category}")
                
                result = analyzer.calculate_seasonality(test_category)
                
                if result:
                    print(f"   ✓ Análise concluída")
                    print(f"   Sazonalidade: {result['seasonality_year'][:6]}...")
                    print(f"   Crescimento: {result['growth_month'][:6]}...")
                else:
                    print("   ✗ Erro na análise")
                    
    except Exception as e:
        print(f"   ✗ Erro no StatisticalAnalyzer: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_excel_processing()
