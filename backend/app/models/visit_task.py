from app.extensions import db


class VisitTask(db.Model):
    __tablename__ = 'visit_task'

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(30), default='routine')
    assigned_to = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    assigned_by = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    assign_time = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='visit_tasks')
    assignee = db.relationship('User', backref='assigned_tasks', foreign_keys=[assigned_to])
    assigner = db.relationship('User', backref='created_tasks', foreign_keys=[assigned_by])

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'assigned_to': self.assigned_to,
            'assignee_name': self.assignee.real_name if self.assignee else None,
            'assigned_by': self.assigned_by,
            'assigner_name': self.assigner.real_name if self.assigner else None,
            'assign_time': self.assign_time.isoformat() if self.assign_time else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
