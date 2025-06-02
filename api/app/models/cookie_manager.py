from app.extensions import db

class CookieManager(db.Model):
    __tablename__ = 'cookie_manager'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    value = db.Column(db.Text, nullable=False)

    def __init__(self, name, value):
        self.name = name
        self.value = value