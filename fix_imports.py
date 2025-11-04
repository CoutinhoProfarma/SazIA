# fix_imports.py
import os
import sys

def fix_project_structure():
    """Corrige a estrutura do projeto e cria todos os arquivos necessários"""
    
    print("=" * 60)
    print("CORRIGINDO ESTRUTURA DO PROJETO")
    print("=" * 60)
    
    # 1. Criar pasta utils se não existir
    if not os.path.exists('utils'):
        os.makedirs('utils')
        print("✓ Pasta utils criada")
    else:
        print("✓ Pasta utils já existe")
    
    # 2. IMPORTANTE: Criar __init__.py na pasta utils
    init_file = os.path.join('utils', '__init__.py')
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write('"""Package initialization for utils"""\n')
        f.write('from .data_processor import DataProcessor\n')
        f.write('from .statistics import StatisticalAnalyzer\n')
    print(f"✓ Arquivo {init_file} criado/atualizado")
    
    # 3. Criar data_processor.py se não existir
    data_processor_file = os.path.join('utils', 'data_processor.py')
    if not os.path.exists(data_processor_file):
        with open(data_processor_file, 'w', encoding='utf-8') as f:
            f.write('''import pandas as pd
import numpy as np
from typing import Optional, Dict, List

class DataProcessor:
    """Classe responsável pelo processamento inicial dos dados."""
    
    def __init__(self, filepath: str, sigma_threshold: float = 2):
        self.filepath = filepath
        self.sigma_threshold = sigma_threshold
        self.df = None
        
    def load_data(self) -> Optional[pd.DataFrame]:
        """Carrega dados do arquivo CSV ou Excel."""
        try:
            if self.filepath.endswith('.csv'):
                self.df = pd.read_csv(self.filepath, encoding='utf-8-sig')
            else:
                self.df = pd.read_excel(self.filepath)
            
            if len(self.df.columns) < 25:
                raise ValueError("Arquivo deve ter pelo menos 25 colunas")
            
            columns = ['categoria'] + [f'mes_{i+1}' for i in range(24)]
            self.df.columns = columns[:len(self.df.columns)]
            
            for col in self.df.columns[1:25]:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            self.df = self.df.dropna(subset=['categoria'])
            return self.df
            
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """Retorna lista de categorias únicas."""
        if self.df is not None:
            return self.df['categoria'].unique().tolist()
        return []
    
    def get_category_data(self, category: str) -> pd.Series:
        """Obtém dados de vendas para uma categoria específica."""
        category_data = self.df[self.df['categoria'] == category].iloc[:, 1:25].values.flatten()
        return pd.Series(category_data)
''')
        print(f"✓ Arquivo {data_processor_file} criado")
    else:
        print(f"✓ Arquivo {data_processor_file} já existe")
    
    # 4. Criar statistics.py se não existir
    statistics_file = os.path.join('utils', 'statistics.py')
    if not os.path.exists(statistics_file):
        with open(statistics_file, 'w', encoding='utf-8') as f:
            f.write('''import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Aviso: scipy não está instalado. Algumas funcionalidades podem estar limitadas.")

class StatisticalAnalyzer:
    """Classe para análises estatísticas e cálculo de sazonalidade."""
    
    def __init__(self, df: pd.DataFrame, sigma_threshold: float = 2):
        self.df = df
        self.sigma_threshold = sigma_threshold
        self.calculation_memory = []
        
    def detect_and_treat_outliers(self, data: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Detecta e trata outliers usando z-score."""
        clean_data = data[~np.isnan(data)]
        
        if len(clean_data) == 0:
            return data, {}
        
        mean = np.mean(clean_data)
        std = np.std(clean_data)
        
        z_scores = np.abs((clean_data - mean) / std) if std > 0 else np.zeros_like(clean_data)
        outlier_mask = z_scores > self.sigma_threshold
        
        outlier_min = mean - (self.sigma_threshold * std)
        outlier_max = mean + (self.sigma_threshold * std)
        
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
        """Calcula sazonalidade para uma categoria."""
        category_rows = self.df[self.df['categoria'] == category]
        if category_rows.empty:
            return {}
        
        category_data = category_rows.iloc[0, 1:25].values.astype(float)
        treated_data, stats_info = self.detect_and_treat_outliers(category_data)
        
        if len(treated_data) >= 24:
            year1 = treated_data[:12]
            year2 = treated_data[12:24]
        elif len(treated_data) >= 12:
            year1 = treated_data[:12]
            year2 = np.array([])
        else:
            year1 = treated_data
            year2 = np.array([])
        
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
        
        total_year = np.sum(monthly_averages)
        if total_year > 0:
            seasonality_year = (monthly_averages / total_year * 100).tolist()
        else:
            seasonality_year = [0] * 12
        
        growth_month = []
        for i in range(12):
            if i == 0:
                prev_value = monthly_averages[11]
            else:
                prev_value = monthly_averages[i-1]
            
            if prev_value > 0:
                growth = ((monthly_averages[i] - prev_value) / prev_value * 100)
            else:
                growth = 0
            
            growth_month.append(round(growth, 2))
        
        memory_entry = {
            'categoria': category,
            'media': round(stats_info.get('mean', 0), 2),
            'desvio_padrao': round(stats_info.get('std', 0), 2),
            'outlier_min': round(stats_info.get('outlier_min', 0), 2),
            'outlier_max': round(stats_info.get('outlier_max', 0), 2),
            'outliers_encontrados': stats_info.get('outliers_found', 0)
        }
        
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
        """Processa todas as categorias do DataFrame."""
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
''')
        print(f"✓ Arquivo {statistics_file} criado")
    else:
        print(f"✓ Arquivo {statistics_file} já existe")
    
    # 5. Testar importações
    print("\n" + "=" * 60)
    print("TESTANDO IMPORTAÇÕES")
    print("=" * 60)
    
    # Adicionar diretório atual ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        from utils.data_processor import DataProcessor
        print("✓ DataProcessor importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar DataProcessor: {e}")
        print("  Tentando correção alternativa...")
        
        # Tentar importação alternativa
        sys.path.insert(0, os.getcwd())
        try:
            from utils.data_processor import DataProcessor
            print("  ✓ Importação alternativa funcionou")
        except Exception as e2:
            print(f"  ✗ Erro na importação alternativa: {e2}")
    
    try:
        from utils.statistics import StatisticalAnalyzer
        print("✓ StatisticalAnalyzer importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar StatisticalAnalyzer: {e}")
    
    # 6. Verificar estrutura
    print("\n" + "=" * 60)
    print("ESTRUTURA DO PROJETO")
    print("=" * 60)
    print(f"Diretório atual: {os.getcwd()}")
    print(f"\nConteúdo da pasta utils:")
    if os.path.exists('utils'):
        for file in os.listdir('utils'):
            file_path = os.path.join('utils', file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")
    else:
        print("  Pasta utils não encontrada!")
    
    print("\n" + "=" * 60)
    print("✓ CORREÇÃO CONCLUÍDA")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Execute novamente: python test_setup.py")
    print("2. Se ainda houver erro, execute: python -m pip install scipy")
    print("3. Depois execute: python app.py")

if __name__ == "__main__":
    fix_project_structure()
