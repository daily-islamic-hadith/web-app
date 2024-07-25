from flask import Flask, jsonify, current_app
from dao.hadith_dao import Database
from flask_cors import cross_origin
from service.hadith_service import get_today_hadith
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_db():
    """
    Initialize the database and store the instance in the Flask app configuration.
    """
    db = Database()
    app.config['DB'] = db
    logger.info("Database setup completed.")


@app.route('/')
def index():
    """
    Index route to check if the server is running.

    Returns:
        Response: A JSON response with a message indicating that the server is running.
    """
    return jsonify(message="Server is running!")


@app.route('/today-hadith')
@cross_origin()
def get_hadith_of_the_day():
    """
    Route to fetch today's hadith.

    Returns:
        Response: A JSON response with the hadith details if found, otherwise an error message.

    Raises:
        ValueError: If there is an error with the provided data.
        KeyError: If the required data is not found.
        Exception: If there is an internal server error.
    """
    try:
        today_hadith = get_today_hadith()
        if today_hadith is not None:
            return today_hadith
        else:
            return jsonify(error="Hadith not found"), 404
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        return jsonify(error="Invalid data provided"), 400
    except KeyError as ke:
        logger.error(f"Key error: {ke}")
        return jsonify(error="Data not found"), 404
    except Exception as e:
        logger.error(f"Error fetching today's hadith: {e}")
        return jsonify(error="Internal server error"), 500


@app.teardown_appcontext
def close_db(error):
    """
    Close the database connection at the end of the request.

    This function closes the database connection stored in the Flask app's configuration under
    the key 'DB' at the end of the request.

    Args:
        error (Exception): An optional error that occurred during the request.
    """
    db = current_app.config.get('DB')
    if db is not None:
        db.close_connection()
        logger.info("Database connection closed.")


with app.app_context():
    setup_db()

if __name__ == '__main__':
    app.run()
