from flask import request
from app.extensions import db
from app.models.operation_log import OperationLog


def log_operation(action, entity_type, entity_id=None, entity_name=None,
                  old_value=None, new_value=None):
    user = getattr(request, 'current_user', None)
    log = OperationLog(
        user_id=user.get('user_id') if user else None,
        username=user.get('username') if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.remote_addr or '',
    )
    db.session.add(log)


def get_changes(old_obj, new_data, fields):
    old_values = {}
    new_values = {}
    for f in fields:
        old_val = getattr(old_obj, f, None)
        if f in new_data:
            new_val = new_data[f]
            if old_val != new_val:
                old_values[f] = str(old_val) if old_val is not None else None
                new_values[f] = str(new_val) if new_val is not None else None
    return old_values, new_values


def mask_id_card(id_card):
    if not id_card or len(id_card) < 10:
        return id_card
    return id_card[:4] + '**********' + id_card[-4:]


def mask_phone(phone):
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + '****' + phone[-4:]
