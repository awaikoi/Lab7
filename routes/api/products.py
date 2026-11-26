import sqlite3

from flask import jsonify, url_for

import models
from . import api_v1
from .errors import ApiError
from .helpers import product_filters_from_request, product_to_dict
from .validation import get_json_body, validate_fields

from flask import request
from .helpers import read_uploaded_image

PRODUCT_RULES = {
    'name': {'type': str, 'required': True, 'max_len': 100},
    'price': {'type': (int, float), 'required': True, 'min': 0},
    'image': {'type': str, 'max_len': 500, 'allow_empty': True},
    'discount_percent': {'type': (int, float), 'min': 0, 'max': 100},
    'category_id': {'type': int, 'nullable': True, 'min': 1},
}


def _get_or_404(product_id):
    row = models.get_product(product_id)
    if row is None:
        raise ApiError('Товар не знайдено', 404)
    return row


def _check_category(category_id):
    if category_id is not None and models.get_category(category_id) is None:
        raise ApiError('Помилка валідації', 400, {'category_id': 'Категорію не знайдено'})


def _save(product_id, v):
    models.update_product(
        product_id, v['name'], round(v['price'], 2), image=v['image'],
        discount_percent=v['discount_percent'], category_id=v['category_id'],
    )


@api_v1.route('/products', methods=['GET'])
def list_products():
    """Список товарів
    ---
    tags: [Products]
    parameters:
      - {name: q, in: query, type: string, description: Пошук за назвою}
      - {name: category_id, in: query, type: integer}
      - {name: min_price, in: query, type: number}
      - {name: max_price, in: query, type: number}
      - {name: on_sale, in: query, type: boolean}
      - {name: sort, in: query, type: string, enum: [id, name, name_desc, price, price_desc, new]}
    responses:
      200:
        description: Масив товарів
        schema:
          type: array
          items: {$ref: '#/definitions/Product'}
      400:
        description: Некоректний параметр
        schema: {$ref: '#/definitions/Error'}
    """
    rows = models.get_products(**product_filters_from_request())
    return jsonify([product_to_dict(r) for r in rows]), 200


@api_v1.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Отримати товар за ID
    ---
    tags: [Products]
    parameters:
      - {name: product_id, in: path, type: integer, required: true}
    responses:
      200:
        description: Дані товару
        schema: {$ref: '#/definitions/Product'}
      404:
        description: Товар не знайдено
        schema: {$ref: '#/definitions/Error'}
    """
    return jsonify(product_to_dict(_get_or_404(product_id))), 200


@api_v1.route('/products', methods=['POST'])
def create_product():
    """Створити товар
    ---
    tags: [Products]
    parameters:
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/ProductInput'}
    definitions:
      ProductInput:
        type: object
        required: [name, price]
        properties:
          name: {type: string, example: Смартфон XYZ}
          price: {type: number, example: 15999}
          image: {type: string}
          discount_percent: {type: number, example: 10}
          category_id: {type: integer}
      Product:
        type: object
        properties:
          id: {type: integer}
          name: {type: string}
          price: {type: number}
          discount_percent: {type: number}
          final_price: {type: number}
          category_id: {type: integer}
          category_name: {type: string}
          image_url: {type: string}
    responses:
      201:
        description: Товар створено
        schema: {$ref: '#/definitions/Product'}
      400:
        description: Помилка валідації
        schema: {$ref: '#/definitions/Error'}
    """
    data = validate_fields(get_json_body(), PRODUCT_RULES)
    _check_category(data.get('category_id'))
    new_id = models.add_product(
        data['name'], round(data['price'], 2), image=data.get('image', ''),
        discount_percent=data.get('discount_percent', 0), category_id=data.get('category_id'),
    )
    return (jsonify(product_to_dict(models.get_product(new_id))), 201,
            {'Location': url_for('api_v1.get_product', product_id=new_id)})


@api_v1.route('/products/<int:product_id>', methods=['PUT'])
def replace_product(product_id):
    """Повністю оновити товар
    ---
    tags: [Products]
    parameters:
      - {name: product_id, in: path, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/ProductInput'}
    responses:
      200:
        description: Товар оновлено
        schema: {$ref: '#/definitions/Product'}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
      404: {description: Товар не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _get_or_404(product_id)
    data = validate_fields(get_json_body(), PRODUCT_RULES)
    _check_category(data.get('category_id'))
    _save(product_id, {
        'name': data['name'], 'price': data['price'], 'image': data.get('image', ''),
        'discount_percent': data.get('discount_percent', 0), 'category_id': data.get('category_id'),
    })
    return jsonify(product_to_dict(models.get_product(product_id))), 200


@api_v1.route('/products/<int:product_id>', methods=['PATCH'])
def patch_product(product_id):
    """Частково оновити товар (лише передані поля)
    ---
    tags: [Products]
    parameters:
      - {name: product_id, in: path, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema:
          type: object
          example: {price: 14999, discount_percent: 15}
    responses:
      200:
        description: Товар оновлено
        schema: {$ref: '#/definitions/Product'}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
      404: {description: Товар не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    row = _get_or_404(product_id)
    data = validate_fields(get_json_body(), PRODUCT_RULES, partial=True)
    if not data:
        raise ApiError('Передайте хоча б одне поле для оновлення', 400)
    _check_category(data.get('category_id'))
    current = {
        'name': row['name'], 'price': row['price'], 'image': row['image'] or '',
        'discount_percent': row['discount_percent'], 'category_id': row['category_id'],
    }
    _save(product_id, {**current, **data})
    return jsonify(product_to_dict(models.get_product(product_id))), 200


@api_v1.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Видалити товар
    ---
    tags: [Products]
    parameters:
      - {name: product_id, in: path, type: integer, required: true}
    responses:
      204: {description: Видалено}
      404: {description: Товар не знайдено, schema: {$ref: '#/definitions/Error'}}
      409: {description: Товар є в замовленнях, schema: {$ref: '#/definitions/Error'}}
    """
    _get_or_404(product_id)
    try:
        models.delete_product(product_id)
    except sqlite3.IntegrityError:
        raise ApiError('Не можна видалити товар, який є в замовленнях', 409)
    return '', 204

@api_v1.route(
    '/products/<int:product_id>/image',
    methods=['POST']
)
def upload_product_image(product_id):
    """Завантажити зображення товару
    ---
    tags: [Products]
    consumes:
      - multipart/form-data
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: image_file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Зображення завантажено
      400:
        description: Неправильний формат
      404:
        description: Товар не знайдено
      413:
        description: Файл завеликий
    """

    product = _get_or_404(product_id)

    uploaded = request.files.get('image_file')

    image_data, image_mimetype = read_uploaded_image(
        uploaded
    )

    models.update_product(
        product_id,
        product['name'],
        product['price'],
        image=product['image'] or '',
        image_data=image_data,
        image_mimetype=image_mimetype,
        discount_percent=product['discount_percent'],
        category_id=product['category_id'],
    )

    return jsonify(
        product_to_dict(models.get_product(product_id))
    ), 200