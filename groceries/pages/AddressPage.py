from abc import ABC, abstractmethod


class AddressPage(ABC):
    currentLocationText: str
    setStoreText: str

    @abstractmethod
    def searchAddress(self, location): ...

    @abstractmethod
    def setAsMyStore(self, address=""): ...

    @abstractmethod
    async def openDirections(self, buttonText: str): ...
