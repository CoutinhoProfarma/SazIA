# utils/statistics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

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
        # Converter para array e remover zeros e NaN para análise de outliers
        data = np.array(data, dtype=float)
        clean_data = data[~np.isnan(data)]
        # Considerar apenas valores positivos para análise
        positive_data = clean_data[clean_data > 0]
        
        if len(positive_data) < 3:  # Precisamos de pelo menos 3 pontos
            return data, {
                'mean': np.mean(clean_data) if len(clean_data) > 0 else 0,
                'std': 0,
                'outlier_min': 0,
                'outlier_max': np.inf,
                'outliers_found': 0,
                'total_points': len(clean_data)
            }
        
        # Calcular estatísticas nos dados positivos
        mean = np.mean(positive_data)
        std = np.std(positive_data)
        
        if std == 0:  # Todos os valores são iguais
            return data, {
                'mean': mean,
                'std': 0,
                'outlier_min': mean,
                'outlier_max': mean,
                'outliers_found': 0,
                'total_points': len(positive_data)
            }
        
        # Calcular z-scores
        z_scores = np.abs((positive_data - mean) / std)
        
        # Identificar outliers
        outlier_mask = z_scores > self.sigma_threshold
        
        # Calcular limites
        outlier_min = max(0, mean - (self.sigma_threshold * std))  # Não pode ser negativo
        outlier_max = mean + (self.sigma_threshold * std)
        
        # Tratar outliers
        treated_data = data.copy()
        
        if np.any(outlier_mask):
            # Calcular média dos valores não-outliers
            non_outlier_values = positive_data[~outlier_mask]
            if len(non_outlier_values) > 0:
                replacement_value = np.mean(non_outlier_values)
            else:
                replacement_value = mean
            
            # Aplicar tratamento no array original
            for i, val in enumerate(data):
                if val > 0:  # Só verificar valores positivos
                    z_score = abs((val - mean) / std)
                    if z_score > self.sigma_threshold:
                        treated_data[i] = replacement_value
        
        stats_info = {
            'mean': mean,
            'std': std,
            'outlier_min': outlier_min,
            'outlier_max': outlier_max,
            'outliers_found': int(np.sum(outlier_mask)),
            'total_points': len(positive_data)
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
        try:
            # Obter dados da categoria
            category_row = self.df[self.df['categoria'] == category]
            
            if category_row.empty:
                print(f"Categoria '{category}' não encontrada")
                return None
            
            # Pegar apenas colunas numéricas (excluir 'categoria')
            numeric_cols = [col for col in category_row.columns if col != 'categoria']
            category_data = category_row[numeric_cols].values.flatten()
            
            # Garantir que temos dados suficientes
            if len(category_data) < 12:
                print(f"Dados insuficientes para categoria '{category}': {len(category_data)} meses")
                return None
            
            # Tratar outliers
            treated_data, stats_info = self.detect_and_treat_outliers(category_data)
            
            # Considerar apenas os primeiros 24 meses (2 anos)
            if len(treated_data) > 24:
                treated_data = treated_data[:24]
            
            # Dividir em anos (máximo 2 anos)
            num_months = len(treated_data)
            
            # Calcular médias mensais
            monthly_averages = np.zeros(12)
            monthly_counts = np.zeros(12)
            
            for i, value in enumerate(treated_data):
                month_index = i % 12  # 0-11 para Jan-Dez
                if not np.isnan(value) and value >= 0:
                    monthly_averages[month_index] += value
                    monthly_counts[month_index] += 1
            
            # Calcular médias
            for i in range(12):
                if monthly_counts[i] > 0:
                    monthly_averages[i] = monthly_averages[i] / monthly_counts[i]
                else:
                    monthly_averages[i] = 0
            
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
                
                curr_value = monthly_averages[i]
                
                if prev_value > 0:
                    growth = ((curr_value - prev_value) / prev_value * 100)
                elif curr_value > 0:
                    growth = 100  # Crescimento de 0 para valor positivo
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
                'outliers_encontrados': stats_info.get('outliers_found', 0),
                'total_meses': num_months
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
            
        except Exception as e:
            print(f"Erro ao calcular sazonalidade para '{category}': {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def process_all_categories(self) -> Dict:
        """
        Processa todas as categorias do DataFrame.
        
        Returns:
            Dicionário com resultados completos
        """
        try:
            categories = self.df['categoria'].unique()
            results = {
                'categories': [],
                'calculation_memory': [],
                'summary': {
                    'total_categories': len(categories),
                    'processed': 0,
                    'errors': 0
                }
            }
            
            print(f"Processando {len(categories)} categorias...")
            
            for i, category in enumerate(categories):
                print(f"Processando categoria {i+1}/{len(categories)}: {category}")
                
                category_result = self.calculate_seasonality(category)
                
                if category_result:
                    results['categories'].append(category_result)
                    results['summary']['processed'] += 1
                else:
                    results['summary']['errors'] += 1
                    print(f"Erro ao processar categoria: {category}")
            
            results['calculation_memory'] = self.calculation_memory
            
            print(f"Processamento concluído: {results['summary']['processed']} categorias processadas")
            
            return results
            
        except Exception as e:
            print(f"Erro no processamento geral: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                'categories': [],
                'calculation_memory': [],
                'error': str(e)
            }
