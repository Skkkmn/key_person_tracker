from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_tag import Tag, PersonTag
from app.api.auth import login_required, admin_required
from app.utils import log_operation

tag_bp = Blueprint('tag', __name__)


@tag_bp.route('', methods=['GET'])
@login_required
def list_tags():
    query = Tag.query.order_by(Tag.sort_order.asc(), Tag.tag_id.asc())
    tags = query.all()
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tags]})


@tag_bp.route('/<int:tag_id>', methods=['GET'])
@login_required
def get_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'code': 404, 'message': '标签不存在'}), 404
    return jsonify({'code': 200, 'data': tag.to_dict()})


@tag_bp.route('', methods=['POST'])
@admin_required
def create_tag():
    data = request.get_json()
    if not data.get('tag_name'):
        return jsonify({'code': 400, 'message': '标签名称不能为空'}), 400

    existing = Tag.query.filter_by(tag_name=data['tag_name']).first()
    if existing:
        return jsonify({'code': 400, 'message': '标签名称已存在'}), 400

    tag = Tag(
        tag_name=data['tag_name'],
        tag_color=data.get('tag_color', '#409eff'),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(tag)
    db.session.commit()
    log_operation('CREATE', 'tag', tag.tag_id, tag.tag_name)
    return jsonify({'code': 200, 'message': '创建成功', 'data': tag.to_dict()})


@tag_bp.route('/<int:tag_id>', methods=['PUT'])
@admin_required
def update_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'code': 404, 'message': '标签不存在'}), 404

    data = request.get_json()
    if 'tag_name' in data and data['tag_name'] != tag.tag_name:
        existing = Tag.query.filter_by(tag_name=data['tag_name']).first()
        if existing:
            return jsonify({'code': 400, 'message': '标签名称已存在'}), 400
        tag.tag_name = data['tag_name']
    if 'tag_color' in data:
        tag.tag_color = data['tag_color']
    if 'sort_order' in data:
        tag.sort_order = data['sort_order']

    db.session.commit()
    log_operation('UPDATE', 'tag', tag.tag_id, tag.tag_name)
    return jsonify({'code': 200, 'message': '更新成功', 'data': tag.to_dict()})


@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if not tag:
        return jsonify({'code': 404, 'message': '标签不存在'}), 404
    PersonTag.query.filter_by(tag_id=tag_id).delete()
    db.session.delete(tag)
    db.session.commit()
    log_operation('DELETE', 'tag', tag_id, tag.tag_name if tag else '')
    return jsonify({'code': 200, 'message': '删除成功'})


@tag_bp.route('/person/<int:person_id>', methods=['GET'])
@login_required
def get_person_tags(person_id):
    mappings = PersonTag.query.filter_by(person_id=person_id).all()
    tags = [Tag.query.get(m.tag_id) for m in mappings]
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tags if t]})


@tag_bp.route('/person/<int:person_id>', methods=['POST'])
@login_required
def set_person_tags(person_id):
    data = request.get_json()
    tag_ids = data.get('tag_ids', [])

    PersonTag.query.filter_by(person_id=person_id).delete()
    for tag_id in tag_ids:
        mapping = PersonTag(person_id=person_id, tag_id=tag_id)
        db.session.add(mapping)

    db.session.commit()
    tags = [Tag.query.get(t) for t in tag_ids]
    log_operation('SET_TAGS', 'tag', entity_id=person_id, entity_name=f'设置{len(tag_ids)}个标签')
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tags if t]})
