# test_setup.py
import os
import sys

print("Testando importações...")

try:
    import flask
    print("✓ Flask importado")
except ImportError as e:
    print(f"✗ Erro ao importar Flask: {e}")

try:
    import pandas
    print("✓ Pandas importado")
except ImportError as e:
    print(f"✗ Erro ao importar Pandas: {e}")

try:
    import numpy
    print("✓ NumPy importado")
except ImportError as e:
    print(f"✗ Erro ao importar NumPy: {e}")

try:
    from utils.data_processor import DataProcessor
    print("✓ DataProcessor importado")
except ImportError as e:
    print(f"✗ Erro ao importar DataProcessor: {e}")

try:
    from utils.statistics import StatisticalAnalyzer
    print("✓ StatisticalAnalyzer importado")
except ImportError as e:
    print(f"✗ Erro ao importar StatisticalAnalyzer: {e}")

print("\nVerificando estrutura de pastas...")
dirs = ['uploads', 'static', 'templates', 'utils']
for d in dirs:
    if os.path.exists(d):
        print(f"✓ Pasta {d} existe")
    else:
        print(f"✗ Pasta {d} NÃO existe")
