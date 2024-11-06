import argparse
import json
import sqlite3


def process(hadiths_json_file_path, db_url):
    """
    Process hadiths from a JSON file and update them in the database.

    This function reads a JSON file containing an array of hadith objects,
    connects to a SQLite database, and updates the 'hadith_meta' table with
    the hadith data.

    Args:
        hadiths_json_file_path (str): Path to the JSON file containing hadith data.
        db_url (str): URL of the SQLite database to update.

    The function performs the following steps:
    1. Loads the JSON data from the file.
    2. Connects to the SQLite database.
    3. For each hadith object in the JSON data:
       - Converts the object to a JSON blob.
       - Updates the corresponding record in the 'hadith_meta' table.
    4. Commits the changes and closes the database connection.
    """
    # Load JSON array from file
    with open(hadiths_json_file_path, 'r') as f:
        json_data = json.load(f)  # the file contains a JSON array of hadith objects

    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    for json_obj in json_data:
        # Convert the JSON object to a binary (blob) format
        json_blob = json.dumps(json_obj).encode('utf-8')
        book = json_obj.get('bookSlug')
        chapter = json_obj.get('chapterId')
        hadith_number = json_obj.get('hadithNumber')
        cursor.execute("UPDATE hadith_meta set hadith_obj=(?) where book=? and chapter=? and hadithnumber=?",
                       (json_blob, book, chapter, hadith_number))
    # Commit and close the database connection
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update hadiths based on input file.")
    parser.add_argument('input_file', help="Path to the input file")
    parser.add_argument('database_url', help="database url")

    args = parser.parse_args()
    process(args.input_file, args.database_url)
