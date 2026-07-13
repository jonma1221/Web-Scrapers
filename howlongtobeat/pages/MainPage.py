import sys
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.BasePage import BasePage

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class MainPage(BasePage):
    consentBtn = (By.ID, "onetrust-accept-btn-handler")
    loginBtn = (By.LINK_TEXT, "Login")

    def clickConsent(self):
        self.wait.until(EC.element_to_be_clickable(self.consentBtn)).click()
        
    def clickLogin(self):
        self.wait.until(EC.visibility_of_element_located(self.loginBtn)).click()