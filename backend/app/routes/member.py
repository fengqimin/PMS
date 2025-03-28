from flask import request, jsonify
from app import db
from app.models import Project, User, ProjectMember
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def add_member(project_id):
    """添加项目成员"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(data['user_id'])
    
    # 检查是否已经是成员
    if ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first():
        return jsonify({'message': '用户已是项目成员'}), 400
    
    member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role=data.get('role', 'member'),
        added_by=current_user_id
    )
    db.session.add(member)
    db.session.commit()
    
    return jsonify(member.to_dict()), 201

@jwt_required()
def remove_member(project_id, user_id):
    """移除项目成员"""
    current_user_id = get_jwt_identity()
    
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'message': '成员已移除'}), 200

@jwt_required()
def update_member_role(project_id, user_id):
    """更新成员角色"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    member.role = data['role']
    db.session.commit()
    
    return jsonify(member.to_dict()), 200

@jwt_required()
def get_project_members(project_id):
    """获取项目成员列表"""
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify([member.to_dict() for member in members]), 200