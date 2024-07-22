import argparse
import logging
import sqlite3
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_db(data_csv_file):
    # Load data from CSV file
    df = pd.read_csv(data_csv_file)
    # Create an in-memory SQLite database
    conn = sqlite3.connect('app.db')
    # Load the DataFrame into the SQLite database
    df.to_sql('hadith_meta', conn, index=False, if_exists='replace')
    close_connection(conn)
    logging.info("Loading DB is Done")

def close_connection(conn):
    if conn:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load CSV hadith data file into local sqlite db")
    parser.add_argument('input_file', help="Path to the input data csv file")
    args = parser.parse_args()
    load_db(args.input_file)
