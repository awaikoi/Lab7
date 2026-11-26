from flask import jsonify, url_for

import models
from . import api_v1
from .errors import ApiError
from .validation import get_json_body, validate_fields

ORDER_RULES = {
    'email': {'type': str, 'required': True, 'email': True, 'max_len': 254},
    'address': {'type': str, 'required': True, 'max_len': 300},
    'promo_code': {'type': str, 'nullable': True, 'max_len': 50},
}
ITEM_RULES = {
    'product_id': {'type': int, 'required': True, 'min': 1},
    'quantity': {'type': int, 'required': True, 'min': 1, 'max': 99},
}
STATUS_RULES = {'status': {'type': str, 'required': True, 'choices': models.ORDER_STATUSES}}


def _order_payload(order_id):
    order, items = models.get_order_details(order_id)
    if order is None:
        raise ApiError('Замовлення не знайдено', 404)
    return {**dict(order), 'items': [dict(i) for i in items]}


@api_v1.route('/orders', methods=['GET'])
def list_orders():
    """Список замовлень
    ---
    tags: [Orders]
    parameters:
      - name: status
        in: query
        type: string
        enum: [Нове, В обробці, Відправлено, Доставлено, Скасовано]
    responses:
      200:
        description: Масив замовлень
        schema:
          type: array
          items: {$ref: '#/definitions/Order'}
      400: {description: Невідомий статус, schema: {$ref: '#/definitions/Error'}}
    """
    from flask import request
    status = request.args.get('status')
    if status and status not in models.ORDER_STATUSES:
        raise ApiError('Невідомий статус', 400, {'allowed': models.ORDER_STATUSES})
    rows = [dict(r) for r in models.get_orders() if not status or r['status'] == status]
    return jsonify(rows), 200


@api_v1.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Замовлення з позиціями
    ---
    tags: [Orders]
    parameters:
      - {name: order_id, in: path, type: integer, required: true}
    responses:
      200: {description: Замовлення, schema: {$ref: '#/definitions/Order'}}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    return jsonify(_order_payload(order_id)), 200


@api_v1.route('/orders', methods=['POST'])
def create_order():
    """Створити замовлення
    ---
    tags: [Orders]
    parameters:
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/OrderInput'}
    definitions:
      OrderInput:
        type: object
        required: [email, address, items]
        properties:
          email: {type: string, example: user@example.com}
          address: {type: string, example: "вул. Шевченка, 1"}
          promo_code: {type: string, example: SALE10}
          items:
            type: array
            items:
              type: object
              properties:
                product_id: {type: integer, example: 1}
                quantity: {type: integer, example: 2}
      Order:
        type: object
        properties:
          id: {type: integer}
          email: {type: string}
          address: {type: string}
          status: {type: string}
          date: {type: string}
          subtotal: {type: number}
          discount_amount: {type: number}
          total_price: {type: number}
          promo_code: {type: string}
          items: {type: array, items: {type: object}}
    responses:
      201: {description: Створено, schema: {$ref: '#/definitions/Order'}}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
    """
    body = get_json_body()
    data = validate_fields(body, ORDER_RULES)

    items = body.get('items')
    if not isinstance(items, list) or not items:
        raise ApiError('Помилка валідації', 400, {'items': 'Потрібен непорожній масив позицій'})
    cart, item_errors = {}, {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            item_errors[f'items[{index}]'] = 'Має бути об\'єктом'
            continue
        try:
            clean = validate_fields(item, ITEM_RULES)
        except ApiError as error:
            item_errors[f'items[{index}]'] = error.details
            continue
        cart[clean['product_id']] = cart.get(clean['product_id'], 0) + clean['quantity']
    if item_errors:
        raise ApiError('Помилка валідації', 400, item_errors)
    if any(qty > 99 for qty in cart.values()):
        raise ApiError('Помилка валідації', 400, {'items': 'Максимум 99 одиниць одного товару'})

    found = {p['id'] for p in models.get_products_by_ids(cart.keys())}
    missing = sorted(set(cart) - found)
    if missing:
        raise ApiError('Помилка валідації', 400, {'items': f'Товари не існують: {missing}'})

    try:
        order_id = models.create_order(
            data['email'], data['address'], cart, promo_code=data.get('promo_code')
        )
    except ValueError as error:  # недійсний промокод тощо
        raise ApiError(str(error), 400)
    return (jsonify(_order_payload(order_id)), 201,
            {'Location': url_for('api_v1.get_order', order_id=order_id)})


@api_v1.route('/orders/<int:order_id>/status', methods=['PATCH'])
def patch_order_status(order_id):
    """Змінити статус замовлення
    ---
    tags: [Orders]
    parameters:
      - {name: order_id, in: path, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [status]
          properties:
            status: {type: string, example: Відправлено}
    responses:
      200: {description: Статус оновлено, schema: {$ref: '#/definitions/Order'}}
      400: {description: Невідомий статус, schema: {$ref: '#/definitions/Error'}}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _order_payload(order_id)  # 404, якщо немає
    data = validate_fields(get_json_body(), STATUS_RULES)
    models.update_order_status(order_id, data['status'])
    return jsonify(_order_payload(order_id)), 200


@api_v1.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Видалити замовлення
    ---
    tags: [Orders]
    parameters:
      - {name: order_id, in: path, type: integer, required: true}
    responses:
      204: {description: Видалено}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _order_payload(order_id)
    models.delete_order(order_id)
    return '', 204
