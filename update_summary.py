import argparse
import glob
import os
import requests

WEBHOOK_URL = "https://auto.uncleben006.site/webhook/update-reviews"

def update_reviews_summary(timestamp):
    data_payload = {'timestamp': timestamp}
    response = requests.post(WEBHOOK_URL, data=data_payload)
    if response.status_code == 200:
        print(f"Updated reviews summary for timestamp {timestamp}. Response: {response.status_code}")
    else:
        print(f"Failed to update reviews summary for timestamp {timestamp}. Response: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update reviews summary by timestamp")
    parser.add_argument("timestamp", help="Timestamp to search what reviews are going to be updated")
    args = parser.parse_args()

    update_reviews_summary(args.timestamp)