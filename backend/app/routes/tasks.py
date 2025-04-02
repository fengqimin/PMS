from flask import Blueprint, request, jsonify
from app import db
from app.models import Task, TaskComment
from auth import jwt_required

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")


@tasks_bp.route("/", methods=["POST"])
@jwt_required()
def create_task():
    """
    创建新任务
    """
    data = request.get_json()
    try:
        task = Task(
            project_id=data["project_id"],
            title=data["title"],
            description=data.get("description", ""),
            assignee_id=data.get("assignee_id"),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date"),
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours", 0),
            dependencies=data.get("dependencies", ""),
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({"code": 200, "data": task.to_dict(), "message": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400


@tasks_bp.route("/", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    获取任务列表
    """
    tasks = Task.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [
                {
                    "id": task.id,
                    "project_id": task.project_id,
                    "title": task.title,
                    "description": task.description,
                    "assignee_id": task.assignee_id,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours,
                    "dependencies": (
                        task.dependencies.split(",") if task.dependencies else []
                    ),
                }
                for task in tasks
            ],
            "message": "success",
        }
    )


@tasks_bp.route("/kanban", methods=["GET"])
@jwt_required()
def get_kanban_tasks():
    """
    获取看板视图任务
    """
    statuses = ["todo", "doing", "done"]
    result = {}
    for status in statuses:
        tasks = Task.query.filter_by(status=status).all()
        result[status] = [task.to_dict() for task in tasks]
    return jsonify({"code": 200, "data": result, "message": "success"})


@tasks_bp.route("/<int:task_id>/comments", methods=["GET"])
@jwt_required()
def get_task_comments(task_id):
    """
    获取任务评论
    """
    comments = TaskComment.query.filter_by(task_id=task_id).all()
    return jsonify(
        {
            "code": 200,
            "data": [
                {
                    "id": comment.id,
                    "task_id": comment.task_id,
                    "user_id": comment.user_id,
                    "content": comment.content,
                    "mentioned_users": (
                        comment.mentioned_users.split(",")
                        if comment.mentioned_users
                        else []
                    ),
                    "created_at": (
                        comment.created_at.isoformat() if comment.created_at else None
                    ),
                    "updated_at": (
                        comment.updated_at.isoformat() if comment.updated_at else None
                    ),
                }
                for comment in comments
            ],
            "message": "success",
        }
    )


@tasks_bp.route("/<int:task_id>/comments", methods=["POST"])
@jwt_required()
def add_task_comment(task_id):
    """
    添加任务评论
    """
    data = request.get_json()
    try:
        comment = TaskComment(
            task_id=task_id,
            user_id=data["user_id"],
            content=data["content"],
            mentioned_users=data.get("mentioned_users", ""),
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({"code": 200, "data": comment.to_dict(), "message": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400


@tasks_bp.route("/<int:task_id>/status", methods=["PUT"])
@jwt_required()
def update_task_status(task_id):
    """
    更新任务状态
    """
    data = request.get_json()
    try:
        task = Task.query.get_or_404(task_id)
        if data["status"] not in ["todo", "doing", "done"]:
            return jsonify({"code": 400, "message": "Invalid status"}), 400
        task.status = data["status"]
        db.session.commit()
        return jsonify({"code": 200, "data": task.to_dict(), "message": "success"})
    except Exception as e:
        db.session.rollback()
        if '404 Not Found' in str(e):
            return jsonify({"code": 404, "message": "Task not found"}), 404
        return jsonify({"code": 400, "message": str(e)}), 400


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """
    根据ID获取任务详情
    """
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify({"code": 200, "data": task.to_dict(), "message": "success"})
    except Exception as e:
        if '404 Not Found' in str(e):
            return jsonify({"code": 404, "message": "Task not found"}), 404
        return jsonify({"code": 400, "message": str(e)}), 400


@tasks_bp.route("/<int:task_id>/assign", methods=["PUT"])
@jwt_required()
def assign_task(task_id):
    """
    分配任务给成员
    """
    data = request.get_json()
    try:
        task = Task.query.get_or_404(task_id)
        task.assignee_id = data["assignee_id"]
        db.session.commit()
        return jsonify({"code": 200, "data": task.to_dict(), "message": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400
