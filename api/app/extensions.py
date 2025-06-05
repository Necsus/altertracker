from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sib_api_v3_sdk.rest import ApiException
from app.config import ConfigEnv
import sib_api_v3_sdk


db = SQLAlchemy()
migrate = Migrate()
mail_conf = sib_api_v3_sdk.Configuration()
mail_conf.api_key['api-key'] = ConfigEnv.BREVO_API_KEY
mail_api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(mail_conf))
socketio = SocketIO()

limiter = Limiter(
    key_func=get_remote_address
)
if ConfigEnv.FLASK_ENV == 'production':
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=f"redis://redis:6379"
    )

