from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.notification import Notification
from app.api.auth import login_required

notif_bp = Blueprint('notification', __name__)


@notif_bp.route('', methods=['GET'])
@login_required
def list_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_read = request.args.get('is_read', type=int)
    notification_type = request.args.get('notification_type', '')

    query = Notification.query.filter_by(receiver_id=request.current_user['user_id'])

    if is_read is not None:
        query = query.filter_by(is_read=bool(is_read))
    if notification_type:
        query = query.filter_by(notification_type=notification_type)

    query = query.order_by(Notification.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [n.to_dict() for n in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@notif_bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    count = Notification.query.filter_by(
        receiver_id=request.current_user['user_id'], is_read=False
    ).count()
    return jsonify({'code': 200, 'data': {'count': count}})


@notif_bp.route('/<int:notif_id>/read', methods=['PUT'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get(notif_id)
    if not notif:
        return jsonify({'code': 404, 'message': '通知不存在'}), 404
    notif.is_read = True
    notif.read_at = datetime.now()
    db.session.commit()
    return jsonify({'code': 200, 'message': '已标记已读'})


@notif_bp.route('/read-all', methods=['PUT'])
@login_required
def mark_all_read():
    Notification.query.filter_by(
        receiver_id=request.current_user['user_id'], is_read=False
    ).update({'is_read': True, 'read_at': datetime.now()})
    db.session.commit()
    return jsonify({'code': 200, 'message': '全部标记已读'})


def send_notification(receiver_id, title, content='', notif_type='system',
                      entity_type=None, entity_id=None, sender_id=None):
    notif = Notification(
        title=title, content=content, notification_type=notif_type,
        sender_id=sender_id, receiver_id=receiver_id,
        entity_type=entity_type, entity_id=entity_id,
    )
    db.session.add(notif)
    return notif
