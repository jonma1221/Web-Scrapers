from abc import ABC, abstractmethod


class LoginPage(ABC):
    emailInput: str
    passwordInput: str
    showPasswordToggle: str
    signInButton: str

    @abstractmethod
    async def login(self, email: str, password: str): ...

    @abstractmethod
    async def toggleShowPassword(self): ...
