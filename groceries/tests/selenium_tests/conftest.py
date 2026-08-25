import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import allure

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from pages.LuckyMeat import LuckySearchSelenium, LuckyAddressSelenium
from pages.FoodMaxxSearch import FoodMaxxSearchSelenium
from pages.FoodMaxxAddress import FoodMaxxAddressSelenium

from conftest import sanitize_test_name


@pytest.fixture
def web_driver(request) -> WebDriver:
    options = webdriver.ChromeOptions()

    chrome_bin = os.environ.get("CHROME_BIN")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    if chrome_bin:
        options.binary_location = chrome_bin
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")

    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    yield driver

    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        name = sanitize_test_name(request.node.name)
        results_dir = Path("test-results")
        results_dir.mkdir(parents=True, exist_ok=True)
        try:
            png_path = results_dir / f"{name}-failure.png"
            driver.save_screenshot(str(png_path))
            allure.attach.file(str(png_path), name=f"{name} Failure",
                               attachment_type=allure.attachment_type.PNG)

            html_path = results_dir / f"{name}-failure.html"
            html_path.write_text(driver.page_source, encoding="utf-8")
            allure.attach.file(str(html_path), name=f"{name} Page HTML",
                               attachment_type=allure.attachment_type.HTML)
        except WebDriverException:
            pass

    driver.quit()

@pytest.fixture
def luckySearchPageSelenium(web_driver: WebDriver) -> LuckySearchSelenium:
    return LuckySearchSelenium(web_driver)

@pytest.fixture
def luckyAddressPageSelenium(web_driver: WebDriver) -> LuckyAddressSelenium:
    return LuckyAddressSelenium(web_driver)

@pytest.fixture
def foodmaxxSearchSelenium(web_driver: WebDriver) -> FoodMaxxSearchSelenium:
    return FoodMaxxSearchSelenium(web_driver)

@pytest.fixture
def foodmaxxAddressSelenium(web_driver: WebDriver) -> FoodMaxxAddressSelenium:
    return FoodMaxxAddressSelenium(web_driver)
