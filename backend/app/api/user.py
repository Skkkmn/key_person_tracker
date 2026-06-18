import bcrypt
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.api.auth import login_required, role_required, get_visible_dept_ids
from app.utils import log_operation

user_bp = Blueprint('user', __name__)


@user_bp.route('', methods=['GET'])
@role_required('dept_admin')
def list_users():
    username = request.args.get('username', '')
    real_name = request.args.get('real_name', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')

    query = User.query
    current_role = request.current_user.get('role', '')
    if current_role != 'super_admin':
        dept_ids = get_visible_dept_ids(request.current_user['user_id'])
        if dept_ids is not None:
            query = query.filter(User.department_id.in_(dept_ids))
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    if real_name:
        query = query.filter(User.real_name.like(f'%{real_name}%'))
    if role:
        query = query.filter_by(role=role)
    if status != '':
        query = query.filter_by(status=int(status))
    query = query.order_by(User.user_id.asc())
    users = query.all()
    return jsonify({'code': 200, 'data': [u.to_dict() for u in users]})


@user_bp.route('/<int:user_id>', methods=['GET'])
@role_required('dept_admin')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()})


@user_bp.route('', methods=['POST'])
@role_required('super_admin')
def create_user():
    data = request.get_json()
    if not data.get('username') or not data.get('password') or not data.get('real_name'):
        return jsonify({'code': 400, 'message': '用户名、密码和姓名不能为空'}), 400

    existing = User.query.filter_by(username=data['username']).first()
    if existing:
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    user = User(
        username=data['username'],
        password=hashed.decode('utf-8'),
        real_name=data['real_name'],
        role=data.get('role', 'operator'),
        department_id=data.get('department_id'),
        phone=data.get('phone'),
        status=data.get('status', True),
    )
    db.session.add(user)
    db.session.commit()
    log_operation('CREATE', 'user', user.user_id, user.username)
    return jsonify({'code': 200, 'message': '创建成功', 'data': user.to_dict()})


@user_bp.route('/<int:user_id>', methods=['PUT'])
@role_required('super_admin')
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    if 'username' in data and data['username'] != user.username:
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        user.username = data['username']
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'password' in data and data['password']:
        hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        user.password = hashed.decode('utf-8')
    if 'role' in data:
        user.role = data['role']
    if 'department_id' in data:
        user.department_id = data.get('department_id')
    if 'phone' in data:
        user.phone = data['phone']
    if 'status' in data:
        user.status = data['status']

    db.session.commit()
    log_operation('UPDATE', 'user', user.user_id, user.username)
    return jsonify({'code': 200, 'message': '更新成功', 'data': user.to_dict()})


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('super_admin')
def delete_user(user_id):
    if user_id == request.current_user['user_id']:
        return jsonify({'code': 400, 'message': '不能删除自己'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    db.session.commit()
    log_operation('DELETE', 'user', user_id, user.username if user else '')
    return jsonify({'code': 200, 'message': '删除成功'})
