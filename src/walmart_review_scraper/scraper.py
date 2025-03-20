import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "accept": "application/json",
    "accept-language": "en-US",
    "accept-encoding": "gzip, deflate, br, zstd",
}

site_url = "https://www.walmart.com"

def extract_prod_reviews(review_url):
    response = requests.get(review_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag is None:
        return None
    
    data = json.loads(script_tag.string)
    initial_data = data["props"]["pageProps"]["initialData"]["data"]
    reviews_data = initial_data["reviews"]["customerReviews"]

    reviews = []
    for review in reviews_data:
        result = {
            "author": review["userNickname"],
            "content": review["reviewText"],
            "rating": review["rating"],
            "title": review["reviewTitle"],
            "review_date": review["reviewSubmissionTime"],
            "verified_purchase": any(badge["id"] == "VerifiedPurchaser" for badge in review["badges"]) if review["badges"] else False,
            "helpful_text": review["positiveFeedback"],
        }
        reviews.append(result)
    return reviews

    

def extract_prod_info(product_url):
    response = requests.get(product_url, headers=HEADERS)

    # use web token counter to find the value for the price or import json lib
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if script_tag is None:
        return None

    data = json.loads(script_tag.string)
    initial_data = data["props"]["pageProps"]["initialData"]["data"]
    product_data = initial_data["product"]

    return {
        "item_id": product_data["usItemId"],
        "product_name": product_data["name"],
        "base_price": product_data["priceInfo"]["wasPrice"]["price"],
        "final_price": product_data["priceInfo"]["currentPrice"]["price"],
        "availability": product_data["availabilityStatus"],
    }