from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from markets.models import Market, Asset, Watchlist, Portfolio, Transaction
from markets.data import ASSETS, USER_PORTFOLIO

class Command(BaseCommand):
    help = 'Seeds initial markets, assets, watchlist, and user portfolio data'

    def handle(self, *args, **options):
        self.stdout.write("Seeding PesaMarkets database...")
        
        # 1. Create or get demo user
        user, _ = User.objects.get_or_create(
            username='user',
            defaults={'email': 'user@pesamarkets.com', 'first_name': 'Richard', 'last_name': 'Cooper'}
        )
        if not user.has_usable_password():
            user.set_password('pesa1234')
            user.save()

        # 2. Create markets
        nse, _ = Market.objects.get_or_create(symbol='NSE', defaults={'name': 'Nairobi Securities Exchange'})
        nasdaq, _ = Market.objects.get_or_create(symbol='NASDAQ', defaults={'name': 'NASDAQ Stock Market'})
        crypto_mkt, _ = Market.objects.get_or_create(symbol='CRYPTO', defaults={'name': 'Global Cryptocurrency Market'})
        com_mkt, _ = Market.objects.get_or_create(symbol='COMEX', defaults={'name': 'Commodities Exchange'})

        market_map = {
            'NSE': nse,
            'NASDAQ': nasdaq,
            'CRYPTO': crypto_mkt,
            'COMMODITIES': com_mkt
        }

        # 3. Create Assets
        asset_objs = {}
        for sym, d in ASSETS.items():
            mkt = market_map.get(d.get('market'), nasdaq)
            asset, _ = Asset.objects.update_or_create(
                symbol=sym,
                defaults={
                    'name': d['name'],
                    'market': mkt,
                    'current_price': Decimal(str(d['price']))
                }
            )
            asset_objs[sym] = asset

        # 4. Create Portfolio
        portfolio, _ = Portfolio.objects.get_or_create(
            user=user,
            defaults={'name': 'Growth & Dividend Portfolio'}
        )

        # 5. Create Watchlist
        watchlist, _ = Watchlist.objects.get_or_create(
            user=user,
            defaults={'name': 'Primary Watchlist'}
        )
        for sym in ['SCOM', 'EQTY', 'AAPL', 'NVDA', 'BTC']:
            if sym in asset_objs:
                watchlist.assets.add(asset_objs[sym])

        # 6. Create Transactions
        for tx in USER_PORTFOLIO['transactions']:
            sym = tx['asset_symbol']
            if sym in asset_objs:
                Transaction.objects.get_or_create(
                    portfolio=portfolio,
                    asset=asset_objs[sym],
                    action=tx['type'],
                    quantity=10,
                    price_at_transaction=Decimal(str(asset_objs[sym].current_price or 10.0)),
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded PesaMarkets database!"))
