from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.key_person import KeyPerson
from app.models.person_tag import Tag, PersonTag
from sqlalchemy import func
from app.api.auth import login_required, get_visible_dept_ids
from app.utils import log_operation, get_changes

person_bp = Blueprint('key_person', __name__)

ALL_FIELDS = [
    'name', 'gender', 'id_card', 'birth_date', 'phone', 'address',
    'current_address', 'photo_url', 'education', 'employment_status',
    'employer', 'political_status', 'ethnicity', 'marital_status',
    'household_type', 'category_id', 'risk_level', 'department_id',
    'control_status', 'case_description', 'category_ext_fields',
]

SEARCH_FIELDS = ['name', 'id_card', 'education', 'employment_status',
                 'political_status', 'ethnicity', 'employer']


@person_bp.route('', methods=['GET'])
@login_required
def list_persons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name = request.args.get('name', '')
    id_card = request.args.get('id_card', '')
    category_id = request.args.get('category_id', type=int)
    risk_level = request.args.get('risk_level', '')
    control_status = request.args.get('control_status', '')
    department_id = request.args.get('department_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    tag_ids = request.args.get('tag_ids', '')
    tag_mode = request.args.get('tag_mode', 'or')
    keyword = request.args.get('keyword', '')

    query = KeyPerson.query

    if name:
        query = query.filter(KeyPerson.name.like(f'%{name}%'))
    if id_card:
        query = query.filter(KeyPerson.id_card.like(f'%{id_card}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    if control_status:
        query = query.filter_by(control_status=control_status)
    if not department_id:
        current_role = request.current_user.get('role', '')
        if current_role != 'super_admin':
            dept_ids = get_visible_dept_ids(request.current_user['user_id'])
            if dept_ids is not None:
                query = query.filter(KeyPerson.department_id.in_(dept_ids))
    if keyword:
        like = f'%{keyword}%'
        filters = [KeyPerson.name.like(like), KeyPerson.id_card.like(like),
                   KeyPerson.phone.like(like), KeyPerson.address.like(like)]
        query = query.filter(db.or_(*filters))
    if tag_ids:
        ids = [int(x) for x in tag_ids.split(',') if x.strip().isdigit()]
        if ids:
            if tag_mode == 'and':
                subq = db.session.query(PersonTag.person_id)\
                    .filter(PersonTag.tag_id.in_(ids))\
                    .group_by(PersonTag.person_id)\
                    .having(func.count(PersonTag.tag_id) == len(ids))
                query = query.filter(KeyPerson.person_id.in_(subq))
            else:
                query = query.filter(KeyPerson.tags.any(Tag.tag_id.in_(ids)))
    elif tag_id:
        query = query.filter(KeyPerson.tags.any(Tag.tag_id == tag_id))

    query = query.order_by(KeyPerson.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@person_bp.route('/all', methods=['GET'])
@login_required
def list_all_persons():
    persons = KeyPerson.query.order_by(KeyPerson.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [p.to_dict() for p in persons]})


@person_bp.route('/<int:person_id>', methods=['GET'])
@login_required
def get_person(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404
    return jsonify({'code': 200, 'data': person.to_dict()})


@person_bp.route('', methods=['POST'])
@login_required
def create_person():
    data = request.get_json()
    if not data.get('name') or not data.get('id_card'):
        return jsonify({'code': 400, 'message': '姓名和身份证号不能为空'}), 400

    existing = KeyPerson.query.filter_by(id_card=data['id_card']).first()
    if existing:
        return jsonify({'code': 400, 'message': '身份证号已存在'}), 400

    person = KeyPerson(
        name=data['name'],
        gender=data.get('gender'),
        id_card=data['id_card'],
        birth_date=data.get('birth_date'),
        phone=data.get('phone'),
        address=data.get('address'),
        current_address=data.get('current_address'),
        photo_url=data.get('photo_url'),
        education=data.get('education'),
        employment_status=data.get('employment_status'),
        employer=data.get('employer'),
        political_status=data.get('political_status'),
        ethnicity=data.get('ethnicity'),
        marital_status=data.get('marital_status'),
        household_type=data.get('household_type'),
        category_id=data.get('category_id'),
        risk_level=data.get('risk_level', 'medium'),
        department_id=data.get('department_id'),
        control_status=data.get('control_status', 'monitored'),
        case_description=data.get('case_description'),
        category_ext_fields=data.get('category_ext_fields'),
        created_by=request.current_user['user_id'],
    )
    db.session.add(person)
    db.session.flush()

    tag_ids = data.get('tag_ids', [])
    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag:
            person.tags.append(tag)

    log_operation('CREATE', 'key_person', person.person_id, person.name)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': person.to_dict()})


@person_bp.route('/<int:person_id>', methods=['PUT'])
@login_required
def update_person(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    data = request.get_json()

    old_values = {}
    for f in ALL_FIELDS:
        old_val = getattr(person, f, None)
        if f in data:
            new_val = data[f]
            if str(old_val) != str(new_val):
                old_values[f] = str(old_val) if old_val is not None else None

    if 'name' in data:
        person.name = data['name']
    if 'gender' in data:
        person.gender = data['gender']
    if 'id_card' in data and data['id_card'] != person.id_card:
        existing = KeyPerson.query.filter_by(id_card=data['id_card']).first()
        if existing:
            return jsonify({'code': 400, 'message': '身份证号已存在'}), 400
        person.id_card = data['id_card']
    if 'birth_date' in data:
        person.birth_date = data['birth_date']
    if 'phone' in data:
        person.phone = data['phone']
    if 'address' in data:
        person.address = data['address']
    if 'current_address' in data:
        person.current_address = data['current_address']
    if 'photo_url' in data:
        person.photo_url = data['photo_url']
    if 'education' in data:
        person.education = data['education']
    if 'employment_status' in data:
        person.employment_status = data['employment_status']
    if 'employer' in data:
        person.employer = data['employer']
    if 'political_status' in data:
        person.political_status = data['political_status']
    if 'ethnicity' in data:
        person.ethnicity = data['ethnicity']
    if 'marital_status' in data:
        person.marital_status = data['marital_status']
    if 'household_type' in data:
        person.household_type = data['household_type']
    if 'category_id' in data:
        person.category_id = data['category_id']
    if 'risk_level' in data:
        person.risk_level = data['risk_level']
    if 'department_id' in data:
        person.department_id = data['department_id']
    if 'control_status' in data:
        person.control_status = data['control_status']
    if 'case_description' in data:
        person.case_description = data['case_description']
    if 'category_ext_fields' in data:
        person.category_ext_fields = data['category_ext_fields']

    if 'tag_ids' in data:
        person.tags = []
        for tag_id in data['tag_ids']:
            tag = Tag.query.get(tag_id)
            if tag:
                person.tags.append(tag)

    log_operation('UPDATE', 'key_person', person.person_id, person.name,
                  old_value=old_values if old_values else None)
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': person.to_dict()})


@person_bp.route('/<int:person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    log_operation('DELETE', 'key_person', person.person_id, person.name)
    db.session.delete(person)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@person_bp.route('/<int:person_id>/archive', methods=['PUT'])
@login_required
def archive_person(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    data = request.get_json()
    person.control_status = 'archived'
    person.archived_at = datetime.now()
    person.archived_by = request.current_user['user_id']
    person.archive_reason = data.get('reason', '')
    person.archived_at_dt = datetime.now()

    log_operation('ARCHIVE', 'key_person', person.person_id, person.name,
                  new_value={'reason': data.get('reason', '')})
    db.session.commit()
    return jsonify({'code': 200, 'message': '归档成功', 'data': person.to_dict()})


@person_bp.route('/<int:person_id>/lost', methods=['PUT'])
@login_required
def mark_lost(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    data = request.get_json()
    person.control_status = 'lost'
    person.lost_at = datetime.now()
    person.lost_info = data.get('lost_info', '')

    log_operation('MARK_LOST', 'key_person', person.person_id, person.name,
                  new_value={'lost_info': data.get('lost_info', '')})
    db.session.commit()
    return jsonify({'code': 200, 'message': '已标记为失联', 'data': person.to_dict()})


@person_bp.route('/<int:person_id>/status', methods=['PUT'])
@login_required
def update_status(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    data = request.get_json()
    new_status = data.get('control_status', '')
    valid_statuses = ['monitored', 'removed', 'archived', 'lost', 'missing']
    if new_status not in valid_statuses:
        return jsonify({'code': 400, 'message': '无效的状态值'}), 400

    old_status = person.control_status
    person.control_status = new_status
    if new_status == 'lost':
        person.lost_at = datetime.now()
        person.lost_info = data.get('lost_info', '')
    elif new_status == 'archived':
        person.archived_at = datetime.now()
        person.archived_by = request.current_user['user_id']
        person.archive_reason = data.get('reason', '')
    elif new_status == 'missing':
        person.lost_at = datetime.now()
        person.lost_info = data.get('lost_info', '')

    log_operation('STATUS_CHANGE', 'key_person', person.person_id, person.name,
                  old_value={'control_status': old_status},
                  new_value={'control_status': new_status})
    db.session.commit()
    return jsonify({'code': 200, 'message': '状态更新成功', 'data': person.to_dict()})


@person_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total = KeyPerson.query.count()
    by_category = db.session.query(
        KeyPerson.category_id, db.func.count(KeyPerson.person_id)
    ).group_by(KeyPerson.category_id).all()

    by_risk = db.session.query(
        KeyPerson.risk_level, db.func.count(KeyPerson.person_id)
    ).group_by(KeyPerson.risk_level).all()

    by_status = db.session.query(
        KeyPerson.control_status, db.func.count(KeyPerson.person_id)
    ).group_by(KeyPerson.control_status).all()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'by_category': {int(k) if isinstance(k, int) or k.isdigit() else k: v for k, v in by_category},
            'by_risk': {k: v for k, v in by_risk},
            'by_status': {k: v for k, v in by_status},
        }
    })
