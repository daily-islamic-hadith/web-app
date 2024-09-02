from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from hadith_app.auth import routes
from hadith_app.auth import utils
