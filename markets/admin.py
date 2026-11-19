from django.contrib import admin
from .models import Market, Asset, UserProfile, OTPVerification, Portfolio, Order, Transaction, CashTransfer, Watchlist, EventReminder

@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ('event_title', 'email', 'event_date', 'event_time', 'country', 'impact', 'email_sent', 'is_active', 'created_at')
    list_filter = ('country', 'impact', 'email_sent', 'is_active', 'event_category')
    search_fields = ('event_title', 'email', 'event_id', 'symbol')

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'country', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('symbol', 'name')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'market', 'current_price', 'currency', 'category', 'is_top_50', 'top_50_rank', 'underperformance_warning', 'christian_ethics_score')
    list_filter = ('market', 'category', 'currency', 'is_top_50', 'underperformance_warning')
    search_fields = ('symbol', 'name', 'sector', 'industry')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'cash_balance_usd', 'phone_number', 'kyc_verified', 'otp_enabled', 'auth_provider')
    list_filter = ('tier', 'kyc_verified', 'otp_enabled', 'auth_provider')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email_or_phone', 'otp_code', 'purpose', 'is_used', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used')
    search_fields = ('email_or_phone', 'otp_code')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'cash_balance_usd', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'portfolio', 'asset', 'action', 'order_type', 'quantity', 'price', 'status', 'created_at')
    list_filter = ('action', 'order_type', 'status')
    search_fields = ('reference', 'asset__symbol', 'user__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'portfolio', 'asset', 'action', 'quantity', 'price_at_transaction', 'total_amount', 'status', 'date')
    list_filter = ('action', 'status')
    search_fields = ('reference', 'asset__symbol', 'portfolio__user__username')

@admin.register(CashTransfer)
class CashTransferAdmin(admin.ModelAdmin):
    list_display = ('reference', 'portfolio', 'transfer_type', 'amount', 'currency', 'method', 'status', 'created_at')
    list_filter = ('transfer_type', 'method', 'status')
    search_fields = ('reference', 'portfolio__user__username')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
