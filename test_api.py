# test_api.py
import requests
import json

# Testar health check
print("Testando health check...")
try:
    response = requests.get("http://localhost:5000/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*50 + "\n")

# Testar endpoint inexistente
print("Testando endpoint 404...")
try:
    response = requests.get("http://localhost:5000/inexistente")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")
