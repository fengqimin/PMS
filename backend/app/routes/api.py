from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db

bp = Blueprint('api', __name__, url_prefix='/api/v1/api')

@bp.route('/call', methods=['POST'])
@jwt_required()
def call_module():
    """
    调用模块接口
    """
    data = request.get_json()
    try:
        # 这里实现模块调用逻辑
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {}
        })
    except Exception as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400