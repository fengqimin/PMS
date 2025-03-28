"""项目归档模块"""

from flask import Blueprint, request, jsonify
from app.models import db, Project, ProjectArchive
from auth import jwt_required

archive_bp = Blueprint('archive', __name__, url_prefix='/api/v1/archive')

@archive_bp.route('/', methods=['POST'])
@jwt_required()
def archive_project():
    """
    归档项目
    """
    data = request.get_json()
    try:
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({
                'code': 404,
                'message': 'Project not found'
            }), 404
        
        # 创建归档记录
        archive = ProjectArchive(
            project_id=project.id,
            archived_by=data['user_id'],
            reason=data.get('reason', ''),
            status='archived'
        )
        
        # 更新项目状态
        project.status = 'archived'
        
        db.session.add(archive)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': {
                'project': project.to_dict(),
                'archive': archive.to_dict()
            },
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400

@archive_bp.route('/', methods=['GET'])
@jwt_required()
def get_archived_projects():
    """
    获取已归档项目列表
    """
    archives = ProjectArchive.query.all()
    return jsonify({
        'code': 200,
        'data': [archive.to_dict() for archive in archives],
        'message': 'success'
    })