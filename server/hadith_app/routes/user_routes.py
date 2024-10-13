from flask import jsonify, render_template, send_from_directory
from flask_cors import cross_origin
from hadith_app import app
from hadith_app.service.hadith_service import get_hadith_by_mode
from hadith_app.models import HadithFetchMode
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """
        Attempts to fetch the hadith of the day using the helper function.

        Returns:
            dict: A dictionary containing either the hadith of the day or an error message,
                  along with the corresponding HTTP status code.
    """
    result = _try_get_hadith(HadithFetchMode.DAILY)
    if result.get('hadith') is not None:
        return render_template("index.html", hadith=result.get('hadith'))
    else:
        return render_template("index.html", error=result.get('error')), result.get('status_code')


@app.route('/privacy-policy')
def privacy():
    return send_from_directory('static', 'privacy-policy.html')


@app.route('/api/today-hadith')
@cross_origin()
def get_hadith_of_the_day():
    """
    Retrieves the hadith of the day.

    This function attempts to fetch the hadith of the day using the _try_get_hadith() helper function.
    If successful, it returns the hadith. If an error occurs, it returns a JSON response with an error message
    and the appropriate HTTP status code.

    Returns:
        dict or tuple: If successful, returns the hadith of the day as a dictionary.
                       If an error occurs, returns a tuple containing a JSON response with an error message
                       and the corresponding HTTP status code.
    """
    result = _try_get_hadith(HadithFetchMode.DAILY)
    if result.get('hadith') is not None:
        return result.get('hadith')
    else:
        return jsonify(error=result.get('error')), result.get('status_code')


@app.route('/api/random-hadith')
@cross_origin()
def get_random_hadith():
    result = _try_get_hadith(HadithFetchMode.RANDOM)
    if result.get('hadith') is not None:
        return result.get('hadith')
    else:
        return jsonify(error=result.get('error')), result.get('status_code')



def _try_get_hadith(hadith_fetch_mode):
    """
    Attempts to fetch the hadith given the input fetch mode.

    This function wraps the `get_hadith_by_mode()` call with error handling.
    It catches various exceptions that might occur during the process and
    returns appropriate error messages and status codes.

    Returns:
        dict: A dictionary containing either the hadith of the day or an error message,
              along with the corresponding HTTP status code.
    """
    try:
        hadith = get_hadith_by_mode(hadith_fetch_mode)
        if hadith is not None:
            return {"hadith": hadith, "status_code": 200}
        return {"error": "Hadith not found", "status_code": 404}
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        error_message = "Something went wrong"
        status_code = 400
    except KeyError as ke:
        logger.error(f"Key error: {ke}")
        error_message = "Hadith not found"
        status_code = 404
    except Exception as e:
        logger.error(f"Error fetching hadith by mode {hadith_fetch_mode}: {e}")
        error_message = "Something went wrong. Please try again later."
        status_code = 500
    return {"error": error_message, "status_code": status_code}
