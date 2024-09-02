from flask import Flask

from hadith_app.auth import auth_bp
from hadith_app.auth.config import Config
from hadith_app.extensions import bcrypt
from hadith_app.extensions import jwt

app = Flask(__name__)

app.config.from_object(Config)

# init extensions
bcrypt.init_app(app)
jwt.init_app(app)

# register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

from hadith_app.routes import user_routes, admin_routes
