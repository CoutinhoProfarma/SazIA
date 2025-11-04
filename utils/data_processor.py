# utils/data_processor.py
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import warnings
warnings.filterwarnings('ignore')

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
            # Tentar carregar o arquivo
            if self.filepath.endswith('.csv'):
                self.df = pd.read_csv(self.filepath, encoding='utf-8-sig')
                if self.df.empty:
                    self.df = pd.read_csv(self.filepath, encoding='latin1')
            else:
                # Para Excel, tentar diferentes engines
                try:
                    self.df = pd.read_excel(self.filepath, engine='openpyxl')
                except:
                    try:
                        self.df = pd.read_excel(self.filepath, engine='xlrd')
                    except:
                        self.df = pd.read_excel(self.filepath)
            
            print(f"Arquivo carregado: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print(f"Colunas encontradas: {list(self.df.columns)[:5]}...")
            
            # Verificar se há dados
            if self.df.empty:
                raise ValueError("Arquivo está vazio")
            
            # Validar estrutura mínima (categoria + pelo menos 12 meses)
            if len(self.df.columns) < 13:
                raise ValueError(f"Arquivo deve ter pelo menos 13 colunas. Encontradas: {len(self.df.columns)}")
            
            # Identificar e renomear colunas
            # Assumir que a primeira coluna é categoria e as demais são meses
            original_columns = self.df.columns.tolist()
            
            # Criar novos nomes de colunas
            new_columns = ['categoria']
            
            # Para as colunas de dados, usar os nomes originais ou criar padrão
            for i in range(1, len(original_columns)):
                if i <= 24:
                    new_columns.append(f'mes_{i}')
                else:
                    new_columns.append(f'extra_{i}')
            
            # Aplicar novos nomes
            self.df.columns = new_columns[:len(self.df.columns)]
            
            # Limpar a coluna categoria
            self.df['categoria'] = self.df['categoria'].astype(str).str.strip()
            
            # Remover linhas onde categoria está vazia ou é NaN
            self.df = self.df[self.df['categoria'].notna()]
            self.df = self.df[self.df['categoria'] != '']
            self.df = self.df[self.df['categoria'] != 'nan']
            
            # Converter colunas numéricas, mantendo apenas as primeiras 24 colunas de dados
            num_cols = min(24, len(self.df.columns) - 1)
            
            for i in range(1, num_cols + 1):
                col_name = f'mes_{i}'
                if col_name in self.df.columns:
                    # Limpar valores não numéricos
                    self.df[col_name] = pd.to_numeric(
                        self.df[col_name].astype(str).str.replace(',', '.').str.replace(' ', ''),
                        errors='coerce'
                    )
                    # Preencher NaN com 0
                    self.df[col_name] = self.df[col_name].fillna(0)
            
            # Manter apenas categoria + 24 meses (ou menos se não houver)
            cols_to_keep = ['categoria'] + [f'mes_{i}' for i in range(1, min(25, len(self.df.columns)))]
            self.df = self.df[cols_to_keep]
            
            # Remover linhas completamente zeradas (exceto categoria)
            numeric_cols = [col for col in self.df.columns if col != 'categoria']
            self.df = self.df[self.df[numeric_cols].sum(axis=1) > 0]
            
            print(f"Dados processados: {self.df.shape[0]} categorias, {len(numeric_cols)} meses")
            print(f"Categorias encontradas: {self.df['categoria'].nunique()}")
            
            return self.df
            
        except Exception as e:
            print(f"Erro detalhado ao carregar arquivo: {str(e)}")
            import traceback
            print(traceback.format_exc())
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
            Series com dados mensais
        """
        category_data = self.df[self.df['categoria'] == category]
        if not category_data.empty:
            # Pegar apenas as colunas numéricas
            numeric_data = category_data.iloc[0, 1:].values
            return pd.Series(numeric_data)
        return pd.Series()
