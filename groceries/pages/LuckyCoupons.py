import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from models.Coupon import Coupon
from shared.BasePage import BasePageSelenium


class LuckyCouponsSelenium(BasePageSelenium):
    COUPONS_URL = "https://luckysupermarkets.com/coupons/*"
    COUPONS_LANDING_URL = "https://luckysupermarkets.com/coupons"
    STORE_LOCATOR_URL = "https://luckysupermarkets.com/coupons?showStoreLocator=true"

    acceptCookieBtnId = (By.ID, "truste-consent-button")
    couponCategorySelector = (By.CSS_SELECTOR, "[data-testid='swiftlyCouponCategory']")
    storeSelectLinkXpath = (By.XPATH, '//button[@data-testid="store-select-link"]')
    storeLocatorInputId = (By.ID, "autocompleteInputId")
    loadingSpinnerSelector = (By.CSS_SELECTOR, '.mantine-Loader-root')

    searchInputSelector = (
        By.CSS_SELECTOR,
        "input[aria-label='Search, press the down arrow to view search history']",
    )
    searchSubmitBtnSelector = (By.CSS_SELECTOR, "button[aria-label='Click to search']")

    categoryRadioGroupSelector = (By.CSS_SELECTOR, "[data-testid='category-radio-group']")
    categoryButtonSelector = (By.CSS_SELECTOR, "[data-testid='category-button']")
    categoryButtonTextSelector = (By.CSS_SELECTOR, "[data-testid='category-button-text']")

    resultsCountSelector = (By.CSS_SELECTOR, "p.coupon-category-subtitle")
    sortByComboboxSelector = (By.CSS_SELECTOR, ".mantine-Select-input")
    sortOptionSelector = (By.CSS_SELECTOR, "[role='option']")

    couponAccordionSelector = (By.CSS_SELECTOR, "[data-testid='coupon-accordion']")
    accordionControlSelector = (By.CSS_SELECTOR, "[data-testid='accordion-control']")
    couponCardSelector = (By.CSS_SELECTOR, ".coupon-card-wrapper")
    couponClipBtnSelector = (By.CSS_SELECTOR, "[data-testid='coupon-clip-button']")
    clipLoginModalNotNowBtnXpath = (By.XPATH, "//button[normalize-space(.)='Not Now']")

    _UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _LOWER = "abcdefghijklmnopqrstuvwxyz"

    def goToCouponsPage(self):
        self.driver.get(self.COUPONS_URL)
        self.wait.until(EC.presence_of_element_located(self.categoryRadioGroupSelector))
        self.waitForResultsCount()

    def acceptCookies(self):
        acceptCookieBtn = self.wait.until(EC.presence_of_element_located(self.acceptCookieBtnId))
        acceptCookieBtn.click()
        self.wait.until(EC.invisibility_of_element(acceptCookieBtn))

    def goToCouponsLandingPage(self):
        self.driver.get(self.COUPONS_LANDING_URL)
        self.wait.until(EC.presence_of_all_elements_located(self.couponCategorySelector))

    def getCouponCategories(self) -> list[WebElement]:
        return self.wait.until(EC.presence_of_all_elements_located(self.couponCategorySelector))

    def clickCouponCategory(self, name: str):
        category = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"[data-testid='swiftlyCouponCategory'][aria-label='{name}']")
            )
        )
        ActionChains(self.driver).scroll_to_element(category).perform()
        category.click()
        # Intermediate sync: the click lands on the category results view.
        self.wait.until(EC.presence_of_element_located(self.categoryRadioGroupSelector))
        self.waitForResultsCount()

    def selectYourStore(self):
        # The header store button opens the locator unreliably without a selected
        # store; the store-locator route is deterministic.
        self.driver.get(self.STORE_LOCATOR_URL)
        self.wait.until(EC.presence_of_element_located(self.storeLocatorInputId))

    def getSelectedStore(self) -> str:
        btn = self.wait.until(EC.visibility_of_element_located(self.storeSelectLinkXpath))
        return btn.text.strip()

    def waitForResultsCount(self) -> int:
        countEl = self.wait.until(EC.visibility_of_element_located(self.resultsCountSelector))
        return int(re.search(r"\d+", countEl.text).group())

    def getResultsCount(self) -> int:
        return self.waitForResultsCount()

    def searchFor(self, query: str):
        searchInput = self.wait.until(EC.element_to_be_clickable(self.searchInputSelector))
        searchInput.clear()
        searchInput.send_keys(query)
        self.wait.until(EC.element_to_be_clickable(self.searchSubmitBtnSelector)).click()

    def selectCategoryByValue(self, value: str):
        group = self.wait.until(EC.presence_of_element_located(self.categoryRadioGroupSelector))
        radio = group.find_element(
            By.CSS_SELECTOR, f"[data-testid='category-button'][value='{value}']"
        )
        self.driver.execute_script("arguments[0].click();", radio)
        self.waitForResultsCount()

    def selectCategoryByLabel(self, label: str):
        # Labels render via CSS text-transform (e.g. "Featured in Ad" -> "Featured In Ad"),
        # so match case-insensitively against the DOM textContent.
        labelEl = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, (
                    f"//*[@data-testid='category-button-text']"
                    f"[translate(normalize-space(.), '{self._UPPER}', '{self._LOWER}')"
                    f"='{label.strip().lower()}']"
                ))
            )
        )
        labelEl.click()
        self.waitForResultsCount()

    def selectBrand(self, name: str):
        # Re-query each attempt so a mid-render disappearance doesn't raise NoSuchElement.
        checkbox = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"[data-testid='swiftly-check-filter'] input[aria-label='{name}']")
            )
        )
        checkbox.click()
        self.waitForResultsCount()

    def selectSortBy(self, option: str):
        combobox = self.wait.until(EC.presence_of_element_located(self.sortByComboboxSelector))
        # The sort control sits under the sticky sub-nav header; keyboard-open
        # bypasses the overlay instead of relying on a pointer click.
        self.driver.execute_script("arguments[0].focus();", combobox)
        combobox.send_keys(Keys.ARROW_DOWN)
        options = self.wait.until(EC.visibility_of_all_elements_located(self.sortOptionSelector))
        target = next(o for o in options if o.text.strip().lower() == option.strip().lower())
        target.click()
        self.waitForResultsCount()

    def getSortOptions(self) -> list[str]:
        combobox = self.wait.until(EC.presence_of_element_located(self.sortByComboboxSelector))
        # The sort control sits under the sticky sub-nav header; keyboard-open
        # bypasses the overlay instead of relying on a pointer click.
        self.driver.execute_script("arguments[0].focus();", combobox)
        combobox.send_keys(Keys.ARROW_DOWN)
        options = self.wait.until(EC.visibility_of_all_elements_located(self.sortOptionSelector))
        labels = [option.text.strip() for option in options]
        combobox.send_keys(Keys.ESCAPE)
        return labels

    def expandAccordionSection(self, label: str):
        control = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[@data-testid='accordion-control'][contains(., '{label}')]")
            )
        )
        if control.get_attribute("aria-expanded") != "true":
            # The accordion control sits under the sticky sub-nav header; JS-click
            # bypasses the overlay instead of relying on a pointer click.
            self.driver.execute_script("arguments[0].click();", control)

    def getCouponCards(self) -> list[WebElement]:
        return self.wait.until(
            EC.presence_of_all_elements_located(self.couponCardSelector)
        )

    def getCoupons(self) -> list[Coupon]:
        coupons = []
        for card in self.getCouponCards():
            try:
                coupons.append(Coupon.from_card_selenium(card))
            except Exception:
                continue
        return coupons

    def clipCoupon(self, card: WebElement) -> WebElement:
        clipBtn = card.find_element(*self.couponClipBtnSelector)
        self.wait.until(EC.element_to_be_clickable(clipBtn)).click()
        # Without a signed-in account, clipping opens a login modal; dismiss
        # it so the page remains usable for subsequent actions.
        try:
            not_now = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.clipLoginModalNotNowBtnXpath)
            )
            not_now.click()
            self.wait.until(EC.invisibility_of_element_located(self.clipLoginModalNotNowBtnXpath))
        except TimeoutException:
            pass

    def getClipButtonLabel(self, card: WebElement) -> str:
        clipBtn = card.find_element(*self.couponClipBtnSelector)
        return clipBtn.get_attribute("aria-label") or ""