from app.extensions import db


class KeyPerson(db.Model):
    __tablename__ = 'key_person'

    person_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('M', 'F'))
    id_card = db.Column(db.String(18), nullable=False, unique=True)
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    current_address = db.Column(db.String(255))
    photo_url = db.Column(db.String(255))
    education = db.Column(db.String(50))
    employment_status = db.Column(db.String(50))
    employer = db.Column(db.String(200))
    political_status = db.Column(db.String(20))
    ethnicity = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    household_type = db.Column(db.String(20))
    category_id = db.Column(db.Integer, db.ForeignKey('person_category.category_id'))
    risk_level = db.Column(db.String(10), nullable=False, default='medium')
    department_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'))
    control_status = db.Column(db.String(20), nullable=False, default='monitored')
    case_description = db.Column(db.Text)
    category_ext_fields = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())
    archived_at = db.Column(db.DateTime)
    archived_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'))
    archive_reason = db.Column(db.Text)
    lost_at = db.Column(db.DateTime)
    lost_info = db.Column(db.Text)

    category = db.relationship('PersonCategory', backref='persons')
    department = db.relationship('Department', backref='persons')
    creator = db.relationship('User', backref='created_persons', foreign_keys=[created_by])
    archiver = db.relationship('User', backref='archived_persons', foreign_keys=[archived_by])
    tags = db.relationship('Tag', secondary='person_tag', lazy='subquery',
                           backref=db.backref('persons', lazy='dynamic'))

    def to_dict(self):
        return {
            'person_id': self.person_id,
            'name': self.name,
            'gender': self.gender,
            'id_card': self.id_card,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'phone': self.phone,
            'address': self.address,
            'current_address': self.current_address,
            'photo_url': self.photo_url,
            'education': self.education,
            'employment_status': self.employment_status,
            'employer': self.employer,
            'political_status': self.political_status,
            'ethnicity': self.ethnicity,
            'marital_status': self.marital_status,
            'household_type': self.household_type,
            'category_id': self.category_id,
            'category_name': self.category.category_name if self.category else None,
            'risk_level': self.risk_level,
            'department_id': self.department_id,
            'department_name': self.department.dept_name if self.department else None,
            'control_status': self.control_status,
            'case_description': self.case_description,
            'category_ext_fields': self.category_ext_fields,
            'tags': [t.to_dict() for t in self.tags] if self.tags else [],
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'archived_by': self.archived_by,
            'archiver_name': self.archiver.real_name if self.archiver else None,
            'archive_reason': self.archive_reason,
            'lost_at': self.lost_at.isoformat() if self.lost_at else None,
            'lost_info': self.lost_info,
        }
