from flask import Flask

from hadith_app.extensions import jwt, principals
from hadith_app.auth.config import Config
from hadith_app.extensions import bcrypt

app = Flask(__name__)

app.config.from_object(Config)

# register blueprints
from hadith_app.auth import auth_bp

# init extensions
bcrypt.init_app(app)
jwt.init_app(app)
principals.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')

from hadith_app.routes import user_routes
