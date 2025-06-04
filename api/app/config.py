from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    JWT_TOKEN_LOCATION = ['headers']  # Assurez-vous que les tokens sont envoyés dans les en-têtes
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    PASSWORD_PEPPER = os.getenv('PASSWORD_PEPPER') or 'ultra-secret-pepper'
class ConfigEnv:
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    ANGULAR_URL = os.getenv('ANGULAR_URL')
    FLASK_ENV = os.getenv('FLASK_ENV')