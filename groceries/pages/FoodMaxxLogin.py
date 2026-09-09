
from pages.LoginPage import LoginPage
from shared.BasePage import BasePageSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class FoodMaxxLoginSelenium(LoginPage, BasePageSelenium):
    emailInputId = (By.ID, "email")
    passwordInputId = (By.ID, "password")
    signInButtonLocator = (By.XPATH, "//button[text()='Sign In']")
    showPasswordToggle = (By.XPATH, "//button[text()='Show Password']")

    def login(self, email: str, password: str):
        self.wait.until(EC.element_to_be_clickable(self.emailInputId)).send_keys(email)
        self.wait.until(EC.element_to_be_clickable(self.passwordInputId)).send_keys(password)
        self.wait.until(EC.element_to_be_clickable(self.signInButtonLocator)).click()

    def toggleShowPassword(self):
        self.wait.until(EC.element_to_be_clickable(self.showPasswordToggle)).click()