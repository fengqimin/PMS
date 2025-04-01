from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models import SystemLog

logs_bp = Blueprint('logs', __name__, url_prefix='/api/v1/logs')

@logs_bp.route('', methods=['GET'])
@jwt_required()
def get_logs():
    """
    获取系统日志
    查询参数:
    - level: 日志级别(可选)
    - start_date: 开始日期(可选)
    - end_date: 结束日期(可选)
    - limit: 返回条数限制(可选，默认100)
    """
    try:
        current_user_id = get_jwt_identity()
        print(current_user_id)  # 打印当前用户ID，用于调试
        
        # 获取查询参数
        level = request.args.get('level')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 如果没有提供任何参数，返回所有日志
        if not any([level, start_date, end_date, request.args.get('limit')]):
            logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
            return jsonify({
                'code': 200,
                'data': [log.to_dict() for log in logs],
                'total': len(logs),
                'message': 'success'
            })
            
        try:
            limit = int(request.args.get('limit', 100))
            if limit <= 0:
                return jsonify({'code': 400, 'message': 'Limit必须为正数'}), 400
            if limit > 1000:
                return jsonify({'code': 400, 'message': 'Limit不能超过1000'}), 400
        except ValueError:
            return jsonify({'code': 400, 'message': '无效的limit格式'}), 400
        
        # 构建查询
        query = SystemLog.query
        
        if level:
            query = query.filter_by(level=level)
            
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(SystemLog.timestamp >= start_date)
            except ValueError:
                return jsonify({'code': 400, 'message': 'Invalid start_date format'}), 400
            
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(SystemLog.timestamp <= end_date)
            except ValueError:
                return jsonify({'code': 400, 'message': 'Invalid end_date format'}), 400
        
        # 执行查询并返回结果
        logs = query.order_by(SystemLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'code': 200,
            'data': [log.to_dict() for log in logs],
            'total': len(logs),
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取日志失败: {str(e)}'
        }), 500

if __name__=='__main__':
    pass