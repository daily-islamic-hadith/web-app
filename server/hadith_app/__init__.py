from flask import Flask
from flask_cors import CORS

from hadith_app.auth import auth_bp
from hadith_app.auth.config import Config
from hadith_app.util import AppJSONProvider
from hadith_app.extensions import bcrypt
from hadith_app.extensions import jwt
from hadith_app.extensions import limiter

from hadith_app.app import register_handlers

app = Flask(__name__)

app.config.from_object(Config)
app.json = AppJSONProvider(app)
register_handlers(app)
# Include headers on errors raised before route decorators run (for example 429).
CORS(app, resources=[r"/api/.*", r"/auth/api/.*", r"/admin/api/.*"],
     allow_private_network=False)

# init extensions
bcrypt.init_app(app)
jwt.init_app(app)
limiter.init_app(app)

# register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

from hadith_app.routes import user_routes, admin_routes
