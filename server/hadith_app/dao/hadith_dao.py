import json
import logging
from hadith_app.extensions import db
from hadith_app.models import HadithMeta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_hadith_meta(row_number: int):
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
            "SELECT reference, hadith_obj, exp_ar, exp_en FROM hadith_meta "
            "left join hadith_explanation on hadith_meta.reference = hadith_explanation.hadith_ref "
            "limit 1 offset ?;",
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


def get_hadith_meta_by_reference(hadith_reference: str):
    """
    Executes a SQL query to fetch a Hadith's metadata and explanations by its reference.

    The query joins the hadith_meta and hadith_explanation tables to retrieve the Hadith's
    reference, object data, and both Arabic and English explanations. The join is performed
    using the reference as the matching key between tables.

    Parameters:
    hadith_reference (str): The reference identifier of the Hadith to fetch.

    Returns:
    result: The query result containing the Hadith metadata and explanations.
    """
    db.connect()
    try:
        result = db.execute_read_query(
            "SELECT reference, hadith_obj, exp_ar, exp_en FROM hadith_meta "
            "left join hadith_explanation on hadith_meta.reference = hadith_explanation.hadith_ref "
            "where reference=?;",
            (hadith_reference,))
        if result:
            return bind_to_hadith_meta(result[0])
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching hadith meta by reference: {e}")
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


def delete_hadith_meta(reference):
    db.connect()
    try:
        result = db.execute_modify_query("DELETE FROM hadith_meta WHERE reference=?;",
                                         (reference,))
        return result
    except Exception as e:
        logger.error(f"Error deleting hadith meta : {e}")
        raise
    finally:
        db.close_connection()


def get_hadith_content(hadith_reference):
    db.connect()
    try:
        result = db.execute_read_query("SELECT hadith_obj FROM hadith_meta where reference=?;", (hadith_reference,))
        if result:
            blob_data = result[0][0]
            return json.loads(blob_data.decode('utf-8')) if isinstance(blob_data, bytes) else blob_data
        else:
            logger.info(f"No hadith found for reference {hadith_reference}")
            return None
    except Exception as e:
        logger.error(f"Error getting hadith content : {e}")
        raise
    finally:
        db.close_connection()

def update_hadith_explanation(hadith_reference, explanation_ar, explanation_en):
    if explanation_ar is None or explanation_en is None or hadith_reference is None:
        return None
    db.connect()
    try:
        exp_ar_encoded = explanation_ar.encode('utf-8')
        exp_en_encoded = explanation_en.encode('utf-8')
        result = db.execute_modify_query("UPDATE hadith_explanation SET exp_ar=?, exp_en=? WHERE hadith_ref=?;",
                                         (exp_ar_encoded, exp_en_encoded, hadith_reference))
        return result
    except Exception as e:
        logger.error(f"Error updating hadith explanation : {e}")
        raise
    finally:
        db.close_connection()

def bind_to_hadith_meta(db_row_result):
    if db_row_result:
        blob_data = db_row_result[1]
        ar_explanation = db_row_result[2]
        if ar_explanation is not None:
            if isinstance(ar_explanation, memoryview):
                ar_explanation = bytes(ar_explanation)
            ar_explanation = ar_explanation.decode('utf-8')
        en_explanation = db_row_result[3]
        if en_explanation is not None:
            if isinstance(en_explanation, memoryview):
                en_explanation = bytes(en_explanation)
            en_explanation = en_explanation.decode('utf-8')
        if isinstance(blob_data, bytes):
            json_blob = json.loads(blob_data.decode('utf-8'))
        else:
            json_blob = blob_data
        return HadithMeta(db_row_result[0], json_blob, ar_explanation, en_explanation)
    else:
        return None
