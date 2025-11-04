# create_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("🔄 Criando dados de exemplo...")

# Criar dados de exemplo
np.random.seed(42)

# Gerar datas mensais
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=30*i) for i in range(12)]

# Criar dados para múltiplos SKUs
data = []

# SKU com alta sazonalidade (vendas de verão)
summer_sales = [50, 60, 80, 100, 150, 200, 250, 200, 150, 100, 70, 50]
for i, (date, sales) in enumerate(zip(dates, summer_sales)):
    data.append({
        'Data': date,
        'SKU': 'PROD001',
        'Descrição': 'Protetor Solar FPS 50',
        'Categoria': 'Verão',
        'Vendas': sales + np.random.randint(-10, 10)
    })

# SKU sem sazonalidade (vendas constantes)
for i, date in enumerate(dates):
    data.append({
        'Data': date,
        'SKU': 'PROD002', 
        'Descrição': 'Shampoo Neutro',
        'Categoria': 'Higiene',
        'Vendas': 100 + np.random.randint(-5, 5)
    })

# SKU com sazonalidade moderada
winter_sales = [150, 180, 120, 80, 60, 50, 40, 50, 70, 100, 140, 170]
for i, (date, sales) in enumerate(zip(dates, winter_sales)):
    data.append({
        'Data': date,
        'SKU': 'PROD003',
        'Descrição': 'Hidratante Corporal',
        'Categoria': 'Inverno',
        'Vendas': sales + np.random.randint(-10, 10)
    })

# Criar DataFrame
df = pd.DataFrame(data)

# Salvar em CSV
df.to_csv('sample_data.csv', index=False, encoding='utf-8-sig')
print("✅ Arquivo sample_data.csv criado com sucesso!")
print(f"📊 Shape: {df.shape}")
print(f"📋 Colunas: {list(df.columns)}")
print("\n👀 Primeiras linhas:")
print(df.head(10))

# Salvar também em Excel
df.to_excel('sample_data.xlsx', index=False)
print("\n✅ Arquivo sample_data.xlsx também criado!")
print("\n📁 Arquivos criados na pasta atual:")
print("  - sample_data.csv")
print("  - sample_data.xlsx")
print("\n🎯 Próximo passo: Execute 'python app_debug.py' para testar")
