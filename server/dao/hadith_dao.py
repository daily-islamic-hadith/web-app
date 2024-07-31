import sqlite3
import pandas as pd
import logging

# Define a constant for the database file path
DATABASE_FILE_PATH = 'db/app.db'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    A class to manage database connections and operations for the Hadith application.
    """

    def __init__(self):
        """
        Initialize the Database instance.

        This constructor initializes the Database instance with a connection attribute set to None.
        """
        self.conn = None

    def connect(self):
        """
        Establish a connection to the SQLite database.

        This method establishes a connection to the SQLite database specified by DATABASE_FILE_PATH.
        If a connection already exists, it does nothing. If an error occurs while connecting, it logs
        the error and raises an exception.

        Raises:
            sqlite3.Error: If there is an error connecting to the database.
        """
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(DATABASE_FILE_PATH)
            except sqlite3.Error as e:
                logger.error(f"Error connecting to database: {e}")
                raise

    def get_hadith_meta(self, row_number):
        """
        Fetch the metadata for a specific hadith from the database.

        This method retrieves the metadata for the hadith corresponding to the given row number
        from the database. It returns the result as a pandas DataFrame.

        Args:
            row_number (int): The row number of the hadith to fetch metadata for.

        Returns:
            pd.DataFrame: A DataFrame containing the hadith metadata.

        Raises:
            Exception: If there is an error in fetching the hadith metadata.
        """
        self.connect()
        try:
            row_number = max(1, row_number)
            query = 'SELECT * FROM hadith_meta WHERE ROWID=?'
            df = pd.read_sql(query, self.conn, params=(row_number,))
            return df
        except Exception as e:
            logger.error(f"Error fetching hadith meta: {e}")
            raise
        finally:
            self.close_connection()

    def get_total_hadith_count(self):
        self.connect()
        try:
            query = 'SELECT count(*) as total_count FROM hadith_meta;'
            df = pd.read_sql(query, self.conn)
            return int(df['total_count'][0])
        except Exception as e:
            logger.error(f"Error fetching hadith count: {e}")
            raise
        finally:
            self.close_connection()

    def close_connection(self):
        """
        Close the database connection.

        This method closes the database connection if it exists. If an error occurs while closing
        the connection, it logs the error. Finally, it sets the connection attribute to None.

        Raises:
            sqlite3.Error: If there is an error closing the database connection.
        """
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self.conn = None
