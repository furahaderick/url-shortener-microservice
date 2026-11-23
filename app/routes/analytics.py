from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.dependencies import AnalyticsServiceDep, require_tiers
from app.models.user import User, UserTier

router = APIRouter(prefix="/api/v1/analytics", tags=["URL Analytics"])

CurrentUserWithPremiumTierDep = Annotated[
    User, Depends(require_tiers(UserTier.PREMIUM))
]


@router.get("/{short_code}")
async def get_short_url_analytics(
    short_code: str,
    current_premium_user: CurrentUserWithPremiumTierDep,
    service: AnalyticsServiceDep,
) -> JSONResponse:
    total_clicks, time_series = await service.get_url_analytics(
        user_id=current_premium_user.id, short_code=short_code
    )

    return JSONResponse(
        content={
            "short_code": short_code,
            "total_clicks": total_clicks or 0,
            "time_series": [
                {"date": str(row.date), "clicks": row.clicks} for row in time_series
            ],
        }
    )
