from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import logging
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
jwt = JWTManager()

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # 配置应用
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 生产环境需要更安全的密钥
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    from routes import auth, api, logs, member, projects, tasks, system, performance, monitor, milestone, document, dictionary, change, audit, archive
    # 注册蓝图
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(logs.logs_bp)
    app.register_blueprint(projects.projects_bp)
    app.register_blueprint(tasks.tasks_bp)
    app.register_blueprint(system.system_bp)
    app.register_blueprint(performance.performance_bp)
    app.register_blueprint(monitor.monitor_bp)
    app.register_blueprint(dictionary.bp)
    app.register_blueprint(change.bp)
    app.register_blueprint(audit.bp)
    app.register_blueprint(archive.archive_bp)
    
    # 注册全局错误处理器
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        
        if isinstance(e, HTTPException):
            response = jsonify({
                'code': e.code,
                'message': str(e.description)
            })
            response.status_code = e.code
        else:
            response = jsonify({
                'code': 500,
                'message': 'Internal server error'
            })
            response.status_code = 500
        
        return response
    
    return app