from playwright.async_api import Page
from shared.BasePage import BasePagePlaywright
from pages.LoginPage import LoginPage


class PlaywrightLoginPage(LoginPage, BasePagePlaywright):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.emailField = page.get_by_role("textbox", name=self.emailInput)
        self.passwordField = page.get_by_role("textbox", name=self.passwordInput)
        self.showPasswordBtn = page.get_by_text(self.showPasswordToggle)
        self.signInBtn = page.get_by_role("button", name=self.signInButton)

    async def login(self, email: str, password: str):
        await self.emailField.fill(email)
        await self.passwordField.fill(password)
        await self.signInBtn.click()

    async def toggleShowPassword(self):
        await self.showPasswordBtn.click()


class FoodMaxxLoginPlaywright(PlaywrightLoginPage):
    emailInput = "Email Enter Email"
    passwordInput = "Password"
    showPasswordToggle = "Show Password"
    signInButton = "Sign In"

class LuckyLoginPlaywright(PlaywrightLoginPage):
    emailInput = "Email Enter Email"
    passwordInput = "Password"
    showPasswordToggle = "Show Password"
    signInButton = "Sign In"