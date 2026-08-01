# -*- coding: utf-8 -*-
"""
Слой 2: извлечение полей через нейронку.
"""
import json
import re
import requests

BASE_URL = "https://hedge-tipoff-sulk.ngrok-free.dev"
MODEL = "qwen2.5:7b"
TIMEOUT = 180
MAX_TEXT_CHARS = 6000
VERBOSE = True

GENERATE_URL = BASE_URL.rstrip("/") + "/api/generate"

HEADERS = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
}

ALL_FIELDS = [
    "number", "date",
    "amount", "parties"
]

FIELD_HINTS = {
    "number": 'номер договора без знака № (например "Д-572" или "274"); null, если номера нет',
    "date": 'дата заключения договора строго в формате YYYY-MM-DD; null, если нет',
    "amount": 'общая сумма договора числом (float) без пробелов и валюты. НЕ сумма НДС; null, если нет',
    "parties": 'массив строк с полными наименованиями сторон (ООО/АО «Название») или ФИО; пустой массив [], если нет',
}


def _build_prompt(text, fields):
    lines = ["  \"%s\": %s" % (f, FIELD_HINTS.get(f, "значение")) for f in fields]
    skeleton = ", ".join('"%s": ...' % f for f in fields)
    return (
        "Ты — система извлечения данных из российских договоров.\n"
        "Извлеки из текста следующие поля:\n"
        + "\n".join(lines) +
        "\n\nПравила:\n"
        "1. Ответь ТОЛЬКО JSON-объектом, без пояснений и без обрамления ```.\n"
        "2. Если значения в тексте нет — поставь null или []. Не выдумывай.\n"
        "3. Копируй значения из текста, не переформулируй.\n\n"
        "Формат ответа: {" + skeleton + "}\n\n"
        "Текст договора:\n\"\"\"\n" + text[:MAX_TEXT_CHARS] + "\n\"\"\""
    )


def _parse_json(raw):
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def extract_fields_llm(text, missing_fields=None):
    fields = list(missing_fields) if missing_fields else list(ALL_FIELDS)
    if not fields or not text or not text.strip():
        return {}

    try:
        response = requests.post(
            GENERATE_URL,
            headers=HEADERS,
            json={
                "model": MODEL,
                "prompt": _build_prompt(text, fields),
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0,
                    "num_predict": 512,
                },
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = _parse_json(response.json().get("response", ""))

        if not isinstance(data, dict):
            if VERBOSE:
                print("    [LLM] модель вернула не JSON — пропускаем")
            return {}

        out = {}
        for f in fields:
            v = data.get(f)
            if v not in (None, "", "null", "нет", "-"):
                if isinstance(v, list) and len(v) == 0:
                    continue
                out[f] = v
        return out

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        if VERBOSE: print(f"    [LLM] HTTP {code} на {GENERATE_URL}")
        return {}
    except requests.exceptions.Timeout:
        if VERBOSE: print(f"    [LLM] таймаут {TIMEOUT} сек — пропускаем документ")
        return {}
    except requests.exceptions.RequestException as e:
        if VERBOSE: print(f"    [LLM] сеть: {type(e).__name__}")
        return {}
    except Exception as e:
        if VERBOSE: print(f"    [LLM] неожиданно: {type(e).__name__}: {e}")
        return {}

extract_llm = extract_fields_llm