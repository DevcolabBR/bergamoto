#!/usr/bin/env python3
"""
Script de configuração e inicialização do sistema Bergamoto
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class BergamotoSetup:
    """Classe para configuração inicial do sistema"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
    
    def run_setup(self):
        """Executa a configuração completa do sistema"""
        print("=" * 60)
        print("Configuração do Sistema Bergamoto")
        print("=" * 60)
        print()
        
        # 1. Criar diretórios necessários
        self.create_directories()
        
        # 2. Configurar arquivo de ambiente
        self.setup_environment_file()
        
        # 3. Verificar dependências
        self.check_dependencies()
        
        # 4. Executar migração do banco de dados
        self.run_database_migration()
        
        # 5. Criar funcionários de exemplo (opcional)
        if self.ask_yes_no("Deseja criar funcionários de exemplo?"):
            self.create_sample_employees()
        
        print("\n" + "=" * 60)
        print("Configuração concluída com sucesso!")
        print("=" * 60)
        print()
        print("Para executar o sistema:")
        print("  python main.py")
        print()
        print("Para ver logs:")
        print(f"  tail -f {self.logs_dir / 'bergamoto.log'}")
        print()
    
    def create_directories(self):
        """Cria diretórios necessários"""
        print("1. Criando diretórios...")
        
        directories = [
            self.data_dir,
            self.logs_dir,
            self.project_root / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
            print(f"   ✓ {directory}")
        
        print("   Diretórios criados com sucesso!\n")
    
    def setup_environment_file(self):
        """Configura arquivo de ambiente"""
        print("2. Configurando arquivo de ambiente...")
        
        env_example = self.config_dir / ".env.example"
        env_file = self.project_root / ".env"
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            print(f"   ✓ Arquivo .env criado a partir do exemplo")
        elif env_file.exists():
            print(f"   ✓ Arquivo .env já existe")
        else:
            # Criar arquivo .env básico
            env_content = """# Configuração do Bergamoto
DB_NAME=bergamoto.db
UI_THEME=equilux
UI_FULLSCREEN=true
LOG_LEVEL=INFO
"""
            env_file.write_text(env_content)
            print(f"   ✓ Arquivo .env criado")
        
        print("   Configuração de ambiente concluída!\n")
    
    def check_dependencies(self):
        """Verifica e instala dependências"""
        print("3. Verificando dependências...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("   ⚠ Arquivo requirements.txt não encontrado")
            return
        
        try:
            # Verificar se pip está disponível
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            
            # Perguntar se deve instalar dependências
            if self.ask_yes_no("Instalar dependências automaticamente?"):
                print("   Instalando dependências...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("   ✓ Dependências instaladas com sucesso!")
                else:
                    print("   ⚠ Erro ao instalar algumas dependências:")
                    print(f"   {result.stderr}")
                    print("   Você pode instalar manualmente com:")
                    print(f"   pip install -r {requirements_file}")
            else:
                print("   Para instalar dependências manualmente:")
                print(f"   pip install -r {requirements_file}")
        
        except subprocess.CalledProcessError:
            print("   ⚠ pip não encontrado. Instale as dependências manualmente.")
        
        print()
    
    def run_database_migration(self):
        """Executa migração do banco de dados"""
        print("4. Configurando banco de dados...")
        
        try:
            # Adicionar src ao path
            src_path = self.project_root / "src"
            sys.path.insert(0, str(src_path))
            
            # Executar migração
            from scripts.migrate_database import main as migrate_main
            result = migrate_main()
            
            if result == 0:
                print("   ✓ Banco de dados configurado com sucesso!")
            else:
                print("   ⚠ Erro na configuração do banco de dados")
        
        except ImportError as e:
            print(f"   ⚠ Erro ao importar migração: {e}")
            print("   Execute manualmente: python scripts/migrate_database.py")
        except Exception as e:
            print(f"   ⚠ Erro na migração: {e}")
        
        print()
    
    def create_sample_employees(self):
        """Cria funcionários de exemplo"""
        print("5. Criando funcionários de exemplo...")
        
        try:
            # Adicionar src ao path
            src_path = self.project_root / "src" 
            sys.path.insert(0, str(src_path))
            
            from bergamoto.database.manager import DatabaseManager
            from bergamoto.core.employee import EmployeeService
            from bergamoto.utils.file_utils import get_data_directory
            
            # Configurar serviços
            data_dir = get_data_directory()
            db_manager = DatabaseManager(data_dir / "bergamoto.db")
            employee_service = EmployeeService(db_manager)
            
            # Funcionários de exemplo
            sample_employees = [
                ("1001", "João Silva", "vendas", "Maria Santos"),
                ("1002", "Maria Oliveira", "ti", "Carlos Lima"),
                ("1003", "Pedro Santos", "adm", "Ana Costa"),
                ("1004", "Ana Costa", "financeiro", "João Silva"),
                ("1005", "Carlos Lima", "vendas", "Maria Santos")
            ]
            
            created = 0
            for pin, name, setor, supervisor in sample_employees:
                if employee_service.create_employee(pin, name, setor, supervisor):
                    created += 1
                    print(f"   ✓ {name} (PIN: {pin})")
            
            print(f"   {created} funcionários criados com sucesso!")
        
        except Exception as e:
            print(f"   ⚠ Erro ao criar funcionários: {e}")
        
        print()
    
    def ask_yes_no(self, question: str) -> bool:
        """Pergunta sim/não para o usuário"""
        while True:
            answer = input(f"{question} [s/N]: ").lower().strip()
            if answer in ['s', 'sim', 'y', 'yes']:
                return True
            elif answer in ['n', 'não', 'nao', 'no', '']:
                return False
            else:
                print("Por favor, responda 's' para sim ou 'n' para não.")


def main():
    """Função principal do setup"""
    try:
        setup = BergamotoSetup()
        setup.run_setup()
        return 0
    except KeyboardInterrupt:
        print("\nConfiguração cancelada pelo usuário.")
        return 1
    except Exception as e:
        print(f"\nErro durante configuração: {e}")
        return 1


if __name__ == "__main__":
    exit(main())