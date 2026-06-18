from app.extensions import db


class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessment'

    assessment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id', ondelete='CASCADE'), nullable=False)
    assessor_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id', ondelete='SET NULL'))
    previous_risk_level = db.Column(db.String(10))
    new_risk_level = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Integer, default=0)
    score_details = db.Column(db.JSON)
    reason = db.Column(db.Text)
    is_auto = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    person = db.relationship('KeyPerson', backref='risk_assessments')
    assessor = db.relationship('User', backref='risk_assessments')

    def to_dict(self):
        return {
            'assessment_id': self.assessment_id,
            'person_id': self.person_id,
            'person_name': self.person.name if self.person else None,
            'assessor_id': self.assessor_id,
            'assessor_name': self.assessor.real_name if self.assessor else None,
            'previous_risk_level': self.previous_risk_level,
            'new_risk_level': self.new_risk_level,
            'score': self.score,
            'score_details': self.score_details,
            'reason': self.reason,
            'is_auto': bool(self.is_auto) if self.is_auto is not None else False,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
