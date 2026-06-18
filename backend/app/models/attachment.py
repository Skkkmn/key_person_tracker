from app.extensions import db


class Attachment(db.Model):
    __tablename__ = 'attachment'

    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entity_type = db.Column(db.String(30), nullable=False)
    entity_id = db.Column(db.Integer)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'attachment_id': self.attachment_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
