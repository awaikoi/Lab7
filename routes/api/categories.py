from flask import jsonify, url_for

import models
from . import api_v1
from .errors import ApiError
from .validation import get_json_body, validate_fields

CATEGORY_RULES = {
    'name': {'type': str, 'required': True, 'max_len': 100},
    'parent_id': {'type': int, 'nullable': True, 'min': 1},
}


def _get_or_404(category_id):
    row = models.get_category(category_id)
    if row is None:
        raise ApiError('Категорію не знайдено', 404)
    return row


def _check_parent(parent_id):
    if parent_id is not None and models.get_category(parent_id) is None:
        raise ApiError('Помилка валідації', 400, {'parent_id': 'Батьківську категорію не знайдено'})


@api_v1.route('/categories', methods=['GET'])
def list_categories():
    """Список категорій
    ---
    tags: [Categories]
    responses:
      200:
        description: Масив категорій (з parent_name)
        schema:
          type: array
          items: {$ref: '#/definitions/Category'}
    """
    return jsonify([dict(r) for r in models.get_categories()]), 200


@api_v1.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Категорія за ID
    ---
    tags: [Categories]
    parameters:
      - {name: category_id, in: path, type: integer, required: true}
    responses:
      200: {description: Категорія, schema: {$ref: '#/definitions/Category'}}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    return jsonify(dict(_get_or_404(category_id))), 200


@api_v1.route('/categories', methods=['POST'])
def create_category():
    """Створити категорію
    ---
    tags: [Categories]
    parameters:
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/CategoryInput'}
    definitions:
      CategoryInput:
        type: object
        required: [name]
        properties:
          name: {type: string, example: Смартфони}
          parent_id: {type: integer}
      Category:
        type: object
        properties:
          id: {type: integer}
          name: {type: string}
          parent_id: {type: integer}
          parent_name: {type: string}
    responses:
      201: {description: Створено, schema: {$ref: '#/definitions/Category'}}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
    """
    data = validate_fields(get_json_body(), CATEGORY_RULES)
    _check_parent(data.get('parent_id'))
    try:
        new_id = models.add_category(data['name'], data.get('parent_id'))
    except ValueError as error:
        raise ApiError(str(error), 400)
    return (jsonify(dict(models.get_category(new_id))), 201,
            {'Location': url_for('api_v1.get_category', category_id=new_id)})


@api_v1.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Оновити категорію
    ---
    tags: [Categories]
    parameters:
      - {name: category_id, in: path, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/CategoryInput'}
    responses:
      200: {description: Оновлено, schema: {$ref: '#/definitions/Category'}}
      400: {description: "Помилка валідації або циклічне вкладення", schema: {$ref: '#/definitions/Error'}}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _get_or_404(category_id)
    data = validate_fields(get_json_body(), CATEGORY_RULES)
    _check_parent(data.get('parent_id'))
    try:
        models.update_category(category_id, data['name'], data.get('parent_id'))
    except ValueError as error:  # сама собі батько / цикл
        raise ApiError(str(error), 400)
    return jsonify(dict(models.get_category(category_id))), 200


@api_v1.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Видалити категорію (товари й підкатегорії залишаються без категорії)
    ---
    tags: [Categories]
    parameters:
      - {name: category_id, in: path, type: integer, required: true}
    responses:
      204: {description: Видалено}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _get_or_404(category_id)
    models.delete_category(category_id)
    return '', 204
