from flask import jsonify
from flask_cors import cross_origin
from .. import app
from service.hadith_service import get_today_hadith
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
