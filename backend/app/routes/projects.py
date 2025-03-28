from flask import Blueprint, request, jsonify
from app import db
from app.models import Project
from auth import jwt_required

projects_bp = Blueprint("projects", __name__, url_prefix="/api/v1/projects")


@projects_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    """
    创建新项目
    """
    data = request.get_json()
    try:
        project = Project(
            name=data["name"],
            description=data.get("description", ""),
            owner_id=data["owner_id"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            status=data.get("status", "pending"),
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({"code": 200, "data": project.to_dict(), "message": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400


@projects_bp.route("/", methods=["GET"])
@jwt_required()
def get_projects():
    """
    获取项目列表
    """
    projects = Project.query.all()
    return jsonify(
        {
            "code": 200,
            "data": [project.to_dict() for project in projects],
            "message": "success",
        }
    )
