from abc import ABC, abstractmethod


class UrlCacheRepository(ABC):
    @abstractmethod
    def get_code_by_url(self, url: str) -> str | None:
        pass

    @abstractmethod
    def save_url(self, code: str, url: str) -> None:
        pass

    @abstractmethod
    def get_url_by_code(self, code: str) -> str | None:
        pass
