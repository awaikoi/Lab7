import math
import re
from datetime import datetime

from flask import request

from .errors import ApiError

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def get_json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Тіло запиту має бути JSON-об'єктом (Content-Type: application/json)", 400)
    return data


def _type_ok(value, expected):
    if expected is bool:
        return isinstance(value, bool)
    return isinstance(value, expected) and not isinstance(value, bool)  # True не є числом


def validate_fields(data, rules, partial=False):
    """Правила поля: type, required, nullable, min, max, max_len, email, date,
    choices, allow_empty. partial=True — для PATCH (required не вимагається).
    Повертає очищені дані або кидає ApiError 400 з details по полях."""
    errors, clean = {}, {}
    for field, rule in rules.items():
        if field not in data:
            if rule.get('required') and not partial:
                errors[field] = "Обов'язкове поле"
            continue
        value = data[field]
        if value is None:
            if rule.get('nullable'):
                clean[field] = None
            else:
                errors[field] = 'Не може бути null'
            continue
        if not _type_ok(value, rule['type']):
            errors[field] = 'Неправильний тип даних'
            continue
        if isinstance(value, float) and not math.isfinite(value):
            errors[field] = 'Некоректне число'
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value and not rule.get('allow_empty'):
                errors[field] = 'Не може бути порожнім'
                continue
            if len(value) > rule.get('max_len', 10 ** 9):
                errors[field] = f"Максимум {rule['max_len']} символів"
                continue
            if rule.get('email') and not EMAIL_RE.match(value):
                errors[field] = 'Некоректний email'
                continue
            if rule.get('date'):
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    errors[field] = 'Формат дати: РРРР-ММ-ДД'
                    continue
        if 'choices' in rule and value not in rule['choices']:
            errors[field] = 'Допустимі значення: ' + ', '.join(rule['choices'])
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if 'min' in rule and value < rule['min']:
                errors[field] = f"Мінімальне значення {rule['min']}"
                continue
            if 'max' in rule and value > rule['max']:
                errors[field] = f"Максимальне значення {rule['max']}"
                continue
        clean[field] = value
    if errors:
        raise ApiError('Помилка валідації', 400, errors)
    return clean
