import json
import logging
from hadith_app.extensions import db
from hadith_app.models import HadithMeta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_hadith_meta(row_number):
    """
    Fetches metadata for a specific Hadith from the database.

    This function connects to the database, executes a query to fetch metadata
    for a Hadith at the specified row number, and returns the result. It ensures
    that the database connection is properly closed after the operation.

    Parameters:
    row_number (int): The row number of the Hadith metadata to fetch.

    Returns:
    result: The target hadithMeta object.

    Raises:
    Exception: If there is an error during the database query execution.

    Example:
    >>> hadith_meta = self.get_hadith_meta(5)
    >>> print(hadith_meta)
    """
    db.connect()
    try:
        result = db.execute_read_query(
            "SELECT book, chapter, hadithnumber, reference, hadith_obj FROM hadith_meta limit 1 offset ?;",
            (row_number,))
        if result:
            return bind_to_hadith_meta(result[0])
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching hadith meta: {e}")
        raise
    finally:
        db.close_connection()


def get_total_hadith_count():
    """
    Executes a query to count the total number of Hadith records in the database.

    This block of code connects to the database, executes a query to count the total number
    of records in the 'hadith_meta' table, and returns the count. If an error occurs during
    the query execution, it logs the error and raises an exception.

    Returns:
    int: The total count of Hadith records.

    Raises:
    Exception: If there is an error during the database query execution.
    """
    db.connect()
    try:
        result = db.execute_read_query("SELECT count(*) as total_count FROM hadith_meta;")
        return result[0][0]
    except Exception as e:
        logger.error(f"Error fetching hadith count: {e}")
        raise
    finally:
        db.close_connection()


def delete_hadith_meta(book, chapter, number):
    db.connect()
    try:
        result = db.execute_modify_query("DELETE FROM hadith_meta WHERE book=? and chapter=? and hadithnumber=?;",
                                         (book, chapter, number,))
        return result
    except Exception as e:
        logger.error(f"Error deleting hadith meta : {e}")
        raise
    finally:
        db.close_connection()


def bind_to_hadith_meta(db_row_result):
    if db_row_result:
        blob_data = db_row_result[4]
        if isinstance(blob_data, bytes):
            json_blob = json.loads(blob_data.decode('utf-8'))
        else:
            json_blob = blob_data
        return HadithMeta(db_row_result[0], db_row_result[1], db_row_result[2], db_row_result[3], json_blob)
    else:
        return None
