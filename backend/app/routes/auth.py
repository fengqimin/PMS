from functools import wraps
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

bp = Blueprint("auth", __name__, url_prefix="/auth")


def admin_required():
    """
    管理员权限装饰器
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                if not get_jwt().get('is_admin', False):
                    return jsonify({"code": 403, "message": "Admin permission required"}), 403
                return jwt_required()(fn)(*args, **kwargs)
            except Exception as e:
                return jsonify({"code": 401, "message": "Invalid or expired token"}), 401
        return decorated_function
    return wrapper


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    ip_address = request.remote_addr

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        # 记录失败的登录尝试
        log = SystemLog(
            level='warning',
            action_type='login_failed',
            user_id=user.id if user else None,
            details=f'Failed login attempt for username: {username} from IP: {ip_address}'
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"error": "Invalid username or password"}), 401

    # 记录成功的登录
    log = SystemLog(
        level='info',
        action_type='login_success',
        user_id=user.id,
        details=f'User {username} logged in from IP: {ip_address}'
    )
    db.session.add(log)
    db.session.commit()

    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200
