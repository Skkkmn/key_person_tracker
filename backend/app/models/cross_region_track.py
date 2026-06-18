from datetime import datetime
from app.extensions import db


class CrossRegionTrack(db.Model):
    __tablename__ = 'cross_region_track'

    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    from_dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'))
    to_dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'))
    detected_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    detected_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    notify_dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'))
    notified = db.Column(db.Boolean, default=False)
    notified_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='cross_region_tracks')
    from_dept = db.relationship('Department', foreign_keys=[from_dept_id])
    to_dept = db.relationship('Department', foreign_keys=[to_dept_id])
    detector = db.relationship('User', foreign_keys=[detected_by])

    def to_dict(self):
        return {
            'track_id': self.track_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'id_card': self.person.id_card if self.person else None,
            'direction': self.direction,
            'from_dept_id': self.from_dept_id,
            'from_dept_name': self.from_dept.dept_name if self.from_dept else None,
            'to_dept_id': self.to_dept_id,
            'to_dept_name': self.to_dept.dept_name if self.to_dept else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'detected_by': self.detected_by,
            'detector_name': self.detector.real_name if self.detector else None,
            'notify_dept_id': self.notify_dept_id,
            'notify_dept_name': self.notify_dept.dept_name if self.notify_dept and hasattr(self.notify_dept, 'dept_name') else None,
            'notified': self.notified,
            'notified_at': self.notified_at.isoformat() if self.notified_at else None,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
