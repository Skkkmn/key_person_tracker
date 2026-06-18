from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.visit_record import VisitRecord
from app.api.auth import login_required
from app.utils import log_operation

record_bp = Blueprint('visit_record', __name__)


@record_bp.route('', methods=['GET'])
@login_required
def list_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    person_id = request.args.get('person_id', type=int)
    task_id = request.args.get('task_id', type=int)
    visitor_id = request.args.get('visitor_id', type=int)

    query = VisitRecord.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if task_id:
        query = query.filter_by(task_id=task_id)
    if visitor_id:
        query = query.filter_by(visitor_id=visitor_id)

    query = query.order_by(VisitRecord.visit_time.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })


@record_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def get_record(record_id):
    record = VisitRecord.query.get(record_id)
    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    return jsonify({'code': 200, 'data': record.to_dict()})


@record_bp.route('', methods=['POST'])
@login_required
def create_record():
    data = request.get_json()
    if not data.get('person_id'):
        return jsonify({'code': 400, 'message': '关联人员不能为空'}), 400

    record = VisitRecord(
        task_id=data.get('task_id'),
        person_id=data['person_id'],
        visitor_id=request.current_user['user_id'],
        visit_time=data.get('visit_time') or datetime.now(),
        location=data.get('location'),
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        content=data.get('content'),
        performance=data.get('performance'),
        thought_dynamics=data.get('thought_dynamics'),
        life_difficulty=data.get('life_difficulty'),
        has_abnormality=data.get('has_abnormality', False),
        abnormality_desc=data.get('abnormality_desc'),
        photo_urls=data.get('photo_urls'),
        audio_url=data.get('audio_url'),
        video_url=data.get('video_url'),
    )
    db.session.add(record)
    db.session.flush()

    if record.task_id:
        from app.models.visit_task import VisitTask
        task = VisitTask.query.get(record.task_id)
        if task:
            task.status = 'completed'

    log_operation('CREATE', 'visit_record', record.record_id,
                  f'走访记录-{record.person.name if record.person else ""}')
    db.session.commit()
    return jsonify({'code': 200, 'message': '记录创建成功', 'data': record.to_dict()})


@record_bp.route('/<int:record_id>', methods=['PUT'])
@login_required
def update_record(record_id):
    record = VisitRecord.query.get(record_id)
    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404

    data = request.get_json()
    for f in ('visit_time', 'location', 'longitude', 'latitude', 'content',
              'performance', 'thought_dynamics', 'life_difficulty',
              'has_abnormality', 'abnormality_desc', 'photo_urls', 'audio_url', 'video_url'):
        if f in data:
            setattr(record, f, data[f])

    db.session.commit()
    log_operation('UPDATE', 'visit_record', record.record_id,
                  f'走访记录-{record.person.name if record.person else ""}')
    return jsonify({'code': 200, 'message': '更新成功', 'data': record.to_dict()})


@record_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(record_id):
    record = VisitRecord.query.get(record_id)
    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    db.session.delete(record)
    db.session.commit()
    log_operation('DELETE', 'visit_record', record_id,
                  f'走访记录-{record.person.name if record.person else ""}' if record else '')
    return jsonify({'code': 200, 'message': '删除成功'})
