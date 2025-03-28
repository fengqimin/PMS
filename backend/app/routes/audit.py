from flask import Blueprint, request, jsonify
from app.models import db, AuditLog
from auth import jwt_required, admin_required
from datetime import datetime

bp = Blueprint('audit', __name__, url_prefix='/api/v1/audit')

@bp.route('/', methods=['GET'])
@admin_required()
def get_audit_logs():
    """
    获取审计日志列表(仅管理员)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "code": 200, 
        "message": "success", 
        "data": {
            "items": [log.to_dict() for log in logs.items],
            "total": logs.total,
            "pages": logs.pages,
            "current_page": page
        }
    })

@bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_audit_logs(user_id):
    """
    获取指定用户的审计日志(仅自己或管理员)
    """
    if request.user_id != user_id and not request.is_admin:
        return jsonify({"code": 403, "message": "无权访问"}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    logs = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "code": 200, 
        "message": "success", 
        "data": {
            "items": [log.to_dict() for log in logs.items],
            "total": logs.total,
            "pages": logs.pages,
            "current_page": page
        }
    })

@bp.route('/', methods=['POST'])
@jwt_required()
def create_audit_log():
    """
    创建审计日志记录
    """
    data = request.get_json()
    try:
        log = AuditLog(
            user_id=request.user_id,
            action_type=data['action_type'],
            details=data.get('details', ''),
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': log.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400