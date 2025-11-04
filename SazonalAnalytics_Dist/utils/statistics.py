import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

class StatisticalAnalyzer:
    """
    Classe para análises estatísticas e cálculo de sazonalidade.
    """
    
    def __init__(self, df: pd.DataFrame, sigma_threshold: float = 2):
        """
        Inicializa o analisador estatístico.
        
        Args:
            df: DataFrame com os dados
            sigma_threshold: Limite de sigmas para outliers
        """
        self.df = df
        self.sigma_threshold = sigma_threshold
        self.calculation_memory = []
        
    def detect_and_treat_outliers(self, data: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Detecta e trata outliers usando z-score.
        
        Args:
            data: Array de dados
            
        Returns:
            Tupla com dados tratados e estatísticas
        """
        # Remover NaN para cálculos
        clean_data = data[~np.isnan(data)]
        
        if len(clean_data) == 0:
            return data, {}
        
        # Calcular estatísticas
        mean = np.mean(clean_data)
        std = np.std(clean_data)
        
        # Calcular z-scores
        z_scores = np.abs((clean_data - mean) / std) if std > 0 else np.zeros_like(clean_data)
        
        # Identificar outliers
        outlier_mask = z_scores > self.sigma_threshold
        
        # Calcular limites
        outlier_min = mean - (self.sigma_threshold * std)
        outlier_max = mean + (self.sigma_threshold * std)
        
        # Tratar outliers - substituir pela média dos valores válidos
        treated_data = clean_data.copy()
        if np.any(outlier_mask):
            valid_mean = np.mean(clean_data[~outlier_mask]) if np.any(~outlier_mask) else mean
            treated_data[outlier_mask] = valid_mean
        
        stats_info = {
            'mean': float(mean),
            'std': float(std),
            'outlier_min': float(outlier_min),
            'outlier_max': float(outlier_max),
            'outliers_found': int(np.sum(outlier_mask)),
            'total_points': len(clean_data)
        }
        
        return treated_data, stats_info
    
    def calculate_seasonality(self, category: str) -> Dict:
        """
        Calcula sazonalidade para uma categoria.
        
        Args:
            category: Nome da categoria
            
        Returns:
            Dicionário com métricas de sazonalidade
        """
        # Obter dados da categoria
        category_rows = self.df[self.df['categoria'] == category]
        if category_rows.empty:
            return {}
        
        # Pegar apenas a primeira linha se houver duplicatas
        category_data = category_rows.iloc[0, 1:25].values.astype(float)
        
        # Tratar outliers
        treated_data, stats_info = self.detect_and_treat_outliers(category_data)
        
        # Reorganizar dados por mês (2 anos = 24 meses)
        # Assumindo que os dados estão em ordem cronológica
        if len(treated_data) >= 24:
            year1 = treated_data[:12]
            year2 = treated_data[12:24]
        elif len(treated_data) >= 12:
            year1 = treated_data[:12]
            year2 = np.array([])
        else:
            year1 = treated_data
            year2 = np.array([])
        
        # Calcular média mensal considerando os 2 anos
        monthly_averages = []
        for month in range(12):
            month_values = []
            if month < len(year1) and not np.isnan(year1[month]):
                month_values.append(year1[month])
            if month < len(year2) and not np.isnan(year2[month]):
                month_values.append(year2[month])
            
            if month_values:
                monthly_averages.append(np.mean(month_values))
            else:
                monthly_averages.append(0)
        
        monthly_averages = np.array(monthly_averages)
        
        # Calcular sazonalidade como % do ano
        total_year = np.sum(monthly_averages)
        if total_year > 0:
            seasonality_year = (monthly_averages / total_year * 100).tolist()
        else:
            seasonality_year = [0] * 12
        
        # Calcular crescimento mês a mês
        growth_month = []
        for i in range(12):
            if i == 0:
                # Janeiro comparado com dezembro
                prev_value = monthly_averages[11]
            else:
                prev_value = monthly_averages[i-1]
            
            if prev_value > 0:
                growth = ((monthly_averages[i] - prev_value) / prev_value * 100)
            else:
                growth = 0
            
            growth_month.append(round(growth, 2))
        
        # Salvar memória de cálculo
        memory_entry = {
            'categoria': category,
            'media': round(stats_info.get('mean', 0), 2),
            'desvio_padrao': round(stats_info.get('std', 0), 2),
            'outlier_min': round(stats_info.get('outlier_min', 0), 2),
            'outlier_max': round(stats_info.get('outlier_max', 0), 2),
            'outliers_encontrados': stats_info.get('outliers_found', 0)
        }
        
        # Adicionar baseline mensal
        for i, value in enumerate(monthly_averages):
            memory_entry[f'baseline_mes_{i+1}'] = round(value, 2)
        
        self.calculation_memory.append(memory_entry)
        
        return {
            'category': category,
            'seasonality_year': [round(x, 2) for x in seasonality_year],
            'growth_month': growth_month,
            'monthly_averages': monthly_averages.tolist(),
            'stats': stats_info
        }
    
    def process_all_categories(self) -> Dict:
        """
        Processa todas as categorias do DataFrame.
        
        Returns:
            Dicionário com resultados completos
        """
        categories = self.df['categoria'].unique()
        results = {
            'categories': [],
            'calculation_memory': []
        }
        
        for category in categories:
            category_result = self.calculate_seasonality(category)
            if category_result:
                results['categories'].append(category_result)
        
        results['calculation_memory'] = self.calculation_memory
        
        return results
