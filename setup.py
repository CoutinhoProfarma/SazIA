# setup.py
import os
import sys

def create_project_structure():
    """Cria a estrutura de pastas necessária."""
    
    directories = [
        'uploads',
        'static',
        'static/css',
        'static/js', 
        'static/img',
        'templates',
        'utils',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Diretório criado/verificado: {directory}")
    
    # Criar __init__.py em utils
    init_file = 'utils/__init__.py'
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"✓ Arquivo criado: {init_file}")
    
    print("\n✓ Estrutura do projeto criada com sucesso!")
    
def check_dependencies():
    """Verifica as dependências necessárias."""
    
    print("\nVerificando dependências...")
    
    required = [
        'flask',
        'pandas',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'scipy',
        'werkzeug'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} instalado")
        except ImportError:
            print(f"✗ {package} NÃO instalado")
            missing.append(package)
    
    if missing:
        print(f"\nPacotes faltando: {', '.join(missing)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("\n✓ Todas as dependências estão instaladas!")
    return True

def check_files():
    """Verifica se os arquivos principais existem."""
    
    print("\nVerificando arquivos...")
    
    required_files = [
        'app.py',
        'utils/data_processor.py',
        'utils/statistics.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} existe")
        else:
            print(f"✗ {file} NÃO existe")
            missing.append(file)
    
    if missing:
        print(f"\nArquivos faltando: {', '.join(missing)}")
        print("Certifique-se de criar todos os arquivos necessários.")
        return False
    
    print("\n✓ Todos os arquivos necessários existem!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("CONFIGURAÇÃO DO PROJETO SAZONAL-ANALYTICS")
    print("=" * 50)
    
    # Criar estrutura
    create_project_structure()
    
    # Verificar dependências
    deps_ok = check_dependencies()
    
    # Verificar arquivos
    files_ok = check_files()
    
    print("\n" + "=" * 50)
    if deps_ok and files_ok:
        print("✓ PROJETO PRONTO PARA EXECUTAR!")
        print("\nExecute: python app.py")
    else:
        print("✗ PROJETO PRECISA DE CONFIGURAÇÃO")
        print("\nVerifique os itens marcados com ✗ acima")
    print("=" * 50)
