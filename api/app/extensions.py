from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sib_api_v3_sdk.rest import ApiException
from app.config import ConfigEnv
import sib_api_v3_sdk
from redis import Redis


db = SQLAlchemy()
migrate = Migrate()
mail_conf = sib_api_v3_sdk.Configuration()
mail_conf.api_key['api-key'] = ConfigEnv.BREVO_API_KEY
mail_api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(mail_conf))
socketio = SocketIO()
# Configuration de Redis pour l'environnement de production
redis_url = 'redis' if ConfigEnv.FLASK_ENV == 'production' else '127.0.0.1'
redis_client = Redis(host=redis_url, port=6379)  # Assurez-vous que l'hôte et le port correspondent à votre configuration Docker
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{redis_url}:6379"  # URI pour Redis
)
