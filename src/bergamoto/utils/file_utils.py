"""
Utilitários para manipulação de arquivos e diretórios
"""
import os
from pathlib import Path


def ensure_directory_exists(directory: Path) -> None:
    """
    Garante que um diretório existe, criando-o se necessário
    
    Args:
        directory: Caminho do diretório
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Retorna o diretório raiz do projeto
    
    Returns:
        Path para o diretório raiz
    """
    current_file = Path(__file__).resolve()
    # Navegar até encontrar o diretório que contém src/
    for parent in current_file.parents:
        if (parent / "src").exists() and (parent / "config").exists():
            return parent
    
    # Fallback para o diretório atual
    return Path.cwd()


def get_data_directory() -> Path:
    """
    Retorna o diretório de dados baseado no sistema operacional
    
    Returns:
        Path para o diretório de dados
    """
    project_root = get_project_root()
    
    # Para desenvolvimento, usar diretório data/ no projeto
    data_dir = project_root / "data"
    ensure_directory_exists(data_dir)
    
    return data_dir