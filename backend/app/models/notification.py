from app.extensions import db


class Notification(db.Model):
    __tablename__ = 'notification'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    notification_type = db.Column(db.String(30), default='system')
    sender_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    entity_type = db.Column(db.String(30))
    entity_id = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    sender = db.relationship('User', backref='sent_notifications', foreign_keys=[sender_id])
    receiver = db.relationship('User', backref='received_notifications', foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'title': self.title,
            'content': self.content,
            'notification_type': self.notification_type,
            'sender_id': self.sender_id,
            'sender_name': self.sender.real_name if self.sender else None,
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver.real_name if self.receiver else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'is_read': bool(self.is_read) if self.is_read is not None else False,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
