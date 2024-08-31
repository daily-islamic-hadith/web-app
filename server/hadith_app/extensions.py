from flask_jwt_extended import JWTManager
from flask_principal import Principal
from flask_bcrypt import Bcrypt

from hadith_app.dao.hadith_dao import Database

bcrypt = Bcrypt()
jwt = JWTManager()
principals = Principal()
db = Database()
