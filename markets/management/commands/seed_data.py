from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from markets.models import Market, Asset, Watchlist, Portfolio, Transaction, UserProfile, OTPVerification
from markets.data import ASSETS, USER_PORTFOLIO, BONDS_CATALOG

class Command(BaseCommand):
    help = 'Seeds initial markets, assets, watchlist, user portfolio, and demo credentials with OTP'

    def handle(self, *args, **options):
        self.stdout.write("Seeding PesaMarkets database...")
        
        # 1. Create or get demo user (Trader)
        user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@pesamarkets.com',
                'first_name': 'Richard',
                'last_name': 'Cooper'
            }
        )
        user.set_password('pesa1234')
        user.save()

        # Ensure user profile
        user_profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '+254 712 345 678',
                'tier': 'Terminal Pro Tier',
                'cash_balance_usd': Decimal('5212.17'),
                'kyc_verified': True,
                'otp_enabled': False
            }
        )
        user_profile.cash_balance_usd = Decimal('5212.17')
        user_profile.otp_enabled = False
        user_profile.save()

        # 2. Create or get admin superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pesamarkets.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin1234')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'phone_number': '+254 700 000 000',
                'tier': 'Institutional Admin',
                'cash_balance_usd': Decimal('100000.00'),
                'kyc_verified': True,
                'otp_enabled': False
            }
        )
        admin_profile.otp_enabled = False
        admin_profile.save()

        # 3. Create markets
        def get_or_create_seeded_market(sym, mkt_name):
            mkt = Market.objects.filter(symbol=sym).first()
            if not mkt:
                mkt = Market.objects.create(symbol=sym, name=mkt_name)
            # Remove any accidental duplicate rows
            Market.objects.filter(symbol=sym).exclude(id=mkt.id).delete()
            return mkt

        nse = get_or_create_seeded_market('NSE', 'Nairobi Securities Exchange')
        nasdaq = get_or_create_seeded_market('NASDAQ', 'NASDAQ Stock Market')
        nyse = get_or_create_seeded_market('NYSE', 'New York Stock Exchange')
        lse = get_or_create_seeded_market('LSE', 'London Stock Exchange')
        tse = get_or_create_seeded_market('TSE', 'Tokyo Stock Exchange')
        us_treasury = get_or_create_seeded_market('US_TREASURY', 'United States Department of the Treasury')
        uk_dmo = get_or_create_seeded_market('UK_DMO', 'United Kingdom Debt Management Office')
        mof_japan = get_or_create_seeded_market('MOF_JAPAN', 'Ministry of Finance Japan')
        cbk_mkt = get_or_create_seeded_market('CBK', 'Central Bank of Kenya (Fixed Income)')
        com_mkt = get_or_create_seeded_market('COMEX', 'Commodity Exchange (COMEX)')
        nymex = get_or_create_seeded_market('NYMEX', 'New York Mercantile Exchange (NYMEX)')
        ice = get_or_create_seeded_market('ICE', 'Intercontinental Exchange (ICE)')
        cbot = get_or_create_seeded_market('CBOT', 'Chicago Board of Trade (CBOT)')

        # Clean up any legacy crypto markets or assets
        Market.objects.filter(symbol='CRYPTO').delete()
        Asset.objects.filter(category='crypto').delete()

        market_map = {
            'NSE': nse,
            'NASDAQ': nasdaq,
            'NYSE': nyse,
            'LSE': lse,
            'TSE': tse,
            'US_TREASURY': us_treasury,
            'UK_DMO': uk_dmo,
            'MOF_JAPAN': mof_japan,
            'COMMODITIES': com_mkt,
            'COMEX': com_mkt,
            'NYMEX': nymex,
            'ICE': ice,
            'CBOT': cbot,
            'CBK': cbk_mkt
        }

        # 4. Create Assets from ASSETS dictionary
        asset_objs = {}
        for sym, d in ASSETS.items():
            mkt = market_map.get(d.get('market'), nasdaq)
            asset, _ = Asset.objects.update_or_create(
                symbol=sym,
                defaults={
                    'name': d.get('name', sym),
                    'market': mkt,
                    'current_price': Decimal(str(d.get('price', 0.0))),
                    'currency': d.get('currency', 'USD'),
                    'category': d.get('category', 'equities'),
                    'change_percent': float(d.get('change_percent', 0.0)),
                    'top_50_rank': d.get('top_50_rank'),
                    'is_top_50': d.get('is_top_50', False),
                    'underperformance_warning': d.get('underperformance_warning', False),
                    'warning_reason': d.get('warning_reason', ''),
                    'christian_ethics_score': d.get('christian_ethics_score', 95),
                    'christian_ethics_notes': d.get('christian_ethics_notes', 'Verified Ethical & Responsible Investment'),
                    'status': d.get('status', 'top_50')
                }
            )
            asset_objs[sym] = asset

        # 5. Create Bond & T-Bill Assets from BONDS_CATALOG
        for b_sym, b_data in BONDS_CATALOG.items():
            if b_sym not in asset_objs:
                mkt = market_map.get(b_data.get('market'), cbk_mkt)
                asset, _ = Asset.objects.update_or_create(
                    symbol=b_sym,
                    defaults={
                        'name': b_data.get('name', b_sym),
                        'market': mkt,
                        'current_price': Decimal(str(b_data.get('price', 100.0))),
                        'currency': b_data.get('currency', 'KES'),
                        'category': 'bonds',
                        'change_percent': float(b_data.get('change_percent', 0.0))
                    }
                )
                asset_objs[b_sym] = asset

        # Prune any stale or non-compliant assets from older seeds
        valid_symbols = set(ASSETS.keys()) | set(BONDS_CATALOG.keys())
        Asset.objects.exclude(symbol__in=valid_symbols).delete()

        # 6. Create Portfolio
        portfolio, _ = Portfolio.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Growth & Dividend Portfolio',
                'cash_balance_usd': Decimal('5212.17')
            }
        )

        # 7. Create Watchlist
        watchlist, _ = Watchlist.objects.get_or_create(
            user=user,
            defaults={'name': 'Primary Watchlist'}
        )
        for sym in ['SCOM', 'EQTY', 'AAPL', 'NVDA', 'UST10Y', 'UKG10Y', 'JGB10Y', 'IFB10Y']:
            if sym in asset_objs:
                watchlist.assets.add(asset_objs[sym])

        # 8. Create Transactions
        for tx in USER_PORTFOLIO.get('transactions', []):
            sym = tx.get('symbol') or tx.get('asset_symbol')
            if sym in asset_objs:
                Transaction.objects.get_or_create(
                    portfolio=portfolio,
                    asset=asset_objs[sym],
                    action=tx.get('type', 'BUY'),
                    quantity=10.0,
                    defaults={
                        'price_at_transaction': Decimal(str(asset_objs[sym].current_price or 10.0)),
                        'total_amount': Decimal(str((asset_objs[sym].current_price or 10.0) * 10)),
                        'reference': tx.get('id', f"TX-{Transaction.objects.count() + 9000}"),
                        'status': tx.get('status', 'Completed')
                    }
                )

        # 9. Create standard demo OTP code
        OTPVerification.objects.filter(user=user, purpose='login').delete()
        demo_otp = OTPVerification.objects.create(
            user=user,
            purpose='login',
            email_or_phone=user.email,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(days=7),
            is_used=False
        )

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Successfully seeded PesaMarkets database!"))
        self.stdout.write(self.style.SUCCESS("Demo Trader Credentials:"))
        self.stdout.write(self.style.SUCCESS("   Username: user"))
        self.stdout.write(self.style.SUCCESS("   Password: pesa1234"))
        self.stdout.write(self.style.SUCCESS("   Default OTP: 123456"))
        self.stdout.write(self.style.SUCCESS("Admin Credentials:"))
        self.stdout.write(self.style.SUCCESS("   Username: admin"))
        self.stdout.write(self.style.SUCCESS("   Password: admin1234"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
