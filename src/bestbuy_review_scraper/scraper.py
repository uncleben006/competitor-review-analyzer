import browsercookie
import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "accept": "application/json",
    "accept-language": "en-US",
    "accept-encoding": "gzip, deflate, br, zstd",
}

site_url = "https://www.bestbuy.com"

def extract_prod_reviews(review_url):
    # dump cookies to file
    # cj = browsercookie.chrome()
    # target_domain = "bestbuy.com"
    # cookies_dict = {cookie.name: cookie.value for cookie in cj if target_domain in cookie.domain}
    # with open('cookies.json', 'w') as f:
    #     json.dump(cookies_dict, f, indent=4)

    with open('cookies.json', 'r') as f:
        cookies_dict = json.load(f)
    response = requests.get(review_url, headers=HEADERS, cookies=cookies_dict)
    soup = BeautifulSoup(response.text, "html.parser")

    reviews_list= soup.find_all("li", class_="review-item")
    reviews = []
    for review in reviews_list:
        review_date = review.find("time", class_="submission-date").text
        review_data = review.find("script")
        review_data = json.loads(review_data.string)
        result = {
            "author": review_data["author"]["name"],
            "content": review_data["reviewBody"],
            "rating": review_data["reviewRating"]["ratingValue"],
            "title": review_data["name"],
            "review_date": review_date,
            "verified_purchase": None,
            "helpful_text": None,
        }
        reviews.append(result)
    return reviews
    

def extract_prod_info(product_url):
    # dump cookies to file
    # cj = browsercookie.chrome()
    # target_domain = "bestbuy.com"
    # cookies_dict = {cookie.name: cookie.value for cookie in cj if target_domain in cookie.domain}
    # with open('cookies.json', 'w') as f:
    #     json.dump(cookies_dict, f, indent=4)
    
    with open('cookies.json', 'r') as f:
        cookies_dict = json.load(f)
    response = requests.get(product_url, headers=HEADERS, cookies=cookies_dict)
    soup = BeautifulSoup(response.text, "html.parser")

    price_script_tag = soup.find("script", id=re.compile(r'pricing-price-\d+-json'))
    price_data = json.loads(price_script_tag.string)
    price_data = price_data["app"]
    item_id = price_data["priceDomain"]["skuId"]
    base_price = price_data["priceDomain"]["regularPrice"]
    final_price = price_data["priceDomain"]["currentPrice"]
    availability = price_data["priceDomain"]["dotComDisplayStatus"]
    product_name = soup.find("div", class_="shop-product-title").find("h1").text
    reviews_link = soup.find("div", class_="see-all-reviews-button-container").find("a")["href"]

    return {
        "ident_code": item_id,
        "name": product_name,
        "base_price": base_price,
        "final_price": final_price,
        "inventory_status": availability,
        "reviews_link": site_url + reviews_link + "&sort=MOST_RECENT",
    }

def main():
    product = extract_prod_info("https://www.bestbuy.com/site/6447382.p")
    # reviews = extract_prod_reviews(product["reviews_link"])
    print(product)
    # print(reviews)


if __name__ == '__main__':
    main()