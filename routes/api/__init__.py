from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Імпорти в кінці, щоб уникнути циклічних імпортів
from . import products, categories, promocodes, orders, feedback, v2  # noqa: E402,F401
