
import re

MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}

_JUNK = re.compile(
    r"(?<![А-Яа-яЁё])(?:паспорт|серия|выдан|рожд|ОГРН|КПП|БИК|"
    r"р/с|к/с|сч[её]т|VIN|индекс)",
    re.IGNORECASE,
)
_VAT = re.compile(r"НДС|включая|в том числе", re.IGNORECASE)
_DOGOVOR = re.compile(r"договор", re.IGNORECASE)


def extract_contract_number(text):
    head = text[:1500]
    for m in re.finditer(r"(?:№|Nº|No\.?|N\s)\s*([0-9A-Za-zА-Яа-яЁё][\w\-/\.]{0,24})", head):
        before = head[max(0, m.start() - 90):m.start()]
        if _JUNK.search(before): continue
        if not _DOGOVOR.search(before): continue
        value = m.group(1).strip().rstrip(".,;:")
        value = re.sub(r"от$", "", value).strip("-/. ")
        if value: return value
    return None


_GOOD_DATE = re.compile(r"договор|заключ|составлен|подписан|дата|г\.\s*$", re.IGNORECASE)
_FUTURE = re.compile(r"не позднее|до\s*$|возврат|срок|действует|истекает", re.IGNORECASE)


def extract_contract_date(text):
    head = text[:2000]
    month_re = "|".join(MONTHS.keys())
    candidates = []

    for m in re.finditer(r"[«\"']?\s*(\d{1,2})\s*[»\"']?\s+(" + month_re + r")\s+(\d{4})", head):
        candidates.append((m.start(), "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2)], int(m.group(1)))))

    for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", head):
        candidates.append((m.start(), "%s-%02d-%02d" % (m.group(3), int(m.group(2)), int(m.group(1)))))

    candidates.sort()

    for pos, value in candidates:
        before = head[max(0, pos - 120):pos]
        junk_at = max((x.start() for x in _JUNK.finditer(before)), default=-1)
        good_at = max((x.start() for x in _GOOD_DATE.finditer(before)), default=-1)
        if junk_at > good_at: continue
        if _FUTURE.search(before[-60:]): continue
        return value

    m = re.search(
        r"(?:подписан|заключ[ёе]н|составлен|дата подписания)\W{0,20}"
        r"[«\"']?\s*(\d{1,2})\s*[»\"']?[\s.]+(" + month_re + r"|\d{1,2})[\s.]+(\d{4})",
        text, re.IGNORECASE,
    )
    if m:
        month = m.group(2)
        month = MONTHS[month] if month in MONTHS else int(month)
        return "%s-%02d-%02d" % (m.group(3), month, int(m.group(1)))

    return None


_ANCHORS = re.compile(
    r"стоимост|цена|цене|сумм|плата|платы|плату|платеж|размер|"
    r"вознаграждени|составляет|равна|оценен|за[ёе]м|займа|"
    r"переда[ёе]т|арендн|уплачивает|оплачивает",
    re.IGNORECASE,
)
_NUM = re.compile(r"(\d{1,3}(?:[ \u00a0\u2009]\d{3})+(?:[.,]\d{1,2})?|\d{4,}(?:[.,]\d{1,2})?)")
_KOP = re.compile(r"руб\w*\s+(\d{1,2})\s*коп", re.IGNORECASE)


def extract_amount(text):
    best = None
    for m in _NUM.finditer(text):
        raw = m.group(1)
        before = text[max(0, m.start() - 130):m.start()]
        near = text[max(0, m.start() - 55):m.start()]
        after = text[m.end():m.end() + 40]

        if _JUNK.search(near): continue
        if not re.search(r"руб|\(", after): continue

        try:
            value = float(raw.replace("\u00a0", "").replace("\u2009", "").replace(" ", "").replace(",", "."))
        except ValueError: continue

        if value < 100: continue

        score = 0
        if _ANCHORS.search(before): score += 3
        if re.match(r"\s*\(", after): score += 2
        if re.match(r"\s*руб", after): score += 1
        if _VAT.search(near): score -= 5

        if score <= 0: continue

        if value == int(value):
            k = _KOP.search(text[m.end():m.end() + 200])
            if k: value += int(k.group(1)) / 100.0

        key = (score, value)
        if best is None or key > best[0]:
            best = (key, value)

    return best[1] if best else None


_ORG = re.compile(r"\b(ООО|АО|ЗАО|ПАО|ИП)\s*[«\"]([^»\"]{2,45})[»\"]")
_FIO = re.compile(
    r"\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+"
    r"([А-ЯЁ][а-яё]+(?:ович|евич|ьевич|ич|овна|евна|ична|инична))\b"
)


def extract_parties(text):
    head = text[:2500]
    orgs = []
    for m in _ORG.finditer(head):
        name = "%s «%s»" % (m.group(1), m.group(2).strip())
        if name not in orgs: orgs.append(name)

    if len(orgs) >= 2: return orgs[0], orgs[1]

    fios = []
    for m in _FIO.finditer(head):
        name = "%s %s %s" % (m.group(1), m.group(2), m.group(3))
        if name not in fios: fios.append(name)

    if len(orgs) == 1 and fios: return orgs[0], fios[0]
    if len(fios) >= 2: return fios[0], fios[1]
    if len(fios) == 1: return fios[0], None
    if len(orgs) == 1: return orgs[0], None
    return None, None



# Главная функция регулярки 
def extract_fields_regex(text):
    p1, p2 = extract_parties(text)
    
    # Формируем массив сторон
    parties = []
    if p1: parties.append(p1)
    if p2: parties.append(p2)

    return {
        "number": extract_contract_number(text),
        "date": extract_contract_date(text),
        "amount": extract_amount(text),
        "parties": parties,
    }


def validate_against_text(fields, text):
    """
    Анти-галлюцинация.
    """
    validated = dict(fields)

    if fields.get("number") and str(fields["number"]) not in text:
        validated["number"] = None

    return validated