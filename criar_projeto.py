# criar_projeto.py
import os
import sys

def criar_estrutura_completa():
    """Cria toda a estrutura do projeto com os arquivos necessários"""
    
    print("=" * 60)
    print("CRIANDO PROJETO SAZONAL ANALYTICS")
    print("=" * 60)
    
    # 1. Criar estrutura de pastas
    print("\n1. Criando estrutura de pastas...")
    pastas = [
        'utils',
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/img',
        'uploads',
        'tests'
    ]
    
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"   ✓ Pasta criada: {pasta}")
    
    # 2. Criar arquivo __init__.py em utils
    print("\n2. Criando arquivo __init__.py em utils...")
    with open('utils/__init__.py', 'w', encoding='utf-8') as f:
        f.write('# Package initialization\n')
    print("   ✓ utils/__init__.py criado")
    
    # 3. Criar data_processor.py
    print("\n3. Criando utils/data_processor.py...")
    data_processor_code = '''import pandas as pd
import numpy as np
from typing import Optional, Dict, List

class DataProcessor:
    """
    Classe responsável pelo processamento inicial dos dados.
    """
    
    def __init__(self, filepath: str, sigma_threshold: float = 2):
        """
        Inicializa o processador de dados.
        
        Args:
            filepath: Caminho do arquivo a ser processado
            sigma_threshold: Número de desvios padrão para outliers
        """
        self.filepath = filepath
        self.sigma_threshold = sigma_threshold
        self.df = None
        
    def load_data(self) -> Optional[pd.DataFrame]:
        """
        Carrega dados do arquivo CSV ou Excel.
        
        Returns:
            DataFrame com os dados ou None se houver erro
        """
        try:
            if self.filepath.endswith('.csv'):
                self.df = pd.read_csv(self.filepath, encoding='utf-8-sig')
            else:
                self.df = pd.read_excel(self.filepath)
            
            # Validar estrutura do arquivo
            if len(self.df.columns) < 25:
                raise ValueError("Arquivo deve ter pelo menos 25 colunas (categoria + 24 meses)")
            
            # Renomear colunas para padronização
            columns = ['categoria'] + [f'mes_{i+1}' for i in range(24)]
            self.df.columns = columns[:len(self.df.columns)]
            
            # Converter valores numéricos
            for col in self.df.columns[1:25]:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Remover linhas com categoria vazia
            self.df = self.df.dropna(subset=['categoria'])
            
            return self.df
            
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """
        Retorna lista de categorias únicas.
        
        Returns:
            Lista com categorias mercadológicas
        """
        if self.df is not None:
            return self.df['categoria'].unique().tolist()
        return []
    
    def get_category_data(self, category: str) -> pd.Series:
        """
        Obtém dados de vendas para uma categoria específica.
        
        Args:
            category: Nome da categoria
            
        Returns:
            Series com dados de 24 meses
        """
        category_data = self.df[self.df['categoria'] == category].iloc[:, 1:25].values.flatten()
        return pd.Series(category_data)
'''
    
    with open('utils/data_processor.py', 'w', encoding='utf-8') as f:
        f.write(data_processor_code)
    print("   ✓ utils/data_processor.py criado")
    
    # 4. Criar statistics.py
    print("\n4. Criando utils/statistics.py...")
    statistics_code = '''import pandas as pd
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
'''
    
    with open('utils/statistics.py', 'w', encoding='utf-8') as f:
        f.write(statistics_code)
    print("   ✓ utils/statistics.py criado")
    
    # 5. Verificar se scipy está instalado
    print("\n5. Verificando scipy...")
    try:
        import scipy
        print("   ✓ scipy já está instalado")
    except ImportError:
        print("   ! scipy não está instalado")
        print("   Execute: pip install scipy")
    
    print("\n" + "=" * 60)
    print("✓ ESTRUTURA CRIADA COM SUCESSO!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Execute: python test_setup.py")
    print("2. Se tudo estiver OK, execute: python app.py")

if __name__ == "__main__":
    criar_estrutura_completa()
