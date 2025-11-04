# build.py
import os
import sys
import shutil
import subprocess

def create_executable():
    """Cria executável da aplicação"""
    
    print("=" * 60)
    print("BUILD - SAZONAL ANALYTICS")
    print("=" * 60)
    
    # Verificar PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Limpar builds anteriores
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    print("\n1. Criando executável principal...")
    
    # Comando PyInstaller
    command = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=SazonalAnalytics',
        '--add-data', 'templates;templates',
        '--add-data', 'static;static',
        '--add-data', 'utils;utils',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=scipy',
        '--hidden-import=flask',
        '--hidden-import=openpyxl',
        '--hidden-import=xlsxwriter',
        '--clean',
        'desktop_launcher.py'
    ]
    
    subprocess.check_call(command)
    
    print("\n2. Criando estrutura de distribuição...")
    
    # Criar pasta de distribuição
    dist_folder = 'SazonalAnalytics_Dist'
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)
    
    # Copiar executável
    shutil.copy('dist/SazonalAnalytics.exe', dist_folder)
    
    # Copiar pastas necessárias
    shutil.copytree('templates', f'{dist_folder}/templates')
    shutil.copytree('static', f'{dist_folder}/static')
    shutil.copytree('utils', f'{dist_folder}/utils')
    
    # Criar pasta uploads
    os.makedirs(f'{dist_folder}/uploads', exist_ok=True)
    
    # Criar arquivo de instruções
    with open(f'{dist_folder}/LEIA-ME.txt', 'w', encoding='utf-8') as f:
        f.write("""
SISTEMA DE ANÁLISE DE SAZONALIDADE - PROFARMA
=============================================

COMO USAR:
1. Execute o arquivo 'SazonalAnalytics.exe'
2. Clique em "Iniciar Sistema"
3. O navegador abrirá automaticamente
4. Faça upload do arquivo de dados
5. Analise os resultados

REQUISITOS:
- Windows 7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge)

SUPORTE:
Entre em contato com a equipe de TI
        """)
    
    print(f"\n✓ Build concluído com sucesso!")
    print(f"✓ Arquivos gerados em: {dist_folder}")
    print("\nPara executar: SazonalAnalytics.exe")

if __name__ == '__main__':
    create_executable()
