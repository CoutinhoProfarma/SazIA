# utils/data_processor.py
import pandas as pd
import numpy as np
from typing import Union, Optional
import os
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Classe para processamento de dados de vendas"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        logger.debug("DataProcessor inicializado")
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Carrega dados do arquivo"""
        logger.info(f"📂 Carregando arquivo: {filepath}")
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext not in self.supported_formats:
            logger.error(f"❌ Formato não suportado: {file_ext}")
            raise ValueError(f"Formato não suportado: {file_ext}")
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(filepath)
                logger.info(f"✅ CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
            else:
                df = pd.read_excel(filepath)
                logger.info(f"✅ Excel carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
        except Exception as e:
            logger.error(f"❌ Erro ao ler arquivo: {e}")
            raise
        
        return self.preprocess_data(df)
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pré-processa os dados para análise"""
        logger.info("🔄 Iniciando pré-processamento")
        logger.debug(f"Colunas originais: {list(df.columns)}")
        
        # Verificar colunas obrigatórias
        required_columns = ['sku', 'sales']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"⚠️ Colunas obrigatórias faltando: {missing_columns}")
            logger.info("🔍 Tentando identificar colunas por padrões...")
            df = self._identify_columns(df)
            logger.debug(f"Colunas após identificação: {list(df.columns)}")
        
        # Converter tipos de dados
        if 'sales' in df.columns:
            before_count = len(df)
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
            df = df.dropna(subset=['sales'])
            after_count = len(df)
            if before_count != after_count:
                logger.warning(f"⚠️ {before_count - after_count} linhas removidas (sales inválidas)")
        
        # Adicionar colunas se não existirem
        if 'date' not in df.columns:
            logger.info("📅 Criando coluna de datas fictícias")
            df['date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
        else:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        if 'description' not in df.columns:
            df['description'] = df['sku'].astype(str)
        
        if 'category' not in df.columns:
            df['category'] = 'Geral'
        
        logger.info(f"✅ Pré-processamento concluído: {df.shape}")
        return df
    
    def _identify_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identifica colunas por padrões comuns"""
        column_mapping = {}
        
        for col in df.columns:
            col_lower = str(col).lower()
            logger.debug(f"Analisando coluna: '{col}' (lower: '{col_lower}')")
            
            # Identificar coluna SKU
            if any(term in col_lower for term in ['sku', 'codigo', 'código', 'produto', 'item']):
                column_mapping[col] = 'sku'
                logger.info(f"✅ Coluna '{col}' identificada como SKU")
            
            # Identificar coluna de vendas
            elif any(term in col_lower for term in ['venda', 'sales', 'quantidade', 'qty', 'volume']):
                column_mapping[col] = 'sales'
                logger.info(f"✅ Coluna '{col}' identificada como VENDAS")
            
            # Identificar coluna de data
            elif any(term in col_lower for term in ['data', 'date', 'periodo', 'período']):
                column_mapping[col] = 'date'
                logger.info(f"✅ Coluna '{col}' identificada como DATA")
            
            # Identificar coluna de descrição
            elif any(term in col_lower for term in ['desc', 'nome', 'name']):
                column_mapping[col] = 'description'
                logger.info(f"✅ Coluna '{col}' identificada como DESCRIÇÃO")
            
            # Identificar coluna de categoria
            elif any(term in col_lower for term in ['categ', 'grupo', 'group']):
                column_mapping[col] = 'category'
                logger.info(f"✅ Coluna '{col}' identificada como CATEGORIA")
        
        # Renomear colunas
        if column_mapping:
            df = df.rename(columns=column_mapping)
            logger.info(f"📝 {len(column_mapping)} colunas renomeadas")
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> tuple[bool, list]:
        """Valida os dados"""
        errors = []
        logger.info("🔍 Validando dados...")
        
        # Verificar se há dados
        if df.empty:
            errors.append("DataFrame está vazio")
            logger.error("❌ DataFrame vazio")
        
        # Verificar colunas obrigatórias
        required_columns = ['sku', 'sales']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            errors.append(f"Colunas obrigatórias faltando: {missing}")
            logger.error(f"❌ Colunas faltando: {missing}")
        
        # Verificar valores negativos em vendas
        if 'sales' in df.columns and (df['sales'] < 0).any():
            errors.append("Existem valores negativos em vendas")
            logger.warning("⚠️ Valores negativos detectados em vendas")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("✅ Dados válidos")
        else:
            logger.error(f"❌ Dados inválidos: {errors}")
        
        return is_valid, errors
