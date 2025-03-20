# Competitor Product Review Analyzer

This repository hosts a technical interview project designed to automatically collect, process, and analyze product reviews from Amazon, Walmart, and BestBuy. Using web scraping techniques and automated workflows powered by N8N, it enables real-time insights into competitor products, including quality assessments, shipping performance, pricing comparisons, and overall market positioning.

## Key Features

- **Automated Scraping**: Collects product review data seamlessly from major e-commerce platforms (Amazon, Walmart, BestBuy).
- **Real-time Analysis**: Processes review content to deliver timely insights into competitor strengths and weaknesses.
- **Competitive Intelligence**: Monitors key metrics such as product quality feedback, shipping reliability, and pricing strategy.
- **Integration with N8N**: Automates workflow orchestration for efficient data management and real-time notifications.

## Project Specification
Detailed project specifications and requirements can be found [here](https://transbiz.notion.site/AI-Agent-Test-Case-1b8bb692e4d380e6938fcafe9a3cac10).

## Getting Started

### Installation

Clone the repository:
```bash
git clone <repository-url>
cd competitor-review-analyzer
poetry install
```

### Usage

Activate the poetry environment and execute the following commands to start scraping and analysis:

```bash
poetry shell

TIMESTAMP=$(date '+%Y%m%d%H%M') && \
python -m amazon_review_scraper --asin-codes=B0D1XD1ZV3,B0BXYCS74H,B0CCZ1L489 --timestamp=$TIMESTAMP && \
python -m walmart_review_scraper --ident_code=5689919121,386006068,2069220904 --timestamp=$TIMESTAMP && \
python -m bestbuy_review_scraper --ident_code=6447382,6505727,6554464 --timestamp=$TIMESTAMP
```

### Automation Workflow
- Scraped data is processed through an N8N workflow for automated sentiment analysis, categorization, and competitor benchmarking.
- Notifications or reports are generated based on the analyzed data, providing actionable insights promptly.

## Contribution

This project is for technical interview purposes. Contributions and improvements are welcome to enhance functionality or performance.

