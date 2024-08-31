import os
import psycopg2
import sqlite3
import logging

# Define a constant for the database url
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///hadith_app/db/app.db')

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

    def execute_read_query(self, query, params=()):
        cursor = self.execute_query_and_return_cursor(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_modify_query(self, query, params=()):
        cursor = self.execute_query_and_return_cursor(query, params)
        result = cursor.rowcount
        self.conn.commit()
        cursor.close()
        return result

    def execute_query_and_return_cursor(self, query, params=()):
        adapted_query = query.replace("?", self.PLACEHOLDER)
        cursor = self.conn.cursor()
        cursor.execute(adapted_query, params)
        return cursor

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
