from app.extensions import db


class Tag(db.Model):
    __tablename__ = 'tag'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(50), nullable=False, unique=True)
    tag_color = db.Column(db.String(20), default='#409eff')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'tag_name': self.tag_name,
            'tag_color': self.tag_color,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PersonTag(db.Model):
    __tablename__ = 'person_tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('key_person.person_id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('person_id', 'tag_id', name='uk_person_tag'),)
