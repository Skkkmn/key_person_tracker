import uuid
from datetime import datetime

from app.extensions import db


class TrackingDevice(db.Model):
    __tablename__ = 'tracking_device'

    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False, unique=True)
    device_name = db.Column(db.String(100))
    device_imei = db.Column(db.String(50), unique=True)
    phone_number = db.Column(db.String(20))
    api_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    last_latitude = db.Column(db.Numeric(10, 7))
    last_longitude = db.Column(db.Numeric(10, 7))
    last_battery_level = db.Column(db.Integer)
    last_online_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    bound_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    bound_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='tracking_device', uselist=False)
    binder = db.relationship('User', backref='bound_devices', foreign_keys=[bound_by])

    def to_dict(self):
        return {
            'device_id': self.device_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'device_name': self.device_name,
            'device_imei': self.device_imei,
            'phone_number': self.phone_number,
            'last_latitude': float(self.last_latitude) if self.last_latitude else None,
            'last_longitude': float(self.last_longitude) if self.last_longitude else None,
            'last_battery_level': self.last_battery_level,
            'last_online_at': self.last_online_at.isoformat() if self.last_online_at else None,
            'is_active': self.is_active,
            'bound_by': self.bound_by,
            'bound_at': self.bound_at.isoformat() if self.bound_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def to_public_dict(self):
        return {
            'person_id': self.person_id,
            'device_name': self.device_name,
            'last_latitude': float(self.last_latitude) if self.last_latitude else None,
            'last_longitude': float(self.last_longitude) if self.last_longitude else None,
            'last_battery_level': self.last_battery_level,
            'last_online_at': self.last_online_at.isoformat() if self.last_online_at else None,
        }
