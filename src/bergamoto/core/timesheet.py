"""
Serviço para gerenciamento de registros de ponto
"""
from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from ..database.manager import DatabaseManager
from ..database.models import Employee, TimeRecord
from ..utils.logger import get_logger
from ..utils.camera import PhotoCapture


class TimesheetService:
    """Serviço para operações de registro de ponto"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = get_logger(__name__)
        self.photo_capture = PhotoCapture()
    
    def clock_in(self, employee: Employee) -> Tuple[bool, str]:
        """
        Registra ponto para um funcionário
        
        Args:
            employee: Dados do funcionário
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Verificar se o funcionário tem ID válido
            if not employee or employee.id <= 0:
                return False, "Funcionário inválido"
            
            today = datetime.now().strftime('%d-%m-%Y')
            
            # Verificar número de registros do dia
            record_count = self.db.count_daily_records(employee.id, today)
            max_records = int(self.db.get_config_value('max_records_per_day', '4'))
            
            if record_count >= max_records:
                return False, f"Limite de {max_records} registros diários atingido"
            
            # Determinar tipo do próximo registro
            try:
                record_type = self.db.get_next_record_type(employee.id, today)
            except ValueError as e:
                return False, str(e)
            
            # Capturar foto
            self.logger.info(f"Iniciando captura de foto para {employee.name}")
            photo_blob = self.photo_capture.capture_photo()
            
            if not photo_blob:
                return False, "Falha na captura da foto"
            
            # Criar registro
            record = TimeRecord(
                employee_id=employee.id,
                date=today,
                time=datetime.now().strftime('%H:%M:%S'),
                record_type=record_type,
                photo=photo_blob
            )
            
            # Inserir no banco
            if self.db.insert_time_record(record):
                self.logger.info(f"Ponto registrado: {record_type} para {employee.name}")
                return True, f"Ponto registrado: {self._get_record_type_description(record_type)}"
            else:
                return False, "Erro ao salvar registro no banco de dados"
            
        except Exception as e:
            self.logger.error(f"Erro no registro de ponto: {e}")
            return False, f"Erro interno: {str(e)}"
    
    def get_daily_records(self, employee_id: int, date: str) -> List[TimeRecord]:
        """
        Busca registros de ponto de um funcionário em uma data
        
        Args:
            employee_id: ID do funcionário
            date: Data no formato dd-mm-yyyy
            
        Returns:
            Lista de registros
        """
        try:
            return self.db.get_daily_records(employee_id, date)
        except Exception as e:
            self.logger.error(f"Erro ao buscar registros diários: {e}")
            return []
    
    def get_daily_summary(self, employee_id: int, date: str) -> Optional[dict]:
        """
        Gera resumo do dia de trabalho
        
        Args:
            employee_id: ID do funcionário
            date: Data no formato dd-mm-yyyy
            
        Returns:
            Dicionário com resumo ou None se não houver dados
        """
        try:
            records = self.get_daily_records(employee_id, date)
            if not records:
                return None
            
            summary = {
                'date': date,
                'employee_id': employee_id,
                'total_records': len(records),
                'records': []
            }
            
            for record in records:
                summary['records'].append({
                    'time': record.time,
                    'type': record.record_type,
                    'description': self._get_record_type_description(record.record_type)
                })
            
            # Calcular horas trabalhadas se houver registros suficientes
            if len(records) >= 2:
                summary.update(self._calculate_work_hours(records))
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo diário: {e}")
            return None
    
    def _calculate_work_hours(self, records: List[TimeRecord]) -> dict:
        """
        Calcula horas trabalhadas baseado nos registros
        
        Args:
            records: Lista de registros ordenados por horário
            
        Returns:
            Dicionário com cálculos de horas
        """
        result = {
            'total_hours': 0.0,
            'periods': [],
            'break_duration': 0.0
        }
        
        # Agrupar registros em pares (entrada/saída)
        times = []
        for record in sorted(records, key=lambda x: x.time):
            times.append(datetime.strptime(record.time, '%H:%M:%S'))
        
        # Calcular períodos trabalhados
        for i in range(0, len(times) - 1, 2):
            if i + 1 < len(times):
                start = times[i]
                end = times[i + 1]
                period_hours = (end - start).total_seconds() / 3600
                
                result['periods'].append({
                    'start': start.strftime('%H:%M'),
                    'end': end.strftime('%H:%M'),
                    'hours': round(period_hours, 2)
                })
                result['total_hours'] += period_hours
        
        # Calcular tempo de intervalo se houver 4+ registros
        if len(times) >= 4:
            break_start = times[1]  # Saída do primeiro período
            break_end = times[2]    # Entrada do segundo período
            result['break_duration'] = (break_end - break_start).total_seconds() / 3600
        
        result['total_hours'] = round(result['total_hours'], 2)
        result['break_duration'] = round(result['break_duration'], 2)
        
        return result
    
    def _get_record_type_description(self, record_type: str) -> str:
        """
        Retorna descrição amigável do tipo de registro
        
        Args:
            record_type: Tipo do registro
            
        Returns:
            Descrição do tipo de registro
        """
        descriptions = {
            'entrada': 'Entrada',
            'saida': 'Saída',
            'almoco_saida': 'Saída para Almoço',
            'almoco_volta': 'Volta do Almoço'
        }
        return descriptions.get(record_type, record_type.capitalize())
    
    def get_incomplete_days(self, employee_id: int, start_date: str, end_date: str) -> List[dict]:
        """
        Busca dias com registros incompletos
        
        Args:
            employee_id: ID do funcionário
            start_date: Data inicial (dd-mm-yyyy)
            end_date: Data final (dd-mm-yyyy)
            
        Returns:
            Lista de dias com registros incompletos
        """
        incomplete_days = []
        
        try:
            # Converter datas
            start = datetime.strptime(start_date, '%d-%m-%Y')
            end = datetime.strptime(end_date, '%d-%m-%Y')
            
            current = start
            while current <= end:
                date_str = current.strftime('%d-%m-%Y')
                record_count = self.db.count_daily_records(employee_id, date_str)
                
                if 0 < record_count < 4:  # Registros incompletos
                    records = self.get_daily_records(employee_id, date_str)
                    incomplete_days.append({
                        'date': date_str,
                        'record_count': record_count,
                        'records': [r.record_type for r in records]
                    })
                
                current += timedelta(days=1)
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dias incompletos: {e}")
        
        return incomplete_days