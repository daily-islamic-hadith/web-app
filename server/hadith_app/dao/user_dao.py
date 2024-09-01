import logging
from hadith_app.extensions import db
from hadith_app.models import User

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_by_username(username):
    db.connect()
    try:
        result = db.execute_read_query("SELECT * FROM user where username=?;", (username,))
        if result:
            return bind_to_user(result[0])
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching user by name: {e}")
        raise
    finally:
        db.close_connection()


def bind_to_user(db_row_result):
    if db_row_result:
        return User(db_row_result[0], db_row_result[1], db_row_result[2],
                    db_row_result[3].split(','))
    else:
        return None
