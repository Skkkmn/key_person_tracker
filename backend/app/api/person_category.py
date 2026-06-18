from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_category import PersonCategory
from app.api.auth import login_required, admin_required
from app.utils import log_operation

category_bp = Blueprint('person_category', __name__)


@category_bp.route('', methods=['GET'])
@login_required
def list_categories():
    status = request.args.get('status', '')
    query = PersonCategory.query.order_by(PersonCategory.sort_order.asc())
    if status != '':
        query = query.filter_by(status=int(status))
    categories = query.all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in categories]})


@category_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    cat = PersonCategory.query.get(category_id)
    if not cat:
        return jsonify({'code': 404, 'message': '类别不存在'}), 404
    return jsonify({'code': 200, 'data': cat.to_dict()})


@category_bp.route('', methods=['POST'])
@admin_required
def create_category():
    data = request.get_json()
    if not data.get('category_name') or not data.get('category_code'):
        return jsonify({'code': 400, 'message': '类别名称和编码不能为空'}), 400

    existing = PersonCategory.query.filter_by(category_code=data['category_code']).first()
    if existing:
        return jsonify({'code': 400, 'message': '类别编码已存在'}), 400

    cat = PersonCategory(
        category_name=data['category_name'],
        category_code=data['category_code'],
        description=data.get('description'),
        status=data.get('status', True),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(cat)
    db.session.commit()
    log_operation('CREATE', 'person_category', cat.category_id, cat.category_name)
    return jsonify({'code': 200, 'message': '创建成功', 'data': cat.to_dict()})


@category_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    cat = PersonCategory.query.get(category_id)
    if not cat:
        return jsonify({'code': 404, 'message': '类别不存在'}), 404

    data = request.get_json()
    if 'category_name' in data:
        cat.category_name = data['category_name']
    if 'category_code' in data and data['category_code'] != cat.category_code:
        existing = PersonCategory.query.filter_by(category_code=data['category_code']).first()
        if existing:
            return jsonify({'code': 400, 'message': '类别编码已存在'}), 400
        cat.category_code = data['category_code']
    if 'description' in data:
        cat.description = data['description']
    if 'status' in data:
        cat.status = data['status']
    if 'sort_order' in data:
        cat.sort_order = data['sort_order']

    db.session.commit()
    log_operation('UPDATE', 'person_category', cat.category_id, cat.category_name)
    return jsonify({'code': 200, 'message': '更新成功', 'data': cat.to_dict()})


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    cat = PersonCategory.query.get(category_id)
    if not cat:
        return jsonify({'code': 404, 'message': '类别不存在'}), 404
    db.session.delete(cat)
    db.session.commit()
    log_operation('DELETE', 'person_category', category_id, cat.category_name if cat else '')
    return jsonify({'code': 200, 'message': '删除成功'})
