from flask_principal import identity_loaded, UserNeed, RoleNeed

from hadith_app.extensions import jwt
from hadith_app.service import user_service


@jwt.user_identity_loader
def user_identity_lookup(identity):
    return identity['username']


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = user_service.fetch_user_by_username(identity)
    return user


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    user = user_service.fetch_user_by_username(identity.id)
    identity.provides.add(UserNeed(identity.id))
    if user:
        for role in user.roles:
            identity.provides.add(RoleNeed(role))
