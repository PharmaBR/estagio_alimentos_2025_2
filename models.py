"""
Modelos de dados para o sistema de preenchimento de documentos de estágio.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserData:
    """Dados do usuário/estudante"""
    nome: str
    ra: str
    polo: str
    turma: str
    telefone_ddd: str
    telefone_numero: str
    email: str
    semestre: str
    data: str


@dataclass
class InternshipData:
    """Dados do estágio"""
    disciplina_estagio: str
    codigo_disciplina: str
    local_estagio: str
    supervisor_estagio: str
    carga_horaria: int
    titulo_atividade_obrigatoria: str


@dataclass
class ShiftData:
    """Dados de turno/atividade individual"""
    horario_inicio: str
    horario_fim: str
    data: str
    atividade_realizada: str
    
    def get_hours(self) -> float:
        """Calcula as horas do turno"""
        try:
            h_inicio = int(self.horario_inicio.split(':')[0])
            m_inicio = int(self.horario_inicio.split(':')[1])
            h_fim = int(self.horario_fim.split(':')[0])
            m_fim = int(self.horario_fim.split(':')[1])
            
            total_minutes = (h_fim * 60 + m_fim) - (h_inicio * 60 + m_inicio)
            return total_minutes / 60.0
        except:
            return 0.0


@dataclass
class ComplementaryActivity:
    """Atividade complementar sem horário específico (Atividade Obrigatória ou Preenchimento de Documentos)"""
    titulo: str
    horas: float
    
    def __post_init__(self):
        if self.horas <= 0:
            raise ValueError("Horas deve ser maior que zero")


@dataclass
class ActivityStorage:
    """Armazenamento de descrições de atividades por encontro"""
    encounter_date: str  # Data do encontro no formato DD/MM/YYYY
    description: str     # Descrição detalhada da atividade
    
    def __post_init__(self):
        if not self.description.strip():
            raise ValueError("Descrição não pode estar vazia")


@dataclass
class DocumentData:
    """
    Agrupa todos os dados necessários para gerar os documentos.
    Facilita o gerenciamento de dados complexos para múltiplos documentos.
    """
    user: UserData
    internship: InternshipData
    shifts: List[ShiftData]
    activity_descriptions: List[ActivityStorage] = field(default_factory=list)
    complementary_activities: List[ComplementaryActivity] = field(default_factory=list)
    
    def __post_init__(self):
        """Validações e cálculos automáticos"""
        if not self.shifts:
            raise ValueError("Pelo menos um turno deve ser fornecido")
        if self.internship.carga_horaria <= 0:
            raise ValueError("Carga horária deve ser positiva")
        
        # Calcular atividades complementares automaticamente
        self._calculate_complementary_activities()
    
    def get_total_shift_hours(self) -> float:
        """Retorna o total de horas dos turnos"""
        return sum(shift.get_hours() for shift in self.shifts)
    
    def get_total_complementary_hours(self) -> float:
        """Retorna o total de horas das atividades complementares"""
        return sum(act.horas for act in self.complementary_activities)
    
    def get_total_hours(self) -> float:
        """Retorna o total de horas (turnos + complementares)"""
        return self.get_total_shift_hours() + self.get_total_complementary_hours()
    
    def get_missing_hours(self) -> float:
        """Retorna as horas faltantes para completar a carga horária"""
        missing = self.internship.carga_horaria - self.get_total_shift_hours()
        return max(0, missing)
    
    def _calculate_complementary_activities(self):
        """Calcula e adiciona atividades complementares automaticamente"""
        # Limpar atividades complementares existentes
        self.complementary_activities = []
        
        missing_hours = self.get_missing_hours()
        
        if missing_hours <= 0:
            # Carga horária já completa
            return
        
        # Adicionar até 20 horas de "Atividade Obrigatória"
        atividade_obrigatoria_hours = min(20, missing_hours)
        if atividade_obrigatoria_hours > 0:
            self.complementary_activities.append(
                ComplementaryActivity(
                    titulo=self.internship.titulo_atividade_obrigatoria,
                    horas=atividade_obrigatoria_hours
                )
            )
            missing_hours -= atividade_obrigatoria_hours
        
        # Se ainda faltam horas, adicionar "Preenchimento de Documentos"
        if missing_hours > 0:
            self.complementary_activities.append(
                ComplementaryActivity(
                    titulo="Preenchimento de Documentos",
                    horas=missing_hours
                )
            )
    
    def get_activity_description(self, date_str: str) -> Optional[str]:
        """Retorna a descrição da atividade para uma data específica"""
        for activity in self.activity_descriptions:
            if activity.encounter_date == date_str:
                return activity.description
        return None
    
    def add_activity_description(self, date_str: str, description: str):
        """Adiciona ou atualiza a descrição de atividade para uma data"""
        # Remover descrição existente se houver
        self.activity_descriptions = [
            act for act in self.activity_descriptions 
            if act.encounter_date != date_str
        ]
        
        # Adicionar nova descrição
        if description.strip():
            self.activity_descriptions.append(
                ActivityStorage(encounter_date=date_str, description=description.strip())
            )
