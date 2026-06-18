from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.cross_region_track import CrossRegionTrack
from app.models.key_person import KeyPerson
from app.models.department import Department
from app.models.user import User
from app.api.auth import login_required, role_required, get_visible_dept_ids
from app.api.notification import send_notification
from app.utils import log_operation

cross_region_bp = Blueprint('cross_region', __name__)


@cross_region_bp.route('', methods=['GET'])
@login_required
def list_tracks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    direction = request.args.get('direction', '')
    status = request.args.get('status', '')
    person_id = request.args.get('person_id', type=int)
    keyword = request.args.get('keyword', '')

    query = CrossRegionTrack.query
    current_role = request.current_user.get('role', '')
    if current_role != 'super_admin':
        dept_ids = get_visible_dept_ids(request.current_user['user_id'])
        if dept_ids is not None:
            query = query.filter(
                db.or_(CrossRegionTrack.from_dept_id.in_(dept_ids),
                       CrossRegionTrack.to_dept_id.in_(dept_ids))
            )
    if direction:
        query = query.filter_by(direction=direction)
    if status:
        query = query.filter_by(status=status)
    if person_id:
        query = query.filter_by(person_id=person_id)
    if keyword:
        like = f'%{keyword}%'
        query = query.join(KeyPerson).filter(
            db.or_(KeyPerson.name.like(like), KeyPerson.id_card.like(like))
        )
    query = query.order_by(CrossRegionTrack.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@cross_region_bp.route('/<int:track_id>', methods=['GET'])
@login_required
def get_track(track_id):
    track = CrossRegionTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '流动记录不存在'}), 404
    return jsonify({'code': 200, 'data': track.to_dict()})


@cross_region_bp.route('', methods=['POST'])
@login_required
def create_track():
    data = request.get_json()
    person_id = data.get('person_id')
    direction = data.get('direction')
    to_dept_id = data.get('to_dept_id')

    if not person_id or not direction:
        return jsonify({'code': 400, 'message': '人员ID和流动方向不能为空'}), 400
    if direction not in ('in', 'out'):
        return jsonify({'code': 400, 'message': '流动方向必须为 in 或 out'}), 400

    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    from_dept_id = data.get('from_dept_id', person.department_id)
    current_user_id = request.current_user['user_id']

    track = CrossRegionTrack(
        person_id=person_id,
        direction=direction,
        from_dept_id=from_dept_id,
        to_dept_id=to_dept_id,
        detected_at=datetime.now(),
        detected_by=current_user_id,
        notify_dept_id=to_dept_id if direction == 'out' else from_dept_id,
        status='pending',
        remark=data.get('remark', ''),
    )
    db.session.add(track)
    db.session.flush()

    notify_dept_id = track.notify_dept_id
    if notify_dept_id:
        dept_users = User.query.filter_by(department_id=notify_dept_id, status=True).all()
        direction_label = '流出' if direction == 'out' else '流入'
        for u in dept_users:
            send_notification(
                receiver_id=u.user_id,
                title=f'异地人员{direction_label}通知',
                content=f'人员 {person.name}({person.id_card}) 发生异地{direction_label}，请关注处理。',
                notif_type='cross_region',
                entity_type='cross_region',
                entity_id=track.track_id,
                sender_id=current_user_id,
            )

    track.notified = True
    track.notified_at = datetime.now()

    log_operation('CREATE', 'cross_region', track.track_id,
                  f'{person.name}-{direction_label}')
    db.session.commit()

    return jsonify({'code': 200, 'message': '创建成功并已推送通知', 'data': track.to_dict()})


@cross_region_bp.route('/<int:track_id>/push', methods=['POST'])
@login_required
def push_notification(track_id):
    track = CrossRegionTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '流动记录不存在'}), 404

    current_user_id = request.current_user['user_id']
    notify_dept_id = track.notify_dept_id
    if not notify_dept_id:
        return jsonify({'code': 400, 'message': '未指定推送部门'}), 400

    dept_users = User.query.filter_by(department_id=notify_dept_id, status=True).all()
    direction_label = '流出' if track.direction == 'out' else '流入'
    person = track.person

    for u in dept_users:
        send_notification(
            receiver_id=u.user_id,
            title=f'异地人员{direction_label}通知',
            content=f'人员 {person.name}({person.id_card}) 发生异地{direction_label}，请关注处理。',
            notif_type='cross_region',
            entity_type='cross_region',
            entity_id=track.track_id,
            sender_id=current_user_id,
        )

    track.notified = True
    track.notified_at = datetime.now()

    log_operation('PUSH', 'cross_region', track.track_id,
                  f'{person.name}-{direction_label}')
    db.session.commit()

    return jsonify({'code': 200, 'message': f'已向 {notify_dept_id} 部门推送通知'})


@cross_region_bp.route('/<int:track_id>', methods=['PUT'])
@login_required
def update_track(track_id):
    track = CrossRegionTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '流动记录不存在'}), 404

    data = request.get_json()
    if 'status' in data:
        track.status = data['status']
    if 'remark' in data:
        track.remark = data['remark']
    if 'to_dept_id' in data:
        track.to_dept_id = data['to_dept_id']

    db.session.commit()
    log_operation('UPDATE', 'cross_region', track.track_id)
    return jsonify({'code': 200, 'message': '更新成功', 'data': track.to_dict()})


@cross_region_bp.route('/<int:track_id>', methods=['DELETE'])
@login_required
def delete_track(track_id):
    track = CrossRegionTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '流动记录不存在'}), 404

    db.session.delete(track)
    db.session.commit()
    log_operation('DELETE', 'cross_region', track_id)
    return jsonify({'code': 200, 'message': '删除成功'})


@cross_region_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total = CrossRegionTrack.query.count()
    by_direction = db.session.query(
        CrossRegionTrack.direction, db.func.count(CrossRegionTrack.track_id)
    ).group_by(CrossRegionTrack.direction).all()
    by_status = db.session.query(
        CrossRegionTrack.status, db.func.count(CrossRegionTrack.track_id)
    ).group_by(CrossRegionTrack.status).all()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'by_direction': {k: v for k, v in by_direction},
            'by_status': {k: v for k, v in by_status},
        }
    })
