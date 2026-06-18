from app.extensions import db


class User(db.Model):
    __tablename__ = 'sys_user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('super_admin', 'dept_admin', 'operator', 'viewer'), nullable=False, default='operator')
    department_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=True)
    phone = db.Column(db.String(20))
    status = db.Column(db.Boolean, default=True, nullable=False)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_updated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    department = db.relationship('Department', backref='users')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'department_id': self.department_id,
            'department_name': self.department.dept_name if self.department else None,
            'phone': self.phone,
            'status': self.status,
            'login_attempts': self.login_attempts or 0,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'password_updated_at': self.password_updated_at.isoformat() if self.password_updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
