from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.department import Department
from app.models.user import User
from app.models.key_person import KeyPerson
from app.api.auth import login_required, admin_required
from app.utils import log_operation

dept_bp = Blueprint('department', __name__)


@dept_bp.route('', methods=['GET'])
@login_required
def list_departments():
    name = request.args.get('dept_name', '')
    status = request.args.get('status', '')

    query = Department.query
    if name:
        query = query.filter(Department.dept_name.like(f'%{name}%'))
    if status != '':
        query = query.filter_by(status=int(status))
    query = query.order_by(Department.dept_id.asc())
    departments = query.all()
    return jsonify({'code': 200, 'data': [d.to_dict() for d in departments]})


@dept_bp.route('/<int:dept_id>', methods=['GET'])
@login_required
def get_department(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'code': 404, 'message': '部门不存在'}), 404
    return jsonify({'code': 200, 'data': dept.to_dict()})


@dept_bp.route('', methods=['POST'])
@admin_required
def create_department():
    data = request.get_json()
    if not data.get('dept_name') or not data.get('dept_code'):
        return jsonify({'code': 400, 'message': '部门名称和编码不能为空'}), 400

    existing = Department.query.filter_by(dept_code=data['dept_code']).first()
    if existing:
        return jsonify({'code': 400, 'message': '部门编码已存在'}), 400

    dept = Department(
        dept_name=data['dept_name'],
        dept_code=data['dept_code'],
        parent_id=data.get('parent_id'),
        address=data.get('address'),
        phone=data.get('phone'),
        status=data.get('status', True),
    )
    db.session.add(dept)
    db.session.commit()
    log_operation('CREATE', 'department', dept.dept_id, dept.dept_name)
    return jsonify({'code': 200, 'message': '创建成功', 'data': dept.to_dict()})


@dept_bp.route('/<int:dept_id>', methods=['PUT'])
@admin_required
def update_department(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'code': 404, 'message': '部门不存在'}), 404

    data = request.get_json()
    if 'dept_name' in data:
        dept.dept_name = data['dept_name']
    if 'dept_code' in data and data['dept_code'] != dept.dept_code:
        existing = Department.query.filter_by(dept_code=data['dept_code']).first()
        if existing:
            return jsonify({'code': 400, 'message': '部门编码已存在'}), 400
        dept.dept_code = data['dept_code']
    if 'parent_id' in data:
        pid = data.get('parent_id')
        if pid is not None:
            if pid == dept_id:
                return jsonify({'code': 400, 'message': '不能将自己设为上级部门'}), 400

            def is_child_of(parent_id, target_id):
                child = Department.query.get(parent_id)
                if not child or child.parent_id is None:
                    return False
                if child.parent_id == target_id:
                    return True
                return is_child_of(child.parent_id, target_id)

            if is_child_of(pid, dept_id):
                return jsonify({'code': 400, 'message': '不能将子部门设为上级部门，会导致循环引用'}), 400
        dept.parent_id = pid
    if 'address' in data:
        dept.address = data['address']
    if 'phone' in data:
        dept.phone = data['phone']
    if 'status' in data:
        dept.status = data['status']

    db.session.commit()
    log_operation('UPDATE', 'department', dept.dept_id, dept.dept_name)
    return jsonify({'code': 200, 'message': '更新成功', 'data': dept.to_dict()})


@dept_bp.route('/<int:dept_id>', methods=['DELETE'])
@admin_required
def delete_department(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({'code': 404, 'message': '部门不存在'}), 404

    if Department.query.filter_by(parent_id=dept_id).first():
        return jsonify({'code': 400, 'message': '该部门下存在子部门，请先删除子部门'}), 400

    if User.query.filter_by(department_id=dept_id).first():
        return jsonify({'code': 400, 'message': '该部门下存在用户，无法删除'}), 400

    if KeyPerson.query.filter_by(department_id=dept_id).first():
        return jsonify({'code': 400, 'message': '该部门下存在重点人员，无法删除'}), 400

    db.session.delete(dept)
    db.session.commit()
    log_operation('DELETE', 'department', dept_id, dept.dept_name if dept else '')
    return jsonify({'code': 200, 'message': '删除成功'})


@dept_bp.route('/tree', methods=['GET'])
@login_required
def get_department_tree():
    departments = Department.query.order_by(Department.dept_id.asc()).all()

    def build_tree(parent_id=None):
        children = []
        for d in departments:
            if d.parent_id == parent_id:
                node = d.to_dict()
                node['children'] = build_tree(d.dept_id)
                children.append(node)
        return children

    tree = build_tree()
    return jsonify({'code': 200, 'data': tree})
