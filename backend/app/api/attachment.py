import os
from datetime import datetime

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.attachment import Attachment
from app.api.auth import login_required
from app.utils import log_operation

attach_bp = Blueprint('attachment', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'mp3', 'mp4', 'avi'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_dir():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@attach_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    ensure_upload_dir()
    entity_type = request.form.get('entity_type', '')
    entity_id = request.form.get('entity_id', type=int)

    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '文件名为空'}), 400

    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400

    original_name = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    saved_name = f'{timestamp}_{original_name}'
    date_path = datetime.now().strftime('%Y/%m')
    full_dir = os.path.join(UPLOAD_FOLDER, date_path)
    os.makedirs(full_dir, exist_ok=True)

    file_path = os.path.join(full_dir, saved_name)
    file.save(file_path)

    relative_path = os.path.join('uploads', date_path, saved_name).replace('\\', '/')

    att = Attachment(
        entity_type=entity_type,
        entity_id=entity_id,
        file_name=original_name,
        file_path=relative_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type,
        created_by=request.current_user['user_id'],
    )
    db.session.add(att)
    db.session.commit()

    log_operation('UPLOAD', 'attachment', att.attach_id, original_name)
    return jsonify({'code': 200, 'message': '上传成功', 'data': att.to_dict()})


@attach_bp.route('/list', methods=['GET'])
@login_required
def list_attachments():
    entity_type = request.args.get('entity_type', '')
    entity_id = request.args.get('entity_id', type=int)

    query = Attachment.query
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if entity_id:
        query = query.filter_by(entity_id=entity_id)

    attachments = query.order_by(Attachment.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [a.to_dict() for a in attachments]})


@attach_bp.route('/<int:attach_id>', methods=['DELETE'])
@login_required
def delete_attachment(attach_id):
    att = Attachment.query.get(attach_id)
    if not att:
        return jsonify({'code': 404, 'message': '附件不存在'}), 404

    full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), att.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    db.session.delete(att)
    db.session.commit()
    log_operation('DELETE', 'attachment', attach_id, att.file_name if att else '')
    return jsonify({'code': 200, 'message': '删除成功'})


@attach_bp.route('/download/<int:attach_id>', methods=['GET'])
@login_required
def download_file(attach_id):
    att = Attachment.query.get(attach_id)
    if not att:
        return jsonify({'code': 404, 'message': '附件不存在'}), 404

    full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), att.file_path)
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    return send_from_directory(directory, filename, as_attachment=True, download_name=att.file_name)
