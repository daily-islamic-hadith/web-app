from datetime import datetime
from flask import current_app
from client.hadith_api_client import fetch_hadith
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment variables or default values
START_DATE = os.getenv('START_DATE', '2024-07-12')


def get_today_hadith():
    hadith_row_number = get_today_hadith_number()
    hadith_meta = fetch_hadith_meta(hadith_row_number)
    if hadith_meta:
        return fetch_hadith(hadith_meta['Book'], hadith_meta['Chapter'], hadith_meta['HadithNumber'])
    else:
        return None


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


def get_today_hadith_number():
    """
    Calculate the hadith number for today based on the start date.

    This function calculates the number of days passed since the START_DATE and returns it as
    the hadith number for today after making sure it is less than the total number of hadiths.

    Returns:
        int: The number of days passed since the START_DATE.

    Raises:
        Exception: If there is an error in calculating the hadith number.
    """
    try:
        start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
        today = datetime.today()
        days_passed = (today - start_date).days
        db = current_app.config['DB']
        hadith_number = days_passed % db.get_total_hadith_count()
        return hadith_number
    except Exception as e:
        logger.error(f"Error calculating today's hadith number: {e}")
        raise
