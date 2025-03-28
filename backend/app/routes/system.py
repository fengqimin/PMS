from flask import Blueprint, request, jsonify
from app import db
from app.models import SystemConfig
from auth import jwt_required

system_bp = Blueprint('system', __name__, url_prefix='/api/v1/system')

@system_bp.route('/email', methods=['POST'])
@jwt_required()
def configure_email():
    """
    配置邮件服务器
    """
    data = request.get_json()
    try:
        config = SystemConfig(
            key='email_config',
            value={
                'host': data['host'],
                'port': data['port'],
                'username': data['username'],
                'password': data['password'],
                'use_ssl': data.get('use_ssl', True)
            }
        )
        db.session.add(config)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400

@system_bp.route('/settings', methods=['POST'])
@jwt_required()
def update_settings():
    """
    更新系统参数设置
    """
    data = request.get_json()
    try:
        for key, value in data.items():
            config = SystemConfig.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = SystemConfig(key=key, value=value)
                db.session.add(config)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400

@system_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """
    获取系统日志
    """
    # 这里需要实现日志查询逻辑
    return jsonify({
        'code': 200,
        'data': [],
        'message': 'success'
    })