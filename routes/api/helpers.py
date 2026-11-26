from flask import request

import models
from .errors import ApiError

SORTS = {'id', 'name', 'name_desc', 'price', 'price_desc', 'new'}


def product_to_dict(row):
    """Товар → dict для JSON. BLOB із зображенням у JSON не віддаємо."""
    data = dict(row)
    has_blob = bool(data.pop('image_data', None))
    data.pop('image_mimetype', None)
    data['final_price'] = models.effective_product_price(row)
    data['image_url'] = f"/products/{data['id']}/image" if has_blob else (data.get('image') or None)
    return data


def number_arg(name, cast=float):
    """Числовий query-параметр; None, якщо не передано."""
    raw = request.args.get(name, '').strip()
    if not raw:
        return None
    try:
        return cast(raw)
    except ValueError:
        raise ApiError(f'Параметр «{name}» має бути числом', 400)


def product_filters_from_request():
    sort = request.args.get('sort', 'id')
    if sort not in SORTS:
        raise ApiError('Невідоме значення sort', 400, {'allowed': sorted(SORTS)})
    return {
        'search': request.args.get('q', '').strip(),
        'category_id': number_arg('category_id', int),
        'min_price': number_arg('min_price'),
        'max_price': number_arg('max_price'),
        'on_sale': request.args.get('on_sale', '').lower() in ('1', 'true'),
        'sort': sort,
    }


MAX_IMAGE_SIZE = 5 * 1024 * 1024


def read_uploaded_image(uploaded):

    if uploaded is None or not uploaded.filename:
        raise ApiError(
            'Файл зображення не передано',
            400
        )

    data = uploaded.read(MAX_IMAGE_SIZE + 1)

    if len(data) > MAX_IMAGE_SIZE:
        raise ApiError(
            'Зображення має бути не більше 5 МБ',
            413
        )

    if data.startswith(b'\xff\xd8\xff'):
        mimetype = 'image/jpeg'

    elif data.startswith(b'\x89PNG\r\n\x1a\n'):
        mimetype = 'image/png'

    elif data.startswith((b'GIF87a', b'GIF89a')):
        mimetype = 'image/gif'

    elif (
        len(data) >= 12
        and data[:4] == b'RIFF'
        and data[8:12] == b'WEBP'
    ):
        mimetype = 'image/webp'

    else:
        raise ApiError(
            'Дозволені лише JPG, PNG, GIF або WEBP',
            400
        )

    return data, mimetype