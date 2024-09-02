import logging
from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError

from hadith_app.extensions import jwt
from hadith_app.service import user_service

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@jwt.user_identity_loader
def user_identity_lookup(identity):
    return identity['username']


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = user_service.fetch_user_by_username(identity)
    return user


@jwt.expired_token_loader
def user_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "msg": "The token has expired, please get a new token",
        "error": "token_expired"
    }), 401


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                jwt_details = get_jwt()
                username = jwt_details.get('sub')
                user = user_service.fetch_user_by_username(username)
                if role in user.roles:
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg="Insufficient permissions"), 403
            except NoAuthorizationError:
                return jsonify(msg="Unauthorized"), 401
            except ExpiredSignatureError as e:
                raise e
            except Exception as e:
                logger.error("Exception happened", e)
                return jsonify(msg="Unauthorized"), 401

        return wrapper

    return decorator
