import argparse
import json
import os

from concurrent.futures import ThreadPoolExecutor
from functools import partial

from openai import OpenAI
from openai.types.shared_params.response_format_json_schema import JSONSchema
from openai.types.shared_params import ResponseFormatJSONSchema
import psycopg2

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', "your openai api key"))


def fetch_and_store_hadith_explanation(db_url, chunk_size):
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute(
        "select reference, hadith_obj from hadith_meta where reference not in ((select hadith_ref from hadith_explanation)) limit 100")
    rows = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    if rows is None or not rows:
        print("All Hadiths Have Explanations")
        exit()
    chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]
    process_in_parallel(db_url, chunks)


# Function to run in parallel
def process_in_parallel(db_url, list_of_rows):
    # Create a partial function with the fixed first parameter (db_url)
    process_with_db_url = partial(_do_process, db_url)
    with ThreadPoolExecutor() as executor:
        executor.map(process_with_db_url, list_of_rows)
    return


def _do_process(db_url, rows):
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    try:
        for row in rows:
            reference = row[0]
            blob_data = row[1]
            if isinstance(blob_data, bytes):
                blob_data = json.loads(blob_data.decode('utf-8'))
            hadith_txt = blob_data.get('hadithArabic')
            explanation = fetch_hadith_explanation(hadith_txt)
            exp_ar = explanation.get('ar').encode('utf-8')
            exp_en = explanation.get('en').encode('utf-8')
            if explanation:
                cursor.execute("insert into hadith_explanation (hadith_ref, exp_ar, exp_en) values (%s,%s,%s)",
                               (reference, exp_ar, exp_en))
            else:
                print(f"Failed to fetch explanation for {reference}")
    except Exception:
        print(f"do nothing on error {Exception}")
    cursor.close()
    conn.commit()
    conn.close()


resp_f = ResponseFormatJSONSchema(
    json_schema=JSONSchema(
        name="language_keys",
        strict=True,
        schema={
            "type": "object",
            "required": [
                "en",
                "ar"
            ],
            "properties": {
                "ar": {
                    "type": "string",
                    "description": "The value for the Arabic language key."
                },
                "en": {
                    "type": "string",
                    "description": "The value for the English language key."
                }
            },
            "additionalProperties": False
        }
    ),
    type="json_schema"
)


def fetch_hadith_explanation(hadith_txt):
    msg = '\n تفسير او شرح الحديث \n ' + hadith_txt
    ai_response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": msg
            }

        ],
        model="gpt-4o-mini",
        response_format=resp_f
    )
    if not ai_response or not ai_response.choices:
        return None
    return json.loads(ai_response.choices[0].message.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and Store Hadith explanations.")
    parser.add_argument('database_url', help="database url")
    parser.add_argument('items_per_thread', help="number of items to be processed within a single thread")

    args = parser.parse_args()
    fetch_and_store_hadith_explanation(args.database_url, args.items_per_thread)
