# test_app.py
import pandas as pd
import numpy as np
from utils.statistics import StatisticsCalculator
from utils.report_generator import ReportGenerator
from utils.data_processor import DataProcessor

def test_basic_flow():
    """Testa o fluxo básico da aplicação"""
    
    # Criar dados de teste
    np.random.seed(42)
    test_data = pd.DataFrame({
        'sku': ['SKU001'] * 12 + ['SKU002'] * 12 + ['SKU003'] * 12,
        'sales': np.concatenate([
            np.random.normal(100, 50, 12),  # SKU001 - alta variação (sazonal)
            np.random.normal(200, 10, 12),  # SKU002 - baixa variação (não sazonal)
            np.random.normal(150, 70, 12),  # SKU003 - muito alta variação (muito sazonal)
        ]),
        'date': pd.date_range('2023-01-01', periods=36, freq='M'),
        'description': ['Produto 1'] * 12 + ['Produto 2'] * 12 + ['Produto 3'] * 12,
        'category': ['Cat A'] * 12 + ['Cat B'] * 12 + ['Cat A'] * 12
    })
    
    # Processar dados
    processor = DataProcessor()
    processed_data = processor.preprocess_data(test_data)
    
    # Calcular estatísticas
    calculator = StatisticsCalculator()
    results = calculator.calculate_seasonality(processed_data)
    
    # Exibir resultados
    print("=" * 50)
    print("TESTE DO SISTEMA SAZIA")
    print("=" * 50)
    print(f"Total de SKUs: {results['total_skus']}")
    print(f"SKUs Sazonais: {results['seasonal_skus']}")
    print(f"% de Sazonalidade: {results['seasonality_percentage']:.2f}%")
    print(f"\nEstatísticas:")
    print(f"  Média: {results['stats']['mean']:.2f}")
    print(f"  CV: {results['stats']['cv']:.2f}%")
    print(f"  Min: {results['stats']['min']:.2f}")
    print(f"  Max: {results['stats']['max']:.2f}")
    
    # Testar geração de relatório
    generator = ReportGenerator()
    report_path = generator.generate_excel_report(results)
    print(f"\nRelatório gerado: {report_path}")
    
    return results

if __name__ == "__main__":
    test_basic_flow()
