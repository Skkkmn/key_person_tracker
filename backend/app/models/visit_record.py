from app.extensions import db


class VisitRecord(db.Model):
    __tablename__ = 'visit_record'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('visit_task.task_id', ondelete='SET NULL'))
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id', ondelete='CASCADE'), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    visit_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    longitude = db.Column(db.Numeric(10, 7))
    latitude = db.Column(db.Numeric(10, 7))
    content = db.Column(db.Text)
    performance = db.Column(db.String(50))
    thought_dynamics = db.Column(db.Text)
    life_difficulty = db.Column(db.Text)
    has_abnormality = db.Column(db.Boolean, default=False)
    abnormality_desc = db.Column(db.Text)
    photo_urls = db.Column(db.JSON)
    audio_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    task = db.relationship('VisitTask', backref='visit_records')
    person = db.relationship('KeyPerson', backref='visit_records')
    visitor = db.relationship('User', backref='visit_records')

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'task_id': self.task_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'visitor_id': self.visitor_id,
            'visitor_name': self.visitor.real_name if self.visitor else None,
            'visit_time': self.visit_time.isoformat() if self.visit_time else None,
            'location': self.location,
            'longitude': float(self.longitude) if self.longitude else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'content': self.content,
            'performance': self.performance,
            'thought_dynamics': self.thought_dynamics,
            'life_difficulty': self.life_difficulty,
            'has_abnormality': bool(self.has_abnormality) if self.has_abnormality is not None else False,
            'abnormality_desc': self.abnormality_desc,
            'photo_urls': self.photo_urls,
            'audio_url': self.audio_url,
            'video_url': self.video_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
