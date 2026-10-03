from django.db import models
from django.contrib.auth.models import User

# 1. Market and Asset Models
class Market(models.Model):
    name = models.CharField(max_length=100) # e.g., "Nairobi Securities Exchange"
    symbol = models.CharField(max_length=10) # e.g., "NSE"

    def __str__(self):
        return self.name

class Asset(models.Model):
    symbol = models.CharField(max_length=20, unique=True) # e.g., "SCOM.NR"
    name = models.CharField(max_length=100) # e.g., "Safaricom PLC"
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

# 2. Watchlist Model (CRUD and Auth prep)
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Watchlist")
    assets = models.ManyToManyField(Asset, blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

# 3. Portfolio and Transaction Models
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Investment Portfolio")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class Transaction(models.Model):
    ACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    price_at_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.quantity} {self.asset.symbol}"
