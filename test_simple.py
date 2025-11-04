# test_simple.py
import sys
import os

# Forçar o path
sys.path.insert(0, os.getcwd())

print("Testando importação simples...")
print(f"Diretório: {os.getcwd()}")
print(f"Arquivos em utils: {os.listdir('utils') if os.path.exists('utils') else 'Não existe'}")

try:
    # Tentar importação direta
    import utils.data_processor
    print("✓ Módulo utils.data_processor importado")
    
    # Tentar importar a classe
    from utils.data_processor import DataProcessor
    print("✓ Classe DataProcessor importada")
    
    # Tentar criar instância
    dp = DataProcessor("test.csv")
    print("✓ Instância DataProcessor criada")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
