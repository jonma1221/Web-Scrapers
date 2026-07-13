import os
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pages.MainPage import MainPagePlaywright
from pages.CategoriesPage import CategoriesPagePlaywright
from pages.VideoGamePage import VideoGamePagePlaywright
from pages.LoginPage import LoginPagePlaywright

import bs4
import asyncio
from models.Deal import Deal
from playwright.async_api import async_playwright, expect
load_dotenv()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        # context = await browser.new_context(storage_state=".auth/slickdeals_state.json")
        page = await context.new_page()
        
        # page = await browser.new_page()
        await page.goto("https://slickdeals.net/")

        loginPage = LoginPagePlaywright(page)
        await loginPage.login(os.getenv("SLICKDEALS_USER"), os.getenv("SLICKDEALS_PASS"))

        # Save storage state
        await context.storage_state(path=".auth/slickdeals_state.json")

        mainPage = MainPagePlaywright(page)
        await mainPage.clickCategories()
        await mainPage.clickViewAllCategories()

        categoryPage = CategoriesPagePlaywright(page)
        await categoryPage.clickCategory()

        videoGamesPage = VideoGamePagePlaywright(page)
        await videoGamesPage.clickDropDown()

        await expect(page.locator("li[data-catalog-item='DealCard']").first).to_be_visible()

        # parse through the html and find the deals
        html = await page.content()
        soup = bs4.BeautifulSoup(html, "html.parser")
        deals = soup.find_all("li", attrs={"data-catalog-item": "DealCard"})
        for deal in deals:
            deal = Deal.from_soup(deal)
            print(f"Title: {deal.title}, Price: {deal.price}, Store: {deal.store}, URL: {deal.url}, Image URL: {deal.image_url}")
        await browser.close()
asyncio.run(main())
