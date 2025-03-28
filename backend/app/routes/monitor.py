from flask import Blueprint, jsonify, request
from app import db
from app.models import Project, Task, ProjectProgress, ProjectRisk
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# 创建监控模块蓝图
monitor_bp = Blueprint('monitor', __name__, url_prefix='/api/v1/monitor')

@monitor_bp.route('/gantt/<int:project_id>', methods=['GET'])
@jwt_required()
def get_gantt_data(project_id):
    """
    获取项目甘特图数据
    :param project_id: 项目ID
    :return: JSON格式的甘特图数据，包含项目信息、任务列表和里程碑进度
    
    数据结构说明:
    - project: 项目基本信息
    - tasks: 任务列表，包含任务依赖关系
    - milestones: 项目里程碑进度
    - risks: 项目风险列表
    """
    try:
        current_user_id = get_jwt_identity()
        project = Project.query.get_or_404(project_id)
        
        # 验证用户是否有权限访问该项目
        if current_user_id != project.owner_id:
            return jsonify({'code': 403, 'message': '无权访问该项目'}), 403
        
        # 获取项目任务数据
        tasks = Task.query.filter_by(project_id=project_id).all()
        task_data = [{
            'id': task.id,
            'title': task.title,
            'start_date': task.start_date.isoformat() if task.start_date else None,
            'end_date': task.due_date.isoformat() if task.due_date else None,
            'progress': task.progress,
            'dependencies': task.dependencies.split(',') if task.dependencies else [],
            'assignee': task.assignee.username if task.assignee else None
        } for task in tasks]
        
        # 获取项目里程碑进度数据
        progresses = ProjectProgress.query.filter_by(project_id=project_id).all()
        progress_data = [progress.to_dict() for progress in progresses]
        
        # 获取项目风险数据
        risks = ProjectRisk.query.filter_by(project_id=project_id).all()
        risk_data = [risk.to_dict() for risk in risks]
        
        return jsonify({
            'code': 200,
            'data': {
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'status': project.status
                },
                'tasks': task_data,
                'milestones': progress_data,
                'risks': risk_data
            },
            'message': 'success'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取甘特图数据失败: {str(e)}'}), 500

@monitor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """
    获取用户所有项目的实时仪表盘数据
    :return: JSON格式的仪表盘数据，包含项目概览、进度统计和风险分析
    
    数据结构说明:
    - projects: 项目列表，包含每个项目的基本信息和统计指标
    - summary: 全局统计信息
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 获取用户参与的所有项目
        projects = Project.query.filter_by(owner_id=current_user_id).all()
        
        dashboard_data = []
        total_tasks = 0
        completed_tasks = 0
        high_risk_count = 0
        
        for project in projects:
            # 获取项目任务统计
            tasks = Task.query.filter_by(project_id=project.id).all()
            task_stats = {
                'total': len(tasks),
                'todo': len([t for t in tasks if t.status == 'todo']),
                'in_progress': len([t for t in tasks if t.status == 'in_progress']),
                'done': len([t for t in tasks if t.status == 'done'])
            }
            
            total_tasks += task_stats['total']
            completed_tasks += task_stats['done']
            
            # 计算项目平均进度
            progresses = ProjectProgress.query.filter_by(project_id=project.id).all()
            avg_progress = sum(p.completion_rate for p in progresses) / len(progresses) if progresses else 0
            
            # 获取项目风险统计
            risks = ProjectRisk.query.filter_by(project_id=project.id).all()
            high_risk_count += len([r for r in risks if r.probability == 'high' and r.impact == 'high'])
            
            dashboard_data.append({
                'project_id': project.id,
                'project_name': project.name,
                'status': project.status,
                'progress': avg_progress,
                'task_stats': task_stats,
                'risk_count': len(risks),
                'high_risk_count': len([r for r in risks if r.probability == 'high' and r.impact == 'high'])
            })
        
        # 计算全局统计信息
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return jsonify({
            'code': 200,
            'data': {
                'projects': dashboard_data,
                'summary': {
                    'total_projects': len(projects),
                    'total_tasks': total_tasks,
                    'completion_rate': round(completion_rate, 2),
                    'high_risk_count': high_risk_count
                }
            },
            'message': 'success'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取仪表盘数据失败: {str(e)}'}), 500