import sqlite3

from flask import jsonify

import models
from . import api_v1
from .errors import ApiError
from .helpers import number_arg
from .validation import get_json_body, validate_fields

PROMO_RULES = {
    'code': {'type': str, 'required': True, 'max_len': 50},
    'discount_percent': {'type': (int, float), 'min': 0, 'max': 100},
    'discount_amount': {'type': (int, float), 'min': 0},
    'min_order': {'type': (int, float), 'min': 0},
    'active': {'type': bool},
    'expires_at': {'type': str, 'nullable': True, 'date': True},
}


def _promo_to_dict(row):
    data = dict(row)
    data['active'] = bool(data['active'])
    return data


@api_v1.route('/promocodes', methods=['GET'])
def list_promocodes():
    """Список промокодів
    ---
    tags: [Promocodes]
    responses:
      200:
        description: Масив промокодів
        schema:
          type: array
          items: {$ref: '#/definitions/Promocode'}
    """
    return jsonify([_promo_to_dict(r) for r in models.get_promocodes()]), 200


@api_v1.route('/promocodes', methods=['POST'])
def create_promocode():
    """Створити промокод
    ---
    tags: [Promocodes]
    parameters:
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/PromocodeInput'}
    definitions:
      PromocodeInput:
        type: object
        required: [code]
        properties:
          code: {type: string, example: SALE10}
          discount_percent: {type: number, example: 10}
          discount_amount: {type: number, example: 0}
          min_order: {type: number, example: 500}
          active: {type: boolean, example: true}
          expires_at: {type: string, example: "2026-12-31"}
      Promocode:
        type: object
        properties:
          id: {type: integer}
          code: {type: string}
          discount_percent: {type: number}
          discount_amount: {type: number}
          min_order: {type: number}
          active: {type: boolean}
          expires_at: {type: string}
    responses:
      201: {description: Створено, schema: {$ref: '#/definitions/Promocode'}}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
      409: {description: Такий код уже існує, schema: {$ref: '#/definitions/Error'}}
    """
    data = validate_fields(get_json_body(), PROMO_RULES)
    if not data.get('discount_percent') and not data.get('discount_amount'):
        raise ApiError('Помилка валідації', 400,
                       {'discount_percent': 'Вкажіть discount_percent або discount_amount більше 0'})
    try:
        models.add_promocode(
            data['code'],
            discount_percent=data.get('discount_percent', 0),
            discount_amount=data.get('discount_amount', 0),
            min_order=data.get('min_order', 0),
            active=data.get('active', True),
            expires_at=data.get('expires_at'),
        )
    except sqlite3.IntegrityError:
        raise ApiError('Промокод з таким кодом уже існує', 409)
    except ValueError as error:
        raise ApiError(str(error), 400)
    return jsonify(_promo_to_dict(models.get_promocode(data['code']))), 201


@api_v1.route('/promocodes/<string:code>/validate', methods=['GET'])
def check_promocode(code):
    """Перевірити промокод для суми кошика
    ---
    tags: [Promocodes]
    parameters:
      - {name: code, in: path, type: string, required: true}
      - {name: subtotal, in: query, type: number, required: true, description: Сума кошика}
    responses:
      200:
        description: "valid=true зі знижкою або valid=false з причиною (неактивний, прострочений, мала сума)"
      400: {description: Не передано subtotal, schema: {$ref: '#/definitions/Error'}}
      404: {description: Промокоду не існує, schema: {$ref: '#/definitions/Error'}}
    """
    subtotal = number_arg('subtotal')
    if subtotal is None or subtotal < 0:
        raise ApiError('Передайте параметр subtotal (число ≥ 0)', 400)
    if models.get_promocode(code) is None:
        raise ApiError('Промокод не знайдено', 404)
    promo, reason = models.validate_promocode(code, subtotal)
    if promo is None:
        return jsonify({'valid': False, 'reason': reason}), 200
    discount = models.calculate_promocode_discount(promo, subtotal)
    return jsonify({'valid': True, 'code': promo['code'], 'discount': discount,
                    'total': round(subtotal - discount, 2)}), 200


@api_v1.route('/promocodes/<int:promo_id>', methods=['DELETE'])
def delete_promocode(promo_id):
    """Видалити промокод
    ---
    tags: [Promocodes]
    parameters:
      - {name: promo_id, in: path, type: integer, required: true}
    responses:
      204: {description: Видалено}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    row = models.get_db().execute('SELECT id FROM promocodes WHERE id = ?', (promo_id,)).fetchone()
    if row is None:
        raise ApiError('Промокод не знайдено', 404)
    models.delete_promocode(promo_id)
    return '', 204
