import requests
import logging
import os

# Constants
API_URL = os.getenv('HADITH_API_URL', 'client-url')
API_KEY = os.getenv('HADITH_API_KEY', 'your-api-key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_hadith(book_name, chapter_number, hadith_number):
    """
    Fetch a hadith from the Hadith API.

    Parameters:
    - book_name (str): The name of the book.
    - chapter_number (int): The chapter number.
    - hadith_number (int): The hadith number.

    Returns:
    - dict: The hadith data if found, otherwise None.
    """
    params = {
        'book': book_name,
        'chapter': chapter_number,
        'hadithNumber': hadith_number,
        'apiKey': API_KEY
    }
    try:
        logger.info(f"Fetching hadith: book={book_name}, chapter={chapter_number}, hadith={hadith_number}")
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        hadith_data = response.json()

        # Validate response structure
        if 'hadiths' in hadith_data and 'data' in hadith_data['hadiths']:
            return hadith_data['hadiths']['data'][0] if hadith_data['hadiths']['data'] else {}
        else:
            logger.error("Unexpected response structure: %s", hadith_data)
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing response: {e}")
        return None
