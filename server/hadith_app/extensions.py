from flask_jwt_extended import JWTManager
from flask_principal import Principal
from flask_bcrypt import Bcrypt

from hadith_app.db.db_utils import Database

bcrypt = Bcrypt()
jwt = JWTManager()
principals = Principal()
db = Database()
