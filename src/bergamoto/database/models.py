"""
Modelos de dados para o sistema Bergamoto
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Employee:
    """Modelo de dados para funcionário"""
    id: int = 0
    pin: str = ''
    name: str = ''
    setor: str = ''
    supervisor: str = ''
    creation_date: str = ''
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.creation_date == '':
            self.creation_date = datetime.now().strftime('%d-%m-%Y')


@dataclass
class TimeRecord:
    """Modelo de dados para registro de ponto"""
    id: Optional[int] = None
    employee_id: int = 0
    date: str = ''
    time: str = ''
    record_type: str = 'entrada'  # entrada, saida, almoco_saida, almoco_volta
    photo: Optional[bytes] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.date == '':
            self.date = datetime.now().strftime('%d-%m-%Y')
        if self.time == '':
            self.time = datetime.now().strftime('%H:%M:%S')


@dataclass
class DailySummary:
    """Modelo de dados para resumo diário de trabalho"""
    id: Optional[int] = None
    employee_id: int = 0
    date: str = ''
    total_hours: float = 0.0
    regular_hours: float = 0.0
    overtime_hours: float = 0.0
    break_duration: float = 0.0
    status: str = 'incomplete'  # complete, incomplete, absent
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.date == '':
            self.date = datetime.now().strftime('%d-%m-%Y')