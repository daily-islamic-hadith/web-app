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
CACHED_HADITH_META = {}


def get_today_hadith():
    """
    Fetch today's hadith.

    This function retrieves the hadith for today's date. It first checks if the metadata for today's
    hadith is cached. If not, it calculates the hadith row number based on today's date and fetches
    the metadata from the database. The metadata is then cached for future use. Finally, it fetches
    the hadith content using the metadata.

    Returns:
        dict or None: A dictionary containing the hadith content if found, otherwise None.
    """
    today = datetime.today().date()
    hadith_meta = CACHED_HADITH_META.get(today)
    if hadith_meta is None:
        hadith_row_number = get_hadith_number(today)
        hadith_meta = fetch_hadith_meta(hadith_row_number)
        CACHED_HADITH_META[today] = hadith_meta
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
        if result:
            return {
                'Book': result[0][0],
                'Chapter': result[0][1],
                'HadithNumber': result[0][2]
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching hadith metadata: {e}")
        raise


def get_hadith_number(target_date):
    """
    Calculate the hadith number for the input date with respect to the start date.

    This function calculates the number of days passed since the START_DATE and returns it as
    the hadith number for today after making sure it is less than the total number of hadiths.

    Returns:
        int: The number of days passed since the START_DATE.

    Raises:
        Exception: If there is an error in calculating the hadith number.
    """
    try:
        start_date = datetime.strptime(START_DATE, '%Y-%m-%d').date()
        days_passed = (target_date - start_date).days
        db = current_app.config['DB']
        hadith_number = days_passed % db.get_total_hadith_count()
        return hadith_number
    except Exception as e:
        logger.error(f"Error calculating hadith number for date {target_date}: {e}")
        raise
