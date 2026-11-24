from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click import Click
from app.repositories.interfaces import ClickRepository


class SqlAlchemyClickRepo(ClickRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_click(self, click: Click) -> None:
        self.session.add(click)

    async def get_url_click_analytics(self, url_id: UUID):
        total_clicks = await self.session.scalar(
            select(func.count(Click.id)).where(Click.short_url_id == url_id)
        )

        # Time-Series Aggregation
        stmt = (
            select(
                func.date(Click.clicked_at).label("date"),
                func.count(Click.id).label("clicks"),
            )
            .where(Click.short_url_id == url_id)
            .group_by(func.date(Click.clicked_at))
            .order_by(func.date(Click.clicked_at))
        )

        result = await self.session.execute(stmt)
        time_series = result.all()

        return total_clicks, time_series
