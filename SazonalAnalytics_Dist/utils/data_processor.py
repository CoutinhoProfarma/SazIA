import pandas as pd
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
