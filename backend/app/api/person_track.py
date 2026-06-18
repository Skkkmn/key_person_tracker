from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person_track import PersonTrack
from app.models.key_person import KeyPerson
from app.api.auth import login_required
from app.utils import log_operation

track_bp = Blueprint('person_track', __name__)


@track_bp.route('', methods=['GET'])
@login_required
def list_tracks():
    person_id = request.args.get('person_id', type=int)
    activity_type = request.args.get('activity_type', '')
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')

    query = PersonTrack.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    if start_time:
        query = query.filter(PersonTrack.track_time >= start_time)
    if end_time:
        query = query.filter(PersonTrack.track_time <= end_time)
    query = query.order_by(PersonTrack.track_time.desc())
    tracks = query.all()
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tracks]})


@track_bp.route('/<int:track_id>', methods=['GET'])
@login_required
def get_track(track_id):
    track = PersonTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '轨迹不存在'}), 404
    return jsonify({'code': 200, 'data': track.to_dict()})


@track_bp.route('', methods=['POST'])
@login_required
def create_track():
    data = request.get_json()
    if not data.get('person_id') or not data.get('track_time') or not data.get('location'):
        return jsonify({'code': 400, 'message': '关联人员、时间和地点不能为空'}), 400

    track = PersonTrack(
        person_id=data['person_id'],
        track_time=data['track_time'],
        location=data['location'],
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        activity_type=data.get('activity_type'),
        description=data.get('description'),
        source=data.get('source'),
    )
    db.session.add(track)
    db.session.commit()
    log_operation('CREATE', 'person_track', track.track_id, track.location)
    return jsonify({'code': 200, 'message': '创建成功', 'data': track.to_dict()})


@track_bp.route('/<int:track_id>', methods=['PUT'])
@login_required
def update_track(track_id):
    track = PersonTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '轨迹不存在'}), 404

    data = request.get_json()
    if 'person_id' in data:
        track.person_id = data['person_id']
    if 'track_time' in data:
        track.track_time = data['track_time']
    if 'location' in data:
        track.location = data['location']
    if 'longitude' in data:
        track.longitude = data['longitude']
    if 'latitude' in data:
        track.latitude = data['latitude']
    if 'activity_type' in data:
        track.activity_type = data['activity_type']
    if 'description' in data:
        track.description = data['description']
    if 'source' in data:
        track.source = data['source']

    db.session.commit()
    log_operation('UPDATE', 'person_track', track.track_id, track.location)
    return jsonify({'code': 200, 'message': '更新成功', 'data': track.to_dict()})


@track_bp.route('/<int:track_id>', methods=['DELETE'])
@login_required
def delete_track(track_id):
    track = PersonTrack.query.get(track_id)
    if not track:
        return jsonify({'code': 404, 'message': '轨迹不存在'}), 404
    db.session.delete(track)
    db.session.commit()
    log_operation('DELETE', 'person_track', track_id, track.location if track else '')
    return jsonify({'code': 200, 'message': '删除成功'})


@track_bp.route('/geo-list', methods=['GET'])
@login_required
def geo_list():
    persons = KeyPerson.query.filter(
        KeyPerson.current_address.isnot(None),
        KeyPerson.current_address != '',
    ).all()
    data = []
    for p in persons:
        data.append({
            'person_id': p.person_id,
            'name': p.name,
            'risk_level': p.risk_level,
            'category_name': p.category.category_name if p.category else '',
            'address': p.current_address,
        })
    return jsonify({'code': 200, 'data': data})


@track_bp.route('/geo-distribution', methods=['GET'])
@login_required
def geo_distribution():
    person_id = request.args.get('person_id', type=int)
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')

    query = PersonTrack.query.filter(
        PersonTrack.longitude.isnot(None),
        PersonTrack.latitude.isnot(None),
    )
    if person_id:
        query = query.filter_by(person_id=person_id)
    if start_time:
        query = query.filter(PersonTrack.track_time >= start_time)
    if end_time:
        query = query.filter(PersonTrack.track_time <= end_time)

    tracks = query.order_by(PersonTrack.track_time.asc()).all()
    data = []
    for t in tracks:
        data.append({
            'track_id': t.track_id,
            'person_id': t.person_id,
            'longitude': float(t.longitude),
            'latitude': float(t.latitude),
            'location': t.location,
            'track_time': t.track_time.isoformat() if t.track_time else '',
            'activity_type': t.activity_type,
        })
    return jsonify({'code': 200, 'data': data})
