import os
from datetime import datetime

from flask import Flask, render_template

import models

from routes import admin_bp, feedback_bp, shop_bp, api_v1, api_v2
from routes.api.errors import register_error_handlers

from flasgger import Swagger

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE', os.path.join(app.root_path, 'db.sqlite'))
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-me')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 + 256 * 1024
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)
register_error_handlers(app)

swagger = Swagger(app, template={
    'info': {'title': 'Shop API', 'description': 'REST API інтернет-магазину', 'version': '2.0'},
    'definitions': {
        'Error': {
            'type': 'object',
            'properties': {'error': {'type': 'object', 'properties': {
                'code': {'type': 'integer', 'example': 404},
                'message': {'type': 'string', 'example': 'Товар не знайдено'},
                'details': {'type': 'object'},
            }}},
        },
    },
})

app.teardown_appcontext(models.close_db)

with app.app_context():
    models.init_db()

app.register_blueprint(feedback_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(shop_bp)


@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
    }


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api-demo')
def api_demo():
    return render_template('api-demo.html')


if __name__ == '__main__':
    app.run(debug=True)

