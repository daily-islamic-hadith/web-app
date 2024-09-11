from flask import jsonify, render_template
from flask_cors import cross_origin
from hadith_app import app
from hadith_app.service.hadith_service import get_today_hadith
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """
       Route for the index page.

       This function handles the rendering of the index page, which displays today's hadith.

       Returns:
           str: Rendered HTML template for the index page.

       Raises:
           ValueError: If there is an error with the provided data.
           KeyError: If the required data is not found.
           Exception: If there is an internal server error.

       Note:
           If an error occurs, the function will render the index template with an error message.
    """
    try:
        today_hadith = get_today_hadith()
        if today_hadith is None:
            error_message = "Hadith not found"
            status_code = 404
        else:
            return render_template("index.html", today_hadith=today_hadith)
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        error_message = "Something went wrong"
        status_code = 400
    except KeyError as ke:
        logger.error(f"Key error: {ke}")
        error_message = "Hadith not found"
        status_code = 404
    except Exception as e:
        logger.error(f"Error fetching today's hadith: {e}")
        error_message = "Something went wrong. Please try again later."
        status_code = 500
    return render_template("index.html", error=error_message), status_code


# TODO to be moved
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
