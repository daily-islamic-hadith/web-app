from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from hadith_app.db.db_utils import Database

bcrypt = Bcrypt()
jwt = JWTManager()
db = Database()
