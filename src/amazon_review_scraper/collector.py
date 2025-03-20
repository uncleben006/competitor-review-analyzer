"""
    Main module for collecting Amazon Review data.
"""
import os
import logging

from typing import List

import pandas as pd

from amazon_review_scraper.models import BaseModel
from amazon_review_scraper.scraper import AmazonReviewScraper


DEFAULT_OUTPUT_FILE = "amazon_reviews.csv"


class AmazonReviewDataCollector:
    """Data collector class for Amazon Reviews"""

    def __init__(
        self,
        output_file: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._scraper = AmazonReviewScraper()
        self._output_file = output_file if output_file else DEFAULT_OUTPUT_FILE
        self._logger = logger if logger else logging.getLogger(__name__)

    def _save_to_csv(self, datas: List[BaseModel]) -> None:
        """Saves given list of model data into a CSV file."""
        self._logger.info(f"Writing {len(datas)} records to {self._output_file}..")
        model_obejcts = [data.model_dump() for data in datas]
        df = pd.DataFrame(model_obejcts)
        df.to_csv(self._output_file, index=False)

    def collect_amazon_review_data(self, asin_codes: List[str], timestamp: str) -> None:
        """
        Scrapes reviews from a given Amazon product page based on given ASIN code and stores it into a CSV file.

        Args:
            asin_codes (List[str]): The ASIN codes of the Amazon product for which to scrape reviews.
            timestamp (str): A timestamp string in the format YYYYMMDDHHMM representing year, month, day, hour, and minute.
        """
        self._logger.info(f"Getting Amazon reviews for ASIN codes {asin_codes}..")
        try:
            for asin_code, product, reviews in self._scraper.scrape_amazon_products_and_reviews(asin_codes):
                if not reviews:
                    self._logger.info(f"No reviews found for given product {asin_code}.")
                    continue
                reviews_folder = os.path.join("reviews", "amazon")
                product_folder = os.path.join("products", "amazon")
                os.makedirs(reviews_folder, exist_ok=True)
                os.makedirs(product_folder, exist_ok=True)
                self._output_file = os.path.join(reviews_folder, f"{timestamp}_amazon_reviews_{asin_code}.csv")
                self._save_to_csv(reviews)
                self._output_file = os.path.join(product_folder, f"{timestamp}_amazon_product_{asin_code}.csv")
                self._save_to_csv([product])

        except Exception:
            self._logger.exception(
                f"Error when scraping Amazon products info and reviews for products {asin_codes}."
            )
            return
