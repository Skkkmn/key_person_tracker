from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from flask import Blueprint, request, jsonify, current_app, send_file

from app.models.user import User
from app.models.department import Department
from app.extensions import db
from app.utils import log_operation
from app.captcha_utils import generate_captcha_text, generate_captcha_image

auth_bp = Blueprint('auth', __name__)

_captcha_store = {}

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
PASSWORD_MIN_LENGTH = 8
PASSWORD_EXPIRE_DAYS = 90

ROLE_HIERARCHY = {
    'viewer': 1,
    'operator': 2,
    'dept_admin': 3,
    'super_admin': 4,
}


def get_visible_dept_ids(user_id):
    user = User.query.get(user_id)
    if not user or not user.department_id:
        return []
    role_level = ROLE_HIERARCHY.get(user.role, 0)
    if role_level >= 4:
        return None
    dept_ids = {user.department_id}
    def collect_children(pid):
        children = Department.query.filter_by(parent_id=pid).all()
        for c in children:
            dept_ids.add(c.dept_id)
            collect_children(c.dept_id)
    if role_level >= 3:
        collect_children(user.department_id)
    return list(dept_ids)


def generate_token(user, remember=False):
    hours = current_app.config.get('JWT_EXPIRATION_HOURS', 24)
    if remember:
        hours = current_app.config.get('JWT_REMEMBER_HOURS', 168)
    payload = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=hours),
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'],
                             algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': '未登录或token已过期'}), 401
        request.current_user = payload
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    return role_required('dept_admin')(f)


def role_required(min_role='operator'):
    from functools import wraps

    min_level = ROLE_HIERARCHY.get(min_role, 2)

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            payload = verify_token(token)
            if not payload:
                return jsonify({'code': 401, 'message': '未登录或token已过期'}), 401
            user_role = payload.get('role', '')
            user_level = ROLE_HIERARCHY.get(user_role, 0)
            if user_level < min_level:
                return jsonify({'code': 403, 'message': '权限不足'}), 403
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated
    return decorator


def validate_password_strength(password):
    errors = []
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f'密码长度不能少于{PASSWORD_MIN_LENGTH}位')
    if not re.search(r'[a-z]', password):
        errors.append('密码需包含小写字母')
    if not re.search(r'[A-Z]', password):
        errors.append('密码需包含大写字母')
    if not re.search(r'\d', password):
        errors.append('密码需包含数字')
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append('密码需包含特殊字符')
    return errors


@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    text = generate_captcha_text()
    img = generate_captcha_image(text)
    if img is None:
        return jsonify({'code': 500, 'message': '验证码生成失败，请安装Pillow库'}), 500
    token = jwt.encode({
        'captcha': text,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    resp = send_file(img, mimetype='image/png')
    resp.headers['X-Captcha-Token'] = token
    return resp


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    captcha = data.get('captcha', '')
    captcha_token = data.get('captcha_token', '')

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    if captcha_token and captcha:
        try:
            ct = jwt.decode(captcha_token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])
            if ct.get('captcha', '').lower() != captcha.lower():
                return jsonify({'code': 400, 'message': '验证码错误'}), 400
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'code': 400, 'message': '验证码已过期，请刷新'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        log_operation('LOGIN', 'auth', entity_name=f'用户{username}登录失败-用户不存在')
        return jsonify({'code': 400, 'message': '用户名或密码错误'}), 400

    if not user.status:
        log_operation('LOGIN', 'auth', entity_name=f'用户{username}登录失败-用户被禁用')
        return jsonify({'code': 400, 'message': '用户已被禁用'}), 400

    if user.locked_until and user.locked_until > datetime.now():
        remain = int((user.locked_until - datetime.now()).total_seconds() // 60)
        return jsonify({'code': 400, 'message': f'账户已锁定，请{remain}分钟后再试'}), 400

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        user.login_attempts = (user.login_attempts or 0) + 1
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
            db.session.commit()
            log_operation('LOGIN', 'auth', entity_name=f'用户{username}登录失败-密码错误，账户已锁定{LOCKOUT_MINUTES}分钟')
            return jsonify({'code': 400, 'message': f'密码错误次数过多，账户已锁定{LOCKOUT_MINUTES}分钟'}), 400
        db.session.commit()
        remain = MAX_LOGIN_ATTEMPTS - user.login_attempts
        log_operation('LOGIN', 'auth', entity_name=f'用户{username}登录失败-密码错误，剩余{remain}次机会')
        return jsonify({'code': 400, 'message': f'用户名或密码错误，还剩{remain}次机会'}), 400

    user.login_attempts = 0
    user.locked_until = None

    remember = data.get('remember', False)
    token = generate_token(user, remember=remember)
    log_operation('LOGIN', 'auth', entity_name=f'用户{username}登录成功')
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': user.to_dict(),
        }
    })


@auth_bp.route('/info', methods=['GET'])
@login_required
def get_user_info():
    user = User.query.get(request.current_user['user_id'])
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()})


@auth_bp.route('/password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    old_pwd = data.get('old_password', '')
    new_pwd = data.get('new_password', '')

    if not old_pwd or not new_pwd:
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    errors = validate_password_strength(new_pwd)
    if errors:
        return jsonify({'code': 400, 'message': '；'.join(errors)}), 400

    user = User.query.get(request.current_user['user_id'])
    if not bcrypt.checkpw(old_pwd.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'code': 400, 'message': '原密码错误'}), 400

    if bcrypt.checkpw(new_pwd.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'code': 400, 'message': '新密码不能与旧密码相同'}), 400

    hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed.decode('utf-8')
    user.password_updated_at = datetime.now()
    db.session.commit()
    log_operation('CHANGE_PASSWORD', 'auth', entity_id=user.user_id, entity_name=user.username)
    return jsonify({'code': 200, 'message': '密码修改成功'})
