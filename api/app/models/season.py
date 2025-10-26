from app.extensions import db

class Season(db.Model):
    __tablename__ = 'seasons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ✅ UUID
    season = db.Column(db.Integer, nullable=False)
    start = db.Column(db.BigInteger, nullable=False)
    end = db.Column(db.BigInteger, nullable=False)

    current = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Season {self.season} ({self.start} - {self.end})>"
    
    def json(self):
        return {
            'id': self.id,
            'season': self.season,
            'start': self.start,
            'end': self.end,
            'current': self.current
        }