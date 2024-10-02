import csv
import io
import hashlib
import json
import os
from datetime import datetime

import requests
import zipfile

from flask import Flask, send_file

app = Flask(__name__)

ZIP_URL = "https://github.com/BrainMonkey/sample-files/archive/refs/heads/main.zip"
BASE_DIR = os.path.dirname(os.getcwd())
ZIP_FILE_PATH = os.path.join(BASE_DIR, 'sample-files-main.zip')
TEXT_FILES_DIR = os.path.join(BASE_DIR, 'sample-files-main')
CSV_FILE_PATH = os.path.join(BASE_DIR, 'interview.csv')


def download_and_extract_zip():

    # Download the zip file.
    response = requests.get(ZIP_URL)
    response.raise_for_status()
    with open(ZIP_FILE_PATH, 'wb') as f:
        f.write(response.content)
    print("Downloaded zip file.")

    # Extract the txt files from zip.
    with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
        zip_ref.extractall(BASE_DIR)
        print("Extracted zip file.")

    # Clean up zip file.
    os.remove(ZIP_FILE_PATH)
    print("Removed zip file.")


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_metadata():
    download_and_extract_zip()
    metadata = []
    for file_name in os.listdir(TEXT_FILES_DIR):
        file_path = os.path.join(TEXT_FILES_DIR, file_name)
        if os.path.isfile(file_path) and file_path.endswith(".txt"):
            words = open(file_path).read().split()
            md_ = {
                "file_name": file_name,
                "sha256": calculate_sha256(file_path),
                "file_size": os.path.getsize(file_path),
                "word_count": len(words),
                "unique_word_count": len(set(words)),
                "date": datetime.now().strftime('%Y-%m-%d')
            }
            metadata.append(md_)
    return metadata


@app.route('/get-metadata-csv', methods=['GET'])
def get_metadata_csv():
    metadata = generate_metadata()
    fields = ['file_name', 'sha256', 'file_size', 'word_count', 'unique_word_count', 'date']

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(fields)
    for item in metadata:
        writer.writerow([item[field] for field in fields])
    csv_buffer.seek(0)

    return send_file(io.BytesIO(csv_buffer.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='metadata.csv')


@app.route('/get-metadata-json', methods=['GET'])
def get_metadata_json():
    metadata = generate_metadata()
    return json.dumps(metadata)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
