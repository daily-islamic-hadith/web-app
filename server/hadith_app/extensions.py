from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from hadith_app.db.db_utils import Database
import os

bcrypt = Bcrypt()
jwt = JWTManager()
os.getenv('DEFAULT_RATE_LIMIT', '100 per hour')
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[os.getenv('DEFAULT_RATE_LIMIT', '10 per minute')])
db = Database()
