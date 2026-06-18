from app.extensions import db


class PersonTrack(db.Model):
    __tablename__ = 'person_track'

    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False)
    track_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    longitude = db.Column(db.Numeric(10, 7))
    latitude = db.Column(db.Numeric(10, 7))
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='tracks')

    def to_dict(self):
        return {
            'track_id': self.track_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'track_time': self.track_time.isoformat() if self.track_time else None,
            'location': self.location,
            'longitude': float(self.longitude) if self.longitude else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'activity_type': self.activity_type,
            'description': self.description,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
