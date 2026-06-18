from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_alert import PersonAlert
from app.models.key_person import KeyPerson
from app.api.auth import login_required
from app.utils import log_operation

alert_bp = Blueprint('person_alert', __name__)


@alert_bp.route('', methods=['GET'])
@login_required
def list_alerts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    person_id = request.args.get('person_id', type=int)
    person_name = request.args.get('person_name', '')
    status = request.args.get('status', '')
    alert_level = request.args.get('alert_level', '')
    alert_type = request.args.get('alert_type', '')
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')

    query = PersonAlert.query

    if person_id:
        query = query.filter_by(person_id=person_id)
    if person_name:
        query = query.join(KeyPerson).filter(
            KeyPerson.name.like(f'%{person_name}%'))
    if status:
        query = query.filter_by(status=status)
    if alert_level:
        query = query.filter_by(alert_level=alert_level)
    if alert_type:
        query = query.filter(PersonAlert.alert_type.like(f'%{alert_type}%'))
    if start_time:
        query = query.filter(PersonAlert.alert_time >= start_time)
    if end_time:
        query = query.filter(PersonAlert.alert_time <= end_time)

    query = query.order_by(PersonAlert.alert_time.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [a.to_dict() for a in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@alert_bp.route('/stats', methods=['GET'])
@login_required
def get_alert_stats():
    total = PersonAlert.query.count()
    pending = PersonAlert.query.filter_by(status='pending').count()
    urgent = PersonAlert.query.filter_by(alert_level='urgent', status='pending').count()
    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'pending': pending,
            'urgent_pending': urgent,
        }
    })


@alert_bp.route('/<int:alert_id>', methods=['GET'])
@login_required
def get_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404
    return jsonify({'code': 200, 'data': alert.to_dict()})


@alert_bp.route('', methods=['POST'])
@login_required
def create_alert():
    data = request.get_json()
    if not data.get('person_id') or not data.get('alert_type') or not data.get('alert_content'):
        return jsonify({'code': 400, 'message': '关联人员、预警类型和内容不能为空'}), 400

    alert = PersonAlert(
        person_id=data['person_id'],
        alert_type=data['alert_type'],
        alert_content=data['alert_content'],
        alert_level=data.get('alert_level', 'normal'),
        alert_time=data.get('alert_time', datetime.now()),
        status='pending',
    )
    db.session.add(alert)
    db.session.commit()
    log_operation('CREATE', 'person_alert', alert.alert_id, f'{alert.alert_type}-{alert.alert_level}')
    return jsonify({'code': 200, 'message': '创建成功', 'data': alert.to_dict()})


@alert_bp.route('/<int:alert_id>', methods=['PUT'])
@login_required
def update_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404

    data = request.get_json()
    if 'person_id' in data:
        alert.person_id = data['person_id']
    if 'alert_type' in data:
        alert.alert_type = data['alert_type']
    if 'alert_content' in data:
        alert.alert_content = data['alert_content']
    if 'alert_level' in data:
        alert.alert_level = data['alert_level']
    if 'alert_time' in data:
        alert.alert_time = data['alert_time']

    db.session.commit()
    log_operation('UPDATE', 'person_alert', alert.alert_id, f'{alert.alert_type}-{alert.alert_level}')
    return jsonify({'code': 200, 'message': '更新成功', 'data': alert.to_dict()})


@alert_bp.route('/<int:alert_id>', methods=['DELETE'])
@login_required
def delete_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404
    db.session.delete(alert)
    db.session.commit()
    log_operation('DELETE', 'person_alert', alert_id, '')
    return jsonify({'code': 200, 'message': '删除成功'})


@alert_bp.route('/<int:alert_id>/handle', methods=['PUT'])
@login_required
def handle_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404

    data = request.get_json()
    alert.status = data.get('status', 'handled')
    alert.handle_result = data.get('handle_result', '')
    alert.handler_id = request.current_user['user_id']
    alert.handle_time = datetime.now()
    db.session.commit()
    log_operation('HANDLE', 'person_alert', alert.alert_id, f'{alert.alert_type}-{alert.status}')
    return jsonify({'code': 200, 'message': '处理成功', 'data': alert.to_dict()})
