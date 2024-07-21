import requests
import logging
import argparse

# Constants
BASE_ENDPOINT = 'https://www.hadithapi.com/api/hadiths'
PAGINATE = 1000
API_KEY = 'Replace with your actual API key'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_input_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        logging.error(f"The file {file_path} was not found.")
        return []
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}")
        return []

def parse_line(line):
    line = line.strip()
    if not line:
        return None
    
    try:
        book_name, chapter_number, hadith_status = line.split(',')
        return book_name, chapter_number, hadith_status
    except ValueError:
        logging.warning(f"Skipping invalid line: {line}")
        return None

def fetch_hadiths(book_name, chapter_number, hadith_status):
    params = {
        'book': book_name,
        'chapter': chapter_number,
        'status': hadith_status,
        'paginate': PAGINATE,
        'apiKey': API_KEY
    }
    try:
        response = requests.get(BASE_ENDPOINT, params=params)
        #logging.info(response.json())
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('hadiths', {}).get('data', [])
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []

def write_output_file(output_file_path, hadiths):
    try:
        with open(output_file_path, 'w') as file:
            for hadith in hadiths:
                book = hadith.get('bookSlug', '')
                chapter = hadith.get('chapterId', '')
                hadith_number = hadith.get('hadithNumber', '')
                file.write(f"{book},{chapter},{hadith_number}\n")
        logging.info(f"Hadiths successfully written to {output_file_path}")
    except Exception as e:
        logging.error(f"An error occurred while writing to the file: {e}")

def main(input_file_path, output_file_path):
    lines = read_input_file(input_file_path)
    all_hadiths = []

    for line in lines:
        parsed_line = parse_line(line)
        if parsed_line:
            book_name, chapter_number, hadith_status = parsed_line
            hadiths = fetch_hadiths(book_name, chapter_number, hadith_status)
            logging.info(f"hadiths size is {len(hadiths)}")
            all_hadiths.extend(hadiths)
    
    write_output_file(output_file_path, all_hadiths)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and process hadiths based on input file.")
    parser.add_argument('input_file', help="Path to the input file")
    parser.add_argument('output_file', help="Path to the output file")
    
    args = parser.parse_args()
    
    main(args.input_file, args.output_file)
