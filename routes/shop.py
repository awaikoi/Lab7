from io import BytesIO

from flask import (
    Blueprint,
    abort,
    render_template,
    send_file,
)

import models

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/shop')
def shop():
    return render_template('shop.html')


@shop_bp.route('/cart')
def cart():
    return render_template('cart.html')


@shop_bp.route('/products/<int:product_id>/image')
def product_image(product_id):
    product = models.get_product(product_id)

    if product is None or not product['image_data']:
        abort(404)

    return send_file(
        BytesIO(product['image_data']),
        mimetype=product['image_mimetype'],
        max_age=3600,
    )