import argparse
import glob
import os
import requests

WEBHOOK_URL = "https://auto.uncleben006.site/webhook/932aef38-4584-487b-9db6-2c39e2474434"

def update_reviews_summary(timestamp):
    data_payload = {'timestamp': timestamp}
    response = requests.post(WEBHOOK_URL, data=data_payload)
    print(f"Updated reviews summary for timestamp {timestamp}. Response: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update reviews summary by timestamp")
    parser.add_argument("timestamp", help="Timestamp to search what reviews are going to be updated")
    args = parser.parse_args()

    update_reviews_summary(args.timestamp)