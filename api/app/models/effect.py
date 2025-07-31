from app.extensions import db

class Effect(db.Model):
    __tablename__ = 'effects'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(2), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('type', 'value', 'language', name='uix_type_value_language'),
    )

    def __repr__(self):
        return f"<EffectFR {self.type}: {self.value}>"

    def json(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'language': self.language
        }