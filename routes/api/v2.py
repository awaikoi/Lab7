from flask import jsonify

import models
from . import api_v2
from .errors import ApiError
from .helpers import number_arg, product_filters_from_request, product_to_dict


@api_v2.route('/health', methods=['GET'])
def health_v2():
    """Перевірка роботи API
    ---
    tags: [v2]
    responses:
      200:
        description: API працює
    """
    return jsonify({'status': 'ok', 'version': 2}), 200


@api_v2.route('/products', methods=['GET'])
def list_products_v2():
    """Список товарів з пагінацією (формат відрізняється від v1)
    ---
    tags: [v2]
    parameters:
      - {name: page, in: query, type: integer, default: 1}
      - {name: per_page, in: query, type: integer, default: 10}
      - {name: q, in: query, type: string}
      - {name: category_id, in: query, type: integer}
      - {name: min_price, in: query, type: number}
      - {name: max_price, in: query, type: number}
      - {name: on_sale, in: query, type: boolean}
      - {name: sort, in: query, type: string}
    responses:
      200:
        description: "Обгортка {data: [...], meta: {page, per_page, total, pages}}"
      400:
        description: Некоректний параметр
        schema: {$ref: '#/definitions/Error'}
    """
    page = number_arg('page', int) or 1
    per_page = number_arg('per_page', int) or 10
    if page < 1 or not 1 <= per_page <= 100:
        raise ApiError('page має бути ≥ 1, per_page — від 1 до 100', 400)
    rows = models.get_products(**product_filters_from_request())
    total = len(rows)
    start = (page - 1) * per_page
    return jsonify({
        'data': [product_to_dict(r) for r in rows[start:start + per_page]],
        'meta': {'page': page, 'per_page': per_page, 'total': total,
                 'pages': -(-total // per_page)},
    }), 200


@api_v2.route('/categories', methods=['GET'])
def list_categories_v2():
    """Дерево категорій (з полем level)
    ---
    tags: [v2]
    responses:
      200:
        description: "{data: [...]}, відсортовано як дерево"
    """
    return jsonify({'data': models.get_category_tree()}), 200
