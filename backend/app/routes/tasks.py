from flask import Blueprint, request, jsonify
from app import db
from app.models import Task
from auth import jwt_required

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/v1/tasks')

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """
    创建新任务
    """
    data = request.get_json()
    try:
        task = Task(
            project_id=data['project_id'],
            title=data['title'],
            description=data.get('description', ''),
            assignee_id=data.get('assignee_id'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date')
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({
            'code': 200,
            'data': task.to_dict(),
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    获取任务列表
    """
    tasks = Task.query.all()
    return jsonify({
        'code': 200,
        'data': [task.to_dict() for task in tasks],
        'message': 'success'
    })