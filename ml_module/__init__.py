"""
Модуль извлечения ключевых полей из договоров.

Схема работы:
    файл -> текст -> регулярки -> LLM только для пустых полей -> словарь
"""

import json
import logging
import requests

from .text_extractor import extract_text
from .field_extractor import extract_fields_regex, validate_against_text
from .llm_extractor import extract_fields_llm

log = logging.getLogger(__name__)

# Строгая схема выходного JSON
FIELDS = (
    "number",
    "date",
    "amount",
    "parties",
)

# Слова-пустышки: LLM часто пишет их вместо null.
_EMPTY_WORDS = {
    "", "-", "\u2014", "\u2013", "null", "none", "nan", "n/a", "нет", "неизвестно",
    "не указан", "не указана", "не указано", "не указаны",
    "отсутствует", "отсутствуют", "не найдено", "нет данных",
}


def is_empty(value) -> bool:
    """Пусто ли значение."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _EMPTY_WORDS
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) == 0
    return False


def extract_fields(file_path: str) -> dict:
    """
    Главная функция модуля.
    """
    fields, _sources = extract_fields_with_sources(file_path)
    return fields


def extract_fields_with_sources(file_path: str):
    """Возвращает значения и источники (rule, llm, mixed, none)."""
    text = extract_text(file_path)
    raw = extract_fields_regex(text)

    fields = {}
    sources = {}
    
    # Инициализация базовыми ответами от регулярок
    for key in FIELDS:
        value = raw.get(key)
        if is_empty(value):
            fields[key] = [] if key == "parties" else None
            sources[key] = "none"
        else:
            fields[key] = value
            sources[key] = "rule"

    # Ищем, что нужно добрать через LLM
    missing = []
    for k in FIELDS:
        if is_empty(fields[k]):
            missing.append(k)
        elif k == "parties" and len(fields[k]) < 2:
            missing.append(k)

    if not missing:
        return fields, sources

    try:
        llm_fields = extract_fields_llm(text, missing_fields=missing)
        llm_fields = validate_against_text(llm_fields, text)

        if not isinstance(llm_fields, dict):
            raise TypeError("ожидался dict, пришло %s" % type(llm_fields).__name__)

        # Дополняем ответы LLM
        for key, value in llm_fields.items():
            if key not in FIELDS or is_empty(value):
                continue
            
            if key == "parties":
                if not isinstance(value, list):
                    continue
                # Добавляем уникальные значения
                added_new = False
                for item in value:
                    if item not in fields[key]:
                        fields[key].append(item)
                        added_new = True
                
                if added_new:
                    sources[key] = "mixed" if sources[key] == "rule" else "llm"
            else:
                if fields[key] is None:
                    fields[key] = value
                    sources[key] = "llm"

    except requests.RequestException as exc:
        log.warning("LLM недоступна (%s), работаем только на регулярках: %s",
                    type(exc).__name__, exc)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        log.warning("Ответ LLM не разобран (%s): %s", type(exc).__name__, exc)

    return fields, sources