from app.extensions import db


class PersonCase(db.Model):
    __tablename__ = 'person_case'

    case_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id'), nullable=False)
    case_number = db.Column(db.String(100))
    case_name = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(50))
    case_date = db.Column(db.Date)
    case_status = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='cases')
    creator = db.relationship('User', backref='created_cases')

    def to_dict(self):
        return {
            'case_id': self.case_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'case_number': self.case_number,
            'case_name': self.case_name,
            'case_type': self.case_type,
            'case_date': self.case_date.isoformat() if self.case_date else None,
            'case_status': self.case_status,
            'description': self.description,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
