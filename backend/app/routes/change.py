from flask import Blueprint, request, jsonify
from app.models import db, ChangeRecord
from auth import jwt_required

bp = Blueprint('change', __name__, url_prefix='/api/v1/change')

@bp.route('/project/<int:project_id>', methods=['POST'])
@jwt_required()
def create_project_change(project_id):
    """
    创建项目变更记录
    """
    data = request.get_json()
    change = ChangeRecord(
        project_id=project_id,
        change_type=data['change_type'],
        description=data['description'],
        before_data=data.get('before_data'),
        after_data=data.get('after_data'),
        created_by=request.user_id
    )
    db.session.add(change)
    db.session.commit()
    return jsonify({"code": 200, "message": "success", "data": change.to_dict()})

@bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_changes(project_id):
    """
    获取项目变更记录列表
    """
    changes = ChangeRecord.query.filter_by(project_id=project_id).order_by(ChangeRecord.created_at.desc()).all()
    return jsonify({"code": 200, "message": "success", "data": [c.to_dict() for c in changes]})