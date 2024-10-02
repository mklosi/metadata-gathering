import os

import requests

BASE_URL = "http://127.0.0.1:4000"
BASE_DIR = os.path.dirname(os.getcwd())
CSV_FILE_NAME = 'interview.csv'
CSV_FILE_PATH = os.path.join(BASE_DIR, CSV_FILE_NAME)


if __name__ == '__main__':

    # Hit 'get_metadata_csv' API route.
    response = requests.get(f'{BASE_URL}/get-metadata-csv')
    response.raise_for_status()
    with open(CSV_FILE_PATH, 'w') as f:
        f.write(response.text)
    print(f"CSV file written to: {CSV_FILE_PATH}")

    # Hit 'get_metadata_json' API route. The call here is disabled (commented out), since it's not part of the reqs.
    response = requests.get(f'{BASE_URL}/get-metadata-json')
    response.raise_for_status()
    print(f"text: {response.text}") # &&&
