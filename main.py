#!/usr/bin/env python3
"""
Bergamoto - Sistema de Registro de Ponto Eletrônico
Ponto de entrada principal da aplicação

Este arquivo substitui os arquivos linux/main.py e win/main-win.py,
fornecendo uma interface unificada que funciona em todos os sistemas operacionais.
"""

import sys
import os
from pathlib import Path

# Adicionar diretório src ao path para importações
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    missing_deps = []
    
    # Dependências obrigatórias
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    # Dependências opcionais (com graceful degradation)
    optional_deps = []
    
    try:
        import cv2
    except ImportError:
        optional_deps.append("opencv-python")
    
    try:
        import PIL
    except ImportError:
        optional_deps.append("Pillow")
    
    try:
        import ttkthemes
    except ImportError:
        optional_deps.append("ttkthemes")
    
    if missing_deps:
        print("ERRO: Dependências obrigatórias não encontradas:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstale as dependências com:")
        print("pip install tkinter")
        return False
    
    if optional_deps:
        print("AVISO: Dependências opcionais não encontradas:")
        for dep in optional_deps:
            print(f"  - {dep}")
        print("\nPara funcionalidade completa, instale com:")
        print(f"pip install {' '.join(optional_deps)}")
        print("O sistema funcionará com funcionalidade limitada.\n")
    
    return True

def setup_environment():
    """Configura o ambiente de execução"""
    # Configurar variáveis de ambiente se necessário
    os.environ.setdefault('BERGAMOTO_ENV', 'production')
    
    # Criar diretórios necessários
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

def main():
    """Função principal da aplicação"""
    print("=" * 50)
    print("Bergamoto - Sistema de Registro de Ponto Eletrônico")
    print("=" * 50)
    print()
    
    # Verificar dependências
    if not check_dependencies():
        return 1
    
    # Configurar ambiente
    setup_environment()
    
    try:
        # Importar e executar aplicação principal
        from bergamoto.core.main_app import BergamotoApp
        from bergamoto.utils.logger import setup_logging
        
        # Configurar logging
        logs_dir = project_root / "logs"
        setup_logging("INFO", logs_dir)
        
        print("Iniciando aplicação...")
        print("Digite '----' no campo PIN para encerrar o sistema")
        print()
        
        # Executar aplicação
        app = BergamotoApp()
        app.run()
        
        print("Aplicação finalizada.")
        return 0
        
    except KeyboardInterrupt:
        print("\nSistema interrompido pelo usuário.")
        return 0
    except ImportError as e:
        print(f"Erro de importação: {e}")
        print("Verifique se todos os arquivos estão no local correto.")
        return 1
    except Exception as e:
        print(f"Erro durante execução: {e}")
        return 1

if __name__ == "__main__":
    exit(main())