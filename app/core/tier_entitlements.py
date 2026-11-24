from dataclasses import dataclass

from app.models.user import UserTier


@dataclass(frozen=True)
class TierEntitlements:
    max_active_urls: int | None  # None means unlimited
    allow_custom_aliases: bool


TIER_ENTITLEMENTS: dict[UserTier, TierEntitlements] = {
    UserTier.FREE: TierEntitlements(max_active_urls=10, allow_custom_aliases=False),
    UserTier.PREMIUM: TierEntitlements(max_active_urls=None, allow_custom_aliases=True),
    UserTier.ADMIN: TierEntitlements(max_active_urls=None, allow_custom_aliases=True),
}
