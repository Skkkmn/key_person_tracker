from app.extensions import db


class OperationLog(db.Model):
    __tablename__ = 'operation_log'

    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    username = db.Column(db.String(50))
    action = db.Column(db.String(30), nullable=False)
    entity_type = db.Column(db.String(30), nullable=False)
    entity_id = db.Column(db.Integer)
    entity_name = db.Column(db.String(200))
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
