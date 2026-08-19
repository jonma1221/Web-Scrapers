from playwright.async_api import Page
from shared.BasePage import BasePagePlaywright
from pages.LoginPage import LoginPage


class SmartFinalLoginPagePlaywright(LoginPage, BasePagePlaywright):
    emailInput = "Email"
    passwordInput = "Password *"
    showPasswordToggle = "Show"
    signInButton = "sign in"

    forgotYourPasswordText = "Forgot your password"
    
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.emailField = page.get_by_role("textbox", name=self.emailInput)
        self.passwordField = page.get_by_role("textbox", name=self.passwordInput)
        self.showPasswordBtn = page.get_by_role("button", name=self.showPasswordToggle)
        self.signInBtn = page.get_by_role("button", name=self.signInButton)
        self.forgotPasswordButton = page.get_by_role("link", name=self.forgotYourPasswordText)

    async def login(self, email: str, password: str):
        await self.emailField.fill(email)
        await self.passwordField.fill(password)
        await self.signInBtn.click()

    async def toggleShowPassword(self):
        await self.showPasswordBtn.click()
