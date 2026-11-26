from flask import jsonify

import models
from . import api_v1
from .errors import ApiError
from .validation import get_json_body, validate_fields

FEEDBACK_RULES = {
    'name': {'type': str, 'required': True, 'max_len': 100},
    'email': {'type': str, 'required': True, 'email': True, 'max_len': 254},
    'message': {'type': str, 'required': True, 'max_len': 2000},
}


def _get_or_404(feedback_id):
    row = models.get_db().execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,)).fetchone()
    if row is None:
        raise ApiError('Відгук не знайдено', 404)
    return row


@api_v1.route('/feedback', methods=['GET'])
def list_feedback():
    """Список відгуків
    ---
    tags: [Feedback]
    responses:
      200:
        description: Масив відгуків
        schema:
          type: array
          items: {$ref: '#/definitions/Feedback'}
    """
    return jsonify([dict(r) for r in models.get_feedback()]), 200


@api_v1.route('/feedback', methods=['POST'])
def create_feedback():
    """Залишити відгук
    ---
    tags: [Feedback]
    parameters:
      - in: body
        name: body
        required: true
        schema: {$ref: '#/definitions/FeedbackInput'}
    definitions:
      FeedbackInput:
        type: object
        required: [name, email, message]
        properties:
          name: {type: string, example: Олена}
          email: {type: string, example: olena@example.com}
          message: {type: string, example: Дуже зручний магазин}
      Feedback:
        type: object
        properties:
          id: {type: integer}
          name: {type: string}
          email: {type: string}
          message: {type: string}
          created_at: {type: string}
    responses:
      201: {description: Створено, schema: {$ref: '#/definitions/Feedback'}}
      400: {description: Помилка валідації, schema: {$ref: '#/definitions/Error'}}
    """
    data = validate_fields(get_json_body(), FEEDBACK_RULES)
    new_id = models.add_feedback(data['name'], data['email'], data['message'])
    return jsonify(dict(_get_or_404(new_id))), 201


@api_v1.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """Видалити відгук
    ---
    tags: [Feedback]
    parameters:
      - {name: feedback_id, in: path, type: integer, required: true}
    responses:
      204: {description: Видалено}
      404: {description: Не знайдено, schema: {$ref: '#/definitions/Error'}}
    """
    _get_or_404(feedback_id)
    models.delete_feedback(feedback_id)
    return '', 204
