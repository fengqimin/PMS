from flask import Blueprint, request, jsonify
from app import db
from app.models import ProjectPerformance
from auth import jwt_required

performance_bp = Blueprint('performance', __name__, url_prefix='/api/v1/performance')

@performance_bp.route('/', methods=['POST'])
@jwt_required()
def create_performance():
    """
    创建项目绩效记录
    """
    data = request.get_json()
    try:
        performance = ProjectPerformance(
            project_id=data['project_id'],
            kpi=data['kpi'],
            budget=data['budget'],
            actual_cost=data.get('actual_cost'),
            completion_rate=data.get('completion_rate', 0),
            remark=data.get('remark', '')
        )
        db.session.add(performance)
        db.session.commit()
        return jsonify({
            'code': 200,
            'data': performance.to_dict(),
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400

@performance_bp.route('/', methods=['GET'])
@jwt_required()
def get_performances():
    """
    获取绩效记录列表
    """
    performances = ProjectPerformance.query.all()
    return jsonify({
        'code': 200,
        'data': [performance.to_dict() for performance in performances],
        'message': 'success'
    })