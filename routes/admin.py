import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import models

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')



# ------------------------------------------------- замовлення та відгуки

@admin_bp.route('/')
def admin():
    return render_template('admin.html')


@admin_bp.route('/order/<int:order_id>')
def order_details(order_id):
    if models.get_order_details(order_id)[0] is None:
        abort(404)

    return render_template(
        'order_details.html',
        order_id=order_id,
    )


@admin_bp.route('/categories')
def categories():
    return render_template('admin_categories.html')


@admin_bp.route('/promocodes')
def promocodes():
    return render_template('admin_promocodes.html')


# ------------------------------------------------------------- товари


@admin_bp.route('/products')
def products():
    return render_template('admin_products.html')


@admin_bp.route('/products/new')
def new_product():
    return render_template(
        'product_form.html',
        is_new=True,
        product_id=None,
    )


@admin_bp.route('/products/<int:product_id>/edit')
def edit_product(product_id):
    if models.get_product(product_id) is None:
        abort(404)

    return render_template(
        'product_form.html',
        is_new=False,
        product_id=product_id,
    )
