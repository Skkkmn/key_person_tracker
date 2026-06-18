from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_alert import PersonAlert
from app.api.auth import login_required
from app.utils import log_operation

review_bp = Blueprint('alert_review', __name__)


@review_bp.route('/<int:alert_id>/verify', methods=['PUT'])
@login_required
def verify_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404

    data = request.get_json()
    alert.verify_result = data.get('verify_result', '')
    db.session.commit()
    log_operation('VERIFY', 'alert', alert_id, f'核实预警-{alert.alert_type}')
    return jsonify({'code': 200, 'message': '核实信息已保存', 'data': alert.to_dict()})


@review_bp.route('/<int:alert_id>/review', methods=['PUT'])
@login_required
def review_alert(alert_id):
    alert = PersonAlert.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': '预警不存在'}), 404

    data = request.get_json()
    alert.review_opinion = data.get('review_opinion', '')
    alert.reviewer_id = request.current_user['user_id']
    alert.review_time = datetime.now()

    if data.get('status') in ('handled', 'dismissed'):
        alert.status = data['status']

    db.session.commit()
    log_operation('REVIEW', 'alert', alert_id, f'审核预警-{alert.alert_type}')
    return jsonify({'code': 200, 'message': '审核完成', 'data': alert.to_dict()})


@review_bp.route('/stats', methods=['GET'])
@login_required
def review_stats():
    total = PersonAlert.query.count()
    pending = PersonAlert.query.filter_by(status='pending').count()
    handled = PersonAlert.query.filter_by(status='handled').count()
    dismissed = PersonAlert.query.filter_by(status='dismissed').count()
    unreviewed = PersonAlert.query.filter(
        PersonAlert.status.in_(('handled', 'dismissed')),
        PersonAlert.reviewer_id.is_(None),
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total, 'pending': pending,
            'handled': handled, 'dismissed': dismissed,
            'unreviewed': unreviewed,
        }
    })
