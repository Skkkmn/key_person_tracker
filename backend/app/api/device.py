import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.tracking_device import TrackingDevice
from app.models.key_person import KeyPerson
from app.models.person_track import PersonTrack
from app.api.auth import login_required, role_required
from app.utils import log_operation

device_bp = Blueprint('device', __name__)


@device_bp.route('', methods=['GET'])
@login_required
def list_devices():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_active = request.args.get('is_active', type=int)

    query = TrackingDevice.query
    if is_active is not None:
        query = query.filter_by(is_active=bool(is_active))
    query = query.order_by(TrackingDevice.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [d.to_dict() for d in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@device_bp.route('/<int:device_id>', methods=['GET'])
@login_required
def get_device(device_id):
    device = TrackingDevice.query.get(device_id)
    if not device:
        return jsonify({'code': 404, 'message': '设备不存在'}), 404
    return jsonify({'code': 200, 'data': device.to_dict()})


@device_bp.route('/bind', methods=['POST'])
@login_required
@role_required(3)
def bind_device():
    data = request.get_json()
    person_id = data.get('person_id')
    if not person_id:
        return jsonify({'code': 400, 'message': 'person_id 不能为空'}), 400

    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '重点人员不存在'}), 404

    existing = TrackingDevice.query.filter_by(person_id=person_id).first()
    if existing:
        return jsonify({'code': 400, 'message': '该人员已绑定设备'}), 400

    device_imei = data.get('device_imei', '')
    if device_imei:
        dup = TrackingDevice.query.filter_by(device_imei=device_imei).first()
        if dup:
            return jsonify({'code': 400, 'message': '该设备已绑定其他人员'}), 400

    device = TrackingDevice(
        person_id=person_id,
        device_name=data.get('device_name', ''),
        device_imei=device_imei,
        phone_number=data.get('phone_number', ''),
        api_token=uuid.uuid4().hex,
        bound_by=request.current_user['user_id'],
    )
    db.session.add(device)
    db.session.commit()
    log_operation('CREATE', 'tracking_device', device.device_id, f'bind person_id={person_id}')
    return jsonify({'code': 200, 'message': '绑定成功', 'data': device.to_dict()})


@device_bp.route('/<int:device_id>/unbind', methods=['POST'])
@login_required
@role_required(3)
def unbind_device(device_id):
    device = TrackingDevice.query.get(device_id)
    if not device:
        return jsonify({'code': 404, 'message': '设备不存在'}), 404
    db.session.delete(device)
    db.session.commit()
    log_operation('DELETE', 'tracking_device', device_id, 'unbind')
    return jsonify({'code': 200, 'message': '解绑成功'})


@device_bp.route('/mobile-report', methods=['POST'])
def mobile_report():
    token = request.headers.get('X-Device-Token', '')
    if not token:
        return jsonify({'code': 401, 'message': '缺少设备令牌'}), 401

    device = TrackingDevice.query.filter_by(api_token=token, is_active=True).first()
    if not device:
        return jsonify({'code': 401, 'message': '设备令牌无效或已停用'}), 401

    data = request.get_json()
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    if longitude is None or latitude is None:
        return jsonify({'code': 400, 'message': '经纬度不能为空'}), 400

    battery = data.get('battery_level')
    track_time_str = data.get('track_time', datetime.utcnow().isoformat())
    try:
        track_time = datetime.fromisoformat(track_time_str)
    except (ValueError, TypeError):
        track_time = datetime.utcnow()

    track = PersonTrack(
        person_id=device.person_id,
        track_time=track_time,
        location=data.get('location', ''),
        longitude=longitude,
        latitude=latitude,
        activity_type='gps_report',
        description=data.get('description', ''),
        source='mobile_app',
    )
    db.session.add(track)

    device.last_latitude = latitude
    device.last_longitude = longitude
    device.last_battery_level = battery
    device.last_online_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'code': 200, 'message': '上报成功'})


@device_bp.route('/person/<int:person_id>/location', methods=['GET'])
@login_required
def get_person_device_location(person_id):
    device = TrackingDevice.query.filter_by(person_id=person_id, is_active=True).first()
    if not device:
        return jsonify({'code': 404, 'message': '该人员未绑定设备'}), 404
    return jsonify({'code': 200, 'data': device.to_public_dict()})
