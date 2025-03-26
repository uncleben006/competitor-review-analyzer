cd /Users/uncleben006/nextgen/code/python/amazon-review-scraper &&\
TIMESTAMP=$(date "+%Y%m%d%H%M") &&\
poetry run bash -c 'python -m amazon_review_scraper --asin-codes=B0D1XD1ZV3,B0BXYCS74H,B0CCZ1L489 --timestamp='$TIMESTAMP' &&\
python -m walmart_review_scraper --ident_code=5689919121,386006068,2069220904 --timestamp='$TIMESTAMP' &&\
python -m bestbuy_review_scraper --ident_code=6447382,6505727,6554464 --timestamp='$TIMESTAMP' &&\
python upload_products.py '$TIMESTAMP' &&\
python upload_reviews.py '$TIMESTAMP' &&\
python update_summary.py '$TIMESTAMP'' >> ./cron/$TIMESTAMP.log 2>&1