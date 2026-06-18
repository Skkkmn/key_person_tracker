from flask import Blueprint, request, jsonify
from app.models.operation_log import OperationLog
from app.api.auth import login_required, admin_required

log_bp = Blueprint('operation_log', __name__)


@log_bp.route('', methods=['GET'])
@login_required
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action = request.args.get('action', '')
    entity_type = request.args.get('entity_type', '')
    username = request.args.get('username', '')
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')

    query = OperationLog.query

    if action:
        query = query.filter_by(action=action)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if username:
        query = query.filter(OperationLog.username.like(f'%{username}%'))
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)

    query = query.order_by(OperationLog.log_id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [l.to_dict() for l in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }
    })
