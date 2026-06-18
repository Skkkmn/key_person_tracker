from app.extensions import db


class PersonAlert(db.Model):
    __tablename__ = 'person_alert'

    alert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    alert_content = db.Column(db.Text, nullable=False)
    alert_level = db.Column(db.Enum('urgent', 'important', 'normal'), nullable=False, default='normal')
    alert_time = db.Column(db.DateTime, nullable=False)
    handler_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    handle_time = db.Column(db.DateTime)
    handle_result = db.Column(db.Text)
    verify_result = db.Column(db.Text)
    review_opinion = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    review_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('pending', 'handled', 'dismissed'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='alerts')
    handler = db.relationship('User', backref='handled_alerts', foreign_keys=[handler_id])
    reviewer = db.relationship('User', backref='reviewed_alerts', foreign_keys=[reviewer_id])

    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'alert_type': self.alert_type,
            'alert_content': self.alert_content,
            'alert_level': self.alert_level,
            'alert_time': self.alert_time.isoformat() if self.alert_time else None,
            'handler_id': self.handler_id,
            'handler_name': self.handler.real_name if self.handler else None,
            'handle_time': self.handle_time.isoformat() if self.handle_time else None,
            'handle_result': self.handle_result,
            'verify_result': self.verify_result,
            'review_opinion': self.review_opinion,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'review_time': self.review_time.isoformat() if self.review_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
