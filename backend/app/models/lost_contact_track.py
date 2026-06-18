from app.extensions import db


class LostContactTrack(db.Model):
    __tablename__ = 'lost_contact_track'

    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id', ondelete='CASCADE'), nullable=False)
    lost_time = db.Column(db.DateTime)
    last_location = db.Column(db.String(255))
    search_measures = db.Column(db.Text)
    family_contact = db.Column(db.Text)
    progress = db.Column(db.Text)
    status = db.Column(db.String(20), default='tracking')
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='lost_contact_tracks')

    def to_dict(self):
        return {
            'track_id': self.track_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'lost_time': self.lost_time.isoformat() if self.lost_time else None,
            'last_location': self.last_location,
            'search_measures': self.search_measures,
            'family_contact': self.family_contact,
            'progress': self.progress,
            'status': self.status,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
