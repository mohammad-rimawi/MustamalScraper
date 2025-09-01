# MustamalScraper
A Python project that scrapes business information from Google Maps using Playwright.   It collects details such as name, address, website, and phone number, and saves the data in CSV and Excel formats.  


# Mustaml Scraper

**Mustaml Scraper** is a Python project that uses [Playwright](https://playwright.dev/python/docs/intro) to scrape product data from [Mstaml](https://www.mstaml.com) automatically.

---

## Features

- Extract product links from the website and different categories.
- Scrape the following product data:
  - Title
  - Price
  - Description
  - Location
  - Seller information
  - Images
  - Post details
- Save data in:
  - JSON (`mstaml_products_final.json`)
  - CSV (`mstaml_products_final.csv`)
- Backup data every 5 products during scraping.
- Handles dynamic pages using Playwright.
- Works on Windows with UTF-8 support.

---

## Requirements

- Python 3.9 or higher
- Required Python packages:
  ```bash
  pip install playwright pandas
  playwright install
