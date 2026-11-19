"""
Global Context Processors for PesaMarkets.
Injects real-time Market Dock telemetry and configuration across all views.
"""

from .services.dock_service import get_dock_data

def market_dock_context(request):
    """
    Supplies the Market Dock dataset (trending, gainers, losers, economic events,
    and upcoming regulatory earnings) to all templates extending base.html.
    """
    try:
        dock_data = get_dock_data()
        reminded_ids = []
        is_paid = False
        user_tier = "Guest Tier"
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.email:
                from .services.events_service import get_user_reminded_ids
                reminded_ids = list(get_user_reminded_ids(request.user.email))
            profile = getattr(request.user, 'profile', None)
            if profile:
                is_paid = getattr(profile, 'is_paid', False)
                user_tier = getattr(profile, 'tier', 'Free Tier')
            else:
                user_tier = "Free Tier"
        dock_data["user_reminded_ids"] = reminded_ids
    except Exception:
        dock_data = {}
        is_paid = False
        user_tier = "Guest Tier"

    return {
        "dock_data": dock_data,
        "is_paid": is_paid,
        "user_tier": user_tier
    }

