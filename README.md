# Web Scrapers

A collection of Python web scrapers and price comparison tools for grocery stores and deal sites, built with Selenium and Playwright. Compares weekly ad prices across Safeway, Lucky, FoodMaxx, Grocery Outlet, and Smart & Final. Includes a FastAPI webapp for searching products by store and location. Created to learn and demonstrate browser automation with Playwright and Selenium, including how to structure page objects and write maintainable tests.

## Prerequisites

- Python 3.11+
- Node.js & npm (required for the webapp frontend build)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Playwright browsers are also required for Playwright tests:

```bash
playwright install
```



## Running Tests



### Command Line (pytest)



#### Playwright tests

```bash
pytest -v groceries/tests/playwright_tests
```



#### Selenium tests

Requires Chrome installed on your machine. Selenium 4.45+ includes Selenium Manager, which automatically downloads the matching ChromeDriver — no manual driver installation needed.

```bash
pytest -v groceries/tests/selenium_tests
```



#### All tests

```bash
pytest -v groceries/tests/playwright_tests groceries/tests/selenium_tests
```



#### Running a specific test

```bash
pytest -v groceries/tests/selenium_tests/filter/test_filter_category.py -k test_multiple_filter_by_brand
```



### Runnings Tests With Docker

The project supports running tests with Docker and skips the local Playwright/Selenium setup. 

To run the Playwright tests:
```bash
docker build -f Dockerfile -t playwright-docker .
docker run playwright-docker
```



To run the Selenium tests:
```bash
docker build -f Dockerfile.selenium -t selenium-docker .
docker run selenium-docker
```



## Project Structure

```
├── slickdeals/              # Slickdeals scraper
├── groceries/               # Scraper for various grocery websites
│   ├── pages/               # Page objects (Selenium + Playwright)
│   ├── tests/
│   │   ├── playwright_tests/
│   │   ├── selenium_tests/
│   │   └── conftest.py      # Shared test utilities
│   ├── webapp/              # FastAPI + Vite webapp
│   └── meat_compare/        # CLI price comparison tool
├── shared/                  # Base page objects
├── Dockerfile               # Playwright test image
└── Dockerfile.selenium      # Selenium test image
```

