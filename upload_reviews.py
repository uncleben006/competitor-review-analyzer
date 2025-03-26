import argparse
import glob
import os
import requests

WEBHOOK_URL = "https://auto.uncleben006.site/webhook/76aece3a-4f8f-4ac1-bed2-2510b3264408"

def upload_reviews(timestamp):
    files_to_upload = glob.glob(f'reviews/*/{timestamp}_*.csv')

    if not files_to_upload:
        print(f"No matching review files found for timestamp {timestamp}.")
        return

    for filepath in files_to_upload:
        ident_code = filepath.split("_")[-1].split(".")[0]
        source = filepath.split("/")[1]
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as file:
            files_payload = {'file': (filename, file, 'text/csv')}
            data_payload = {'source': source}
            response = requests.post(WEBHOOK_URL, files=files_payload, data=data_payload)
            if response.status_code == 200:
                print(f"Uploaded {filename} with source {source}. Response: {response.status_code}")
            else:
                print(f"Failed to upload {filename} with source {source}. Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload review files by timestamp")
    parser.add_argument("timestamp", help="Timestamp of review CSV files to upload")
    args = parser.parse_args()

    upload_reviews(args.timestamp)