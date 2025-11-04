# utils/statistics.py
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional

class StatisticsCalculator:
    """Classe para cálculos estatísticos de sazonalidade"""
    
    def __init__(self, threshold_cv: float = 0.3):
        """
        Inicializa o calculador
        
        Args:
            threshold_cv: Limite de CV para considerar sazonal (padrão 30%)
        """
        self.threshold_cv = threshold_cv
    
    def calculate_seasonality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula índices de sazonalidade e estatísticas
        
        Args:
            data: DataFrame com dados de vendas
            
        Returns:
            Dict com análise completa de sazonalidade
        """
        results = {
            'items': [],
            'stats': {},
            'seasonal_skus': 0,
            'total_skus': 0,
            'seasonality_percentage': 0.0,
            'period': {},
            'threshold_cv': self.threshold_cv * 100,
            'sku_metrics': []
        }
        
        # Processar cada SKU
        seasonal_count = 0
        total_count = 0
        all_sales = []
        
        for sku in data['sku'].unique():
            sku_data = data[data['sku'] == sku]
            
            # Calcular métricas do SKU
            sku_metrics = self._calculate_sku_metrics(sku_data)
            results['items'].append(sku_metrics)
            results['sku_metrics'].append(sku_metrics)
            
            # Contadores
            total_count += 1
            if sku_metrics['is_seasonal']:
                seasonal_count += 1
            
            # Coletar todas as vendas
            all_sales.extend(sku_data['sales'].tolist())
        
        # Estatísticas gerais
        if all_sales:
            sales_array = np.array(all_sales)
            mean_val = float(np.mean(sales_array))
            std_val = float(np.std(sales_array))
            
            results['stats'] = {
                'mean': mean_val,
                'median': float(np.median(sales_array)),
                'std': std_val,
                'cv': (std_val / mean_val * 100) if mean_val > 0 else 0,
                'min': float(np.min(sales_array)),
                'max': float(np.max(sales_array)),
                'range': float(np.max(sales_array) - np.min(sales_array)),
                'q1': float(np.percentile(sales_array, 25)),
                'q3': float(np.percentile(sales_array, 75))
            }
        else:
            results['stats'] = {
                'mean': 0, 'median': 0, 'std': 0, 'cv': 0,
                'min': 0, 'max': 0, 'range': 0, 'q1': 0, 'q3': 0
            }
        
        # Resumo geral
        results['total_skus'] = total_count
        results['seasonal_skus'] = seasonal_count
        results['seasonality_percentage'] = (seasonal_count / total_count * 100) if total_count > 0 else 0
        
        # Período analisado
        if 'date' in data.columns:
            results['period'] = {
                'start': data['date'].min().strftime('%Y-%m-%d') if pd.notna(data['date'].min()) else '',
                'end': data['date'].max().strftime('%Y-%m-%d') if pd.notna(data['date'].max()) else ''
            }
        else:
            results['period'] = {'start': '', 'end': ''}
        
        return results
    
    def _calculate_sku_metrics(self, sku_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula métricas para um SKU específico
        
        Args:
            sku_data: Dados de vendas do SKU
            
        Returns:
            Dict com métricas do SKU
        """
        sales = sku_data['sales'].values
        mean_sales = np.mean(sales)
        std_sales = np.std(sales)
        
        # Calcular coeficiente de variação
        cv = (std_sales / mean_sales) if mean_sales > 0 else 0
        
        # Determinar se é sazonal
        is_seasonal = cv > self.threshold_cv
        
        # Calcular índice de sazonalidade (0-100)
        seasonality_index = min(cv * 100, 100)
        
        return {
            'sku': sku_data['sku'].iloc[0],
            'description': sku_data['description'].iloc[0] if 'description' in sku_data.columns else '',
            'category': sku_data['category'].iloc[0] if 'category' in sku_data.columns else '',
            'is_seasonal': is_seasonal,
            'seasonality_index': float(seasonality_index),
            'avg_sales': float(mean_sales),
            'total_sales': float(np.sum(sales)),
            'cv': float(cv * 100),
            'std': float(std_sales),
            'min_sales': float(np.min(sales)),
            'max_sales': float(np.max(sales))
        }
