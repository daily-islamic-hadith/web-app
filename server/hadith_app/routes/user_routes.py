from flask import jsonify, request, send_from_directory
from flask_cors import cross_origin
from hadith_app import app
from hadith_app.language import is_supported_lang
from hadith_app.service.hadith_service import get_hadith_by_mode, get_hadith_by_reference
from hadith_app.models import HadithFetchMode
from hadith_app.routes.helper.response_helper import get_template_response, handle_fetch_hadith_success, handle_fetch_hadith_error
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
    result = _try_get_hadith(HadithFetchMode.DAILY, None)
    return get_template_response(request, result, True)

@app.route('/hadith/<hadith_reference>')
def hadith(hadith_reference):
    try:
        hadith_by_reference = get_hadith_by_reference(hadith_reference)
        result = handle_fetch_hadith_success(hadith_by_reference)
    except Exception as e:
        result = handle_fetch_hadith_error(e)
    return get_template_response(request, result, False)


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
        return jsonify(result.get('hadith'))
    else:
        return jsonify(error=result.get('error')), result.get('status_code')


@app.route('/api/random-hadith')
@cross_origin()
def get_random_hadith():
    result = _try_get_hadith(HadithFetchMode.RANDOM)
    if result.get('hadith') is not None:
        return jsonify(result.get('hadith'))
    else:
        return jsonify(error=result.get('error')), result.get('status_code')


@app.route('/api/fetch-hadith')
@cross_origin()
def fetch_hadith():
    fetch_mode_param = request.args.get('fetch-mode')  # mandatory
    lang_param = request.args.get("lang")  # optional
    lang_param = lang_param.lower() if lang_param else None
    if lang_param and not is_supported_lang(lang_param.lower()):
        return jsonify(error='provided lang is not supported'), 400
    if not fetch_mode_param:
        return jsonify(error='fetch-mode param is missing'), 400
    try:
        hadith_fetch_mode = HadithFetchMode(fetch_mode_param.lower())
    except ValueError:
        logger.error(f"Invalid fetch mode {repr(fetch_mode_param)[:10]}")
        return jsonify(error='Invalid request fields'), 400
    result = _try_get_hadith(hadith_fetch_mode, lang_param)
    if result.get('hadith') is not None:
        return jsonify(result.get('hadith'))
    else:
        return jsonify(error=result.get('error')), result.get('status_code')


def _try_get_hadith(hadith_fetch_mode, lang_code: str | None):
    """
    Helper function to fetch a hadith based on the specified mode and language.

    This function attempts to fetch a hadith using the get_hadith_by_mode() function with the provided
    fetch mode and language code. If successful, it processes the result through _handle_fetch_hadith_success().
    If an error occurs, it processes the error through _handle_fetch_hadith_error().

    Args:
        hadith_fetch_mode (HadithFetchMode): The mode to use when fetching the hadith (DAILY or RANDOM).
        lang_code (str | None): Optional language code for the hadith translation.

    Returns:
        dict: A dictionary containing either the hadith data and status code on success,
              or an error message and status code on failure.
    """
    try:
        hadith = get_hadith_by_mode(hadith_fetch_mode, lang_code)
        return handle_fetch_hadith_success(hadith)
    except Exception as e:
        return handle_fetch_hadith_error(e)