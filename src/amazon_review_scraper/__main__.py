"""
    Main module for amazon_review_scraper.
"""

import logging

import click

from amazon_review_scraper.collector import AmazonReviewDataCollector


logging.basicConfig(level=logging.INFO)


@click.command()
@click.option(
    "--asin-codes",
    required=True,
    multiple=True,
    type=str,
    help="The ASIN code(s) of the product(s) for which to scrape Amazon reviews. "
         "You can pass a single code, a comma-separated list, or multiple options."
)
def scrape_amazon_reviews(asin_codes) -> None:
    # 如果只提供了一個元素，檢查是否包含逗號
    if len(asin_codes) == 1:
        if "," in asin_codes[0]:
            asin_codes = [code.strip() for code in asin_codes[0].split(",")]
        else:
            asin_codes = [asin_codes[0]]
    else:
        asin_codes = list(asin_codes)
    
    collector = AmazonReviewDataCollector()
    collector.collect_amazon_review_data(asin_codes)


if __name__ == "__main__":
    scrape_amazon_reviews()
