from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.lost_contact_track import LostContactTrack
from app.models.key_person import KeyPerson
from app.api.auth import login_required
from app.utils import log_operation

lost_bp = Blueprint('lost_contact', __name__)


@lost_bp.route('', methods=['GET'])
@login_required
def list_tracks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    person_id = request.args.get('person_id', type=int)
    status = request.args.get('status', '')

    query = LostContactTrack.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(LostContactTrack.created_at.desc())
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


@lost_bp.route('/<int:track_id>', methods=['GET'])
@login_required
def get_track(track_id):
    track = LostContactTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    return jsonify({'code': 200, 'data': track.to_dict()})


@lost_bp.route('', methods=['POST'])
@login_required
def create_track():
    data = request.get_json()
    if not data.get('person_id'):
        return jsonify({'code': 400, 'message': '关联人员不能为空'}), 400

    person = KeyPerson.query.get(data['person_id'])
    if person:
        person.control_status = 'lost'
        person.lost_at = datetime.now()
        person.lost_info = data.get('search_measures', '')

    raw_lost = data.get('lost_time')
    track = LostContactTrack(
        person_id=data['person_id'],
        lost_time=raw_lost if raw_lost else datetime.now(),
        last_location=data.get('last_location'),
        search_measures=data.get('search_measures'),
        family_contact=data.get('family_contact'),
        progress=data.get('progress'),
        status='tracking',
    )
    db.session.add(track)
    log_operation('CREATE', 'lost_contact', track.track_id,
                  f'失联台账-{person.name if person else ""}')
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': track.to_dict()})


@lost_bp.route('/<int:track_id>', methods=['PUT'])
@login_required
def update_track(track_id):
    track = LostContactTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404

    data = request.get_json()
    for f in ('lost_time', 'last_location', 'search_measures', 'family_contact', 'progress', 'status'):
        if f in data:
            setattr(track, f, data[f])

    if data.get('status') == 'resolved':
        track.resolved_at = datetime.now()
        person = KeyPerson.query.get(track.person_id)
        if person and person.control_status in ('lost', 'missing'):
            person.control_status = 'monitored'

    db.session.commit()
    person = KeyPerson.query.get(track.person_id)
    log_operation('UPDATE', 'lost_contact', track.track_id,
                  f'失联台账-{person.name if person else ""}')
    return jsonify({'code': 200, 'message': '更新成功', 'data': track.to_dict()})


@lost_bp.route('/<int:track_id>', methods=['DELETE'])
@login_required
def delete_track(track_id):
    track = LostContactTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    db.session.delete(track)
    db.session.commit()
    person = KeyPerson.query.get(track.person_id) if track else None
    log_operation('DELETE', 'lost_contact', track_id,
                  f'失联台账-{person.name if person else ""}' if track else '')
    return jsonify({'code': 200, 'message': '删除成功'})
