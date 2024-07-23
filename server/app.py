from datetime import datetime
from flask import Flask, jsonify, current_app
from client.hadith_api_client import fetch_hadith
from dao.hadith_dao import Database
from flask_cors import cross_origin
import logging
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment variables or default values
START_DATE = os.getenv('START_DATE', '2024-07-12')


def setup_db():
    """
    Initialize the database and store the instance in the Flask app configuration.
    """
    db = Database()
    app.config['DB'] = db
    logger.info("Database setup completed.")


def get_today_hadith_number():
    """
    Calculate the hadith number for today based on the start date.

    This function calculates the number of days passed since the START_DATE and returns it as
    the hadith number for today.

    Returns:
        int: The number of days passed since the START_DATE.

    Raises:
        Exception: If there is an error in calculating the hadith number.
    """
    try:
        start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
        today = datetime.today()
        days_passed = (today - start_date).days
        return days_passed
    except Exception as e:
        logger.error(f"Error calculating today's hadith number: {e}")
        raise


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

    This route calculates the hadith number for today, fetches the corresponding hadith metadata
    from the database, and then fetches the hadith details using the hadith metadata.

    Returns:
        Response: A JSON response with the hadith details if found, otherwise an error message.

    Raises:
        ValueError: If there is an error with the provided data.
        KeyError: If the required data is not found.
        Exception: If there is an internal server error.
    """
    try:
        hadith_row_number = get_today_hadith_number()
        hadith_meta = fetch_hadith_meta(hadith_row_number)
        if hadith_meta:
            return fetch_hadith(hadith_meta['Book'], hadith_meta['Chapter'], hadith_meta['HadithNumber'])
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


def fetch_hadith_meta(hadith_row_number):
    """
    Fetch the metadata for a specific hadith from the database.

    This function retrieves the metadata for the hadith corresponding to the given row number
    from the database.

    Args:
        hadith_row_number (int): The row number of the hadith to fetch metadata for.

    Returns:
        dict: A dictionary containing the hadith metadata (Book, Chapter, HadithNumber) if found,
              otherwise None.

    Raises:
        Exception: If there is an error in fetching the hadith metadata.
    """
    try:
        db = current_app.config['DB']
        result = db.get_hadith_meta(hadith_row_number)
        if not result.empty:
            return {
                'Book': result['Book'][0],
                'Chapter': result['Chapter'][0],
                'HadithNumber': result['HadithNumber'][0]
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching hadith metadata: {e}")
        raise


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
