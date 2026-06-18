from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_contact import PersonContact
from app.api.auth import login_required
from app.utils import log_operation

contact_bp = Blueprint('person_contact', __name__)


@contact_bp.route('', methods=['GET'])
@login_required
def list_contacts():
    person_id = request.args.get('person_id', type=int)
    name = request.args.get('name', '')

    query = PersonContact.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if name:
        query = query.filter(PersonContact.name.like(f'%{name}%'))
    query = query.order_by(PersonContact.contact_id.desc())
    contacts = query.all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in contacts]})


@contact_bp.route('/<int:contact_id>', methods=['GET'])
@login_required
def get_contact(contact_id):
    contact = PersonContact.query.get(contact_id)
    if not contact:
        return jsonify({'code': 404, 'message': '联系人不存在'}), 404
    return jsonify({'code': 200, 'data': contact.to_dict()})


@contact_bp.route('', methods=['POST'])
@login_required
def create_contact():
    data = request.get_json()
    if not data.get('person_id') or not data.get('name'):
        return jsonify({'code': 400, 'message': '关联人员和联系人姓名不能为空'}), 400

    contact = PersonContact(
        person_id=data['person_id'],
        name=data['name'],
        relation=data.get('relation'),
        phone=data.get('phone'),
        address=data.get('address'),
        is_emergency=data.get('is_emergency', False),
    )
    db.session.add(contact)
    db.session.commit()
    log_operation('CREATE', 'person_contact', contact.contact_id, contact.name)
    return jsonify({'code': 200, 'message': '创建成功', 'data': contact.to_dict()})


@contact_bp.route('/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    contact = PersonContact.query.get(contact_id)
    if not contact:
        return jsonify({'code': 404, 'message': '联系人不存在'}), 404

    data = request.get_json()
    if 'person_id' in data:
        contact.person_id = data['person_id']
    if 'name' in data:
        contact.name = data['name']
    if 'relation' in data:
        contact.relation = data['relation']
    if 'phone' in data:
        contact.phone = data['phone']
    if 'address' in data:
        contact.address = data['address']
    if 'is_emergency' in data:
        contact.is_emergency = data['is_emergency']

    db.session.commit()
    log_operation('UPDATE', 'person_contact', contact.contact_id, contact.name)
    return jsonify({'code': 200, 'message': '更新成功', 'data': contact.to_dict()})


@contact_bp.route('/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = PersonContact.query.get(contact_id)
    if not contact:
        return jsonify({'code': 404, 'message': '联系人不存在'}), 404
    db.session.delete(contact)
    db.session.commit()
    log_operation('DELETE', 'person_contact', contact_id, contact.name if contact else '')
    return jsonify({'code': 200, 'message': '删除成功'})
