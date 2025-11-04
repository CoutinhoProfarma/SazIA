# tests/test_processor.py
import unittest
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
from utils.statistics import StatisticalAnalyzer

class TestDataProcessor(unittest.TestCase):
    """Testes para o processador de dados."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar dados de teste
        self.test_data = pd.DataFrame({
            'categoria': ['Cat A', 'Cat A', 'Cat B', 'Cat B'],
            'mes_1': [100, 110, 200, 210],
            'mes_2': [105, 115, 205, 215],
            'mes_3': [95, 105, 195, 205],
            'mes_4': [110, 120, 210, 220],
            'mes_5': [115, 125, 215, 225],
            'mes_6': [120, 130, 220, 230],
            'mes_7': [125, 135, 225, 235],
            'mes_8': [130, 140, 230, 240],
            'mes_9': [135, 145, 235, 245],
            'mes_10': [140, 150, 240, 250],
            'mes_11': [145, 155, 245, 255],
            'mes_12': [150, 160, 250, 260],
            'mes_13': [105, 115, 205, 215],
            'mes_14': [110, 120, 210, 220],
            'mes_15': [100, 110, 200, 210],
            'mes_16': [115, 125, 215, 225],
            'mes_17': [120, 130, 220, 230],
            'mes_18': [125, 135, 225, 235],
            'mes_19': [130, 140, 230, 240],
            'mes_20': [135, 145, 235, 245],
            'mes_21': [140, 150, 240, 250],
            'mes_22': [145, 155, 245, 255],
            'mes_23': [150, 160, 250, 260],
            'mes_24': [155, 165, 255, 265]
        })
        
    def test_outlier_detection(self):
        """Testa detecção de outliers."""
        analyzer = StatisticalAnalyzer(self.test_data, sigma_threshold=2)
        
        # Adicionar outlier artificial
        data_with_outlier = np.array([100, 105, 110, 500, 115, 120])  # 500 é outlier
        treated_data, stats = analyzer.detect_and_treat_outliers(data_with_outlier)
        
        # Verificar se outlier foi detectado
        self.assertEqual(stats['outliers_found'], 1)
        
        # Verificar se outlier foi tratado
        self.assertNotIn(500, treated_data)
        
    def test_seasonality_calculation(self):
        """Testa cálculo de sazonalidade."""
        analyzer = StatisticalAnalyzer(self.test_data, sigma_threshold=2)
        result = analyzer.calculate_seasonality('Cat A')
        
        # Verificar estrutura do resultado
        self.assertIn('category', result)
        self.assertIn('seasonality_year', result)
        self.assertIn('growth_month', result)
        
        # Verificar tamanho dos arrays
        self.assertEqual(len(result['seasonality_year']), 12)
        self.assertEqual(len(result['growth_month']), 12)
        
        # Verificar que soma da sazonalidade é ~100%
        total_seasonality = sum(result['seasonality_year'])
        self.assertAlmostEqual(total_seasonality, 100, places=1)
        
    def test_growth_calculation(self):
        """Testa cálculo de crescimento mensal."""
        analyzer = StatisticalAnalyzer(self.test_data, sigma_threshold=2)
        result = analyzer.calculate_seasonality('Cat B')
        
        growth = result['growth_month']
        
        # Verificar que crescimento está calculado corretamente
        self.assertEqual(len(growth), 12)
        
        # Verificar que valores são numéricos
        for value in growth:
            self.assertIsInstance(value, (int, float))

if __name__ == '__main__':
    unittest.main()
