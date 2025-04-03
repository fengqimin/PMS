"""
项目管理模块的路由和视图函数

"""

import logging

from flask import Blueprint, request, jsonify
from app import db
from app.models import Project
from auth import jwt_required


projects_bp = Blueprint("projects", __name__, url_prefix="/api/v1/projects")

logger = logging.getLogger(__name__)


@projects_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    """
    创建新项目

    请求参数:
    - name: 项目名称(必填)
    - description: 项目描述(可选)
    - owner_id: 项目负责人ID(必填)
    - start_date: 开始日期(可选)
    - end_date: 结束日期(可选)
    - status: 项目状态(可选，默认为'pending')

    返回:
    - 成功: 200状态码和项目数据
    - 失败: 400状态码和错误信息
    """
    data = request.get_json()
    if not data or "name" not in data or "owner_id" not in data:
        return jsonify({"code": 400, "message": "缺少必要参数: name或owner_id"}), 400

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
        return jsonify(
            {"code": 200, "data": project.to_dict(), "message": "项目创建成功"}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": f"创建项目失败: {str(e)}"}), 400


@projects_bp.route("/", methods=["GET"])
@jwt_required()
def get_projects():
    """
    获取所有项目列表

    返回:
    - 200状态码和项目列表数据
    - 按创建时间倒序排列
    """
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify(
            {
                "code": 200,
                "data": [project.to_dict() for project in projects],
                "message": "获取项目列表成功",
                "count": len(projects),
            }
        )
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取项目列表失败: {str(e)}"}), 500


@projects_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    """
    根据项目ID获取项目详情

    参数:
    - project_id: 项目ID

    返回:
    - 成功: 200状态码和项目详情
    - 项目不存在: 404状态码
    """
    try:
        project = db.session.get(Project, project_id)
        if project is None:
            return jsonify({"code": 404, "message": "项目不存在"}), 404
        return jsonify(
            {"code": 200, "data": project.to_dict(), "message": "获取项目详情成功"}
        )
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取项目详情失败: {str(e)}"}), 500


@projects_bp.route("/<int:project_id>/archive", methods=["POST"])
@jwt_required()
def archive_project(project_id):
    """
    归档指定项目

    参数:
    - project_id: 项目ID

    返回:
    - 成功: 200状态码
    - 项目不存在: 404状态码
    """
    try:
        project = db.session.get(Project, project_id)
        if project is None:
            return jsonify({"code": 404, "message": "项目不存在"}), 404

        if project.status == "archived":
            return jsonify({"code": 400, "message": "项目已归档"}), 400

        project.status = "archived"
        db.session.commit()
        return jsonify({"code": 200, "message": "项目归档成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"项目归档失败: {str(e)}"}), 500
