import os
import psycopg2
import sqlite3
import logging

# Define a constant for the database url
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db/app.db')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    A class to manage database connections and operations for the Hadith application.
    """

    def __init__(self):
        self.conn = None
        if 'sqlite' in DATABASE_URL:
            self.PLACEHOLDER = '?'
        elif 'postgres' in DATABASE_URL:
            self.PLACEHOLDER = '%s'

    def get_hadith_meta(self, row_number):
        """
        Fetches metadata for a specific Hadith from the database.

        This function connects to the database, executes a query to fetch metadata
        for a Hadith at the specified row number, and returns the result. It ensures
        that the database connection is properly closed after the operation.

        Parameters:
        row_number (int): The row number of the Hadith metadata to fetch.

        Returns:
        result: The metadata of the Hadith at the specified row number.

        Raises:
        Exception: If there is an error during the database query execution.

        Example:
        >>> hadith_meta = self.get_hadith_meta(5)
        >>> print(hadith_meta)
        """
        self.connect()
        try:
            result = self.execute_query("SELECT * FROM hadith_meta limit 1 offset ?;", (row_number,))
            return result
        except Exception as e:
            logger.error(f"Error fetching hadith meta: {e}")
            raise
        finally:
            self.close_connection()

    def get_total_hadith_count(self):
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
        self.connect()
        try:
            result = self.execute_query("SELECT count(*) as total_count FROM hadith_meta;")
            return result[0][0]
        except Exception as e:
            logger.error(f"Error fetching hadith count: {e}")
            raise
        finally:
            self.close_connection()

    def execute_query(self, query, params=()):
        adapted_query = query.replace("?", self.PLACEHOLDER)
        cursor = self.conn.cursor()
        cursor.execute(adapted_query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def connect(self):
        # Establish a database connection using the appropriate library
        try:
            if 'sqlite' in DATABASE_URL:
                self.conn = sqlite3.connect(DATABASE_URL.replace('sqlite:///', ''))
                self.PLACEHOLDER = "?"
            elif 'postgres' in DATABASE_URL:
                self.conn = psycopg2.connect(DATABASE_URL)
                self.PLACEHOLDER = "%s"
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close_connection(self):
        """
        Close the database connection.

        This method closes the database connection if it exists. If an error occurs while closing
        the connection, it logs the error. Finally, it sets the connection attribute to None.

        Raises:
            Exception: If there is an error closing the database connection.
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self.conn = None
