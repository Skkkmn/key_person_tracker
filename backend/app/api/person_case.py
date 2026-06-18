from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_case import PersonCase
from app.api.auth import login_required
from app.utils import log_operation

case_bp = Blueprint('person_case', __name__)


@case_bp.route('', methods=['GET'])
@login_required
def list_cases():
    person_id = request.args.get('person_id', type=int)
    case_name = request.args.get('case_name', '')

    query = PersonCase.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if case_name:
        query = query.filter(PersonCase.case_name.like(f'%{case_name}%'))
    query = query.order_by(PersonCase.case_date.desc().nullslast())
    cases = query.all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in cases]})


@case_bp.route('/<int:case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    case = PersonCase.query.get(case_id)
    if not case:
        return jsonify({'code': 404, 'message': '案件不存在'}), 404
    return jsonify({'code': 200, 'data': case.to_dict()})


@case_bp.route('', methods=['POST'])
@login_required
def create_case():
    data = request.get_json()
    if not data.get('person_id') or not data.get('case_name'):
        return jsonify({'code': 400, 'message': '关联人员和案件名称不能为空'}), 400

    case = PersonCase(
        person_id=data['person_id'],
        case_number=data.get('case_number'),
        case_name=data['case_name'],
        case_type=data.get('case_type'),
        case_date=data.get('case_date'),
        case_status=data.get('case_status'),
        description=data.get('description'),
        created_by=request.current_user['user_id'],
    )
    db.session.add(case)
    db.session.commit()
    log_operation('CREATE', 'person_case', case.case_id, case.case_name)
    return jsonify({'code': 200, 'message': '创建成功', 'data': case.to_dict()})


@case_bp.route('/<int:case_id>', methods=['PUT'])
@login_required
def update_case(case_id):
    case = PersonCase.query.get(case_id)
    if not case:
        return jsonify({'code': 404, 'message': '案件不存在'}), 404

    data = request.get_json()
    if 'person_id' in data:
        case.person_id = data['person_id']
    if 'case_number' in data:
        case.case_number = data['case_number']
    if 'case_name' in data:
        case.case_name = data['case_name']
    if 'case_type' in data:
        case.case_type = data['case_type']
    if 'case_date' in data:
        case.case_date = data['case_date']
    if 'case_status' in data:
        case.case_status = data['case_status']
    if 'description' in data:
        case.description = data['description']

    db.session.commit()
    log_operation('UPDATE', 'person_case', case.case_id, case.case_name)
    return jsonify({'code': 200, 'message': '更新成功', 'data': case.to_dict()})


@case_bp.route('/<int:case_id>', methods=['DELETE'])
@login_required
def delete_case(case_id):
    case = PersonCase.query.get(case_id)
    if not case:
        return jsonify({'code': 404, 'message': '案件不存在'}), 404
    db.session.delete(case)
    db.session.commit()
    log_operation('DELETE', 'person_case', case_id, case.case_name if case else '')
    return jsonify({'code': 200, 'message': '删除成功'})
