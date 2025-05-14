from flask_bcrypt import Bcrypt
from flask import current_app
import hmac

bcrypt = Bcrypt()

def hash_password(password: str) -> str:
    pepper = current_app.config['PASSWORD_PEPPER']
    peppered = hmac.new(pepper.encode(), password.encode(), 'sha256').hexdigest()
    return bcrypt.generate_password_hash(peppered).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    pepper = current_app.config['PASSWORD_PEPPER']
    peppered = hmac.new(pepper.encode(), password.encode(), 'sha256').hexdigest()
    return bcrypt.check_password_hash(hashed, peppered)