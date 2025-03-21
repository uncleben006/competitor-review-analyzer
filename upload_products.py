import argparse
import glob
import os
import pandas as pd
import requests

WEBHOOK_URL = "https://auto.uncleben006.site/webhook/f69a9e9b-db3b-47ad-a63f-3a37442a3f86"

def post_to_webhook(data):
    response = requests.post(WEBHOOK_URL, json=data)
    print(f"Posted {data['id']} - Status Code: {response.status_code}")

def process_csv_files(timestamp):
    csv_files = glob.glob(f'products/*/{timestamp}_*.csv')
    
    if not csv_files:
        print("No matching files found.")
        return
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        ident_code = csv_file.split("_")[-1].split(".")[0]
        source = csv_file.split("/")[1]
        
        for _, row in df.iterrows():
            payload = {
                "source": source,
                "id": f"{timestamp}_{ident_code}",
                "timestamp": timestamp,
                "product ident code": ident_code,
                "product name": row.get("name"),
                "base price": row.get("base_price"),
                "final price": row.get("final_price"),
                "inventory status": row.get("inventory_status"),
            }
        # print(payload)
        post_to_webhook(payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload products by timestamp")
    parser.add_argument("timestamp", help="Timestamp of CSV files to upload")
    args = parser.parse_args()
    
    process_csv_files(args.timestamp)