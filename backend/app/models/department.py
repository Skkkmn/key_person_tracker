from app.extensions import db


class Department(db.Model):
    __tablename__ = 'department'

    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept_name = db.Column(db.String(100), nullable=False)
    dept_code = db.Column(db.String(50), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=True)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    parent = db.relationship('Department', remote_side='Department.dept_id', backref='children')

    def to_dict(self):
        return {
            'dept_id': self.dept_id,
            'dept_name': self.dept_name,
            'dept_code': self.dept_code,
            'parent_id': self.parent_id,
            'parent_name': self.parent.dept_name if self.parent else None,
            'address': self.address,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
