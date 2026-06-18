from app.extensions import db


class PersonContact(db.Model):
    __tablename__ = 'person_contact'

    contact_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    relation = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    is_emergency = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='contacts')

    def to_dict(self):
        return {
            'contact_id': self.contact_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'name': self.name,
            'relation': self.relation,
            'phone': self.phone,
            'address': self.address,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
