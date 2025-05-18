from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.config import ConfigEnv


db = SQLAlchemy()
migrate = Migrate()
mail_conf = sib_api_v3_sdk.Configuration()
mail_conf.api_key['api-key'] = ConfigEnv.BREVO_API_KEY
mail_api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(mail_conf))
