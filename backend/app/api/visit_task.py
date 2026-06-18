from datetime import datetime

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.visit_task import VisitTask
from app.models.key_person import KeyPerson
from app.api.auth import login_required
from app.utils import log_operation

visit_bp = Blueprint('visit_task', __name__)


@visit_bp.route('', methods=['GET'])
@login_required
def list_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    person_id = request.args.get('person_id', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    status = request.args.get('status', '')
    task_type = request.args.get('task_type', '')

    query = VisitTask.query
    if person_id:
        query = query.filter_by(person_id=person_id)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    if status:
        query = query.filter_by(status=status)
    if task_type:
        query = query.filter_by(task_type=task_type)

    query = query.order_by(VisitTask.created_at.desc())
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


@visit_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = VisitTask.query.get(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({'code': 200, 'data': task.to_dict()})


@visit_bp.route('', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    if not data.get('person_id') or not data.get('title'):
        return jsonify({'code': 400, 'message': '关联人员和任务标题不能为空'}), 400

    task = VisitTask(
        person_id=data['person_id'],
        title=data['title'],
        description=data.get('description', ''),
        task_type=data.get('task_type', 'routine'),
        assigned_to=data.get('assigned_to'),
        assigned_by=request.current_user['user_id'],
        deadline=data.get('deadline') or None,
        status='pending',
    )
    db.session.add(task)
    db.session.commit()
    log_operation('CREATE', 'visit_task', task.task_id, task.title)
    return jsonify({'code': 200, 'message': '创建成功', 'data': task.to_dict()})


@visit_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = VisitTask.query.get(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    data = request.get_json()
    for f in ('title', 'description', 'task_type', 'assigned_to', 'deadline', 'status'):
        if f in data:
            setattr(task, f, data[f])

    db.session.commit()
    log_operation('UPDATE', 'visit_task', task.task_id, task.title)
    return jsonify({'code': 200, 'message': '更新成功', 'data': task.to_dict()})


@visit_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = VisitTask.query.get(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    db.session.delete(task)
    db.session.commit()
    log_operation('DELETE', 'visit_task', task_id, task.title if task else '')
    return jsonify({'code': 200, 'message': '删除成功'})


@visit_bp.route('/stats', methods=['GET'])
@login_required
def task_stats():
    total = VisitTask.query.count()
    pending = VisitTask.query.filter_by(status='pending').count()
    in_progress = VisitTask.query.filter_by(status='in_progress').count()
    completed = VisitTask.query.filter_by(status='completed').count()
    overdue = VisitTask.query.filter(
        VisitTask.deadline.isnot(None),
        VisitTask.deadline < datetime.now(),
        VisitTask.status.in_(('pending', 'in_progress'))
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'overdue': overdue,
        }
    })


@visit_bp.route('/auto-generate', methods=['POST'])
@login_required
def auto_generate():
    from datetime import timedelta

    high_risk = KeyPerson.query.filter_by(risk_level='high', control_status='monitored').all()
    mid_risk = KeyPerson.query.filter_by(risk_level='medium', control_status='monitored').all()
    low_risk = KeyPerson.query.filter_by(risk_level='low', control_status='monitored').all()

    now = datetime.now()
    created = 0

    for p in high_risk:
        recent = VisitTask.query.filter_by(person_id=p.person_id).order_by(VisitTask.created_at.desc()).first()
        if not recent or (now - recent.created_at).days >= 1:
            task = VisitTask(
                person_id=p.person_id, title=f'【高风险】{p.name}日常走访',
                task_type='daily', assigned_to=None,
                assigned_by=request.current_user['user_id'],
                deadline=now + timedelta(days=1), status='pending',
            )
            db.session.add(task); created += 1

    for p in mid_risk:
        recent = VisitTask.query.filter_by(person_id=p.person_id).order_by(VisitTask.created_at.desc()).first()
        if not recent or (now - recent.created_at).days >= 7:
            task = VisitTask(
                person_id=p.person_id, title=f'【中风险】{p.name}每周走访',
                task_type='weekly', assigned_to=None,
                assigned_by=request.current_user['user_id'],
                deadline=now + timedelta(days=7), status='pending',
            )
            db.session.add(task); created += 1

    for p in low_risk:
        recent = VisitTask.query.filter_by(person_id=p.person_id).order_by(VisitTask.created_at.desc()).first()
        if not recent or (now - recent.created_at).days >= 30:
            task = VisitTask(
                person_id=p.person_id, title=f'【低风险】{p.name}月度回访',
                task_type='monthly', assigned_to=None,
                assigned_by=request.current_user['user_id'],
                deadline=now + timedelta(days=30), status='pending',
            )
            db.session.add(task); created += 1

    db.session.commit()
    log_operation('AUTO_GENERATE', 'visit_task', entity_name=f'自动生成{created}条走访任务')
    return jsonify({'code': 200, 'message': f'自动生成{created}条走访任务', 'data': {'created': created}})
