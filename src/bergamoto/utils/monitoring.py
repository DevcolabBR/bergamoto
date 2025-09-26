"""
Sistema de monitoramento e health check para o Bergamoto
"""
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import platform

from ..utils.logger import get_logger
from ..utils.file_utils import get_data_directory


class HealthChecker:
    """Sistema de monitoramento de saúde da aplicação"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.data_dir = get_data_directory()
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Verifica a saúde geral do sistema
        
        Returns:
            Dicionário com status dos componentes
        """
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Verificar componentes individuais
        checks = [
            ('database', self._check_database),
            ('filesystem', self._check_filesystem),
            ('dependencies', self._check_dependencies),
            ('system_resources', self._check_system_resources)
        ]
        
        failed_checks = 0
        
        for component, check_func in checks:
            try:
                result = check_func()
                health_report['components'][component] = result
                
                if not result.get('healthy', False):
                    failed_checks += 1
                    
            except Exception as e:
                self.logger.error(f"Erro no health check de {component}: {e}")
                health_report['components'][component] = {
                    'healthy': False,
                    'error': str(e)
                }
                failed_checks += 1
        
        # Determinar status geral
        if failed_checks == 0:
            health_report['overall_status'] = 'healthy'
        elif failed_checks < len(checks) // 2:
            health_report['overall_status'] = 'degraded'
        else:
            health_report['overall_status'] = 'unhealthy'
        
        return health_report
    
    def _check_database(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        db_path = self.data_dir / "bergamoto.db"
        
        result = {
            'healthy': False,
            'details': {}
        }
        
        try:
            # Verificar se arquivo existe
            if not db_path.exists():
                result['details']['error'] = 'Arquivo de banco não encontrado'
                return result
            
            # Verificar se é possível conectar
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar integridade
                cursor.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()[0]
                
                if integrity != 'ok':
                    result['details']['integrity_error'] = integrity
                    return result
                
                # Contar registros nas tabelas principais
                tables_info = {}
                
                for table in ['employees', 'time_records']:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        tables_info[table] = count
                    except sqlite3.Error:
                        tables_info[table] = 'table_not_found'
                
                result['details']['tables'] = tables_info
                result['details']['database_size'] = db_path.stat().st_size
                result['healthy'] = True
                
        except sqlite3.Error as e:
            result['details']['database_error'] = str(e)
        
        return result
    
    def _check_filesystem(self) -> Dict[str, Any]:
        """Verifica sistema de arquivos"""
        result = {
            'healthy': False,
            'details': {}
        }
        
        try:
            # Verificar diretórios necessários
            required_dirs = [
                self.data_dir,
                self.data_dir.parent / "logs",
                self.data_dir.parent / "config"
            ]
            
            missing_dirs = []
            for dir_path in required_dirs:
                if not dir_path.exists():
                    missing_dirs.append(str(dir_path))
            
            if missing_dirs:
                result['details']['missing_directories'] = missing_dirs
                return result
            
            # Verificar espaço em disco
            statvfs = os.statvfs(self.data_dir)
            free_space = statvfs.f_frsize * statvfs.f_available
            total_space = statvfs.f_frsize * statvfs.f_blocks
            
            result['details']['disk_space'] = {
                'free_bytes': free_space,
                'total_bytes': total_space,
                'free_percentage': (free_space / total_space) * 100
            }
            
            # Verificar permissões de escrita
            test_file = self.data_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                result['details']['write_permissions'] = True
            except (PermissionError, OSError):
                result['details']['write_permissions'] = False
                return result
            
            result['healthy'] = True
            
        except Exception as e:
            result['details']['filesystem_error'] = str(e)
        
        return result
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica dependências do sistema"""
        result = {
            'healthy': True,
            'details': {
                'required': {},
                'optional': {}
            }
        }
        
        # Dependências obrigatórias
        required_deps = {
            'tkinter': 'tkinter',
            'sqlite3': 'sqlite3'
        }
        
        # Dependências opcionais
        optional_deps = {
            'opencv': 'cv2',
            'pillow': 'PIL',
            'ttkthemes': 'ttkthemes',
            'pandas': 'pandas'
        }
        
        # Verificar dependências obrigatórias
        for name, module in required_deps.items():
            try:
                __import__(module)
                result['details']['required'][name] = 'available'
            except ImportError:
                result['details']['required'][name] = 'missing'
                result['healthy'] = False
        
        # Verificar dependências opcionais
        for name, module in optional_deps.items():
            try:
                __import__(module)
                result['details']['optional'][name] = 'available'
            except ImportError:
                result['details']['optional'][name] = 'missing'
        
        return result
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Verifica recursos do sistema"""
        result = {
            'healthy': True,
            'details': {}
        }
        
        try:
            # Informações do sistema
            result['details']['platform'] = {
                'system': platform.system(),
                'release': platform.release(),
                'python_version': platform.python_version()
            }
            
            # Verificar se há processos travados (simulado)
            # Em uma implementação real, verificaria processos específicos
            result['details']['processes'] = 'normal'
            
        except Exception as e:
            result['details']['system_error'] = str(e)
            result['healthy'] = False
        
        return result
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do banco de dados"""
        db_path = self.data_dir / "bergamoto.db"
        
        if not db_path.exists():
            return {'error': 'Database not found'}
        
        stats = {}
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Estatísticas de funcionários
                cursor.execute("SELECT COUNT(*) FROM employees WHERE active = 1")
                stats['active_employees'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT setor) FROM employees WHERE active = 1")
                stats['departments_count'] = cursor.fetchone()[0]
                
                # Estatísticas de registros
                today = datetime.now().strftime('%d-%m-%Y')
                cursor.execute("SELECT COUNT(*) FROM time_records WHERE date = ?", (today,))
                stats['today_records'] = cursor.fetchone()[0]
                
                # Registros da última semana
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%d-%m-%Y')
                cursor.execute("""
                    SELECT COUNT(*) FROM time_records 
                    WHERE date >= ? AND date <= ?
                """, (week_ago, today))
                stats['week_records'] = cursor.fetchone()[0]
                
                # Top 5 funcionários com mais registros
                cursor.execute("""
                    SELECT e.name, COUNT(tr.id) as record_count
                    FROM employees e
                    LEFT JOIN time_records tr ON e.id = tr.employee_id
                    GROUP BY e.id, e.name
                    ORDER BY record_count DESC
                    LIMIT 5
                """)
                stats['top_employees'] = [
                    {'name': name, 'records': count}
                    for name, count in cursor.fetchall()
                ]
                
        except sqlite3.Error as e:
            stats['database_error'] = str(e)
        
        return stats


class ErrorHandler:
    """Manipulador centralizado de erros"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def handle_critical_error(self, error: Exception, context: str = ""):
        """
        Trata erros críticos que podem interromper a aplicação
        
        Args:
            error: Exceção capturada
            context: Contexto onde o erro ocorreu
        """
        error_msg = f"Erro crítico{f' em {context}' if context else ''}: {error}"
        self.logger.critical(error_msg, exc_info=True)
        
        # Em produção, poderia enviar alerta por email/webhook
        self._log_error_for_analysis(error, context, "critical")
    
    def handle_recoverable_error(self, error: Exception, context: str = ""):
        """
        Trata erros recuperáveis que não interrompem a aplicação
        
        Args:
            error: Exceção capturada  
            context: Contexto onde o erro ocorreu
        """
        error_msg = f"Erro recuperável{f' em {context}' if context else ''}: {error}"
        self.logger.error(error_msg, exc_info=True)
        
        self._log_error_for_analysis(error, context, "recoverable")
    
    def _log_error_for_analysis(self, error: Exception, context: str, severity: str):
        """Log estruturado para análise posterior"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'severity': severity,
            'platform': platform.system()
        }
        
        # Log em formato JSON para facilitar análise
        import json
        self.logger.info(f"ERROR_ANALYSIS: {json.dumps(error_data)}")


# Instância global do error handler
error_handler = ErrorHandler()