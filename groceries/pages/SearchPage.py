from abc import ABC, abstractmethod


class SearchPage(ABC):
    acceptCookieBtnLocator: str
    selectAStoreLink: str
    selectStoreForPricingLink: str
    productCard: str
    loadingSpinner: str
    clearAllFilters: str
    appliedFiltersLocator: str
    salePriceTestId: str
    signInLinkText: str

    @abstractmethod
    def acceptCookies(self): ...

    @abstractmethod
    def selectYourStore(self): ...

    @abstractmethod
    def applyFilter(self): ...
    
    @abstractmethod
    def clickClearAllFilters(self): ...
    
    @abstractmethod
    def scrapeDeals(self): ...

    @abstractmethod
    def clickSignIn(self): ...
