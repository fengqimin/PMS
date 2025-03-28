"""项目里程碑管理功能
    实现项目里程碑的创建、查询、更新和删除API
"""
from flask import request, jsonify
from app import db
from app.models import ProjectMilestone
from auth import jwt_required as token_required

def milestone_routes(app):
    @app.route('/api/projects/<int:project_id>/milestones', methods=['POST'])
    @token_required
    def create_milestone(current_user, project_id):
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Milestone name is required'}), 400
            
        milestone = ProjectMilestone(
            project_id=project_id,
            name=data['name'],
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            status=data.get('status', 'pending'),
            created_by=current_user.id
        )
        db.session.add(milestone)
        db.session.commit()
        
        return jsonify(milestone.to_dict()), 201
    
    @app.route('/api/projects/<int:project_id>/milestones', methods=['GET'])
    @token_required
    def get_project_milestones(current_user, project_id):
        milestones = ProjectMilestone.query.filter_by(project_id=project_id).all()
        return jsonify([milestone.to_dict() for milestone in milestones])
    
    @app.route('/api/projects/<int:project_id>/milestones/<int:milestone_id>', methods=['GET'])
    @token_required
    def get_milestone(current_user, project_id, milestone_id):
        milestone = ProjectMilestone.query.filter_by(id=milestone_id, project_id=project_id).first()
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        return jsonify(milestone.to_dict())
    
    @app.route('/api/projects/<int:project_id>/milestones/<int:milestone_id>', methods=['PUT'])
    @token_required
    def update_milestone(current_user, project_id, milestone_id):
        milestone = ProjectMilestone.query.filter_by(id=milestone_id, project_id=project_id).first()
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
            
        data = request.get_json()
        if 'name' in data:
            milestone.name = data['name']
        if 'description' in data:
            milestone.description = data['description']
        if 'due_date' in data:
            milestone.due_date = data['due_date']
        if 'status' in data:
            milestone.status = data['status']
            
        db.session.commit()
        return jsonify(milestone.to_dict())
    
    @app.route('/api/projects/<int:project_id>/milestones/<int:milestone_id>', methods=['DELETE'])
    @token_required
    def delete_milestone(current_user, project_id, milestone_id):
        milestone = ProjectMilestone.query.filter_by(id=milestone_id, project_id=project_id).first()
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
            
        db.session.delete(milestone)
        db.session.commit()
        return jsonify({'message': 'Milestone deleted successfully'})