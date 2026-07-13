import sys
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.BasePage import BasePage

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class LoginPage(BasePage):
    loginInput = (By.ID, "user_name")
    passwordInput = (By.ID, "user_name")

    def clickLoginInput(self):
        self.wait.until(EC.visibility_of_element_located(self.loginInput)).send_keys("Username")
    
    def clickPasswordInput(self):
        time.sleep(5)
        self.wait.until(EC.visibility_of_element_located(self.passwordInput)).send_keys("Password")
    
    
