"""
Utilitários para manipulação de datas e feriados brasileiros.
"""
import holidays
from datetime import date, timedelta
from typing import List, Dict
import json
import os


# Caminho para arquivo de feriados personalizados
CUSTOM_HOLIDAYS_FILE = "./custom_holidays.json"


def load_custom_holidays() -> Dict[str, str]:
    """Carrega feriados personalizados do arquivo"""
    if os.path.exists(CUSTOM_HOLIDAYS_FILE):
        try:
            with open(CUSTOM_HOLIDAYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_custom_holidays(holidays_dict: Dict[str, str]):
    """Salva feriados personalizados no arquivo"""
    with open(CUSTOM_HOLIDAYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(holidays_dict, f, ensure_ascii=False, indent=2)


def add_custom_holiday(date_obj: date, name: str):
    """Adiciona um feriado personalizado"""
    holidays_dict = load_custom_holidays()
    holidays_dict[date_obj.isoformat()] = name
    save_custom_holidays(holidays_dict)


def remove_custom_holiday(date_obj: date):
    """Remove um feriado personalizado"""
    holidays_dict = load_custom_holidays()
    date_str = date_obj.isoformat()
    if date_str in holidays_dict:
        del holidays_dict[date_str]
        save_custom_holidays(holidays_dict)


def clear_custom_holidays():
    """Limpa todos os feriados personalizados"""
    save_custom_holidays({})


def get_custom_holidays() -> Dict[date, str]:
    """Retorna todos os feriados personalizados"""
    holidays_dict = load_custom_holidays()
    return {date.fromisoformat(k): v for k, v in holidays_dict.items()}


def get_brazilian_holidays(year: int) -> holidays.HolidayBase:
    """Retorna os feriados brasileiros para um ano específico"""
    return holidays.Brazil(years=year)


def is_brazilian_holiday(date_obj: date) -> bool:
    """Verifica se uma data é feriado brasileiro (oficial ou personalizado)"""
    # Verificar feriados personalizados
    custom_holidays = get_custom_holidays()
    if date_obj in custom_holidays:
        return True
    
    # Verificar feriados oficiais
    br_holidays = get_brazilian_holidays(date_obj.year)
    return date_obj in br_holidays


def get_holiday_name(date_obj: date) -> str:
    """Retorna o nome do feriado se a data for feriado"""
    # Verificar feriados personalizados primeiro
    custom_holidays = get_custom_holidays()
    if date_obj in custom_holidays:
        return f"{custom_holidays[date_obj]} (Personalizado)"
    
    # Verificar feriados oficiais
    br_holidays = get_brazilian_holidays(date_obj.year)
    return br_holidays.get(date_obj, "")


def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """Gera uma lista de datas entre start_date e end_date (inclusivo)"""
    if start_date > end_date:
        raise ValueError("Data inicial deve ser anterior à data final")
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def get_weekday_name(date_obj: date) -> str:
    """Retorna o nome do dia da semana em português"""
    weekdays = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    return weekdays[date_obj.weekday()]
