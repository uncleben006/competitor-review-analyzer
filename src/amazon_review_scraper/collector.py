"""
    Main module for collecting Amazon Review data.
"""
import os
import logging

from typing import List

import pandas as pd

from amazon_review_scraper.models import Review
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

    def _save_to_csv(self, reviews: List[Review]) -> None:
        """Saves given list of product reviews to a CSV file."""
        self._logger.info(f"Writing {len(reviews)} reviews to {self._output_file}..")
        review_obejcts = [review.model_dump() for review in reviews]
        df = pd.DataFrame(review_obejcts)
        df.to_csv(self._output_file)

    def collect_amazon_review_data(self, asin_codes: List[str]) -> None:
        """
        Scrapes reviews from a given Amazon product page based on given ASIN code and stores it into a CSV file.

        Args:
            asin_code (str): The ASIN code of the Amazon product for which to scrape reviews.
        """
        self._logger.info(f"Getting Amazon reviews for ASIN codes {asin_codes}..")
        try:
            for asin_code, reviews_batch in self._scraper.scrape_amazon_reviews(asin_codes):
                if not reviews_batch:
                    self._logger.info(f"No reviews found for given product {asin_code}.")
                    continue
                folder = os.path.join("data", asin_code)
                os.makedirs(folder, exist_ok=True)
                timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M")
                self._output_file = os.path.join(folder, f"{timestamp}_reviews.csv")
                self._save_to_csv(reviews_batch)

        except Exception:
            self._logger.exception(
                f"Error when scraping Amazon reviews for product {asin_codes}."
            )
            return
