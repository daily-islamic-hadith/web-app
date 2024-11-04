import argparse
import json
import sqlite3


def process(hadiths_json_file_path, db_url):
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
