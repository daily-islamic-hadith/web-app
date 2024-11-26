from datetime import datetime
from dataclasses import dataclass
from random import randint
from typing import Optional

from hadith_app.dao import hadith_dao
from hadith_app.service import explanation_store
from hadith_app.language import AR, EN
from hadith_app.models import HadithFetchMode, HadithMeta
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment variables or default values
START_DATE = os.getenv('START_DATE', '2024-07-12')
# TODO replace with cache package.
CACHED_HADITH_META = {}
CACHED_HADITH_DATA_SET_SIZE = -1


@dataclass
class HadithDto:
    reference: str
    hadithArabic: str
    hadithEnglish: str
    bookName: Optional[str] = None
    bookWriterName: Optional[str] = None
    hadithExplanationArabic: Optional[str] = None
    hadithExplanationEnglish: Optional[str] = None


def get_hadith_by_mode(hadith_fetch_mode, hadith_lang_code: str|None):
    match hadith_fetch_mode:
        case HadithFetchMode.DAILY:
            return get_today_hadith(hadith_lang_code)
        case HadithFetchMode.RANDOM:
            return get_random_hadith(hadith_lang_code)
        case _:
            logger.error(f"Invalid fetch mode {hadith_fetch_mode}")
            return None

def get_today_hadith(hadith_lang_code):
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
    #TODO pass lang_code to be filtered on db level
    return to_dto(hadith_meta, hadith_lang_code)

def get_random_hadith(hadith_lang_code):
    hadith_row_number = get_random_hadith_number()
    hadith_meta = CACHED_HADITH_META.get(hadith_row_number)
    if hadith_meta is None:
        hadith_meta = fetch_hadith_meta(hadith_row_number)
        CACHED_HADITH_META[hadith_row_number] = hadith_meta
    return to_dto(hadith_meta, hadith_lang_code)

def delete_today_hadith():
    global CACHED_HADITH_DATA_SET_SIZE
    today = datetime.today().date()
    hadith_meta = CACHED_HADITH_META.pop(today, None)
    if hadith_meta is None:
        hadith_row_number = get_hadith_number(today)
        hadith_meta = fetch_hadith_meta(hadith_row_number)
    delete_count = hadith_dao.delete_hadith_meta(hadith_meta.reference)
    deleted = delete_count is not None and delete_count > 0
    if deleted:
        CACHED_HADITH_DATA_SET_SIZE = -1
    return deleted


def generate_new_hadith_explanation(hadith_reference: str):
    hadith_content = fetch_hadith_content(hadith_reference, AR)
    explanation = explanation_store.fetch_hadith_explanation(hadith_content)
    if explanation is None:
        return None
    generated = hadith_dao.update_hadith_explanation(hadith_reference, explanation.get(AR), explanation.get(EN))
    if generated:
        remove_cached_hadith_by_reference(hadith_reference)
    return generated


def fetch_hadith_content(hadith_reference: str, hadith_lang_code: str):
    try:
        hadith_json = hadith_dao.get_hadith_content(hadith_reference)
        if hadith_json is None:
            return None
        return hadith_json.get('hadithArabic') if AR == hadith_lang_code else hadith_json.get('hadithEnglish')
    except Exception as e:
        logger.error(
            f"Error fetching hadith content for reference {hadith_reference} and language {hadith_lang_code}: {e}")
        raise

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

def get_random_hadith_number():
    try:
        return randint(0, get_total_hadith_count())
    except Exception as e:
        logger.error(f"Error calculating random hadith number: {e}")
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
        hadith_number = days_passed % get_total_hadith_count()
        return hadith_number
    except Exception as e:
        logger.error(f"Error calculating hadith number for date {target_date}: {e}")
        raise

def get_total_hadith_count():
    global CACHED_HADITH_DATA_SET_SIZE
    if CACHED_HADITH_DATA_SET_SIZE < 0:
        CACHED_HADITH_DATA_SET_SIZE = hadith_dao.get_total_hadith_count()
    return CACHED_HADITH_DATA_SET_SIZE


def remove_cached_hadith_by_reference(target_reference: str):
    """
    Remove hadith from cache by its reference

    Args:
        target_reference: Hadith reference to remove from cache
    """
    keys_to_remove = [k for k, v in CACHED_HADITH_META.items() if v.reference == target_reference]
    if keys_to_remove:
        for key in keys_to_remove:
            CACHED_HADITH_META.pop(key)


def to_dto(hadith_meta: HadithMeta, hadith_lang_code: str) -> Optional[HadithDto]:
    """
    Convert a hadithMeta object to a HadithDto object.

    Args:
        hadith_meta (HadithMeta): A HadithMeta object
        hadith_lang_code (str): Target hadith language

    Returns:
        Optional[HadithDto]: A HadithDto object if the input is not None, otherwise None.
    """
    if hadith_meta is None:
        return None
    hadith_entity = hadith_meta.hadith_json
    if hadith_entity is None:
        return None
    book = hadith_entity.get('book', {})
    return HadithDto(
        hadith_meta.reference,
        hadith_entity.get('hadithArabic') if hadith_lang_code is None or AR == hadith_lang_code else None,
        hadith_entity.get('hadithEnglish') if hadith_lang_code is None or EN == hadith_lang_code else None,
        book.get('bookName'),
        book.get('writerName'),
        hadith_meta.ar_explanation if hadith_lang_code is None or AR == hadith_lang_code else None,
        hadith_meta.en_explanation if hadith_lang_code is None or EN == hadith_lang_code else None
    )
