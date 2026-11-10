from app.core.config import settings
from app.exceptions import InvalidUrlException
from app.repositories.interfaces import UrlCacheRepository
from app.schemas.url import UrlRequest
from app.utils import generate_unique_id


class UrlShortenerService:
    def __init__(self, repo: UrlCacheRepository):
        self.repo = repo

    def shorten_url(self, req: UrlRequest) -> str:
        url = str(req.url)

        # Check if the code for this url already exists
        existing_id_code = self.repo.get_code_by_url(url)

        if existing_id_code is not None:
            return f"{settings.APP_DOMAIN}/{existing_id_code}"

        unique_id_code = generate_unique_id()

        self.repo.save_url(unique_id_code, url)

        return f"{settings.APP_DOMAIN}/{unique_id_code}"

    def get_long_url_from_code(self, code: str) -> str:

        long_url = self.repo.get_url_by_code(code)

        if long_url is None:
            raise InvalidUrlException()

        return long_url
