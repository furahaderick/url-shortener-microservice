from uuid import UUID

from app.core.exceptions import UrlNotFoundException
from app.core.uow import SqlAlchemyUnitOfWork


class AnalyticsService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    async def get_url_analytics(self, user_id: UUID, short_code: str):
        async with self.uow:
            # Fetch url by short code AND user id (ownership)
            url = await self.uow.urls.get_url_by_short_code_and_user_id(
                short_code, user_id
            )
            if url is None:
                raise UrlNotFoundException()

            # Total clicks and time series analytics
            total_clicks, time_series = await self.uow.clicks.get_url_click_analytics(
                url.id
            )

            return total_clicks, time_series
