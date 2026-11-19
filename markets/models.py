import secrets
import uuid
from decimal import Decimal
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# 1. Market and Asset Models
class Market(models.Model):
    name = models.CharField(max_length=100) # e.g., "Nairobi Securities Exchange"
    symbol = models.CharField(max_length=10, unique=True) # e.g., "NSE"
    country = models.CharField(max_length=50, blank=True, default='')
    exchange_code = models.CharField(max_length=20, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['symbol']
        verbose_name = "Financial Market"
        verbose_name_plural = "Financial Markets"

    def clean(self):
        super().clean()
        if self.symbol:
            self.symbol = self.symbol.upper().strip()

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class Asset(models.Model):
    symbol = models.CharField(max_length=20, unique=True, db_index=True) # e.g., "SCOM"
    name = models.CharField(max_length=100) # e.g., "Safaricom PLC"
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='assets')
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=5, default="USD")
    category = models.CharField(max_length=50, default="equities", db_index=True)
    sector = models.CharField(max_length=100, blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    volume = models.CharField(max_length=50, blank=True, default='')
    market_cap = models.CharField(max_length=50, blank=True, default='')
    change_percent = models.FloatField(default=0.0)
    top_50_rank = models.IntegerField(null=True, blank=True, db_index=True)
    is_top_50 = models.BooleanField(default=False, db_index=True)
    underperformance_warning = models.BooleanField(default=False, db_index=True)
    warning_reason = models.CharField(max_length=255, blank=True, default="")
    christian_ethics_score = models.IntegerField(default=95)
    christian_ethics_notes = models.TextField(blank=True, default="Verified Ethical & Responsible Investment")
    status = models.CharField(max_length=30, default="top_50")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['top_50_rank', 'symbol']
        verbose_name = "Market Asset"
        verbose_name_plural = "Market Assets"

    def clean(self):
        super().clean()
        if self.symbol:
            self.symbol = self.symbol.upper().strip()
        if self.current_price is not None and self.current_price < 0:
            raise ValidationError({'current_price': 'Price cannot be negative.'})
        if self.christian_ethics_score < 0 or self.christian_ethics_score > 100:
            raise ValidationError({'christian_ethics_score': 'Ethics score must be between 0 and 100.'})

    @property
    def logo_url(self):
        from .data import get_asset_logo
        return get_asset_logo(self.symbol)

    @property
    def logo(self):
        return self.logo_url

    @property
    def company_image_url(self):
        from .data import get_company_image
        return get_company_image(self.symbol)

    @property
    def image(self):
        return self.company_image_url
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

# 2. User Profile Model
class UserProfile(models.Model):
    AUTH_PROVIDER_CHOICES = (
        ('credentials', 'Email / Password'),
        ('google', 'Google Single Sign-On'),
        ('apple', 'Apple ID'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=30, blank=True, default='')
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    tier = models.CharField(max_length=50, default='Terminal Pro Tier')
    cash_balance_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('5212.17'))
    avatar_url = models.CharField(max_length=255, default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80')
    bio = models.TextField(blank=True, default='')
    job_title = models.CharField(max_length=100, blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='')
    preferred_currency = models.CharField(max_length=5, default='USD')
    kyc_verified = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True, default='')
    otp_enabled = models.BooleanField(default=True)
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default='credentials')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    def can_afford(self, amount_usd):
        return self.cash_balance_usd >= Decimal(str(amount_usd))

    def deposit(self, amount_usd):
        amt = Decimal(str(amount_usd))
        if amt <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.cash_balance_usd += amt
        self.save(update_fields=['cash_balance_usd', 'updated_at'])
        return self.cash_balance_usd

    def withdraw(self, amount_usd):
        amt = Decimal(str(amount_usd))
        if amt <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.cash_balance_usd < amt:
            raise ValueError("Insufficient balance.")
        self.cash_balance_usd -= amt
        self.save(update_fields=['cash_balance_usd', 'updated_at'])
        return self.cash_balance_usd

    @property
    def is_pro(self):
        return self.tier in ['Terminal Pro Tier', 'Institutional Tier', 'Pro Tier']

    @property
    def is_paid(self):
        return self.is_pro

    def upgrade_to_pro(self):
        self.tier = 'Terminal Pro Tier'
        self.save(update_fields=['tier', 'updated_at'])
        return self.tier

    def downgrade_to_free(self):
        self.tier = 'Free Tier'
        self.save(update_fields=['tier', 'updated_at'])
        return self.tier

    def __str__(self):
        return f"{self.user.username} Profile ({self.tier})"

# 3. OTP Verification Model
class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ('login', 'Login Verification'),
        ('register', 'Registration Verification'),
        ('trade', 'Trade Confirmation'),
        ('password_reset', 'Password Reset'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps', null=True, blank=True)
    email_or_phone = models.CharField(max_length=100)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='login')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    @classmethod
    def generate_otp(cls, user=None, email_or_phone=None, purpose='login', minutes_valid=10):
        # Invalidate old unused OTPs for this user / target
        identifier = email_or_phone or (user.email if user else '')
        cls.objects.filter(email_or_phone=identifier, purpose=purpose, is_used=False).update(is_used=True)

        # Generate a 6-digit code
        code = f"{secrets.randbelow(900000) + 100000}"
        expires = timezone.now() + timedelta(minutes=minutes_valid)

        otp_instance = cls.objects.create(
            user=user,
            email_or_phone=identifier,
            otp_code=code,
            purpose=purpose,
            expires_at=expires,
            is_used=False
        )
        return otp_instance

    def __str__(self):
        return f"OTP {self.otp_code} for {self.email_or_phone} ({self.purpose})"

# 4. Watchlist Model
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100, default="Primary Watchlist")
    assets = models.ManyToManyField(Asset, blank=True, related_name='watchlists')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def add_asset(self, asset):
        self.assets.add(asset)

    def remove_asset(self, asset):
        self.assets.remove(asset)

    def has_asset(self, asset):
        return self.assets.filter(id=asset.id).exists()

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

# 5. Portfolio Model
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100, default="My Investment Portfolio")
    cash_balance_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('5212.17'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def deposit(self, amount_usd):
        amt = Decimal(str(amount_usd))
        if amt <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.cash_balance_usd += amt
        self.save(update_fields=['cash_balance_usd', 'updated_at'])
        if hasattr(self.user, 'profile'):
            self.user.profile.cash_balance_usd = self.cash_balance_usd
            self.user.profile.save(update_fields=['cash_balance_usd'])
        return self.cash_balance_usd

    def withdraw(self, amount_usd):
        amt = Decimal(str(amount_usd))
        if amt <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.cash_balance_usd < amt:
            raise ValueError("Insufficient cash in portfolio.")
        self.cash_balance_usd -= amt
        self.save(update_fields=['cash_balance_usd', 'updated_at'])
        if hasattr(self.user, 'profile'):
            self.user.profile.cash_balance_usd = self.cash_balance_usd
            self.user.profile.save(update_fields=['cash_balance_usd'])
        return self.cash_balance_usd

    def get_holdings(self):
        """Calculates aggregated holdings from transactions."""
        txs = self.transactions.select_related('asset').order_by('date')
        holdings_dict = {}
        for tx in txs:
            sym = tx.asset.symbol
            if sym not in holdings_dict:
                holdings_dict[sym] = {
                    'asset': tx.asset,
                    'symbol': sym,
                    'name': tx.asset.name,
                    'currency': tx.asset.currency,
                    'shares': Decimal('0'),
                    'total_cost': Decimal('0'),
                }
            qty = Decimal(str(tx.quantity))
            cost = Decimal(str(tx.total_amount or (tx.price_at_transaction * qty)))
            if tx.action == 'BUY':
                holdings_dict[sym]['shares'] += qty
                holdings_dict[sym]['total_cost'] += cost
            elif tx.action == 'SELL':
                holdings_dict[sym]['shares'] -= qty
                holdings_dict[sym]['total_cost'] -= cost

        result = []
        for sym, h in holdings_dict.items():
            if h['shares'] > 0:
                avg_price = round(h['total_cost'] / h['shares'], 2) if h['shares'] else Decimal('0')
                curr_price = h['asset'].current_price or avg_price
                curr_val = round(curr_price * h['shares'], 2)
                result.append({
                    'asset': h['asset'],
                    'symbol': sym,
                    'name': h['name'],
                    'currency': h['currency'],
                    'shares': float(h['shares']),
                    'avg_price': float(avg_price),
                    'current_price': float(curr_price),
                    'total_value': float(curr_val),
                })
        return result

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

# 6. Order Model
class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ('MARKET', 'Market Order'),
        ('LIMIT', 'Limit Order'),
        ('STOP', 'Stop Order'),
    )
    ACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='orders')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='MARKET')
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=18, decimal_places=8)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='EXECUTED')
    reference = models.CharField(max_length=50, unique=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ORD-{secrets.token_hex(6).upper()}"
        if self.status == 'EXECUTED' and not self.executed_at:
            self.executed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} {self.quantity} {self.asset.symbol} ({self.status})"

# 7. Transaction Model
class Transaction(models.Model):
    ACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=18, decimal_places=8, default=1.0)
    price_at_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reference = models.CharField(max_length=50, blank=True, default='', unique=True)
    status = models.CharField(max_length=20, default='Completed')
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self.total_amount is None:
            self.total_amount = round(self.price_at_transaction * Decimal(str(self.quantity)), 2)
        if not self.reference:
            self.reference = f"TX-{secrets.token_hex(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} {self.quantity} {self.asset.symbol}"

# 8. Cash Transfer / Deposit & Withdrawal Model
class CashTransfer(models.Model):
    TRANSFER_TYPE_CHOICES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    )
    METHOD_CHOICES = (
        ('MPESA', 'M-PESA Express'),
        ('BANK_TRANSFER', 'Bank Wire Transfer'),
        ('CARD', 'Debit / Credit Card'),
    )
    STATUS_CHOICES = (
        ('COMPLETED', 'Completed'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    )

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='cash_transfers')
    transfer_type = models.CharField(max_length=12, choices=TRANSFER_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='MPESA')
    reference = models.CharField(max_length=50, unique=True, blank=True)
    account_or_phone = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='COMPLETED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"CT-{secrets.token_hex(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transfer_type} ${self.amount} ({self.status})"

class EventReminder(models.Model):
    """
    User reminders for upcoming macroeconomic releases and corporate earnings events.
    Dispatches alerts to the user's registered email address.
    """
    EVENT_CATEGORY_CHOICES = [
        ('ECONOMIC', 'Macroeconomic Release'),
        ('EARNINGS', 'Corporate Earnings Filing'),
        ('CENTRAL_BANK', 'Central Bank & Policy'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='event_reminders')
    email = models.EmailField(help_text="Registered email address receiving reminders")
    event_id = models.CharField(max_length=100, db_index=True)
    event_title = models.CharField(max_length=255)
    event_category = models.CharField(max_length=50, default='ECONOMIC', choices=EVENT_CATEGORY_CHOICES)
    event_date = models.CharField(max_length=50)
    event_time = models.CharField(max_length=50, blank=True, default='')
    country = models.CharField(max_length=50, default='All')
    symbol = models.CharField(max_length=20, blank=True, default='')
    impact = models.CharField(max_length=20, default='High')
    notes = models.TextField(blank=True, default='')
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('email', 'event_id')

    def __str__(self):
        return f"Reminder: {self.event_title} ({self.event_date}) -> {self.email}"

# Signals to guarantee defaults
@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        portfolio, _ = Portfolio.objects.get_or_create(
            user=instance, 
            defaults={'name': 'Growth & Dividend Portfolio'}
        )
        watchlist, _ = Watchlist.objects.get_or_create(
            user=instance, 
            defaults={'name': 'Primary Watchlist'}
        )
        default_assets = Asset.objects.filter(symbol__in=['SCOM', 'EQTY', 'AAPL', 'NVDA', 'BTC'])
        if default_assets.exists():
            watchlist.assets.set(default_assets)
