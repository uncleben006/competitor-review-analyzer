import argparse
import os
import csv

from bestbuy_review_scraper.scraper import extract_prod_info, extract_prod_reviews


def save_csv(data, filepath):
    # If data is a dictionary, write it as a single row CSV
    if isinstance(data, dict):
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            writer.writeheader()
            writer.writerow(data)
    # If data is a list of dictionaries, write each dictionary as a row
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
    else:
        # Fallback: write data as rows
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Bestbuy Review Scraper")
    parser.add_argument("--ident_code", required=True, help="Comma separated list of product codes")
    parser.add_argument("--timestamp", required=True, help="Timestamp string used as prefix for output files")
    args = parser.parse_args()

    timestamp = args.timestamp
    product_codes = [code.strip() for code in args.ident_code.split(",") if code.strip()]

    # Ensure output directories exist
    product_dir = os.path.join("products", "bestbuy")
    reviews_dir = os.path.join("reviews", "bestbuy")
    os.makedirs(product_dir, exist_ok=True)
    os.makedirs(reviews_dir, exist_ok=True)

    for code in product_codes:
        print(f"Processing product code: {code}")
        product_url = f"https://www.bestbuy.com/site/{code}.p"

        # Extract product information
        product_info = extract_prod_info(product_url)
        if product_info:
            product_file = os.path.join(product_dir, f"{timestamp}_bestbuy_product_{code}.csv")
            save_csv(product_info, product_file)
            print(f"Saved product info to {product_file}")
        else:
            print(f"Failed to extract product info for product code {code}")

        # Extract reviews by iterating through pages until no more reviews are found
        reviews = extract_prod_reviews(product_info["reviews_link"])

        if reviews:
            reviews_file = os.path.join(reviews_dir, f"{timestamp}_bestbuy_reviews_{code}.csv")
            save_csv(reviews, reviews_file)
            print(f"Saved reviews to {reviews_file}")
        else:
            print(f"No reviews found for product code {code}")


if __name__ == '__main__':
    main()