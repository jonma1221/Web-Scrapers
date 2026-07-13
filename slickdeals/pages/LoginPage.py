from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from shared.BasePage import BasePage, BasePagePlaywright

class LoginPagePlaywright(BasePagePlaywright):
    def __init__(self, page):
        super().__init__(page)
        self.loginBtn = self.page.get_by_role("button", name="Sign Up / Log In")
        self.emailOrUsernameTextBox= self.page.get_by_role("textbox", name="Email or Username")
        self.agreementCheckbox = self.page.get_by_role("checkbox", name="By continuing, you agree to")
        self.continueBtn = self.page.get_by_role("button", name="Continue", exact=True)
        self.passwordTextBox = self.page.get_by_role("textbox", name="Password")
        self.confirmLoginBtn = self.page.get_by_role("button", name="Log in", exact=True)
    
    async def login(self, username, password):
        await self.loginBtn.click()
        await self.emailOrUsernameTextBox.click()
        await self.emailOrUsernameTextBox.fill(username)

        await self.continueBtn.click()
        await self.passwordTextBox.click()
        await self.passwordTextBox.fill(password)
        await self.confirmLoginBtn.click()