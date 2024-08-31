from flask import Blueprint
from flask_principal import Permission, RoleNeed

auth_bp = Blueprint('auth', __name__)

# Define roles
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))

from hadith_app.auth import routes
from hadith_app.auth import utils
