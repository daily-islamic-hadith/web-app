from datetime import datetime
from hadith_app.client.hadith_api_client import fetch_hadith
from hadith_app.dao import hadith_dao
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
        return fetch_hadith(hadith_meta.book, hadith_meta.chapter, hadith_meta.number)
    else:
        return None


def delete_today_hadith():
    today = datetime.today().date()
    hadith_meta = CACHED_HADITH_META.pop(today, None)
    if hadith_meta is None:
        hadith_row_number = get_hadith_number(today)
        hadith_meta = fetch_hadith_meta(hadith_row_number)
    delete_count = hadith_dao.delete_hadith_meta(hadith_meta['Book'], hadith_meta['Chapter'],
                                                 hadith_meta['HadithNumber'])
    return delete_count is not None and delete_count > 0


def fetch_hadith_meta(hadith_row_number):
    """
    Fetch the metadata for a specific hadith from the database.

    This function retrieves the metadata for the hadith corresponding to the given row number
    from the database.

    Args:
        hadith_row_number (int): The row number of the hadith to fetch metadata for.

    Returns:
        model: A HadithMeta object containing the hadith metadata if found,
              otherwise None.

    Raises:
        Exception: If there is an error in fetching the hadith metadata.
    """
    try:
        return hadith_dao.get_hadith_meta(hadith_row_number)
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
        hadith_number = days_passed % hadith_dao.get_total_hadith_count()
        return hadith_number
    except Exception as e:
        logger.error(f"Error calculating hadith number for date {target_date}: {e}")
        raise
