"""
Aplicação principal unificada do sistema Bergamoto
"""
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from pathlib import Path
from typing import Optional

try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = tk.Tk

from ..database.manager import DatabaseManager
from ..core.employee import EmployeeService
from ..core.timesheet import TimesheetService
from ..utils.logger import get_logger
from ..utils.file_utils import get_data_directory


class BergamotoApp:
    """Aplicação principal do sistema Bergamoto"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Inicializar banco de dados
        data_dir = get_data_directory()
        db_path = data_dir / "bergamoto.db"
        
        try:
            self.db_manager = DatabaseManager(db_path)
            self.employee_service = EmployeeService(self.db_manager)
            self.timesheet_service = TimesheetService(self.db_manager)
            self.logger.info("Serviços inicializados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar serviços: {e}")
            raise
        
        # Estado da aplicação
        self.running = True
        self.lock = threading.Lock()
        
        # Configurações da UI
        self.ui_config = {
            'theme': 'equilux',
            'fullscreen': True,
            'font_family': 'Helvetica',
            'font_size': 16
        }
    
    def run(self):
        """Executa o loop principal da aplicação"""
        self.logger.info("Iniciando aplicação Bergamoto")
        
        try:
            # Verificar se há funcionários cadastrados
            employees = self.employee_service.get_all_employees()
            if not employees:
                self._show_no_employees_message()
                return
            
            # Loop principal
            while self.running:
                try:
                    # Obter PIN do usuário
                    pin = self._get_pin_input()
                    
                    if pin == '----':
                        self.logger.info("Encerrando aplicação por solicitação do usuário")
                        break
                    
                    if not pin:
                        continue
                    
                    # Buscar funcionário
                    employee = self.employee_service.get_employee_by_pin(pin)
                    if not employee:
                        messagebox.showerror("Erro", "PIN não encontrado. Tente novamente.")
                        continue
                    
                    # Confirmar identidade
                    if self._confirm_employee_identity(employee):
                        # Registrar ponto
                        success, message = self.timesheet_service.clock_in(employee)
                        
                        if success:
                            messagebox.showinfo("Sucesso", message)
                            self._show_daily_summary(employee)
                        else:
                            messagebox.showerror("Erro", message)
                    
                    # Pequena pausa entre operações
                    time.sleep(2)
                    
                except KeyboardInterrupt:
                    self.logger.info("Interrompido pelo usuário")
                    break
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {e}")
                    messagebox.showerror("Erro", f"Erro interno: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Erro crítico na aplicação: {e}")
            messagebox.showerror("Erro Crítico", f"Erro ao executar aplicação: {str(e)}")
        
        finally:
            self.logger.info("Aplicação finalizada")
    
    def _get_pin_input(self) -> Optional[str]:
        """
        Exibe janela para entrada de PIN
        
        Returns:
            PIN digitado pelo usuário ou None se cancelado
        """
        pin = None
        
        def submit_pin():
            nonlocal pin
            pin = pin_entry.get().strip()
            root.quit()
        
        with self.lock:
            # Criar janela
            try:
                root = ThemedTk(theme=self.ui_config['theme'])
                style = ttk.Style(root)
                style.theme_use(self.ui_config['theme'])
            except:
                root = tk.Tk()
            
            root.title("Bergamoto - Entrada de PIN")
            root.attributes("-topmost", True)
            
            if self.ui_config['fullscreen']:
                root.attributes("-fullscreen", True)
            
            # Frame principal
            main_frame = ttk.Frame(root, padding="20") if hasattr(ttk, 'Frame') else tk.Frame(root)
            main_frame.pack(expand=True, fill=tk.BOTH)
            
            # Título
            title_label = ttk.Label(
                main_frame, 
                text="Sistema de Ponto Eletrônico",
                font=(self.ui_config['font_family'], self.ui_config['font_size'] + 4, 'bold')
            ) if hasattr(ttk, 'Label') else tk.Label(
                main_frame,
                text="Sistema de Ponto Eletrônico",
                font=(self.ui_config['font_family'], self.ui_config['font_size'] + 4, 'bold')
            )
            title_label.pack(pady=20)
            
            # Instrução
            instruction_label = ttk.Label(
                main_frame,
                text="Digite seu PIN:",
                font=(self.ui_config['font_family'], self.ui_config['font_size'])
            ) if hasattr(ttk, 'Label') else tk.Label(
                main_frame,
                text="Digite seu PIN:",
                font=(self.ui_config['font_family'], self.ui_config['font_size'])
            )
            instruction_label.pack(pady=10)
            
            # Campo de entrada
            pin_entry = ttk.Entry(
                main_frame,
                font=(self.ui_config['font_family'], self.ui_config['font_size']),
                justify='center',
                width=20
            ) if hasattr(ttk, 'Entry') else tk.Entry(
                main_frame,
                font=(self.ui_config['font_family'], self.ui_config['font_size']),
                justify='center',
                width=20
            )
            pin_entry.pack(pady=10)
            pin_entry.focus_set()
            
            # Botão
            submit_button = ttk.Button(
                main_frame,
                text="Confirmar",
                command=submit_pin
            ) if hasattr(ttk, 'Button') else tk.Button(
                main_frame,
                text="Confirmar",
                command=submit_pin
            )
            submit_button.pack(pady=20)
            
            # Instruções adicionais
            help_label = ttk.Label(
                main_frame,
                text="Digite '----' para encerrar o sistema",
                font=(self.ui_config['font_family'], self.ui_config['font_size'] - 2),
                foreground='gray'
            ) if hasattr(ttk, 'Label') else tk.Label(
                main_frame,
                text="Digite '----' para encerrar o sistema",
                font=(self.ui_config['font_family'], self.ui_config['font_size'] - 2),
                fg='gray'
            )
            help_label.pack(pady=10)
            
            # Bind Enter
            root.bind('<Return>', lambda e: submit_pin())
            
            # Executar
            root.mainloop()
            root.destroy()
        
        return pin
    
    def _confirm_employee_identity(self, employee) -> bool:
        """
        Exibe janela de confirmação de identidade
        
        Args:
            employee: Dados do funcionário
            
        Returns:
            True se confirmado, False caso contrário
        """
        confirmed = False
        
        def confirm():
            nonlocal confirmed
            confirmed = True
            root.quit()
        
        def cancel():
            root.quit()
        
        with self.lock:
            # Criar janela
            try:
                root = ThemedTk(theme=self.ui_config['theme'])
                style = ttk.Style(root)
                style.theme_use(self.ui_config['theme'])
            except:
                root = tk.Tk()
            
            root.title("Bergamoto - Confirmação")
            root.attributes("-topmost", True)
            
            if self.ui_config['fullscreen']:
                root.attributes("-fullscreen", True)
            
            # Frame principal
            main_frame = ttk.Frame(root, padding="20") if hasattr(ttk, 'Frame') else tk.Frame(root)
            main_frame.pack(expand=True, fill=tk.BOTH)
            
            # Informações do funcionário
            info_text = f"Nome: {employee.name}\nSetor: {employee.setor}\n\nEsse é você?"
            info_label = ttk.Label(
                main_frame,
                text=info_text,
                font=(self.ui_config['font_family'], self.ui_config['font_size']),
                justify='center'
            ) if hasattr(ttk, 'Label') else tk.Label(
                main_frame,
                text=info_text,
                font=(self.ui_config['font_family'], self.ui_config['font_size']),
                justify='center'
            )
            info_label.pack(pady=30)
            
            # Frame dos botões
            button_frame = ttk.Frame(main_frame) if hasattr(ttk, 'Frame') else tk.Frame(main_frame)
            button_frame.pack(pady=20)
            
            # Botões
            yes_button = ttk.Button(
                button_frame,
                text="Sim",
                command=confirm,
                width=15
            ) if hasattr(ttk, 'Button') else tk.Button(
                button_frame,
                text="Sim",
                command=confirm,
                width=15
            )
            yes_button.pack(side=tk.LEFT, padx=10)
            
            no_button = ttk.Button(
                button_frame,
                text="Não",
                command=cancel,
                width=15
            ) if hasattr(ttk, 'Button') else tk.Button(
                button_frame,
                text="Não",
                command=cancel,
                width=15
            )
            no_button.pack(side=tk.RIGHT, padx=10)
            
            # Bind Enter para confirmar
            root.bind('<Return>', lambda e: confirm())
            
            # Executar
            root.mainloop()
            root.destroy()
        
        return confirmed
    
    def _show_daily_summary(self, employee):
        """Exibe resumo do dia após registro"""
        try:
            from datetime import datetime
            today = datetime.now().strftime('%d-%m-%Y')
            summary = self.timesheet_service.get_daily_summary(employee.id, today)
            
            if summary:
                records_text = "\n".join([
                    f"{r['time']} - {r['description']}" 
                    for r in summary['records']
                ])
                
                total_text = ""
                if 'total_hours' in summary:
                    total_text = f"\nHoras trabalhadas: {summary['total_hours']:.2f}h"
                
                info_text = f"Registros de hoje:\n\n{records_text}{total_text}"
                messagebox.showinfo("Resumo do Dia", info_text)
        except Exception as e:
            self.logger.error(f"Erro ao mostrar resumo diário: {e}")
    
    def _show_no_employees_message(self):
        """Mostra mensagem quando não há funcionários cadastrados"""
        message = ("Nenhum funcionário encontrado no sistema.\n\n"
                  "Por favor, execute o script de criação de funcionários primeiro:\n"
                  "python scripts/create_sample_employees.py")
        messagebox.showerror("Sistema Não Inicializado", message)
        self.logger.warning("Sistema executado sem funcionários cadastrados")


def main():
    """Função principal para executar a aplicação"""
    from ..utils.logger import setup_logging
    
    # Configurar logging
    setup_logging("INFO")
    
    try:
        # Criar e executar aplicação
        app = BergamotoApp()
        app.run()
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Erro ao executar aplicação: {e}")
        messagebox.showerror("Erro Fatal", f"Erro ao executar aplicação: {str(e)}")


if __name__ == "__main__":
    main()