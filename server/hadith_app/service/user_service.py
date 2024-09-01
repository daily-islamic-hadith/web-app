from hadith_app.dao import user_dao
from hadith_app.extensions import bcrypt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: add cache per need


def fetch_user_by_username(username):
    try:
        user = user_dao.get_user_by_username(username)
        return user
    except Exception as e:
        logger.error(f"Error fetching user by username: {e}")
        raise


def validate_user_credentials(username, password):
    user = fetch_user_by_username(username)
    return user and validate_password(user.password, password)


def validate_password(encrypted_password, password):
    return bcrypt.check_password_hash(encrypted_password, password)
