"""
    Pydantic models for Amazon Review scraper.
"""

from pydantic import BaseModel


class Product(BaseModel):
    ident_code: str
    name: str
    base_price: float
    final_price: float
    inventory_status: str


class Review(BaseModel):
    author: str
    content: str
    rating: int
    title: str
    review_date: str
    verified_purchase: bool
    helpful_text: str
