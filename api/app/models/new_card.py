from app.extensions import db

class NewCard(db.Model):
    __tablename__ = 'new_cards'

    reference = db.Column(db.String(200), primary_key=True, nullable=False)

    def json(self):
        return {
            'reference': self.reference
        }

    def __init__(self, reference):
        self.reference = reference