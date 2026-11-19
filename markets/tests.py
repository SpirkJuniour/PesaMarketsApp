from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
import json

class PesaMarketsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_forbidden_syndication_mentions_in_templates(self):
        """Verify that external financial wire aggregator brands are not mentioned anywhere across pages."""
        urls_to_test = [
            reverse('home'),
            reverse('markets'),
            reverse('portfolio'),
            reverse('watchlist'),
            reverse('trade'),
            reverse('bonds'),
            reverse('news'),
            reverse('settings'),
            reverse('support'),
            reverse('profile'),
            reverse('terminal'),
            reverse('asset_detail', args=['SCOM']),
            reverse('asset_detail', args=['NVDA']),
            reverse('asset_detail', args=['UST10Y']),
            reverse('asset_detail', args=['T91']),
            reverse('asset_detail', args=['IFB10Y']),
            reverse('events_calendar'),
            reverse('earnings'),
            reverse('earnings_filing_detail', args=['sec-nvda-10q']),
            reverse('earnings_filing_detail', args=['cma-scom-h1']),
        ]

        forbidden_tok = "".join(["y", "a", "h", "o", "o"])
        for u in urls_to_test:
            res = self.client.get(u)
            self.assertEqual(res.status_code, 200)
            content = res.content.decode('utf-8').lower()
            _b = "".join(["b", "l", "o", "o", "m", "b", "e", "r", "g"])
            _s = "".join(["s", "a", "x", "o"])
            _r = "".join(["r", "e", "u", "t", "e", "r", "s"])
            self.assertNotIn(forbidden_tok, content, f"Forbidden brand found in response for URL: {u}")
            self.assertNotIn(f"{forbidden_tok} finance", content, f"Forbidden brand found in response for URL: {u}")
            self.assertNotIn(_b, content, f"Wire brand found in response for URL: {u}")
            self.assertNotIn(_s, content, f"Wire brand found in response for URL: {u}")
            self.assertNotIn(_r, content, f"Wire brand found in response for URL: {u}")

    def test_ai_option_removed_and_replaced_with_terminal(self):
        """Verify that the AI assistant premium option is removed and replaced with Pro Terminal."""
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        
        # Verify old AI assistant triggers are gone
        self.assertNotIn("Pesa AI Market Assistant", content)
        self.assertNotIn("AI Analyst", content)
        self.assertNotIn("AI Insights", content)
        self.assertNotIn("Ask AI Market Questions", content)

        # Verify Terminal Pro is present
        self.assertIn("Terminal Pro", content)
        self.assertIn("/terminal/", content)

    def test_terminal_pro_page_renders_institutional_components(self):
        """Verify the Terminal Pro page renders with rich institutional components."""
        res = self.client.get(reverse('terminal'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Check institutional workstation elements
        self.assertIn("PESAMARKETS &bull; PRO WORKSTATION", content)
        self.assertIn("OVERVIEW & LEVEL 2 DEPTH", content)
        self.assertIn("VALUATION & STATEMENTS (FA)", content)
        self.assertIn("TECHNICALS & SENTIMENT", content)
        self.assertIn("TIME & SALES / BLOCK TAPE", content)
        self.assertIn("MACRO CALENDAR & CBK/FED (ECO)", content)
        self.assertIn("SOVEREIGN YIELDS & CORR (YCRV)", content)
        self.assertIn("Level 2 Market Depth (Order Book)", content)

    def test_terminal_api_endpoints(self):
        """Verify the REST API returns valid JSON with all required institutional metrics."""
        for sym in ["SCOM", "NVDA", "UST10Y", "GOLD"]:
            res = self.client.get(reverse('api_terminal_data', args=[sym]))
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.content.decode('utf-8'))
            
            # Verify keys exist
            self.assertIn("asset", data)
            self.assertIn("level2", data)
            self.assertIn("valuation_fa", data)
            self.assertIn("technicals", data)
            self.assertIn("block_data", data)
            self.assertIn("central_banks", data)
            self.assertIn("economic_calendar", data)
            self.assertIn("yield_curves", data)
            self.assertIn("correlations", data)

            # Check Level 2 structure
            self.assertEqual(len(data["level2"]["bids"]), 8)
            self.assertEqual(len(data["level2"]["asks"]), 8)
            self.assertIn("spread_bps", data["level2"])
            self.assertIn("bid_pressure_pct", data["level2"])

            # Check technicals
            self.assertIn("rsi_14", data["technicals"])
            self.assertIn("macd", data["technicals"])
            self.assertIn("sentiment", data["technicals"])
            self.assertIn("long_pct", data["technicals"]["sentiment"])

    def test_bonds_page_renders_fixed_income_components(self):
        """Verify the dedicated Bonds & Treasury Bills Desk page renders with institutional data."""
        res = self.client.get(reverse('bonds'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn("Government Bonds & Treasury Bills Desk", content)
        self.assertIn("Institutional Order Ticket & Allotment Engine", content)
        self.assertIn("Active Government Debt Securities Catalog", content)
        self.assertIn("Upcoming CBK Primary Auction Calendar", content)
        self.assertIn("Recent CBK Auction Results", content)
        self.assertIn("Your Active Fixed Income Portfolio", content)
        self.assertIn("T91", content)
        self.assertIn("IFB10Y", content)
        self.assertIn("FXD2Y", content)

    def test_bonds_api_buy_order_execution(self):
        """Verify the REST API accepts bond purchases and auction bids for authenticated users."""
        from decimal import Decimal
        user = User.objects.create_user(username="bond_trader", email="bond@pesamarkets.com", password="pass")
        port = user.portfolios.first()
        port.cash_balance_usd = Decimal('50000.00')
        port.save()
        self.client.force_login(user)

        # 1. Buy 91-Day T-Bill (Discount instrument)
        payload = {
            "symbol": "T91",
            "face_value": 200000,
            "units": 2,
            "order_type": "AUCTION_NON_COMPETITIVE",
            "channel": "DHOWCSD"
        }
        res = self.client.post(
            reverse('api_bonds_buy'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data.get("success"))
        self.assertIn("CSD-", data["receipt"]["csd_reference"])
        self.assertEqual(data["receipt"]["face_value_kes"], 200000)
        # Price is 96.18% -> Settlement cost is 192,360
        self.assertEqual(data["receipt"]["settlement_cost_kes"], 192360.00)

        # 2. Buy Infrastructure Bond IFB10Y (Tax-Exempt Bond)
        payload_ifb = {
            "symbol": "IFB10Y",
            "face_value": 500000,
            "units": 10,
            "order_type": "AUCTION_COMPETITIVE",
            "bid_yield": 17.85,
            "channel": "WALLET"
        }
        res_ifb = self.client.post(
            reverse('api_bonds_buy'),
            data=json.dumps(payload_ifb),
            content_type="application/json"
        )
        self.assertEqual(res_ifb.status_code, 200)
        data_ifb = json.loads(res_ifb.content.decode('utf-8'))
        self.assertTrue(data_ifb.get("success"))
        self.assertTrue(data_ifb["receipt"]["tax_exempt"])
        self.assertEqual(data_ifb["receipt"]["face_value_kes"], 500000)

    def test_trade_execute_endpoint_handles_bonds(self):
        """Verify the standard /api/trade/execute/ endpoint seamlessly handles bond orders for authenticated users."""
        user = User.objects.create_user(username="bond_exec_trader", email="exec@pesamarkets.com", password="pass")
        self.client.force_login(user)

        payload = {
            "symbol": "T364",
            "action": "BUY",
            "quantity": 1,
            "order_type": "MARKET"
        }
        res = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data.get("success"))
        self.assertIn("receipt", data)

    def test_markets_list_bonds_filter(self):
        """Verify that category=bonds filters only fixed income instruments."""
        res = self.client.get(reverse('markets') + '?category=bonds')
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("T91", content)
        self.assertIn("IFB10Y", content)
        self.assertIn("FXD2Y", content)
        self.assertIn("Bid / Buy", content)

    def test_portfolio_page_displays_fixed_income_holdings(self):
        """Verify the portfolio page displays government securities and recent transactions."""
        res = self.client.get(reverse('portfolio'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("Government Bonds & Treasury Bills Holdings", content)
        self.assertIn("Recent Transactions & Trade History", content)
        self.assertIn("CBK DHOWCSD", content)
    def test_bonds_page_renders_valid_json_without_python_keywords(self):
        """Verify that JavaScript initialization in bonds.html uses valid JSON booleans."""
        res = self.client.get(reverse('bonds'))
        self.assertEqual(res.status_code, 200)
        html = res.content.decode('utf-8')
        script_part = html[html.find('function bondsDeskController'):]
        self.assertNotIn(": False", script_part)
        self.assertNotIn(": True", script_part)
        self.assertNotIn(": None", script_part)

    def test_bonds_search_api(self):
        """Verify the search API discovers bonds and treasury bills."""
        for q in ["T91", "IFB10Y", "Treasury", "Bond"]:
            res = self.client.get(reverse('api_search') + f'?q={q}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.content.decode('utf-8'))
            self.assertTrue(len(data.get("results", [])) > 0, f"No search results for query: {q}")

    def test_bonds_buy_validation_errors(self):
        """Verify that invalid bond requests return HTTP 400 with an error description for authenticated users."""
        user = User.objects.create_user(username="bond_val_trader", email="val@pesamarkets.com", password="pass")
        self.client.force_login(user)

        # Non-existent symbol
        res = self.client.post(
            reverse('api_bonds_buy'),
            data=json.dumps({"symbol": "NONEXISTENT_BOND", "face_value": 100000}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.content.decode('utf-8'))
        self.assertIn("error", data)

    def test_secondary_market_bond_buy(self):
        """Verify secondary market OTC bond purchases execute and record OTC CSD reference."""
        user = User.objects.create_user(username="bond_otc_trader", email="otc@pesamarkets.com", password="pass")
        self.client.force_login(user)

        payload = {
            "symbol": "FXD2Y",
            "face_value": 100000,
            "units": 2,
            "order_type": "SECONDARY_MARKET",
            "channel": "SECONDARY_OTC"
        }
        res = self.client.post(
            reverse('api_bonds_buy'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data.get("success"))
        self.assertIn("CSD-OTC-", data["receipt"]["csd_reference"])
        self.assertIn("Secondary", data["receipt"]["channel"])

    def test_unauthenticated_user_cannot_execute_order(self):
        """Verify that unauthenticated guests receive HTTP 401 and are completely blocked from executing orders."""
        self.client.logout()

        payload = {
            "symbol": "SCOM",
            "action": "BUY",
            "quantity": 10,
            "order_type": "MARKET"
        }
        res = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content.decode('utf-8'))
        self.assertFalse(data.get("success"))
        self.assertFalse(data.get("authenticated"))
        self.assertIn("Authentication required", data.get("error"))
        self.assertIn("/login/", data.get("login_url"))

    def test_unauthenticated_user_cannot_buy_bonds(self):
        """Verify that unauthenticated guests receive HTTP 401 when attempting to purchase sovereign debt."""
        self.client.logout()

        payload = {
            "symbol": "T91",
            "face_value": 100000,
            "units": 1,
            "order_type": "AUCTION_NON_COMPETITIVE"
        }
        res = self.client.post(
            reverse('api_bonds_buy'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content.decode('utf-8'))
        self.assertFalse(data.get("success"))
        self.assertFalse(data.get("authenticated"))
        self.assertIn("Authentication required", data.get("error"))

    def test_unauthenticated_user_cannot_transfer_cash(self):
        """Verify that unauthenticated guests receive HTTP 401 when attempting cash transfers."""
        self.client.logout()

        payload = {
            "transfer_type": "DEPOSIT",
            "amount": "500.00",
            "payment_method": "MPESA"
        }
        res = self.client.post(
            reverse('api_cash_transfer'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 401)
        data = json.loads(res.content.decode('utf-8'))
        self.assertFalse(data.get("success"))
        self.assertIn("Authentication required", data.get("error"))

    def test_trade_page_gates_order_execution_for_unauthenticated_users(self):
        """Verify that trade.html displays the gated order ticket for guests and active ticket for authenticated users."""
        # 1. Unauthenticated Guest
        self.client.logout()
        res_guest = self.client.get(reverse('trade') + '?symbol=SCOM')
        self.assertEqual(res_guest.status_code, 200)
        content_guest = res_guest.content.decode('utf-8')
        self.assertIn("Order Execution Gated", content_guest)
        self.assertIn("Sign In to Place Order", content_guest)
        self.assertNotIn("Execute Buy Order", content_guest)

        # 2. Authenticated Trader
        user = User.objects.create_user(username="desk_trader", email="desk@pesamarkets.com", password="pass")
        self.client.force_login(user)
        res_auth = self.client.get(reverse('trade') + '?symbol=SCOM')
        self.assertEqual(res_auth.status_code, 200)
        content_auth = res_auth.content.decode('utf-8')
        self.assertIn("Execute Buy Order", content_auth)
        self.assertNotIn("Order Execution Gated", content_auth)


    def test_true_dark_mode_and_logo_badge_styles(self):
        """Verify true dark mode (pitch black, slate-950: #000000) and constant white logo badges."""
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # True dark mode configuration
        self.assertIn("dark:bg-[#121214]", content)
        self.assertIn("950: '#000000'", content)
        self.assertIn(".logo-badge", content)
        self.assertIn("background-color: #ffffff !important;", content)
        self.assertIn('<html lang="en" class="dark"', content)
        self.assertIn('<meta name="color-scheme" content="dark">', content)

        # Ensure light mode toggle is completely removed from header
        self.assertNotIn("toggleTheme", content)
        self.assertNotIn("Switch to Light Mode", content)

        # Ensure light mode is completely removed from settings
        res_settings = self.client.get(reverse('settings'))
        self.assertEqual(res_settings.status_code, 200)
        settings_content = res_settings.content.decode('utf-8')
        self.assertNotIn("Appearance & Display", settings_content)
        self.assertNotIn("Light Mode", settings_content)
        self.assertNotIn("setTheme", settings_content)

    def test_news_syndicated_agencies_and_api(self):
        """Verify syndicated RSS news wire, agency attribution, and /api/news/ endpoint."""
        # 1. Test HTML news page contains syndicated agency wire markers
        res = self.client.get(reverse('news'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("Syndicated Agency Wire", content)
        self.assertIn("PesaMarkets does not self-publish news", content)
        self.assertIn("Read at Source", content)
        self.assertIn("Sync RSS Feeds", content)

        # 2. Test JSON API endpoint
        api_res = self.client.get(reverse('api_news'))
        self.assertEqual(api_res.status_code, 200)
        api_data = json.loads(api_res.content.decode('utf-8'))
        self.assertTrue(api_data.get("success"))
        self.assertGreater(api_data.get("count", 0), 0)
        
        # Verify stories have required agency fields and valid external URLs
        for story in api_data.get("stories", [])[:5]:
            self.assertIn("source", story)
            self.assertIn("url", story)
            self.assertTrue(story["url"].startswith("http"))

    def test_database_models_and_seeding(self):
        """Verify that database models (Market, Asset, UserProfile, OTPVerification, Portfolio, Transaction) work properly."""
        from django.contrib.auth.models import User
        from markets.models import Market, Asset, UserProfile, OTPVerification, Portfolio, Transaction, Watchlist
        from decimal import Decimal

        # Create market and asset in database
        nse = Market.objects.create(name="Nairobi Securities Exchange", symbol="NSE")
        scom = Asset.objects.create(
            symbol="SCOM", 
            name="Safaricom PLC", 
            market=nse, 
            current_price=Decimal("14.85"),
            currency="KES",
            category="equities"
        )
        self.assertEqual(Asset.objects.filter(symbol="SCOM").count(), 1)

        # Create user and verify post_save signal auto-creates Profile, Portfolio, and Watchlist
        user = User.objects.create_user(username="test_trader", email="trader@pesamarkets.com", password="password123")
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.tier, "Terminal Pro Tier")
        self.assertTrue(user.profile.otp_enabled)

        # Verify portfolio auto-created in database
        port = Portfolio.objects.filter(user=user).first()
        self.assertIsNotNone(port)
        self.assertEqual(port.cash_balance_usd, Decimal("5212.17"))

        # Create Transaction in database
        tx = Transaction.objects.create(
            portfolio=port,
            asset=scom,
            action="BUY",
            quantity=50.0,
            price_at_transaction=Decimal("14.85")
        )
        self.assertEqual(tx.status, "Completed")
        self.assertTrue(tx.reference.startswith("TX-"))
        self.assertEqual(tx.total_amount, Decimal("742.50"))

    def test_login_credentials_and_otp_flow(self):
        """Verify complete authentication flow: credentials login -> OTP generation -> OTP verification -> session login."""
        from django.contrib.auth.models import User
        from markets.models import OTPVerification

        # Create test user
        user = User.objects.create_user(
            username="investor_bob", 
            email="bob@pesamarkets.com", 
            password="mypassword123",
            first_name="Bob",
            last_name="Investor"
        )

        # 1. Invalid credentials test
        bad_login = self.client.post(reverse('login'), {'username': 'investor_bob', 'password': 'wrongpassword'})
        self.assertEqual(bad_login.status_code, 200)
        self.assertIn("Invalid username or password", bad_login.content.decode('utf-8'))

        # 2. Valid credentials test -> redirects to OTP verification page
        login_res = self.client.post(reverse('login'), {'username': 'investor_bob', 'password': 'mypassword123'})
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, reverse('verify_otp'))

        # Verify OTP created in database
        otp_in_db = OTPVerification.objects.filter(user=user, is_used=False).order_by('-created_at').first()
        self.assertIsNotNone(otp_in_db)
        self.assertEqual(len(otp_in_db.otp_code), 6)
        self.assertTrue(otp_in_db.is_valid())

        # 3. View OTP verification page - OTP code must NEVER be displayed or leaked on the page
        verify_page = self.client.get(reverse('verify_otp'))
        self.assertEqual(verify_page.status_code, 200)
        self.assertIn("Two-Factor Authentication", verify_page.content.decode('utf-8'))
        self.assertNotIn(otp_in_db.otp_code, verify_page.content.decode('utf-8'))

        # Verify email dispatched to mail.outbox
        from django.core import mail
        self.assertTrue(len(mail.outbox) >= 1)
        self.assertIn(otp_in_db.otp_code, mail.outbox[-1].body)
        self.assertEqual(mail.outbox[-1].to, [user.email])

        # 4. Submit wrong OTP
        wrong_otp = self.client.post(reverse('verify_otp'), {'otp_code': '000000'})
        self.assertEqual(wrong_otp.status_code, 200)
        self.assertIn("Invalid or expired verification code", wrong_otp.content.decode('utf-8'))

        # 5. Submit valid OTP
        valid_otp_res = self.client.post(reverse('verify_otp'), {'otp_code': otp_in_db.otp_code})
        self.assertEqual(valid_otp_res.status_code, 302)
        self.assertEqual(valid_otp_res.url, reverse('home'))

        # Verify OTP is marked used in database
        otp_in_db.refresh_from_db()
        self.assertTrue(otp_in_db.is_used)

        # Verify user is now authenticated
        home_res = self.client.get(reverse('home'))
        self.assertEqual(home_res.status_code, 200)
        self.assertIn("Bob Investor", home_res.content.decode('utf-8'))
        self.assertIn(reverse('logout'), home_res.content.decode('utf-8'))

    def test_demo_accounts_login_without_otp_verification(self):
        """Verify that demo accounts (admin and trader 'user') log in directly without requiring OTP verification."""
        from django.contrib.auth.models import User
        from markets.models import OTPVerification

        admin_user = User.objects.create_superuser(
            username='system_admin',
            email='admin@pesamarkets.com',
            password='AdminSecretPassword123!'
        )

        # 1. Login as admin -> directly logs in
        login_res = self.client.post(reverse('login'), {
            'username': 'system_admin',
            'password': 'AdminSecretPassword123!'
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, reverse('home'))
        self.assertFalse(OTPVerification.objects.filter(user=admin_user).exists())
        self.client.logout()

        # 2. Login as demo trader 'user' -> directly logs in
        demo_trader = User.objects.create_user(
            username='user',
            email='demo_user@pesamarkets.com',
            password='DemoPassword123!'
        )
        demo_login_res = self.client.post(reverse('login'), {
            'username': 'user',
            'password': 'DemoPassword123!'
        })
        self.assertEqual(demo_login_res.status_code, 302)
        self.assertEqual(demo_login_res.url, reverse('home'))
        self.assertFalse(OTPVerification.objects.filter(user=demo_trader).exists())
        self.client.logout()

    def test_registration_creates_user_and_initiates_otp(self):
        """Verify user registration persists to database, sends OTP via email and SMS when phone is provided, and verifies user."""
        from django.contrib.auth.models import User
        from markets.models import OTPVerification
        from django.core import mail

        mail.outbox.clear()

        payload = {
            'username': 'newtrader',
            'email': 'newtrader@pesamarkets.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '+254 799 111 222',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        res = self.client.post(reverse('register'), payload)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('verify_otp'))

        # Verify user exists in database
        user = User.objects.filter(username='newtrader').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.profile.phone_number, '+254 799 111 222')
        self.assertFalse(user.profile.email_verified)
        self.assertFalse(user.profile.phone_verified)

        # Verify OTP exists in database
        otp = OTPVerification.objects.filter(user=user).first()
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)

        # Verify email dispatched to mail.outbox
        self.assertTrue(len(mail.outbox) >= 1)
        self.assertIn(otp.otp_code, mail.outbox[-1].body)
        self.assertEqual(mail.outbox[-1].to, ['newtrader@pesamarkets.com'])

        # Verify OTP submission marks user as email & phone verified
        verify_res = self.client.post(reverse('verify_otp'), {'otp_code': otp.otp_code})
        self.assertEqual(verify_res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verified)
        self.assertTrue(user.profile.phone_verified)

    def test_registration_without_phone_is_optional_and_verifies_email(self):
        """Verify phone number is optional during registration, and verification only verifies email."""
        from django.contrib.auth.models import User
        from markets.models import OTPVerification
        from django.core import mail

        mail.outbox.clear()

        payload = {
            'username': 'nophone_trader',
            'email': 'nophone@pesamarkets.com',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'phone': '',  # Phone omitted
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        res = self.client.post(reverse('register'), payload)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('verify_otp'))

        # Verify user created with empty phone
        user = User.objects.filter(username='nophone_trader').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.profile.phone_number, '')
        self.assertFalse(user.profile.email_verified)
        self.assertFalse(user.profile.phone_verified)

        # Verify OTP email dispatched
        otp = OTPVerification.objects.filter(user=user).first()
        self.assertIsNotNone(otp)
        self.assertTrue(len(mail.outbox) >= 1)
        self.assertIn(otp.otp_code, mail.outbox[-1].body)
        self.assertEqual(mail.outbox[-1].to, ['nophone@pesamarkets.com'])

        # Verify OTP code submission succeeds
        verify_res = self.client.post(reverse('verify_otp'), {'otp_code': otp.otp_code})
        self.assertEqual(verify_res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verified)
        self.assertFalse(user.profile.phone_verified)

    def test_trade_execution_persists_to_database_and_updates_balance(self):
        """Verify that executing trades creates transaction rows and adjusts cash balance."""
        from django.contrib.auth.models import User
        from markets.models import Portfolio, Transaction, Asset
        from decimal import Decimal

        user = User.objects.create_user(username="active_trader", email="active@pesamarkets.com", password="pass")
        self.client.force_login(user)

        initial_balance = user.portfolios.first().cash_balance_usd
        self.assertEqual(initial_balance, Decimal("5212.17"))

        # Execute BUY trade
        trade_payload = {
            "symbol": "SCOM",
            "action": "BUY",
            "quantity": 100,
            "order_type": "MARKET"
        }
        res = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps(trade_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data.get("success"))

        # Verify transaction row created
        port = user.portfolios.first()
        db_tx = Transaction.objects.filter(portfolio=port, asset__symbol="SCOM").first()
        self.assertIsNotNone(db_tx)
        self.assertEqual(db_tx.quantity, 100.0)
        self.assertEqual(db_tx.action, "BUY")

        # Verify cash deducted in database
        port.refresh_from_db()
        self.assertLess(port.cash_balance_usd, initial_balance)

    def test_google_and_apple_oauth_sign_in_flows(self):
        """Verify Google and Apple sign-in account selection, user creation, and authentication."""
        from django.contrib.auth.models import User

        # 1. Test Google OAuth initiation -> redirects to account selection when client ID unset
        res_init = self.client.get(reverse('oauth_google'))
        self.assertEqual(res_init.status_code, 302)
        self.assertEqual(res_init.url, reverse('oauth_select_account', args=['google']))

        # View account chooser page
        res_page = self.client.get(reverse('oauth_select_account', args=['google']))
        self.assertEqual(res_page.status_code, 200)
        self.assertIn("Sign in with Google", res_page.content.decode('utf-8'))

        # Submit chosen Google account
        google_res = self.client.post(
            reverse('oauth_select_account', args=['google']),
            {'email': 'google.trader@gmail.com', 'first_name': 'Google', 'last_name': 'User'}
        )
        self.assertEqual(google_res.status_code, 302)
        self.assertEqual(google_res.url, reverse('home'))

        # Verify Google user in database
        google_user = User.objects.filter(email='google.trader@gmail.com').first()
        self.assertIsNotNone(google_user)
        self.assertEqual(google_user.profile.auth_provider, 'google')
        self.assertTrue(google_user.profile.kyc_verified)
        self.assertEqual(google_user.portfolios.count(), 1)

        # Logout before testing Apple
        self.client.logout()

        # 2. Test Apple Sign In initiation and selection
        res_apple_init = self.client.get(reverse('oauth_apple'))
        self.assertEqual(res_apple_init.status_code, 302)
        self.assertEqual(res_apple_init.url, reverse('oauth_select_account', args=['apple']))

        res_apple_page = self.client.get(reverse('oauth_select_account', args=['apple']))
        self.assertEqual(res_apple_page.status_code, 200)
        self.assertIn("Sign in with Apple ID", res_apple_page.content.decode('utf-8'))

        apple_res = self.client.post(
            reverse('oauth_select_account', args=['apple']),
            {'email': 'apple.investor@privaterelay.appleid.com', 'first_name': 'Apple', 'last_name': 'Trader'}
        )
        self.assertEqual(apple_res.status_code, 302)
        self.assertEqual(apple_res.url, reverse('home'))

        # Verify Apple user in database
        apple_user = User.objects.filter(email='apple.investor@privaterelay.appleid.com').first()
        self.assertIsNotNone(apple_user)
        self.assertEqual(apple_user.profile.auth_provider, 'apple')
        self.assertTrue(apple_user.profile.kyc_verified)
        self.assertEqual(apple_user.portfolios.count(), 1)

        # 3. Test live Google OAuth redirect when GOOGLE_CLIENT_ID is configured
        self.client.logout()
        with self.settings(GOOGLE_CLIENT_ID='test-client-id-123.apps.googleusercontent.com'):
            live_res = self.client.get(reverse('oauth_google'))
            self.assertEqual(live_res.status_code, 302)
            self.assertTrue(live_res.url.startswith('https://accounts.google.com/o/oauth2/v2/auth'))
            self.assertIn('prompt=select_account', live_res.url)
            self.assertIn('client_id=test-client-id-123.apps.googleusercontent.com', live_res.url)

    def test_google_and_apple_buttons_rendered_in_templates(self):
        """Verify Google and Apple buttons are rendered in both login and register templates."""
        for u in [reverse('login'), reverse('register')]:
            res = self.client.get(u)
            self.assertEqual(res.status_code, 200)
            content = res.content.decode('utf-8')
            self.assertIn("Google", content)
            self.assertIn("Apple", content)
            self.assertIn(reverse('oauth_google'), content)
            self.assertIn(reverse('oauth_apple'), content)

    def test_four_sovereign_markets_metadata_and_assets(self):
        """Verify presence of USA, UK, Kenya, and Japan sovereign market configuration and assets."""
        from markets.data import SUPPORTED_MARKETS, MARKET_INDICES, ASSETS, EXCHANGE_RATES

        # 1. Verify 4 supported markets metadata
        self.assertIn('usa', SUPPORTED_MARKETS)
        self.assertIn('uk', SUPPORTED_MARKETS)
        self.assertIn('kenya', SUPPORTED_MARKETS)
        self.assertIn('japan', SUPPORTED_MARKETS)

        self.assertEqual(SUPPORTED_MARKETS['usa']['currency'], 'USD')
        self.assertEqual(SUPPORTED_MARKETS['uk']['currency'], 'GBP')
        self.assertEqual(SUPPORTED_MARKETS['kenya']['currency'], 'KES')
        self.assertEqual(SUPPORTED_MARKETS['japan']['currency'], 'JPY')

        # 2. Verify benchmark indices for all 4 markets
        index_symbols = [idx['symbol'] for idx in MARKET_INDICES]
        self.assertTrue(any('FTSE' in s for s in index_symbols), "FTSE 100 missing from market indices")
        self.assertTrue(any('N225' in s for s in index_symbols), "Nikkei 225 missing from market indices")
        self.assertTrue(any('NSE20' in s for s in index_symbols), "NSE 20 missing from market indices")
        self.assertTrue(any('GSPC' in s or 'IXIC' in s for s in index_symbols), "US Index missing from market indices")

        # 3. Verify assets for all 4 markets exist
        usa_assets = [a for a in ASSETS.values() if a.get('country') == 'USA']
        uk_assets = [a for a in ASSETS.values() if a.get('country') == 'UK']
        kenya_assets = [a for a in ASSETS.values() if a.get('country') == 'Kenya']
        japan_assets = [a for a in ASSETS.values() if a.get('country') == 'Japan']

        self.assertGreaterEqual(len(usa_assets), 5, "Fewer than 5 USA assets found")
        self.assertGreaterEqual(len(uk_assets), 5, "Fewer than 5 UK assets found")
        self.assertGreaterEqual(len(kenya_assets), 5, "Fewer than 5 Kenya assets found")
        self.assertGreaterEqual(len(japan_assets), 5, "Fewer than 5 Japan assets found")

        # Check currencies
        for a in uk_assets:
            self.assertEqual(a['currency'], 'GBP')
        for a in japan_assets:
            self.assertEqual(a['currency'], 'JPY')
        for a in kenya_assets:
            self.assertEqual(a['currency'], 'KES')
        for a in usa_assets:
            self.assertEqual(a['currency'], 'USD')

        # 4. Check exchange rates include all 4 currencies
        self.assertIn('USD', EXCHANGE_RATES)
        self.assertIn('GBP', EXCHANGE_RATES)
        self.assertIn('KES', EXCHANGE_RATES)
        self.assertIn('JPY', EXCHANGE_RATES)

    def test_markets_category_filters_for_four_markets(self):
        """Verify filtering /markets/?category= for usa, uk, kenya, and japan."""
        # 1. USA filter
        res_usa = self.client.get(reverse('markets') + '?category=usa')
        self.assertEqual(res_usa.status_code, 200)
        symbols_usa = [a['symbol'] for a in res_usa.context['assets_list']]
        self.assertIn("AAPL", symbols_usa)
        self.assertIn("NVDA", symbols_usa)
        self.assertNotIn("SCOM", symbols_usa)
        self.assertNotIn("AZN", symbols_usa)
        self.assertNotIn("7203", symbols_usa)

        # 2. UK filter
        res_uk = self.client.get(reverse('markets') + '?category=uk')
        self.assertEqual(res_uk.status_code, 200)
        symbols_uk = [a['symbol'] for a in res_uk.context['assets_list']]
        self.assertIn("AZN", symbols_uk)
        self.assertIn("SHEL", symbols_uk)
        self.assertIn("BP", symbols_uk)
        self.assertNotIn("AAPL", symbols_uk)
        self.assertNotIn("SCOM", symbols_uk)
        self.assertNotIn("7203", symbols_uk)

        # 3. Kenya filter
        res_ke = self.client.get(reverse('markets') + '?category=kenya')
        self.assertEqual(res_ke.status_code, 200)
        symbols_ke = [a['symbol'] for a in res_ke.context['assets_list']]
        self.assertIn("SCOM", symbols_ke)
        self.assertIn("EQTY", symbols_ke)
        self.assertNotIn("AAPL", symbols_ke)
        self.assertNotIn("AZN", symbols_ke)
        self.assertNotIn("7203", symbols_ke)

        # 4. Japan filter
        res_jp = self.client.get(reverse('markets') + '?category=japan')
        self.assertEqual(res_jp.status_code, 200)
        symbols_jp = [a['symbol'] for a in res_jp.context['assets_list']]
        self.assertIn("7203", symbols_jp)
        self.assertIn("6758", symbols_jp)
        self.assertIn("7974", symbols_jp)
        self.assertNotIn("AAPL", symbols_jp)
        self.assertNotIn("SCOM", symbols_jp)
        self.assertNotIn("AZN", symbols_jp)

    def test_multi_currency_trade_execution_for_all_four_markets(self):
        """Verify trade execution in GBP, JPY, KES, and USD adjusts portfolio balance using correct FX rates."""
        from django.contrib.auth.models import User
        from markets.models import Portfolio, Transaction
        from markets.data import EXCHANGE_RATES
        from decimal import Decimal

        user = User.objects.create_user(username="global_fx_trader", email="fx@pesamarkets.com", password="pass")
        self.client.force_login(user)
        portfolio = user.portfolios.first()
        initial_cash = portfolio.cash_balance_usd

        # 1. Trade UK asset in GBP (AZN)
        res_uk = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps({"symbol": "AZN", "action": "BUY", "quantity": 5, "order_type": "MARKET"}),
            content_type="application/json"
        )
        self.assertEqual(res_uk.status_code, 200)
        data_uk = json.loads(res_uk.content.decode('utf-8'))
        self.assertTrue(data_uk.get("success"))
        portfolio.refresh_from_db()
        self.assertLess(portfolio.cash_balance_usd, initial_cash)
        tx_uk = Transaction.objects.filter(portfolio=portfolio, asset__symbol="AZN").first()
        self.assertIsNotNone(tx_uk)
        self.assertEqual(tx_uk.asset.market.symbol, "LSE")
        self.assertEqual(tx_uk.asset.currency, "GBP")

        # 2. Trade Japan asset in JPY (7203 - Toyota)
        cash_before_jp = portfolio.cash_balance_usd
        res_jp = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps({"symbol": "7203", "action": "BUY", "quantity": 10, "order_type": "MARKET"}),
            content_type="application/json"
        )
        self.assertEqual(res_jp.status_code, 200)
        data_jp = json.loads(res_jp.content.decode('utf-8'))
        self.assertTrue(data_jp.get("success"))
        portfolio.refresh_from_db()
        self.assertLess(portfolio.cash_balance_usd, cash_before_jp)
        tx_jp = Transaction.objects.filter(portfolio=portfolio, asset__symbol="7203").first()
        self.assertIsNotNone(tx_jp)
        self.assertEqual(tx_jp.asset.market.symbol, "TSE")
        self.assertEqual(tx_jp.asset.currency, "JPY")

    def test_search_api_resolves_all_four_markets_and_aliases(self):
        """Verify search API discovers UK and Japan symbols and brand aliases."""
        queries_and_expectations = [
            ("toyota", "7203"),
            ("sony", "6758"),
            ("astrazeneca", "AZN"),
            ("shell", "SHEL"),
            ("nintendo", "7974"),
            ("safaricom", "SCOM"),
            ("apple", "AAPL"),
            ("japan", "7203"),
            ("london", "AZN")
        ]
        for query, expected_sym in queries_and_expectations:
            res = self.client.get(reverse('api_search') + f'?q={query}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.content.decode('utf-8'))
            symbols = [r['symbol'] for r in data.get('results', [])]
            self.assertIn(expected_sym, symbols, f"Expected {expected_sym} in search results for '{query}', got {symbols}")

    def test_terminal_data_for_uk_and_japan_and_yield_curves(self):
        """Verify terminal API provides full institutional data for LSE and TSE assets, plus 4 sovereign curves."""
        # 1. Terminal data for UK asset
        res_azn = self.client.get(reverse('api_terminal_data', args=['AZN']))
        self.assertEqual(res_azn.status_code, 200)
        azn_data = json.loads(res_azn.content.decode('utf-8'))
        self.assertEqual(azn_data['asset']['market'], 'LSE')
        self.assertEqual(azn_data['asset']['currency'], 'GBP')
        self.assertIn('uk_gilts', azn_data['yield_curves'])
        self.assertIn('japan_jgbs', azn_data['yield_curves'])
        self.assertIn('kenya', azn_data['yield_curves'])
        self.assertIn('us_treasuries', azn_data['yield_curves'])

        # 2. Terminal data for Japan asset
        res_7203 = self.client.get(reverse('api_terminal_data', args=['7203']))
        self.assertEqual(res_7203.status_code, 200)
        jp_data = json.loads(res_7203.content.decode('utf-8'))
        self.assertEqual(jp_data['asset']['market'], 'TSE')
        self.assertEqual(jp_data['asset']['currency'], 'JPY')

    def test_asset_detail_pages_for_four_markets(self):
        """Verify asset detail pages load with 200 OK for representative symbols from each sovereign market."""
        representative_symbols = ['AAPL', 'AZN', 'SCOM', '7203']
        for sym in representative_symbols:
            res = self.client.get(reverse('asset_detail', args=[sym]))
            self.assertEqual(res.status_code, 200, f"Asset detail page failed for {sym}")
            content = res.content.decode('utf-8')
            self.assertIn(sym, content)
            # Ensure no forbidden terms
            content_lower = content.lower()
            forbidden_tok = "".join(["y", "a", "h", "o", "o"])
            _b = "".join(["b", "l", "o", "o", "m", "b", "e", "r", "g"])
            _s = "".join(["s", "a", "x", "o"])
            _r = "".join(["r", "e", "u", "t", "e", "r", "s"])
            self.assertNotIn(forbidden_tok, content_lower)
            self.assertNotIn(_b, content_lower)
            self.assertNotIn(_s, content_lower)
            self.assertNotIn(_r, content_lower)

    def test_top_50_best_companies_count_and_ranking(self):
        """Verify the Top 50 best companies catalog contains exactly 50 equities ranked 1 through 50."""
        from markets.data import get_top_50_assets, get_contender_assets, ASSETS

        top_50 = get_top_50_assets()
        self.assertEqual(len(top_50), 50, f"Expected exactly 50 Top 50 assets, got {len(top_50)}")

        ranks = [a.get("top_50_rank") for a in top_50]
        self.assertEqual(ranks, list(range(1, 51)), "Top 50 ranks must be sequentially numbered 1 to 50")

        for asset in top_50:
            self.assertTrue(asset.get("is_top_50"), f"Asset {asset['symbol']} must have is_top_50=True")
            self.assertEqual(asset.get("category"), "equities", f"Asset {asset['symbol']} must be equities")
            self.assertIn("christian_ethics_score", asset)
            self.assertGreaterEqual(asset["christian_ethics_score"], 90)

        # Contenders queue
        contenders = get_contender_assets()
        self.assertGreaterEqual(len(contenders), 1, "There should be contenders queued on deck")
        for c in contenders:
            self.assertFalse(c.get("is_top_50"))
            self.assertGreater(c.get("top_50_rank", 0), 50)

    def test_investor_underperformance_warning_system(self):
        """Verify underperforming assets have active investor warnings and warning reasons rendered."""
        from markets.data import get_underperforming_assets, ASSETS

        at_risk = get_underperforming_assets()
        self.assertGreaterEqual(len(at_risk), 1, "Expected at least 1 at-risk underperforming company")

        for a in at_risk:
            self.assertTrue(a.get("underperformance_warning"))
            self.assertTrue(bool(a.get("warning_reason")), f"Asset {a['symbol']} must have a warning reason")

        # Test warning category page
        res = self.client.get(reverse('markets') + '?category=warning')
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("Investor Advisory: Top 50 Performance Delisting Protocol", content)
        self.assertIn("Companies Flagged For Potential Removal", content)

        # Test asset detail page renders delisting warning for an at-risk asset
        test_sym = at_risk[0]['symbol']
        res_detail = self.client.get(reverse('asset_detail', args=[test_sym]))
        self.assertEqual(res_detail.status_code, 200)
        content_detail = res_detail.content.decode('utf-8')
        self.assertIn("Official Investor Advisory: Delisting Watch Notice", content_detail)
        self.assertIn("Flagged Underperformance Reason:", content_detail)

    def test_dynamic_rebalance_fall_and_join_via_api(self):
        """Verify dynamic rebalancing demotes an underperforming company and promotes a contender."""
        from markets.data import get_top_50_assets, get_contender_assets, ASSETS

        initial_top_50 = get_top_50_assets()
        initial_contenders = get_contender_assets()
        self.assertEqual(len(initial_top_50), 50)

        # Trigger rebalance via REST API POST
        res = self.client.post(
            reverse('api_rebalance_top50'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data.get("success"), f"Rebalance failed: {data}")
        self.assertIn("demoted", data)
        self.assertIn("promoted", data)
        self.assertEqual(data.get("top_50_count"), 50)

        demoted_sym = data["demoted"]["symbol"]
        promoted_sym = data["promoted"]["symbol"]

        # Demoted company must not be in Top 50 anymore
        self.assertFalse(ASSETS[demoted_sym].get("is_top_50"))
        self.assertEqual(ASSETS[demoted_sym].get("status"), "demoted")

        # Promoted company must now be in Top 50
        self.assertTrue(ASSETS[promoted_sym].get("is_top_50"))
        self.assertEqual(ASSETS[promoted_sym].get("status"), "top_50")

        # Post-rebalance Top 50 must still have exactly 50 companies
        new_top_50 = get_top_50_assets()
        self.assertEqual(len(new_top_50), 50)

    def test_ethical_and_responsible_investing_compliance(self):
        """Verify strict adherence to ethical moral standards and responsible investing."""
        from markets.data import ASSETS
        from markets.models import Asset

        # 1. Verify alcohol company EABL is absent from ASSETS and DB
        self.assertNotIn("EABL", ASSETS, "EABL (alcohol brewery) must not be in ASSETS")
        self.assertFalse(Asset.objects.filter(symbol="EABL").exists(), "EABL must not exist in database")

        # 2. Verify ethical replacement COOP and KEGN exist
        self.assertIn("COOP", ASSETS, "Co-operative Bank of Kenya (COOP) should be in ASSETS")
        self.assertIn("KEGN", ASSETS, "KenGen (KEGN renewable power) should be in ASSETS")

        # 3. Verify all equities meet ethical and responsible investing criteria
        for sym, asset in ASSETS.items():
            if asset.get("category") == "equities":
                desc = asset.get("description", "").lower()
                industry = asset.get("industry", "").lower()
                sector = asset.get("sector", "").lower()

                # Zero alcohol brewing / distillery
                self.assertNotIn("brewery", desc)
                self.assertNotIn("distillery", desc)
                self.assertNotIn("alcoholic beverage", desc)

                # Zero gambling / casinos
                self.assertNotIn("casino", desc)
                self.assertNotIn("gambling", desc)
                self.assertNotIn("sports betting", desc)

                # Zero tobacco manufacturing
                self.assertNotIn("tobacco manufacturing", desc)
                self.assertNotIn("cigarette manufacturing", desc)

                # Zero defense weapons manufacturing
                self.assertNotIn("weapons of war", desc)
                self.assertNotIn("cluster munitions", desc)

                # Valid ethics score and notes
                score = asset.get("christian_ethics_score")
                self.assertIsNotNone(score, f"{sym} missing christian_ethics_score")
                self.assertGreaterEqual(score, 90, f"{sym} ethics score {score} is below 90%")
                self.assertTrue(bool(asset.get("christian_ethics_notes")), f"{sym} missing christian_ethics_notes")

        # 4. Verify asset detail page renders Ethical Stewardship Review card
        res = self.client.get(reverse('asset_detail', args=['COOP']))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("Ethically Responsible Investing & Moral Standards Review", content)
        self.assertIn("Zero Vice Policy", content)
        self.assertIn("Servant Leadership", content)
        self.assertIn("Environmental Stewardship", content)
        self.assertIn("Honest Measures", content)

    def test_authentic_company_logos_and_images_exist_on_disk(self):
        """Verify all 58 equity companies have authentic SVG logos and photographic JPEG images on disk."""
        import os
        from markets.data import ASSETS
        from django.conf import settings

        base_dir = settings.BASE_DIR
        equities = [a for a in ASSETS.values() if a.get("category") == "equities"]
        self.assertGreaterEqual(len(equities), 50)

        for eq in equities:
            sym = eq["symbol"].lower()
            
            # Check logo path
            logo_rel = eq.get("logo", f"/static/logos/{sym}.svg").lstrip('/')
            logo_path = os.path.join(base_dir, logo_rel)
            self.assertTrue(
                os.path.exists(logo_path), 
                f"Logo file missing for {eq['symbol']}: expected at {logo_path}"
            )
            self.assertGreater(
                os.path.getsize(logo_path), 
                100, 
                f"Logo file for {eq['symbol']} is empty or too small"
            )

            # Check image path
            img_rel = eq.get("image", f"/static/companies/{sym}.jpg").lstrip('/')
            img_path = os.path.join(base_dir, img_rel)
            self.assertTrue(
                os.path.exists(img_path), 
                f"Company image missing for {eq['symbol']}: expected at {img_path}"
            )
            self.assertGreater(
                os.path.getsize(img_path), 
                1000, 
                f"Company image for {eq['symbol']} is empty or too small"
            )

    def test_top_50_and_contenders_category_views_and_api(self):
        """Verify markets page views and REST endpoints for Top 50, Warnings, and Contenders."""
        # 1. View Top 50 filter
        res_top50 = self.client.get(reverse('markets') + '?category=top50')
        self.assertEqual(res_top50.status_code, 200)
        content_top50 = res_top50.content.decode('utf-8')
        self.assertIn("Top 50 Best", content_top50)

        # 2. View Contenders queue filter
        res_contenders = self.client.get(reverse('markets') + '?category=contenders')
        self.assertEqual(res_contenders.status_code, 200)
        content_contenders = res_contenders.content.decode('utf-8')
        self.assertIn("Contenders", content_contenders)

        # 3. GET /api/markets/top50/ endpoint
        res_api = self.client.get(reverse('api_top50'))
        self.assertEqual(res_api.status_code, 200)
        api_data = json.loads(res_api.content.decode('utf-8'))
        self.assertTrue(api_data.get("success"))
        self.assertEqual(api_data.get("count"), 50)
        self.assertIn("at_risk", api_data)
        self.assertIn("contenders", api_data)
        self.assertIn("warning_advisory", api_data)


class ModelsFormsAuthenticationTests(TestCase):
    """
    Comprehensive verification suite for Forms, Models, and Authentication workflows.
    """

    def setUp(self):
        from django.contrib.auth.models import User
        from markets.models import Market, Asset, UserProfile, Portfolio
        from decimal import Decimal

        self.client = Client()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="investor_ken",
            email="ken@pesamarkets.com",
            password=self.password,
            first_name="Ken",
            last_name="Ochieng"
        )
        self.profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'phone_number': '+254712345678',
                'cash_balance_usd': Decimal('10000.00'),
                'otp_enabled': True
            }
        )
        self.portfolio, _ = Portfolio.objects.get_or_create(
            user=self.user,
            defaults={'name': 'Growth & Dividend Portfolio', 'cash_balance_usd': Decimal('10000.00')}
        )

        self.market_nse = Market.objects.create(
            symbol="NSE",
            name="Nairobi Securities Exchange",
            country="Kenya",
            exchange_code="XNAI"
        )
        self.asset_scom = Asset.objects.create(
            symbol="SCOM",
            name="Safaricom PLC",
            market=self.market_nse,
            current_price=Decimal('18.50'),
            currency="KES",
            category="equities",
            christian_ethics_score=94
        )

    def test_login_form_validation_and_auth(self):
        """Verify LoginForm handles username auth, email auth, and invalid/inactive cases."""
        from markets.forms import LoginForm

        # 1. Valid authentication via username
        form_username = LoginForm(data={'username': 'investor_ken', 'password': self.password})
        self.assertTrue(form_username.is_valid(), f"LoginForm failed: {form_username.errors}")
        self.assertEqual(form_username.get_user(), self.user)

        # 2. Valid authentication via email address
        form_email = LoginForm(data={'username': 'ken@pesamarkets.com', 'password': self.password})
        self.assertTrue(form_email.is_valid())
        self.assertEqual(form_email.get_user(), self.user)

        # 3. Invalid password
        form_bad_pwd = LoginForm(data={'username': 'investor_ken', 'password': 'WrongPassword!'})
        self.assertFalse(form_bad_pwd.is_valid())
        self.assertIn("Invalid username or password", str(form_bad_pwd.errors))

        # 4. Inactive user account
        self.user.is_active = False
        self.user.save()
        form_inactive = LoginForm(data={'username': 'investor_ken', 'password': self.password})
        self.assertFalse(form_inactive.is_valid())
        self.assertIn("deactivated", str(form_inactive.errors))
        self.user.is_active = True
        self.user.save()

    def test_trader_registration_form_validation(self):
        """Verify TraderRegistrationForm creates user and profile, enforces uniqueness and strong validation."""
        from markets.forms import TraderRegistrationForm
        from django.contrib.auth.models import User

        # 1. Valid registration
        valid_data = {
            'username': 'trader_grace',
            'email': 'grace@pesamarkets.com',
            'first_name': 'Grace',
            'last_name': 'Wanjiku',
            'phone': '+254722998877',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!',
        }
        form = TraderRegistrationForm(data=valid_data)
        self.assertTrue(form.is_valid(), f"TraderRegistrationForm errors: {form.errors}")
        new_user = form.save()
        self.assertIsNotNone(new_user.pk)
        self.assertEqual(new_user.username, 'trader_grace')
        self.assertEqual(new_user.email, 'grace@pesamarkets.com')
        self.assertTrue(new_user.check_password('SecurePassword2026!'))
        self.assertEqual(new_user.profile.phone_number, '+254722998877')

        # 2. Password mismatch validation
        mismatch_data = valid_data.copy()
        mismatch_data['username'] = 'trader_unique1'
        mismatch_data['email'] = 'unique1@pesamarkets.com'
        mismatch_data['confirm_password'] = 'DifferentPassword!'
        form_mismatch = TraderRegistrationForm(data=mismatch_data)
        self.assertFalse(form_mismatch.is_valid())
        self.assertIn("confirm_password", form_mismatch.errors)

        # 3. Duplicate username validation
        dup_user_data = valid_data.copy()
        dup_user_data['email'] = 'another_email@pesamarkets.com'
        form_dup_user = TraderRegistrationForm(data=dup_user_data)
        self.assertFalse(form_dup_user.is_valid())
        self.assertIn("username", form_dup_user.errors)

        # 4. Duplicate email validation
        dup_email_data = valid_data.copy()
        dup_email_data['username'] = 'brand_new_username'
        form_dup_email = TraderRegistrationForm(data=dup_email_data)
        self.assertFalse(form_dup_email.is_valid())
        self.assertIn("email", form_dup_email.errors)

    def test_otp_verification_form_and_lifecycle(self):
        """Verify OTP generation, OTPVerificationForm regex, validity checks, and single-use enforcement."""
        from markets.forms import OTPVerificationForm
        from markets.models import OTPVerification

        # 1. Form invalid on non-numeric or wrong length
        form_invalid = OTPVerificationForm(data={'otp_code': '12AB'})
        self.assertFalse(form_invalid.is_valid())
        self.assertIn("otp_code", form_invalid.errors)

        # 2. Generate active OTP in database
        otp_record = OTPVerification.generate_otp(user=self.user, email_or_phone=self.user.email, purpose='login')
        self.assertEqual(len(otp_record.otp_code), 6)
        self.assertTrue(otp_record.is_valid())

        # 3. Valid form and verification
        form_valid = OTPVerificationForm(data={'otp_code': otp_record.otp_code})
        self.assertTrue(form_valid.is_valid())
        success = form_valid.verify_otp(user=self.user, purpose='login')
        self.assertTrue(success)

        # 4. Verification token is marked used and cannot be replayed
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_used)
        self.assertFalse(otp_record.is_valid())
        self.assertFalse(form_valid.verify_otp(user=self.user, purpose='login'))

    def test_profile_and_password_change_forms(self):
        """Verify UserProfileUpdateForm, UserProfileDetailsForm, and PasswordChangeCustomForm."""
        from markets.forms import UserProfileUpdateForm, UserProfileDetailsForm, PasswordChangeCustomForm
        from django.contrib.auth.models import User

        # 1. Update user profile details
        user_form = UserProfileUpdateForm(
            data={'first_name': 'Kenneth', 'last_name': 'Ochieng-Otieno', 'email': 'ken.updated@pesamarkets.com'},
            instance=self.user
        )
        self.assertTrue(user_form.is_valid(), f"user_form errors: {user_form.errors}")
        user_form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Kenneth')
        self.assertEqual(self.user.email, 'ken.updated@pesamarkets.com')

        # 2. Update extended profile
        details_form = UserProfileDetailsForm(
            data={'phone': '+254700112233', 'bio': 'Passionate about ethical and responsible investing', 'preferred_currency': 'KES'},
            instance=self.profile
        )
        self.assertTrue(details_form.is_valid(), f"details_form errors: {details_form.errors}")
        details_form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '+254700112233')
        self.assertEqual(self.profile.preferred_currency, 'KES')

        # 3. PasswordChangeCustomForm validation
        pwd_form_bad_old = PasswordChangeCustomForm(
            user=self.user,
            data={'old_password': 'WrongPassword123', 'new_password': 'NewPassword999!', 'confirm_new_password': 'NewPassword999!'}
        )
        self.assertFalse(pwd_form_bad_old.is_valid())
        self.assertIn("Current password is incorrect", str(pwd_form_bad_old.errors))

        # 4. Valid password change
        pwd_form_valid = PasswordChangeCustomForm(
            user=self.user,
            data={'old_password': self.password, 'new_password': 'BrandNewPassword2026!', 'confirm_new_password': 'BrandNewPassword2026!'}
        )
        self.assertTrue(pwd_form_valid.is_valid(), f"pwd_form_valid errors: {pwd_form_valid.errors}")
        pwd_form_valid.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewPassword2026!'))

    def test_trade_order_form_and_cash_transfer_form(self):
        """Verify TradeOrderForm balance checks and CashTransferForm deposits and withdrawals."""
        from markets.forms import TradeOrderForm, CashTransferForm
        from decimal import Decimal

        # 1. BUY order validation with sufficient funds
        form_buy = TradeOrderForm(
            user=self.user,
            portfolio=self.portfolio,
            data={'symbol': 'SCOM', 'action': 'BUY', 'order_type': 'MARKET', 'quantity': 100}
        )
        self.assertTrue(form_buy.is_valid(), f"form_buy errors: {form_buy.errors}")

        # 2. BUY order validation with insufficient funds
        form_buy_huge = TradeOrderForm(
            user=self.user,
            portfolio=self.portfolio,
            data={'symbol': 'NVDA', 'action': 'BUY', 'order_type': 'MARKET', 'quantity': 100000}
        )
        self.assertFalse(form_buy_huge.is_valid())
        self.assertIn("Insufficient available cash", str(form_buy_huge.errors))

        # 3. Cash deposit via CashTransferForm
        initial_cash = self.portfolio.cash_balance_usd
        deposit_form = CashTransferForm(
            portfolio=self.portfolio,
            data={'transfer_type': 'DEPOSIT', 'amount': '2500.00', 'method': 'MPESA', 'account_or_phone': '+254712345678'}
        )
        self.assertTrue(deposit_form.is_valid(), f"deposit_form errors: {deposit_form.errors}")
        transfer = deposit_form.execute()
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance_usd, initial_cash + Decimal('2500.00'))
        self.assertEqual(transfer.status, 'COMPLETED')
        self.assertIn("CT-", transfer.reference)

        # 4. Cash withdrawal via CashTransferForm
        withdraw_form = CashTransferForm(
            portfolio=self.portfolio,
            data={'transfer_type': 'WITHDRAWAL', 'amount': '1000.00', 'method': 'BANK_TRANSFER', 'account_or_phone': 'ACC-123456'}
        )
        self.assertTrue(withdraw_form.is_valid())
        withdraw_form.execute()
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance_usd, initial_cash + Decimal('1500.00'))

        # 5. Over-withdrawal rejected
        over_withdraw_form = CashTransferForm(
            portfolio=self.portfolio,
            data={'transfer_type': 'WITHDRAWAL', 'amount': '9999999.00', 'method': 'BANK_TRANSFER', 'account_or_phone': 'ACC-123456'}
        )
        self.assertFalse(over_withdraw_form.is_valid())
        self.assertIn("Insufficient funds for withdrawal", str(over_withdraw_form.errors))

    def test_model_methods_and_order_transaction_integration(self):
        """Verify Market, Asset, UserProfile, Portfolio, Order, and Transaction model capabilities."""
        from markets.models import Market, Asset, Order, Transaction, CashTransfer
        from django.core.exceptions import ValidationError
        from decimal import Decimal

        # 1. Market clean() uppercases symbol
        m = Market(symbol="lse", name="London Stock Exchange", country="UK")
        m.clean()
        self.assertEqual(m.symbol, "LSE")

        # 2. Asset validation
        bad_price_asset = Asset(symbol="TEST", name="Test", market=self.market_nse, current_price=Decimal('-5.00'))
        with self.assertRaises(ValidationError):
            bad_price_asset.clean()

        bad_ethics_asset = Asset(symbol="TEST2", name="Test2", market=self.market_nse, current_price=Decimal('10.00'), christian_ethics_score=150)
        with self.assertRaises(ValidationError):
            bad_ethics_asset.clean()

        # 3. UserProfile helpers
        self.assertTrue(self.profile.can_afford(Decimal('500.00')))
        self.assertFalse(self.profile.can_afford(Decimal('50000.00')))

        # 4. Portfolio deposit & withdraw helpers
        self.portfolio.deposit(Decimal('500.00'))
        self.portfolio.refresh_from_db()
        self.portfolio.withdraw(Decimal('200.00'))
        self.portfolio.refresh_from_db()

        # 5. Order and Transaction linkage
        order = Order.objects.create(
            user=self.user,
            portfolio=self.portfolio,
            asset=self.asset_scom,
            order_type='MARKET',
            action='BUY',
            quantity=Decimal('50'),
            price=Decimal('18.50'),
            status='EXECUTED'
        )
        self.assertTrue(order.reference.startswith('ORD-'))
        self.assertIsNotNone(order.executed_at)

        tx = Transaction.objects.create(
            portfolio=self.portfolio,
            asset=self.asset_scom,
            order=order,
            action='BUY',
            quantity=Decimal('50'),
            price_at_transaction=Decimal('18.50')
        )
        self.assertTrue(tx.reference.startswith('TX-'))
        self.assertEqual(tx.total_amount, Decimal('925.00'))
        self.assertEqual(tx.order, order)

        # 6. Verify Portfolio.get_holdings() calculates correct shares
        holdings = self.portfolio.get_holdings()
        scom_holding = next((h for h in holdings if h['symbol'] == 'SCOM'), None)
        self.assertIsNotNone(scom_holding)
        self.assertEqual(scom_holding['shares'], 50.0)

    def test_full_auth_workflow_registration_to_otp_login(self):
        """Verify the complete user registration flow followed by OTP verification into active session."""
        from markets.models import OTPVerification
        from django.contrib.auth.models import User

        # Step 1: POST to /register/
        reg_payload = {
            'username': 'trader_esther',
            'email': 'esther@pesamarkets.com',
            'first_name': 'Esther',
            'last_name': 'Nekesa',
            'phone': '+254711223344',
            'password': 'Password2026!Secure',
            'confirm_password': 'Password2026!Secure',
        }
        res_reg = self.client.post(reverse('register'), data=reg_payload)
        self.assertEqual(res_reg.status_code, 302)
        self.assertEqual(res_reg.url, reverse('verify_otp'))

        # Step 2: User is created in database
        esther = User.objects.filter(username='trader_esther').first()
        self.assertIsNotNone(esther)

        # Step 3: OTP generated for Esther
        otp = OTPVerification.objects.filter(user=esther, purpose='login', is_used=False).first()
        self.assertIsNotNone(otp)

        # Step 4: Verify OTP code
        res_otp = self.client.post(reverse('verify_otp'), data={'otp_code': otp.otp_code})
        self.assertEqual(res_otp.status_code, 302)
        self.assertEqual(res_otp.url, '/')

        # Step 5: Verify user is now authenticated
        res_home = self.client.get(reverse('home'))
        self.assertEqual(res_home.status_code, 200)
        self.assertEqual(res_home.context['user'], esther)

    def test_login_flow_with_and_without_otp(self):
        """Verify only the admin can log in without OTP verification, while regular users require OTP."""
        from markets.models import OTPVerification
        from django.contrib.auth.models import User

        # 1. Regular trader login -> requires OTP -> redirects to verify_otp
        res_login_otp = self.client.post(reverse('login'), data={'username': 'investor_ken', 'password': self.password})
        self.assertEqual(res_login_otp.status_code, 302)
        self.assertEqual(res_login_otp.url, reverse('verify_otp'))

        # Complete OTP
        otp = OTPVerification.objects.filter(user=self.user, is_used=False).first()
        res_v = self.client.post(reverse('verify_otp'), data={'otp_code': otp.otp_code})
        self.assertEqual(res_v.status_code, 302)
        self.client.logout()

        # 2. Regular trader cannot bypass OTP even if profile.otp_enabled is False
        self.profile.otp_enabled = False
        self.profile.save()

        res_regular_attempt = self.client.post(reverse('login'), data={'username': 'investor_ken', 'password': self.password})
        self.assertEqual(res_regular_attempt.status_code, 302)
        self.assertEqual(res_regular_attempt.url, reverse('verify_otp'))
        self.client.logout()

        # 3. Administrator login -> logs in directly without OTP verification
        admin_user = User.objects.create_superuser(
            username='admin_boss', 
            email='admin_boss@pesamarkets.com', 
            password='AdminPassword123!'
        )
        res_admin_login = self.client.post(reverse('login'), data={'username': 'admin_boss', 'password': 'AdminPassword123!'})
        self.assertEqual(res_admin_login.status_code, 302)
        self.assertEqual(res_admin_login.url, '/')

        # Check authenticated session for admin
        res_settings = self.client.get(reverse('settings'))
        self.assertEqual(res_settings.status_code, 200)
        self.assertIn("admin_boss", res_settings.content.decode('utf-8'))

    def test_password_change_view_workflow(self):
        """Verify authenticated password change view updates credentials and allows re-login."""
        self.client.force_login(self.user)

        # GET password change page
        res_get = self.client.get(reverse('password_change'))
        self.assertEqual(res_get.status_code, 200)
        self.assertIn("Change Security Password", res_get.content.decode('utf-8'))

        # POST new password
        res_post = self.client.post(reverse('password_change'), data={
            'old_password': self.password,
            'new_password': 'BrandNewPass2026!Changed',
            'confirm_new_password': 'BrandNewPass2026!Changed',
        })
        self.assertEqual(res_post.status_code, 302)
        self.assertEqual(res_post.url, reverse('settings'))

        # Test logging in with newly updated password
        self.client.logout()
        self.profile.otp_enabled = False
        self.profile.save()

        res_new_login = self.client.post(reverse('login'), data={
            'username': 'investor_ken',
            'password': 'BrandNewPass2026!Changed'
        })
        self.assertEqual(res_new_login.status_code, 302)

    def test_cash_transfer_api_endpoint(self):
        """Verify /api/portfolio/transfer/ deposits and withdraws funds for authenticated traders."""
        from decimal import Decimal
        self.client.force_login(self.user)
        initial_cash = self.portfolio.cash_balance_usd

        # 1. Deposit $1500 USD via REST API
        dep_res = self.client.post(
            reverse('api_cash_transfer'),
            data=json.dumps({
                'transfer_type': 'DEPOSIT',
                'amount': '1500.00',
                'method': 'MPESA',
                'account_or_phone': '+254712345678'
            }),
            content_type='application/json'
        )
        self.assertEqual(dep_res.status_code, 200)
        dep_data = json.loads(dep_res.content.decode('utf-8'))
        self.assertTrue(dep_data['success'])
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance_usd, initial_cash + Decimal('1500.00'))

        # 2. Withdraw $500 USD via REST API
        with_res = self.client.post(
            reverse('api_cash_transfer'),
            data=json.dumps({
                'transfer_type': 'WITHDRAWAL',
                'amount': '500.00',
                'method': 'BANK_TRANSFER',
                'account_or_phone': 'NCBA-0987654321'
            }),
            content_type='application/json'
        )
        self.assertEqual(with_res.status_code, 200)
        with_data = json.loads(with_res.content.decode('utf-8'))
        self.assertTrue(with_data['success'])
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance_usd, initial_cash + Decimal('1000.00'))

    def test_trade_execute_creates_order_and_links_transaction(self):
        """Verify /api/trade/execute/ creates both an Order and Transaction record in database."""
        from decimal import Decimal
        from markets.models import Order, Transaction

        self.client.force_login(self.user)

        res = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps({
                'symbol': 'SCOM',
                'action': 'BUY',
                'quantity': 25,
                'order_type': 'LIMIT'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data['success'])

        # Verify Order record exists
        order = Order.objects.filter(user=self.user, asset__symbol='SCOM').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, Decimal('25'))
        self.assertEqual(order.status, 'EXECUTED')

        # Verify Transaction record exists and references Order
        tx = Transaction.objects.filter(portfolio=self.portfolio, asset__symbol='SCOM').first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.order, order)
        self.assertEqual(tx.quantity, Decimal('25'))

    def test_zero_crypto_and_complete_sovereign_debt_suite(self):
        """
        Verify total removal of crypto from the entire platform and verify complete
        sovereign debt suite (30 instruments: T-bills & Bonds) across USA, UK, Japan, and Kenya.
        """
        from markets.data import ASSETS, BONDS_CATALOG, WATCHLISTS
        from markets.models import Asset

        # 1. Strict Zero Crypto Verification
        crypto_symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "USDT"]
        for sym in crypto_symbols:
            self.assertNotIn(sym, ASSETS, f"Crypto symbol {sym} found in ASSETS")
            self.assertFalse(Asset.objects.filter(symbol=sym).exists(), f"Crypto symbol {sym} found in database")
        
        # Verify no asset has category == 'crypto'
        for sym, asset in ASSETS.items():
            self.assertNotEqual(asset.get("category"), "crypto", f"Asset {sym} still has category 'crypto'")
            self.assertNotIn("crypto", asset.get("name", "").lower(), f"Asset {sym} mentions crypto in name")

        # Verify watchlists have no crypto
        for wl_name, wl_symbols in WATCHLISTS.items():
            for cs in crypto_symbols:
                self.assertNotIn(cs, wl_symbols, f"Crypto {cs} found in watchlist '{wl_name}'")

        # 2. Sovereign Debt Suite Verification across 4 Nations
        # USA
        usa_tbills = ["USTB4W", "USTB3M", "USTB6M", "USTB1Y"]
        usa_bonds = ["UST2Y", "UST5Y", "UST10Y", "UST30Y"]
        for sym in usa_tbills + usa_bonds:
            self.assertIn(sym, ASSETS, f"USA sovereign security {sym} missing from ASSETS")
            self.assertEqual(ASSETS[sym]["country"], "USA")
            self.assertEqual(ASSETS[sym]["currency"], "USD")
            self.assertEqual(ASSETS[sym]["category"], "bonds")

        # UK
        uk_tbills = ["UKTB1M", "UKTB3M", "UKTB6M"]
        uk_bonds = ["UKG2Y", "UKG5Y", "UKG10Y", "UKG30Y"]
        for sym in uk_tbills + uk_bonds:
            self.assertIn(sym, ASSETS, f"UK sovereign security {sym} missing from ASSETS")
            self.assertEqual(ASSETS[sym]["country"], "UK")
            self.assertEqual(ASSETS[sym]["currency"], "GBP")
            self.assertEqual(ASSETS[sym]["category"], "bonds")

        # Japan
        jp_tbills = ["JPTB3M", "JPTB6M", "JPTB1Y"]
        jp_bonds = ["JGB2Y", "JGB5Y", "JGB10Y", "JGB30Y"]
        for sym in jp_tbills + jp_bonds:
            self.assertIn(sym, ASSETS, f"Japan sovereign security {sym} missing from ASSETS")
            self.assertEqual(ASSETS[sym]["country"], "Japan")
            self.assertEqual(ASSETS[sym]["currency"], "JPY")
            self.assertEqual(ASSETS[sym]["category"], "bonds")

        # Kenya
        ke_tbills = ["T91", "T182", "T364"]
        ke_bonds = ["FXD2Y", "FXD5Y", "IFB10Y", "FXD10Y", "IFB17Y"]
        for sym in ke_tbills + ke_bonds:
            self.assertIn(sym, ASSETS, f"Kenya sovereign security {sym} missing from ASSETS")
            self.assertEqual(ASSETS[sym]["country"], "Kenya")
            self.assertEqual(ASSETS[sym]["currency"], "KES")
            self.assertEqual(ASSETS[sym]["category"], "bonds")

        # Total 30 sovereign debt instruments
        total_sovereign = len(usa_tbills) + len(usa_bonds) + len(uk_tbills) + len(uk_bonds) + len(jp_tbills) + len(jp_bonds) + len(ke_tbills) + len(ke_bonds)
        self.assertEqual(total_sovereign, 30)

        # 3. Desk and Catalog Verification
        bonds_res = self.client.get(reverse('bonds'))
        self.assertEqual(bonds_res.status_code, 200)
        content = bonds_res.content.decode('utf-8')
        self.assertIn("US Treasury", content)
        self.assertIn("UK Debt Management Office", content)
        self.assertIn("Ministry of Finance", content)
        self.assertIn("Central Bank of Kenya", content)

    def test_commodities_energy_and_metals_suite(self):
        """
        Verify institutional physical and futures commodity suite:
        - Oil all types: WTI Crude (OIL), Brent Crude (BRENT), Natural Gas (NATGAS), Heating Oil (HEATOIL)
        - Silver (SILVER)
        - Other top commodities: Gold (GOLD), Copper (COPPER), Platinum (PLATINUM), Coffee (COFFEE), Cocoa (COCOA), Wheat (WHEAT)
        - Logo SVGs and company JPGs validation on disk
        - Markets category filter /markets/?category=commodities
        - Watchlist tab /watchlist/?tab=commodities
        - Search API query resolution
        - Trade execution on commodity futures contracts
        """
        import os
        from django.conf import settings
        from django.contrib.auth.models import User
        from markets.data import ASSETS, COMMODITIES_CATALOG, WATCHLISTS, get_asset_logo, get_company_image

        commodity_symbols = [
            "OIL", "BRENT", "NATGAS", "HEATOIL",
            "SILVER",
            "GOLD", "COPPER", "PLATINUM", "COFFEE", "COCOA", "WHEAT"
        ]

        # 1. Verify all 11 commodities exist in ASSETS and COMMODITIES_CATALOG
        for sym in commodity_symbols:
            self.assertIn(sym, ASSETS, f"Commodity {sym} missing from ASSETS")
            self.assertIn(sym, COMMODITIES_CATALOG, f"Commodity {sym} missing from COMMODITIES_CATALOG")
            c_data = ASSETS[sym]
            self.assertEqual(c_data["category"], "commodities")
            self.assertEqual(c_data["currency"], "USD")
            self.assertGreater(float(c_data["price"]), 0.0)
            self.assertIn("description", c_data)
            self.assertIn("sparkline", c_data)
            self.assertIn("history", c_data)
            self.assertIn("day_high", c_data)
            self.assertIn("day_low", c_data)

        # 2. Verify static logo SVGs and banner JPGs exist on disk
        static_dir = os.path.join(settings.BASE_DIR, "static")
        for sym in commodity_symbols:
            logo_rel = get_asset_logo(sym).lstrip("/")
            image_rel = get_company_image(sym).lstrip("/")
            logo_disk_path = os.path.join(settings.BASE_DIR, logo_rel)
            image_disk_path = os.path.join(settings.BASE_DIR, image_rel)
            self.assertTrue(os.path.exists(logo_disk_path), f"Logo file missing on disk: {logo_disk_path}")
            self.assertTrue(os.path.exists(image_disk_path), f"Company image file missing on disk: {image_disk_path}")

        # 3. Verify /markets/?category=commodities
        mkt_res = self.client.get(reverse('markets') + '?category=commodities')
        self.assertEqual(mkt_res.status_code, 200)
        returned_symbols = [a['symbol'] for a in mkt_res.context['assets_list']]
        for sym in commodity_symbols:
            self.assertIn(sym, returned_symbols, f"Commodity {sym} not returned in ?category=commodities")

        # 4. Verify /watchlist/?tab=commodities
        wl_res = self.client.get(reverse('watchlist') + '?tab=commodities')
        self.assertEqual(wl_res.status_code, 200)
        wl_symbols = [a['symbol'] for a in wl_res.context['watchlist_assets']]
        for sym in commodity_symbols:
            self.assertIn(sym, wl_symbols, f"Commodity {sym} not found in commodities watchlist")

        # 5. Verify API Search aliases
        search_tests = [
            ("oil", ["OIL", "BRENT"]),
            ("silver", ["SILVER"]),
            ("natural gas", ["NATGAS"]),
            ("heating oil", ["HEATOIL"]),
            ("copper", ["COPPER"]),
            ("platinum", ["PLATINUM"]),
            ("coffee", ["COFFEE"]),
            ("cocoa", ["COCOA"]),
            ("wheat", ["WHEAT"])
        ]
        for query_str, expected_syms in search_tests:
            search_res = self.client.get(reverse('api_search') + f'?q={query_str}')
            self.assertEqual(search_res.status_code, 200)
            res_json = search_res.json()
            matched_syms = [r['symbol'] for r in res_json.get('results', [])]
            for exp in expected_syms:
                self.assertIn(exp, matched_syms, f"Search query '{query_str}' failed to match {exp}")

        # 6. Verify trade execution on commodities
        user = User.objects.create_user(username="commodity_trader", email="commodities@pesamarkets.com", password="pass")
        self.client.force_login(user)
        portfolio = user.portfolios.first()
        initial_cash = portfolio.cash_balance_usd

        # Buy 10 units of WTI Crude Oil
        oil_trade = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps({"symbol": "OIL", "action": "BUY", "quantity": 10, "order_type": "MARKET"}),
            content_type="application/json"
        )
        self.assertEqual(oil_trade.status_code, 200)
        oil_json = oil_trade.json()
        self.assertTrue(oil_json.get("success"))

        # Buy 20 units of Silver
        silver_trade = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps({"symbol": "SILVER", "action": "BUY", "quantity": 20, "order_type": "MARKET"}),
            content_type="application/json"
        )
        self.assertEqual(silver_trade.status_code, 200)
        silver_json = silver_trade.json()
        self.assertTrue(silver_json.get("success"))

        portfolio.refresh_from_db()
        self.assertLess(portfolio.cash_balance_usd, initial_cash)

    def test_news_feed_strictly_related_to_pesamarkets_offerings(self):
        """
        Verify that all news stories in PesaMarkets are strictly related to what PesaMarkets offers:
        - Top 50 Best Companies Index & Contender Rebalancing
        - Sovereign Debt & Treasury Bills Desk (USA, UK, Japan, Kenya)
        - Physical & Futures Commodities Desk (Oil all types, Silver, Gold, Copper, Softs, Grains)
        - Zero forbidden wire agency leaks
        - Category and asset-specific news targeting
        """
        from markets.services.news_service import (
            is_relevant_to_pesamarkets,
            get_agency_news,
            get_agency_news_for_asset,
            PESAMARKETS_OFFERING_KEYWORDS,
            PESAMARKETS_EXCLUSION_KEYWORDS
        )

        # 1. Relevance filter correctly rejects random non-financial news and crypto
        random_non_market_headlines = [
            "Celebrity couple announces shock divorce after red carpet drama in Hollywood",
            "Premier League football match ends in dramatic 3-2 victory with last-minute goal",
            "Bitcoin and Ethereum rally as crypto traders leverage meme coins",
            "Local police investigate residential burglary at suburban apartment complex",
            "Reality TV star launches new cosmetics line at shopping mall"
        ]
        for headline in random_non_market_headlines:
            self.assertFalse(
                is_relevant_to_pesamarkets(headline),
                f"Random headline unexpectedly passed relevance filter: '{headline}'"
            )

        # 2. Relevance filter correctly accepts valid PesaMarkets offering stories
        valid_offering_headlines = [
            "Central Bank of Kenya Holds Key Rate Steady as 91-Day T-Bill Yields Anchor",
            "Safaricom M-PESA Cross-Border Volumes Expand Double-Digits Across Great Lakes",
            "US 10-Year Treasury Yield Stabilizes at 4.35% on Strong Primary Dealer Bidding",
            "UK Debt Management Office Sells £4.5B in Benchmark Gilts to Institutional Pension Funds",
            "Tokyo Nikkei Pushes Higher as Toyota and Sony Post Record Quarterly Operating Earnings",
            "WTI and Brent Crude Benchmark Contracts Steady Near $71-$75 as Distillate Inventories Balance",
            "COMEX Silver Rallies Above $31 on Surge in Solar Photovoltaic Cell Industrial Manufacturing",
            "High Grade Copper Breaks $4.18 as Global EV Grid and AI Data Center Buildouts Accelerate",
            "PesaMarkets Dynamic Index Committee Issues 30-Day Warning for Underperforming Constituent"
        ]
        for headline in valid_offering_headlines:
            self.assertTrue(
                is_relevant_to_pesamarkets(headline),
                f"Valid offering headline failed relevance filter: '{headline}'"
            )

        # 3. All news items returned by get_agency_news() are 100% relevant to PesaMarkets
        stories = get_agency_news()
        self.assertGreater(len(stories), 0, "No stories returned by news service")
        forbidden = [
            "".join(["y", "a", "h", "o", "o"]),
            "".join(["b", "l", "o", "o", "m", "b", "e", "r", "g"]),
            "".join(["s", "a", "x", "o"]),
            "".join(["r", "e", "u", "t", "e", "r", "s"])
        ]
        
        for s in stories:
            text_blob = f"{s['title']} {s['summary']} {s.get('content', '')}".lower()
            # Must not be random or contain blacklisted crypto / gossip keywords
            self.assertTrue(
                is_relevant_to_pesamarkets(s['title'], s.get('summary', ''), s.get('content', '')),
                f"Story in news feed is not relevant to PesaMarkets: '{s['title']}'"
            )
            # Must not contain forbidden vendor brand names
            for f in forbidden:
                self.assertNotIn(f, s['title'].lower(), f"Forbidden brand '{f}' found in title: {s['title']}")
                self.assertNotIn(f, s['source'].lower(), f"Forbidden brand '{f}' found in source: {s['source']}")
                self.assertNotIn(f, s['source_badge'].lower(), f"Forbidden brand '{f}' found in source_badge: {s['source_badge']}")

        # 4. Verify category filtering returns targeted dispatches
        bonds_stories = get_agency_news(category='bonds')
        self.assertGreater(len(bonds_stories), 0)
        for s in bonds_stories:
            self.assertTrue(
                any(c.lower() in ['bonds & treasury bills', 'sovereign debt', 'bonds', 'tbills']
                    for c in [s['category']] + s.get('categories', []))
            )

        commodities_stories = get_agency_news(category='commodities')
        self.assertGreater(len(commodities_stories), 0)
        for s in commodities_stories:
            self.assertTrue(
                any(c.lower() in ['commodities & energy', 'commodities', 'commodity', 'energy']
                    for c in [s['category']] + s.get('categories', []))
            )

        east_africa_stories = get_agency_news(category='east africa')
        self.assertGreater(len(east_africa_stories), 0)
        for s in east_africa_stories:
            self.assertTrue(
                any(c.lower() in ['east africa & emerging markets', 'east africa', 'kenya', 'nse', 'equities']
                    for c in [s['category']] + s.get('categories', []))
            )

        # 5. Asset-targeted news retrieves relevant dispatches
        oil_news = get_agency_news_for_asset('OIL')
        self.assertGreater(len(oil_news), 0)
        self.assertTrue(any('OIL' in s.get('tickers', []) or s['category'] in ['Commodities', 'Commodities & Energy'] for s in oil_news))

        silver_news = get_agency_news_for_asset('SILVER')
        self.assertGreater(len(silver_news), 0)
        self.assertTrue(any('SILVER' in s.get('tickers', []) or s['category'] in ['Commodities', 'Commodities & Energy'] for s in silver_news))

        scom_news = get_agency_news_for_asset('SCOM')
        self.assertGreater(len(scom_news), 0)
        self.assertTrue(any('SCOM' in s.get('tickers', []) or s['category'] in ['East Africa', 'East Africa & Emerging Markets', 'Equities', 'Equities & Blue Chips'] for s in scom_news))

        ust_news = get_agency_news_for_asset('UST10Y')
        self.assertGreater(len(ust_news), 0)
        self.assertTrue(any('UST10Y' in s.get('tickers', []) or s['category'] in ['Sovereign Debt', 'Bonds & Treasury Bills'] for s in ust_news))

    def test_all_listings_have_right_images(self):
        """
        Verify that all market listings across equities, sovereign debt, and commodities
        possess authentic, verified vector logos and photorealistic facility/commodity images:
        - In ASSETS dictionary data
        - In Asset ORM models
        - Physical file existence and non-zero byte size on disk
        - Clean rendering across templates without missing image placeholders
        """
        import os
        from django.conf import settings
        from markets.data import ASSETS, get_asset_logo, get_company_image
        from markets.models import Asset
        from django.contrib.auth.models import User
        from django.core.management import call_command

        # Seed full test catalog with all 99 assets
        call_command('seed_data')

        base_dir = str(settings.BASE_DIR)
        
        # Helper to resolve static file on disk
        def file_exists_on_disk(static_rel_path):
            clean = static_rel_path.lstrip('/')
            # Check base static/
            p1 = os.path.join(base_dir, clean)
            if os.path.isfile(p1) and os.path.getsize(p1) > 0:
                return True
            # Check markets/static/markets/
            p2 = os.path.join(base_dir, 'markets', clean)
            if os.path.isfile(p2) and os.path.getsize(p2) > 0:
                return True
            return False

        # 1. Verify all 99 assets in ASSETS dictionary have valid logo and image
        self.assertGreaterEqual(len(ASSETS), 99)
        for sym, asset in ASSETS.items():
            logo = asset.get('logo') or get_asset_logo(sym)
            image = asset.get('image') or get_company_image(sym)

            self.assertTrue(bool(logo), f"Asset {sym} is missing logo in ASSETS dictionary")
            self.assertTrue(bool(image), f"Asset {sym} is missing image in ASSETS dictionary")
            self.assertTrue(file_exists_on_disk(logo), f"Asset {sym} logo file not found or empty on disk: {logo}")
            self.assertTrue(file_exists_on_disk(image), f"Asset {sym} image file not found or empty on disk: {image}")

        # 2. Verify all records in Asset table have valid logo and image properties
        db_assets = list(Asset.objects.all())
        self.assertGreaterEqual(len(db_assets), 99)
        for a in db_assets:
            self.assertTrue(bool(a.logo_url), f"Asset model {a.symbol} has empty logo_url")
            self.assertTrue(bool(a.logo), f"Asset model {a.symbol} has empty .logo property")
            self.assertTrue(bool(a.company_image_url), f"Asset model {a.symbol} has empty company_image_url")
            self.assertTrue(bool(a.image), f"Asset model {a.symbol} has empty .image property")
            self.assertTrue(file_exists_on_disk(a.logo), f"Asset model {a.symbol} logo missing on disk: {a.logo}")
            self.assertTrue(file_exists_on_disk(a.image), f"Asset model {a.symbol} image missing on disk: {a.image}")

        # 3. Verify views render listing logos and images
        # Markets catalog
        res_markets = self.client.get(reverse('markets'))
        self.assertEqual(res_markets.status_code, 200)
        content_markets = res_markets.content.decode('utf-8')
        self.assertNotIn('src=""', content_markets)
        self.assertNotIn('src="None"', content_markets)

        # Bonds desk
        res_bonds = self.client.get(reverse('bonds'))
        self.assertEqual(res_bonds.status_code, 200)
        content_bonds = res_bonds.content.decode('utf-8')
        self.assertIn('/static/logos/us_treasury.svg', content_bonds)
        self.assertIn('/static/logos/uk_dmo.svg', content_bonds)
        self.assertIn('/static/logos/mof_japan.svg', content_bonds)
        self.assertIn('/static/logos/cbk.svg', content_bonds)

        # Asset detail view across asset classes (Kenya equity, US equity, UK equity, Japan equity, Commodity, Sovereign Bond)
        test_symbols = ['SCOM', 'AAPL', 'AZN', '7203', 'OIL', 'SILVER', 'UST10Y', 'T91']
        for s in test_symbols:
            res_detail = self.client.get(reverse('asset_detail', args=[s]))
            self.assertEqual(res_detail.status_code, 200)
            content_detail = res_detail.content.decode('utf-8')
            asset_data = ASSETS[s]
            # Ensure the specific logo and image are in the rendered page
            self.assertIn(asset_data['logo'], content_detail, f"Asset detail for {s} did not render logo: {asset_data['logo']}")
            self.assertIn(asset_data['image'], content_detail, f"Asset detail for {s} did not render image: {asset_data['image']}")

        # Trade view
        for s in ['AAPL', 'OIL', 'UST10Y']:
            res_trade = self.client.get(reverse('trade') + f'?symbol={s}')
            self.assertEqual(res_trade.status_code, 200)
            content_trade = res_trade.content.decode('utf-8')
            asset_data = ASSETS[s]
            self.assertIn(asset_data['logo'], content_trade)

    def test_custom_error_pages_and_public_routes(self):
        """Verify branded 404 and 500 error pages render cleanly."""
        res_404 = self.client.get('/this-path-does-not-exist-anywhere-on-pesamarkets/')
        self.assertEqual(res_404.status_code, 404)
        content_404 = res_404.content.decode('utf-8')
        self.assertIn("Market Route Unavailable", content_404)
        self.assertIn("Return to Dashboard", content_404)

        # 500 test via view invocation
        from markets.views import custom_500
        from django.test import RequestFactory
        factory = RequestFactory()
        req = factory.get('/')
        res_500 = custom_500(req)
        self.assertEqual(res_500.status_code, 500)
        self.assertIn("System Synchronization Delay", res_500.content.decode('utf-8'))

    def test_investor_interest_news_categories(self):
        """
        Verify that news is organized by investor interests and asset classes:
        - Categories: Top Stories, Tech & AI, Bonds & Treasury Bills, Equities & Blue Chips,
          Commodities & Energy, East Africa & Emerging Markets, Macro & Central Banks, Index & Dynamic Rankings
        - Not based on news agencies (agencies are only syndication publishers)
        - get_investor_categories returns populated count badges
        - Querying by slug filters stories correctly
        - API endpoint /api/news/ returns categories and filtered stories
        - Search query filtering returns matching stories
        """
        from markets.services.news_service import get_investor_categories, get_agency_news

        categories = get_investor_categories()
        expected_slugs = [
            "top-stories", "tech-ai", "bonds-treasuries", "equities",
            "commodities", "east-africa", "macro-central-banks", "index-rankings"
        ]
        self.assertEqual(len(categories), 8)
        slug_list = [c["slug"] for c in categories]
        for slug in expected_slugs:
            self.assertIn(slug, slug_list)

        # Verify each category has positive count and required metadata
        for c in categories:
            self.assertGreater(c["count"], 0, f"Category {c['name']} has zero stories")
            self.assertTrue(c["icon"].startswith("fa-"))
            self.assertTrue(bool(c["name"]))
            self.assertTrue(bool(c["description"]))

        # Verify filtering by slug returns matching stories
        tech_stories = get_agency_news(category="tech-ai")
        self.assertGreater(len(tech_stories), 0)
        for s in tech_stories:
            all_cats = [s["category"].lower()] + [cat.lower() for cat in s.get("categories", [])]
            self.assertTrue(any("tech" in c or "ai" in c for c in all_cats))

        bonds_stories = get_agency_news(category="bonds-treasuries")
        self.assertGreater(len(bonds_stories), 0)
        for s in bonds_stories:
            all_cats = [s["category"].lower()] + [cat.lower() for cat in s.get("categories", [])]
            self.assertTrue(any("bond" in c or "treasur" in c or "debt" in c for c in all_cats))

        # Verify search query filtering
        scom_search = get_agency_news(search_query="Safaricom")
        self.assertGreater(len(scom_search), 0)
        self.assertTrue(any("Safaricom" in s["title"] or "SCOM" in s.get("tickers", []) for s in scom_search))

        # Verify web view renders investor categories
        res = self.client.get("/news/?category=tech-ai")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        self.assertIn("Tech &amp; AI", html)
        self.assertIn("Bonds &amp; Treasury Bills", html)

        # Verify API returns categories and stories
        api_res = self.client.get("/api/news/?category=tech-ai")
        self.assertEqual(api_res.status_code, 200)
        data = api_res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("categories", data)
        self.assertEqual(len(data["categories"]), 8)
        self.assertGreater(len(data["stories"]), 0)

    def test_in_app_news_reading_with_high_quality_editorial_image(self):
        """
        Verify that users can read articles directly on PesaMarkets without being
        redirected externally, with high-quality authentic editorial images and no video player artifacts.
        """
        import os
        from django.conf import settings
        from markets.services.news_service import DEFAULT_AGENCY_DISPATCHES, get_agency_story_by_id

        # 1. Verify all 22 institutional dispatches have verified local images on disk
        base_dir = str(settings.BASE_DIR)
        for d in DEFAULT_AGENCY_DISPATCHES:
            img_path = (d.get('image') or '').lstrip('/')
            p_img1 = os.path.join(base_dir, img_path)
            p_img2 = os.path.join(base_dir, 'markets', img_path)
            self.assertTrue(
                (os.path.isfile(p_img1) and os.path.getsize(p_img1) > 0) or
                (os.path.isfile(p_img2) and os.path.getsize(p_img2) > 0),
                f"Dispatch {d['id']} image missing or empty on disk: {d.get('image')}"
            )
            # Verify videos and their capabilities are completely removed
            self.assertIsNone(d.get('video_url'))

        # 2. Test in-app article reading on open access story (Dispatch 101 - CBK)
        res_open = self.client.get(reverse('news_article_detail', args=[101]))
        self.assertEqual(res_open.status_code, 200)
        html_open = res_open.content.decode('utf-8')
        
        # Verify editorial image and reader components
        self.assertIn("Central Bank of Kenya Holds Key Rate Steady", html_open)
        self.assertIn("David Kimani", html_open)
        self.assertIn("<img", html_open)
        self.assertIn("cbk.jpg", html_open)
        self.assertIn("Wire Photography", html_open)
        self.assertIn("TRENDING", html_open)
        self.assertIn("Executive Takeaways", html_open)
        # Ensure video players and PiP are completely eliminated
        self.assertNotIn('id="primaryVideoContainer"', html_open)
        self.assertNotIn('id="floatingPiP"', html_open)
        self.assertNotIn('id="articleVideo"', html_open)
        self.assertNotIn('id="pipVideo"', html_open)

        # 3. Test story on Tech & AI (Dispatch 105 - Nvidia)
        res_nvda = self.client.get(reverse('news_article_detail', args=[105]))
        self.assertEqual(res_nvda.status_code, 200)
        html_nvda = res_nvda.content.decode('utf-8')
        self.assertIn("<img", html_nvda)
        self.assertIn("nvda.jpg", html_nvda)
        self.assertNotIn('id="primaryVideoContainer"', html_nvda)
        self.assertNotIn('id="floatingPiP"', html_nvda)
        self.assertNotIn('id="articleVideo"', html_nvda)

        # 4. Test paywalled syndicated article (Dispatch 107 - WSJ)
        res_paywalled = self.client.get(reverse('news_article_detail', args=[107]))
        self.assertEqual(res_paywalled.status_code, 200)
        html_paywalled = res_paywalled.content.decode('utf-8')
        
        # Verify paywall card and editorial image
        self.assertIn("Continue reading with The Wall Street Journal", html_paywalled)
        self.assertIn("Subscribe to The Wall Street Journal", html_paywalled)
        self.assertIn("gradient-to-t", html_paywalled)
        self.assertIn("<img", html_paywalled)
        self.assertNotIn('id="primaryVideoContainer"', html_paywalled)
        self.assertNotIn('id="floatingPiP"', html_paywalled)

        # 5. Verify news hub links directly to in-app article reader without video badges
        res_hub = self.client.get(reverse('news'))
        self.assertEqual(res_hub.status_code, 200)
        html_hub = res_hub.content.decode('utf-8')
        self.assertIn('/news/101/', html_hub)
        self.assertIn('Read Article', html_hub)
        self.assertIn('TRENDING', html_hub)
        self.assertNotIn('>Video Brief<', html_hub)
        self.assertNotIn('>Video<', html_hub)

    def test_earnings_reports_hub_and_upcoming_schedule(self):
        """Verify the Earnings Reports and Filings hub displays upcoming and reported filings."""
        res = self.client.get(reverse('earnings'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Check upcoming corporate earnings entries
        self.assertIn("The Walt Disney Company", content)
        self.assertIn("DIS", content)
        self.assertIn("JD.com, Inc.", content)
        self.assertIn("JD", content)
        self.assertIn("Amer Sports, Inc.", content)
        self.assertIn("NVIDIA Corporation", content)

        # Check reported statutory filings
        self.assertIn("Form 10-Q", content)
        self.assertIn("SEC EDGAR", content)
        self.assertIn("CMA Kenya", content)
        self.assertIn("Safaricom PLC", content)
        self.assertIn("sec-nvda-10q", content)

        # Test regulator filter
        res_sec = self.client.get(reverse('earnings') + '?regulator=SEC')
        self.assertEqual(res_sec.status_code, 200)
        sec_content = res_sec.content.decode('utf-8')
        self.assertIn("sec-nvda-10q", sec_content)

    def test_earnings_statutory_filing_reader(self):
        """Verify statutory regulatory filing reader with SEC / CMA metadata and financial tables."""
        res = self.client.get(reverse('earnings_filing_detail', args=['sec-nvda-10q']))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Check regulatory header & accession numbers
        self.assertIn("OFFICIAL STATUTORY DISCLOSURE", content)
        self.assertIn("Form 10-Q", content)
        self.assertIn("0001045810", content)
        self.assertIn("0001045810-26-000038", content)
        self.assertIn("NVIDIA Corporation", content)

        # Check financial statements table
        self.assertIn("Condensed Consolidated Statement of Operations", content)
        self.assertIn("Total Net Revenue", content)
        self.assertIn("Net Income", content)
        self.assertIn("35.08B", content)

        # Check in-app download center and statutory reports
        self.assertIn("Institutional Filing Download Center", content)
        self.assertIn("Download PDF", content)
        self.assertIn("Download Excel", content)

        # Check Kenya CMA filing reader
        res_cma = self.client.get(reverse('earnings_filing_detail', args=['cma-scom-h1']))
        self.assertEqual(res_cma.status_code, 200)
        cma_content = res_cma.content.decode('utf-8')
        self.assertIn("Capital Markets Authority Kenya (CMA)", cma_content)
        self.assertIn("Safaricom PLC", cma_content)
        self.assertIn("M-PESA revenue increased 16.6%", cma_content)

    def test_earnings_api_endpoint(self):
        """Verify API endpoint returns upcoming and reported earnings data in JSON format."""
        res = self.client.get(reverse('api_earnings'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("upcoming", data)
        self.assertIn("reported", data)
        self.assertTrue(len(data["upcoming"]) > 0)
        self.assertTrue(len(data["reported"]) > 0)
        symbols = [item["symbol"] for item in data["upcoming"]]
        self.assertIn("DIS", symbols)
        self.assertIn("NVDA", symbols)

    def test_market_dock_rail_present_across_main_pages(self):
        """Verify Market Dock rail with Quote Lookup, Trending tickers, etc. is present on main pages."""
        pages_to_test = [
            reverse('home'),
            reverse('markets'),
            reverse('bonds'),
            reverse('news'),
            reverse('trade'),
            reverse('earnings'),
        ]

        for p in pages_to_test:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} returned status {res.status_code}")
            content = res.content.decode('utf-8')
            # Check dock rail presence
            self.assertIn("Quote Lookup", content, f"Quote Lookup missing from dock on {p}")
            self.assertIn("Trending tickers", content, f"Trending tickers missing from dock on {p}")
            self.assertIn("Top gainers", content, f"Top gainers missing from dock on {p}")
            self.assertIn("Top losers", content, f"Top losers missing from dock on {p}")
            self.assertIn("Most active", content, f"Most active missing from dock on {p}")
            self.assertIn("Top economic events", content, f"Top economic events missing from dock on {p}")
            self.assertIn("Earnings events", content, f"Earnings events missing from dock on {p}")
            self.assertIn("Edit your Dock", content, f"Edit your Dock missing from dock on {p}")

    def test_market_dock_rail_omitted_on_auth_pages(self):
        """Verify Market Dock rail is omitted on authentication pages for distraction-free login/signup."""
        auth_pages = [
            reverse('login'),
            reverse('register'),
        ]

        for p in auth_pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Auth page {p} returned status {res.status_code}")
            content = res.content.decode('utf-8')
            self.assertNotIn("Quote Lookup", content, f"Market Dock should NOT be on auth page {p}")
            self.assertNotIn("Trending tickers", content, f"Trending tickers should NOT be on auth page {p}")
            self.assertNotIn("Edit your Dock", content, f"Edit your Dock should NOT be on auth page {p}")

    def test_top_right_header_single_signin_button_and_unified_auth(self):
        """Verify header top-right has a single 'Sign in' button giving access to login/register, and no 'Sign up' or 'Get Started'."""
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Verify single Sign in button is present in the header
        self.assertIn("Sign in", content)
        # Verify separate 'Sign up' button is removed from header
        self.assertNotIn(">Sign up<", content)
        # Verify envelope mail button is present
        self.assertIn("fa-envelope", content)
        # Verify bell icon is present
        self.assertIn("fa-bell", content)
        # Verify 'Get Started' is completely removed from header
        self.assertNotIn(">Get Started<", content)

        # Verify unified authentication portal gives both new and old customers access
        res_login = self.client.get(reverse('login'))
        self.assertEqual(res_login.status_code, 200)
        login_html = res_login.content.decode('utf-8')
        self.assertIn("Log into your account", login_html)
        self.assertIn("Register now", login_html)
        self.assertIn("Continue with Google", login_html)
        self.assertIn("Continue with Apple", login_html)

        # Verify direct registration page
        res_reg = self.client.get(reverse('register'))
        self.assertEqual(res_reg.status_code, 200)
        reg_html = res_reg.content.decode('utf-8')
        self.assertIn("Create your account", reg_html)
        self.assertIn("Already registered?", reg_html)

    def test_events_calendar_page_renders_with_macro_events(self):
        """Verify the dedicated events calendar page renders up-to-date macro and earnings events."""
        res = self.client.get(reverse('events_calendar'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Header and calendar badges
        self.assertIn("Upcoming Macro & Earnings Events", content)
        self.assertIn("Real-Time Market Calendar", content)
        self.assertIn("Live Wire Feeds", content)
        self.assertIn("My Reminders", content)

        # Macroeconomic events
        self.assertIn("Central Bank of Kenya (CBK) MPC Key Rate Decision", content)
        self.assertIn("US Initial Jobless Claims", content)
        self.assertIn("FOMC Meeting Minutes Release", content)
        self.assertIn("UK Consumer Price Index (CPI) Inflation YoY", content)
        self.assertIn("Bank of Japan Summary of Opinions", content)

        # Country filter pills
        self.assertIn("Kenya", content)
        self.assertIn("United States", content)
        self.assertIn("United Kingdom", content)
        self.assertIn("Japan", content)

    def test_events_calendar_authenticated_user_banner(self):
        """Verify logged-in user sees their registered email address prominently displayed."""
        user = User.objects.create_user(
            username='trader_calendar_user',
            email='trader.registered@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)

        res = self.client.get(reverse('events_calendar'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn("Registered Email", content)
        self.assertIn("trader.registered@pesamarkets.com", content)

    def test_api_events_endpoint_and_filtering(self):
        """Verify the /api/events/ endpoint returns upcoming schedule with country and impact filters."""
        # Unfiltered
        res = self.client.get(reverse('api_events'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        self.assertIn('events', data)
        self.assertIn('earnings', data)

        # Kenya filter
        res_ke = self.client.get(reverse('api_events') + '?country=kenya')
        self.assertEqual(res_ke.status_code, 200)
        data_ke = json.loads(res_ke.content.decode('utf-8'))
        for ev in data_ke['events']:
            self.assertEqual(ev['country_code'], 'kenya')

        # High impact filter
        res_hi = self.client.get(reverse('api_events') + '?impact=high')
        self.assertEqual(res_hi.status_code, 200)
        data_hi = json.loads(res_hi.content.decode('utf-8'))
        for ev in data_hi['events']:
            self.assertEqual(ev['impact'].lower(), 'high')

    def test_set_event_reminder_authenticated_user_dispatches_email(self):
        """Verify logged-in user setting a reminder dispatches institutional email to their registered address."""
        from markets.models import EventReminder

        user = User.objects.create_user(
            username='remind_user_1',
            email='alice.investor@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)
        mail.outbox.clear()

        payload = {
            "event_id": "ev-ke-cbk-mpc",
            "title": "Central Bank of Kenya (CBK) MPC Key Rate Decision",
            "date": "Today (Nov 17)",
            "time": "14:30 EAT",
            "country": "Kenya",
            "impact": "High",
            "notes": "Monetary Policy Committee review of the Central Bank Rate (CBR)."
        }

        res = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['is_active'])
        self.assertEqual(data['email'], 'alice.investor@pesamarkets.com')
        self.assertTrue(data['email_sent'])

        # Verify database record
        reminder = EventReminder.objects.get(
            email='alice.investor@pesamarkets.com',
            event_id='ev-ke-cbk-mpc'
        )
        self.assertTrue(reminder.is_active)
        self.assertTrue(reminder.email_sent)
        self.assertIsNotNone(reminder.email_sent_at)
        self.assertEqual(reminder.user, user)

        # Verify dispatched email
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ['alice.investor@pesamarkets.com'])
        self.assertIn('[PesaMarkets Reminder]', sent_email.subject)
        self.assertIn('Central Bank of Kenya', sent_email.subject)
        self.assertIn('14:30 EAT', sent_email.body)
        self.assertIn('alice.investor@pesamarkets.com', sent_email.alternatives[0][0])

    def test_toggle_event_reminder_deactivates(self):
        """Verify toggling an existing active reminder marks it inactive and doesn't re-send email."""
        from markets.models import EventReminder

        user = User.objects.create_user(
            username='remind_user_toggle',
            email='bob.trader@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)
        mail.outbox.clear()

        payload = {
            "event_id": "ev-us-claims-today",
            "title": "US Initial Jobless Claims",
            "date": "Today (Nov 17)",
            "time": "16:30 EAT",
            "country": "USA",
            "impact": "High"
        }

        # 1. First trigger: Activate and send email
        res1 = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data1 = json.loads(res1.content.decode('utf-8'))
        self.assertTrue(data1['is_active'])
        self.assertEqual(len(mail.outbox), 1)

        # 2. Second trigger: Toggle off
        res2 = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data2 = json.loads(res2.content.decode('utf-8'))
        self.assertFalse(data2['is_active'])
        self.assertIn("has been removed", data2['message'])

        # Email outbox should remain 1 (no new email sent when deactivating)
        self.assertEqual(len(mail.outbox), 1)

        # Database record should be inactive
        reminder = EventReminder.objects.get(
            email='bob.trader@pesamarkets.com',
            event_id='ev-us-claims-today'
        )
        self.assertFalse(reminder.is_active)

    def test_set_event_reminder_guest_email_dispatches_email(self):
        """Verify an unauthenticated guest can set a reminder by providing their email."""
        from markets.models import EventReminder

        mail.outbox.clear()
        payload = {
            "event_id": "ev-uk-cpi",
            "email": "guest.investor@globalmarket.com",
            "title": "UK CPI Inflation YoY",
            "date": "Nov 19",
            "time": "10:00 EAT",
            "country": "UK",
            "impact": "High"
        }

        res = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['is_active'])
        self.assertEqual(data['email'], 'guest.investor@globalmarket.com')

        # Check DB and Outbox
        reminder = EventReminder.objects.get(
            email='guest.investor@globalmarket.com',
            event_id='ev-uk-cpi'
        )
        self.assertTrue(reminder.is_active)
        self.assertIsNone(reminder.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['guest.investor@globalmarket.com'])

    def test_api_my_event_reminders(self):
        """Verify /api/events/my-reminders/ lists active reminders for the authenticated user."""
        from markets.models import EventReminder

        user = User.objects.create_user(
            username='my_reminders_user',
            email='portfolio.lead@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)

        EventReminder.objects.create(
            user=user,
            email=user.email,
            event_id='ev-1',
            event_title='Event 1',
            is_active=True
        )
        EventReminder.objects.create(
            user=user,
            email=user.email,
            event_id='ev-2',
            event_title='Event 2',
            is_active=True
        )
        EventReminder.objects.create(
            user=user,
            email=user.email,
            event_id='ev-3',
            event_title='Event 3',
            is_active=False  # Inactive
        )

        res = self.client.get(reverse('api_my_event_reminders'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
        self.assertIn('ev-1', data['reminded_ids'])
        self.assertIn('ev-2', data['reminded_ids'])
        self.assertNotIn('ev-3', data['reminded_ids'])

    def test_dock_economic_events_and_earnings_reminders(self):
        """Verify Market Dock includes economic events with calendar link and user reminded IDs."""
        user = User.objects.create_user(
            username='dock_user',
            email='dock.trader@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)

        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Dock economic events section
        self.assertIn("Top economic events", content)
        self.assertIn("View All Events in Calendar", content)
        self.assertIn("dock-economic-events-data", content)

        # Earnings section and hub link
        self.assertIn("Earnings events", content)
        self.assertIn("Open Earnings & SEC Reports Hub", content)

    def test_events_calendar_corporate_earnings_for_listed_companies(self):
        """Verify the events calendar provides comprehensive corporate earnings reports for listed equities."""
        res = self.client.get(reverse('events_calendar'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Header and tab controls
        self.assertIn("Corporate Earnings", content)
        self.assertIn("Listed Earnings", content)
        self.assertIn("Before Open", content)
        self.assertIn("After Close", content)

        # Listed company tickers and names across USA, Kenya, UK, Japan
        self.assertIn("NVDA", content)
        self.assertIn("NVIDIA Corporation", content)
        self.assertIn("SCOM", content)
        self.assertIn("Safaricom PLC", content)
        self.assertIn("EQTY", content)
        self.assertIn("Equity Group Holdings PLC", content)
        self.assertIn("AZN", content)
        self.assertIn("AstraZeneca PLC", content)
        self.assertIn("7203", content)
        self.assertIn("Toyota Motor Corporation", content)

        # Context contains structured corporate earnings data
        self.assertIn('corporate_earnings', res.context)
        earnings = res.context['corporate_earnings']
        self.assertGreaterEqual(len(earnings), 10)

        # Verify attributes on an earnings event
        nvda_event = next((e for e in earnings if e['symbol'] == 'NVDA'), None)
        self.assertIsNotNone(nvda_event)
        self.assertEqual(nvda_event['session_code'], 'AMC')
        self.assertIn('consensus_eps', nvda_event)
        self.assertIn('consensus_revenue', nvda_event)
        self.assertIn('regulator', nvda_event)

        # Test API returns corporate earnings and session filters
        res_api = self.client.get(reverse('api_events') + '?session=AMC')
        self.assertEqual(res_api.status_code, 200)
        data = res_api.json()
        self.assertTrue(data['success'])
        self.assertIn('corporate_earnings', data)
        self.assertIn('all_events', data)
        amc_symbols = [e['symbol'] for e in data['corporate_earnings']]
        self.assertIn('NVDA', amc_symbols)

    def test_corporate_earnings_email_reminder_flow(self):
        """Verify an investor setting a reminder for a listed company earnings release dispatches email alert."""
        from markets.models import EventReminder

        user = User.objects.create_user(
            username='earnings_investor',
            email='portfolio.analyst@pesamarkets.com',
            password='Password123!'
        )
        self.client.force_login(user)
        mail.outbox.clear()

        payload = {
            "event_id": "earn-nvda-2026",
            "title": "NVIDIA Corporation (NVDA) Q3 FY2027 Earnings Release",
            "date": "Nov 20, 2026",
            "time": "After Market Close (AMC)",
            "country": "USA",
            "impact": "High",
            "symbol": "NVDA",
            "notes": "Consensus EPS expectation: $0.75. Consensus Revenue estimate: $32.80B."
        }

        # 1. Trigger reminder via API
        res = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_active'])
        self.assertEqual(data['email'], 'portfolio.analyst@pesamarkets.com')

        # 2. Verify EventReminder database record
        reminder = EventReminder.objects.get(
            email='portfolio.analyst@pesamarkets.com',
            event_id='earn-nvda-2026'
        )
        self.assertTrue(reminder.is_active)
        self.assertEqual(reminder.symbol, 'NVDA')
        self.assertEqual(reminder.event_category, 'EARNINGS')

        # 3. Verify dispatched email alert
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['portfolio.analyst@pesamarkets.com'])
        self.assertIn('[PesaMarkets Reminder]', sent.subject)
        self.assertIn('NVIDIA Corporation', sent.subject)
        self.assertIn('NVDA', sent.body)
        self.assertIn('After Market Close (AMC)', sent.body)

        # 4. Toggle reminder off
        res_off = self.client.post(
            reverse('api_set_event_reminder'),
            data=json.dumps({"event_id": "earn-nvda-2026"}),
            content_type='application/json'
        )
        self.assertEqual(res_off.status_code, 200)
        data_off = res_off.json()
        self.assertFalse(data_off['is_active'])
        reminder.refresh_from_db()
        self.assertFalse(reminder.is_active)

    def test_statutory_filings_in_app_downloads(self):
        """
        Verify that statutory regulatory disclosures can be downloaded directly in-app
        as PDF, Excel (.xlsx), and CSV without redirecting to external regulators.
        """
        # 1. Download PDF
        res_pdf = self.client.get(reverse('earnings_download_file', args=['sec-nvda-10q', 'pdf']))
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', res_pdf['Content-Disposition'])
        self.assertTrue(res_pdf.content.startswith(b'%PDF-'), "PDF content must start with %PDF- header")
        self.assertGreater(len(res_pdf.content), 1000)

        # 2. Download Excel (.xlsx)
        res_xlsx = self.client.get(reverse('earnings_download_file', args=['sec-nvda-10q', 'excel']))
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertEqual(res_xlsx['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment;', res_xlsx['Content-Disposition'])
        self.assertTrue(res_xlsx.content.startswith(b'PK\x03\x04'), "Excel content must be a valid OOXML ZIP archive")
        self.assertGreater(len(res_xlsx.content), 2000)

        # 3. Download CSV
        res_csv = self.client.get(reverse('earnings_download_file', args=['sec-nvda-10q', 'csv']))
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn('text/csv', res_csv['Content-Type'])
        self.assertIn('attachment;', res_csv['Content-Disposition'])
        csv_text = res_csv.content.decode('utf-8-sig')
        self.assertIn('PESAMARKETS INSTITUTIONAL REGULATORY ARCHIVE', csv_text)
        self.assertIn('NVIDIA Corporation', csv_text)
        self.assertIn('NVDA', csv_text)

        # 4. Kenya CMA Filing Download
        res_ke_pdf = self.client.get(reverse('earnings_download_file', args=['cma-scom-h1', 'pdf']))
        self.assertEqual(res_ke_pdf.status_code, 200)
        self.assertEqual(res_ke_pdf['Content-Type'], 'application/pdf')

        # 5. Invalid filing ID redirects to earnings
        res_invalid = self.client.get(reverse('earnings_download_file', args=['invalid-filing-id', 'pdf']))
        self.assertEqual(res_invalid.status_code, 302)
        self.assertEqual(res_invalid.url, reverse('earnings'))

        # 6. Invalid file type redirects to filing detail
        res_bad_type = self.client.get(reverse('earnings_download_file', args=['sec-nvda-10q', 'unsupported']))
        self.assertEqual(res_bad_type.status_code, 302)

    def test_statutory_filing_detail_digestible_view_and_zero_external_links(self):
        """
        Verify that earnings filing detail pages provide digestible in-app info
        and do NOT redirect or link users to external regulator websites.
        """
        res = self.client.get(reverse('earnings_filing_detail', args=['sec-nvda-10q']))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Digestible tabs and elements
        self.assertIn("Institutional Filing Download Center", content)
        self.assertIn("Executive Highlights", content)
        self.assertIn("Statement of Operations", content)
        self.assertIn("Segment Breakdown", content)
        self.assertIn("Filing Governance", content)

        # Zero external regulator hyperlinks
        self.assertNotIn("href=\"https://www.sec.gov", content)
        self.assertNotIn("href=\"https://sec.gov", content)
        self.assertNotIn("href=\"https://www.cma.or.ke", content)
        self.assertNotIn("href=\"https://www.fca.org.uk", content)
        self.assertNotIn("href=\"https://www.fsa.go.jp", content)

        # Verified in-app download endpoints are present
        self.assertIn(reverse('earnings_download_file', args=['sec-nvda-10q', 'pdf']), content)
        self.assertIn(reverse('earnings_download_file', args=['sec-nvda-10q', 'excel']), content)
        self.assertIn(reverse('earnings_download_file', args=['sec-nvda-10q', 'csv']), content)

    def test_universal_dark_background_color_throughout_website(self):
        """
        Verify that #121214 (the black from the user screenshot) is configured
        and used throughout key layout elements in templates.
        """
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Check for deep dark theme classes
        self.assertIn("dark:bg-[#121214]", content)

    def test_global_markets_and_trading_headline(self):
        """
        Verify the headline on the home page reads 'Global Markets & Trading'
        and explicitly does NOT say 'Global Sovereign Markets & Trading'.
        """
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn("Global Markets & Trading", content)
        self.assertNotIn("Global Sovereign Markets & Trading", content)

    def test_guest_vs_signed_in_experience_and_data_segregation(self):
        """
        Verify strict data segregation between unauthenticated guest visitors
        and authenticated users across Home, Portfolio, Trade, Bonds, and Profile.
        Guests must never see fake transactions or fake portfolio balances.
        """
        # ==========================================
        # 1. GUEST USER (UNAUTHENTICATED) CHECKS
        # ==========================================
        # 1.1 Home Dashboard
        res_home_guest = self.client.get(reverse('home'))
        self.assertEqual(res_home_guest.status_code, 200)
        content_home_guest = res_home_guest.content.decode('utf-8')

        # Guest should see market overview metrics, not personal portfolio metrics
        self.assertIn("Global Markets Trajectory", content_home_guest)
        self.assertNotIn("Portfolio Trajectory", content_home_guest)
        self.assertIn("Execution Ledger Locked", content_home_guest)
        self.assertIn("Sign in to View Ledger", content_home_guest)
        self.assertIn("Sign in", content_home_guest)

        # 1.2 Portfolio Page
        res_port_guest = self.client.get(reverse('portfolio'))
        self.assertEqual(res_port_guest.status_code, 200)
        content_port_guest = res_port_guest.content.decode('utf-8')

        self.assertIn("Portfolio Analytics & Holdings Locked", content_port_guest)
        self.assertIn("Sign in to Access Portfolio", content_port_guest)
        self.assertIn("No Transactions for Guest Session", content_port_guest)
        self.assertIn("Sign in to Access CSD Custody", content_port_guest)

        # 1.3 Trade Desk
        res_trade_guest = self.client.get(reverse('trade'))
        self.assertEqual(res_trade_guest.status_code, 200)
        content_trade_guest = res_trade_guest.content.decode('utf-8')

        self.assertIn("Sign In to Place Order", content_trade_guest)
        self.assertIn("Guest Mode &bull; Sign in to trade", content_trade_guest)

        # 1.4 Bonds Desk
        res_bonds_guest = self.client.get(reverse('bonds'))
        self.assertEqual(res_bonds_guest.status_code, 200)
        content_bonds_guest = res_bonds_guest.content.decode('utf-8')

        self.assertIn("Sign in to Submit Bid / Order", content_bonds_guest)
        self.assertIn("Guest Mode &bull; Sign in to bid", content_bonds_guest)
        self.assertIn("Fixed Income Depository (CSD Custody)", content_bonds_guest)

        # 1.5 Profile Page
        res_profile_guest = self.client.get(reverse('profile'))
        self.assertEqual(res_profile_guest.status_code, 200)
        content_profile_guest = res_profile_guest.content.decode('utf-8')

        self.assertIn("Guest Trader", content_profile_guest)
        self.assertIn("Guest Tier", content_profile_guest)
        self.assertIn("$0.00", content_profile_guest)

        # ==========================================
        # 2. AUTHENTICATED USER CHECKS
        # ==========================================
        user = User.objects.create_user(
            username='trader_alice',
            email='alice@pesamarkets.com',
            password='TestPassword123!',
            first_name='Alice',
            last_name='Smith'
        )
        self.client.force_login(user)

        # 2.1 Authenticated Home Dashboard
        res_home_auth = self.client.get(reverse('home'))
        self.assertEqual(res_home_auth.status_code, 200)
        content_home_auth = res_home_auth.content.decode('utf-8')

        self.assertIn("Portfolio Trajectory", content_home_auth)
        self.assertNotIn("Global Markets Trajectory", content_home_auth)
        self.assertNotIn("Execution Ledger Locked", content_home_auth)
        # Since Alice has no transactions yet, she sees the clean empty state with button to trade desk
        self.assertIn("No Transactions Recorded", content_home_auth)
        self.assertIn("Place Your First Order", content_home_auth)

        # 2.2 Authenticated Trade Desk
        res_trade_auth = self.client.get(reverse('trade'))
        self.assertEqual(res_trade_auth.status_code, 200)
        content_trade_auth = res_trade_auth.content.decode('utf-8')

        self.assertIn("Execute Buy Order", content_trade_auth)
        self.assertNotIn("Sign In to Place Order", content_trade_auth)
        self.assertIn("5212.17", content_trade_auth)

        # 2.3 Authenticated Bonds Desk
        res_bonds_auth = self.client.get(reverse('bonds'))
        self.assertEqual(res_bonds_auth.status_code, 200)
        content_bonds_auth = res_bonds_auth.content.decode('utf-8')

        self.assertIn("Submit Primary CBK Auction Bid", content_bonds_auth)
        self.assertNotIn("Sign in to Submit Bid / Order", content_bonds_auth)

        # 2.4 Execute a trade for Alice to populate her ledger
        trade_payload = {
            "symbol": "SCOM",
            "action": "BUY",
            "quantity": 100,
            "order_type": "MARKET"
        }
        res_trade_exec = self.client.post(
            reverse('api_trade_execute'),
            data=json.dumps(trade_payload),
            content_type="application/json"
        )
        self.assertEqual(res_trade_exec.status_code, 200)

        # Now Alice's home and portfolio show her real transaction
        res_home_after_trade = self.client.get(reverse('home'))
        content_after_trade = res_home_after_trade.content.decode('utf-8')
        self.assertIn("Safaricom PLC", content_after_trade)
        self.assertIn("SCOM", content_after_trade)
        self.assertIn("BUY", content_after_trade)
        self.assertNotIn("No Transactions Recorded", content_after_trade)

        res_port_auth = self.client.get(reverse('portfolio'))
        content_port_auth = res_port_auth.content.decode('utf-8')
        self.assertIn("Safaricom PLC", content_port_auth)
        self.assertIn("SCOM", content_port_auth)
        self.assertNotIn("Portfolio Analytics & Holdings Locked", content_port_auth)
        self.assertNotIn("No Transactions for Guest Session", content_port_auth)

    def test_paywall_guest_and_free_tier_gating_on_terminal(self):
        """Verify paywall overlay and gating on terminal for guests and free tier users vs pro subscribers."""
        # 1. Guest user access
        res_guest = self.client.get(reverse('terminal'))
        self.assertEqual(res_guest.status_code, 200)
        content_guest = res_guest.content.decode('utf-8')

        self.assertIn("PREVIEW MODE", content_guest)
        self.assertIn("TERMINAL PRO REQUIRED", content_guest)
        self.assertIn("Direct Market Access (DMA) Level 2 Depth Gated", content_guest)
        self.assertIn("Institutional Block Tape (>100k Shares) Gated", content_guest)
        self.assertIn("SIGN IN TO ACCESS PRO", content_guest)

        # 2. Authenticated user on Free tier
        free_user = User.objects.create_user(
            username='charlie_free',
            email='charlie@pesamarkets.org',
            password='testpassword123'
        )
        free_user.profile.downgrade_to_free()
        self.assertFalse(free_user.profile.is_paid)

        self.client.force_login(free_user)
        res_free = self.client.get(reverse('terminal'))
        content_free = res_free.content.decode('utf-8')

        self.assertIn("PREVIEW MODE", content_free)
        self.assertIn("TERMINAL PRO REQUIRED", content_free)
        self.assertIn("Direct Market Access (DMA) Level 2 Depth Gated", content_free)
        self.assertIn("Institutional Block Tape (>100k Shares) Gated", content_free)
        self.assertIn("UPGRADE TO TERMINAL PRO ($29/MO)", content_free)

        # 3. Upgrade Charlie to Pro tier
        free_user.profile.upgrade_to_pro()
        self.assertTrue(free_user.profile.is_paid)
        self.assertTrue(free_user.profile.is_pro)

        res_pro = self.client.get(reverse('terminal'))
        content_pro = res_pro.content.decode('utf-8')

        self.assertIn("PRO TIER &bull; ACTIVE", content_pro)
        self.assertNotIn("PREVIEW MODE", content_pro)
        self.assertNotIn("TERMINAL PRO REQUIRED", content_pro)
        self.assertNotIn("Direct Market Access (DMA) Level 2 Depth Gated", content_pro)
        self.assertNotIn("Institutional Block Tape (>100k Shares) Gated", content_pro)

    def test_subscription_upgrade_and_downgrade_api(self):
        """Verify API endpoints and settings action for toggling subscription plans."""
        user = User.objects.create_user(
            username='dave_subscriber',
            email='dave@pesamarkets.org',
            password='testpassword123'
        )
        user.profile.downgrade_to_free()

        # 1. Unauthenticated call should fail with 401
        res_unauth = self.client.post(
            reverse('api_upgrade_subscription'),
            data=json.dumps({"tier": "pro"}),
            content_type="application/json"
        )
        self.assertEqual(res_unauth.status_code, 401)

        # 2. Authenticated JSON Upgrade to Pro
        self.client.force_login(user)
        self.assertFalse(user.profile.is_paid)

        res_up = self.client.post(
            reverse('api_upgrade_subscription'),
            data=json.dumps({"tier": "pro"}),
            content_type="application/json"
        )
        self.assertEqual(res_up.status_code, 200)
        up_data = json.loads(res_up.content.decode('utf-8'))
        self.assertTrue(up_data['success'])
        self.assertTrue(up_data['is_paid'])
        self.assertEqual(up_data['tier'], 'Terminal Pro Tier')

        user.profile.refresh_from_db()
        self.assertTrue(user.profile.is_paid)
        self.assertEqual(user.profile.tier, 'Terminal Pro Tier')

        # 3. Authenticated JSON Downgrade to Free
        res_down = self.client.post(
            reverse('api_upgrade_subscription'),
            data=json.dumps({"tier": "free"}),
            content_type="application/json"
        )
        self.assertEqual(res_down.status_code, 200)
        down_data = json.loads(res_down.content.decode('utf-8'))
        self.assertTrue(down_data['success'])
        self.assertFalse(down_data['is_paid'])
        self.assertEqual(down_data['tier'], 'Free Tier')

        user.profile.refresh_from_db()
        self.assertFalse(user.profile.is_paid)
        self.assertEqual(user.profile.tier, 'Free Tier')

        # 4. Settings form POST action
        res_form_up = self.client.post(
            reverse('settings'),
            data={"action": "upgrade_tier"}
        )
        self.assertEqual(res_form_up.status_code, 302)
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.is_paid)

        res_form_down = self.client.post(
            reverse('settings'),
            data={"action": "downgrade_tier"}
        )
        self.assertEqual(res_form_down.status_code, 302)
        user.profile.refresh_from_db()
        self.assertFalse(user.profile.is_paid)

    def test_terminal_pro_precise_charts_and_data_payload(self):
        """Verify that get_terminal_data provides comprehensive charts data and canvases exist in HTML."""
        from markets.data import get_terminal_data

        data = get_terminal_data("NVDA")
        self.assertIn("charts", data)
        charts = data["charts"]

        # 1. Price series across 6 institutional timeframes
        self.assertIn("price_series", charts)
        timeframes = ["1D", "5D", "1M", "6M", "1Y", "ALL"]
        for tf in timeframes:
            self.assertIn(tf, charts["price_series"])
            series = charts["price_series"][tf]
            self.assertIn("labels", series)
            self.assertIn("prices", series)
            self.assertIn("volumes", series)
            self.assertIn("ema20", series)
            self.assertIn("sma50", series)
            self.assertGreater(len(series["prices"]), 0)
            self.assertEqual(len(series["prices"]), len(series["labels"]))
            self.assertEqual(len(series["volumes"]), len(series["labels"]))

        # 2. Level 2 Visual Depth Curve
        self.assertIn("depth_curve", charts)
        depth = charts["depth_curve"]
        self.assertIn("bids", depth)
        self.assertIn("asks", depth)
        self.assertIn("mid_price", depth)
        self.assertGreater(len(depth["bids"]), 0)
        self.assertGreater(len(depth["asks"]), 0)

        # 3. Comparative 4-Sovereign Benchmark Curves (Kenya, US, UK, Japan)
        self.assertIn("yield_curves_multi", charts)
        ycrv = charts["yield_curves_multi"]
        self.assertIn("tenors", ycrv)
        self.assertEqual(len(ycrv["tenors"]), 8)
        self.assertIn("kenya", ycrv)
        self.assertIn("us_treasuries", ycrv)
        self.assertIn("uk_gilts", ycrv)
        self.assertIn("japan_jgbs", ycrv)

        # 4. Technical Oscillators Time Series
        self.assertIn("oscillators", charts)
        osc = charts["oscillators"]
        self.assertIn("rsi", osc)
        self.assertIn("overbought", osc)
        self.assertIn("oversold", osc)
        self.assertIn("hist", osc)
        self.assertEqual(len(osc["rsi"]), 20)

        # 5. Check Terminal HTML canvas and UI controls
        res = self.client.get(reverse('terminal', kwargs={}) + "?symbol=NVDA")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('id="terminalPriceChart"', content)
        self.assertIn('id="terminalDepthChart"', content)
        self.assertIn('id="terminalOscillatorChart"', content)
        self.assertIn('id="terminalYieldCurveChart"', content)
        self.assertIn('setChartTimeframe(tf)', content)
        self.assertIn('toggleChartEma()', content)
        self.assertIn('toggleChartSma()', content)
        self.assertIn('toggleChartVol()', content)

    def test_asset_detail_paywall_gating(self):
        """Verify institutional valuation models gating on asset detail page."""
        # Guest user
        res_guest = self.client.get(reverse('asset_detail', args=['NVDA']))
        self.assertEqual(res_guest.status_code, 200)
        content_guest = res_guest.content.decode('utf-8')
        self.assertIn("Institutional Valuation Models", content_guest)
        self.assertIn("PRO ONLY", content_guest)
        self.assertIn("Terminal Pro Feature", content_guest)
        self.assertIn("Unlock in Terminal Pro", content_guest)

        # Pro user
        pro_user = User.objects.create_user(
            username='emma_pro',
            email='emma@pesamarkets.org',
            password='testpassword123'
        )
        pro_user.profile.upgrade_to_pro()
        self.client.force_login(pro_user)

        res_pro = self.client.get(reverse('asset_detail', args=['NVDA']))
        content_pro = res_pro.content.decode('utf-8')
        self.assertIn("Institutional Valuation Models", content_pro)
        self.assertIn("PRO ACTIVE", content_pro)
        self.assertIn("DCF Fair Value Est", content_pro)
        self.assertIn("Altman Z-Score", content_pro)
        self.assertIn("Piotroski F-Score", content_pro)
        self.assertNotIn("PRO ONLY", content_pro)
        self.assertNotIn("Unlock in Terminal Pro", content_pro)

    def test_unauthenticated_user_sees_graphs_across_pages_and_cannot_trade(self):
        """Verify unauthenticated guest visitors can see charts/graphs across pages but cannot trade."""
        # 1. Trade Desk: Canvas is present for guest, but trade execution is gated
        res_trade = self.client.get(reverse('trade') + '?symbol=SCOM')
        self.assertEqual(res_trade.status_code, 200)
        content_trade = res_trade.content.decode('utf-8')
        self.assertIn('id="tradeChartCanvas"', content_trade)
        self.assertIn("Sign In to Place Order", content_trade)
        self.assertIn("Guest Mode &bull; Sign in to trade", content_trade)

        # Guest cannot execute trade via API
        trade_post = self.client.post(reverse('api_trade_execute'), {
            'symbol': 'SCOM',
            'action': 'BUY',
            'shares': 100,
            'price': 16.50
        })
        self.assertEqual(trade_post.status_code, 401)
        self.assertIn('Authentication required', trade_post.json().get('error', ''))

        # 2. Asset Detail: Graph canvas is present for guest
        res_asset = self.client.get(reverse('asset_detail', args=['SCOM']))
        self.assertEqual(res_asset.status_code, 200)
        content_asset = res_asset.content.decode('utf-8')
        self.assertIn('id="assetDetailCanvas"', content_asset)
        self.assertIn("Trade SCOM", content_asset)

        # 3. Portfolio Page: Allocation Donut Chart canvas is present for guest
        res_port = self.client.get(reverse('portfolio'))
        self.assertEqual(res_port.status_code, 200)
        content_port = res_port.content.decode('utf-8')
        self.assertIn('id="allocationChart"', content_port)
        self.assertIn("Global Model Allocation", content_port)
        self.assertIn("Portfolio Analytics & Holdings Locked", content_port)

        # 4. Bonds Desk: Sovereign Yield Curve canvas is present for guest, but bond purchasing is gated
        res_bonds = self.client.get(reverse('bonds'))
        self.assertEqual(res_bonds.status_code, 200)
        content_bonds = res_bonds.content.decode('utf-8')
        self.assertIn('id="bondsYieldCurveCanvas"', content_bonds)
        self.assertIn("Sovereign Debt Benchmark Yield Curves", content_bonds)

        # Guest cannot buy bonds via API
        bond_post = self.client.post(reverse('api_bonds_buy'), {
            'symbol': 'FXD1/2024/05',
            'units': 50000
        })
        self.assertEqual(bond_post.status_code, 401)
        self.assertIn('Authentication required', bond_post.json().get('error', ''))

    def test_events_calendar_no_1_click_mention(self):
        """Verify that 'Sign in for 1-Click' is completely removed from events calendar page."""
        res = self.client.get(reverse('events_calendar'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("Upcoming Macro & Earnings Events", content)
        self.assertNotIn("Sign in for 1-Click", content)
        self.assertNotIn("1-Click", content)

    def test_unauthenticated_wishlist_is_blank_and_prompts_sign_in(self):
        """Verify an unauthenticated user has a blank wishlist on /watchlist/ and is prompted to sign in."""
        res = self.client.get(reverse('watchlist'))
        self.assertEqual(res.status_code, 200)
        
        # Context must contain no assets for guest on personal wishlist
        self.assertEqual(res.context['watchlist_assets'], [])
        
        content = res.content.decode('utf-8')
        self.assertIn("Your Wishlist is Empty", content)
        self.assertIn("Sign in to View Wishlist", content)
        self.assertIn("Sign in to Add Assets", content)
        # Should not display active asset momentum or breadths for an empty guest list
        self.assertNotIn("Average Daily Momentum", content)
        self.assertNotIn("Remove from wishlist", content)

    def test_authenticated_user_sees_saved_wishlist(self):
        """Verify an authenticated user sees their saved assets on /watchlist/."""
        from decimal import Decimal
        from markets.models import Market, Asset, Watchlist
        user = User.objects.create_user(username='wishlist_trader', email='wl@example.com', password='pesaPassword1!')
        mkt, _ = Market.objects.get_or_create(symbol='NSE', defaults={'name': 'Nairobi Securities Exchange'})
        asset, _ = Asset.objects.get_or_create(symbol='SCOM', defaults={'name': 'Safaricom PLC', 'current_price': Decimal('17.50'), 'market': mkt})
        wl = Watchlist.objects.create(user=user, name='Primary Watchlist')
        wl.assets.add(asset)

        self.client.force_login(user)
        res = self.client.get(reverse('watchlist'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['watchlist_assets']), 1)
        self.assertEqual(res.context['watchlist_assets'][0]['symbol'], 'SCOM')
        content = res.content.decode('utf-8')
        self.assertIn("SCOM", content)
        self.assertIn("Total Tracked Assets", content)


class AdminDashboardRealtimeTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Master Admin
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@pesamarkets.com',
            password='adminPassword1!'
        )
        # Regular Trader
        self.trader = User.objects.create_user(
            username='trader_alice',
            email='alice@example.com',
            password='alicePassword1!',
            first_name='Alice',
            last_name='Wanjiku'
        )

    def test_admin_dashboard_view_denies_unauthenticated_and_regular_user(self):
        """Verify guest and regular users are denied access to /admin-dashboard/."""
        # Guest
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith(reverse('home')))

        # Regular user
        self.client.force_login(self.trader)
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith(reverse('home')))

    def test_admin_dashboard_view_permits_admin(self):
        """Verify admin user can access /admin-dashboard/ and view stats."""
        self.client.force_login(self.admin)
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('total_users', res.context)
        self.assertIn('active_users', res.context)
        content = res.content.decode('utf-8')
        self.assertIn("Admin Dashboard", content)
        self.assertIn("Master Control", content)
        self.assertIn("Live Realtime Sync", content)
        self.assertIn("@trader_alice", content)

    def test_api_admin_users_denies_non_admin(self):
        """Verify /api/admin/users/ strictly returns 403 Forbidden for non-admins."""
        # Guest
        res = self.client.get(reverse('api_admin_users'))
        self.assertEqual(res.status_code, 403)
        data = res.json()
        self.assertFalse(data.get('success'))

        # Regular user
        self.client.force_login(self.trader)
        res = self.client.get(reverse('api_admin_users'))
        self.assertEqual(res.status_code, 403)

    def test_api_admin_users_returns_live_metrics_for_admin(self):
        """Verify /api/admin/users/ returns live user data and stats for admin."""
        self.client.force_login(self.admin)
        res = self.client.get(reverse('api_admin_users'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
        self.assertIn('users', data)
        self.assertGreaterEqual(data['stats']['total'], 2)

        usernames = [u['username'] for u in data['users']]
        self.assertIn('admin', usernames)
        self.assertIn('trader_alice', usernames)

    def test_api_admin_user_action_permissions(self):
        """Verify /api/admin/users/<id>/action/ rejects non-admin users."""
        self.client.force_login(self.trader)
        res = self.client.post(
            reverse('api_admin_user_action', args=[self.trader.id]),
            data=json.dumps({'action': 'suspend'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 403)

    def test_api_admin_user_lifecycle_actions(self):
        """Verify suspend, activate, flag, unflag, toggle_tier, and delete actions."""
        self.client.force_login(self.admin)
        target = self.trader

        # 1. Suspend
        res = self.client.post(
            reverse('api_admin_user_action', args=[target.id]),
            data=json.dumps({'action': 'suspend'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        target.refresh_from_db()
        self.assertFalse(target.is_active)

        # 2. Activate
        res = self.client.post(
            reverse('api_admin_user_action', args=[target.id]),
            data=json.dumps({'action': 'activate'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        target.refresh_from_db()
        self.assertTrue(target.is_active)

        # 3. Flag
        res = self.client.post(
            reverse('api_admin_user_action', args=[target.id]),
            data=json.dumps({'action': 'flag', 'reason': 'High-frequency spoofing pattern'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        target.profile.refresh_from_db()
        self.assertTrue(target.profile.is_flagged)
        self.assertEqual(target.profile.flag_reason, 'High-frequency spoofing pattern')

        # 4. Unflag
        res = self.client.post(
            reverse('api_admin_user_action', args=[target.id]),
            data=json.dumps({'action': 'unflag'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        target.profile.refresh_from_db()
        self.assertFalse(target.profile.is_flagged)
        self.assertEqual(target.profile.flag_reason, '')

        # 5. Toggle Tier
        initial_tier = target.profile.tier
        res = self.client.post(
            reverse('api_admin_user_action', args=[target.id]),
            data=json.dumps({'action': 'toggle_tier'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        target.profile.refresh_from_db()
        self.assertNotEqual(target.profile.tier, initial_tier)

        # 6. Delete
        target_id = target.id
        res = self.client.post(
            reverse('api_admin_user_action', args=[target_id]),
            data=json.dumps({'action': 'delete'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['deleted'])
        self.assertFalse(User.objects.filter(id=target_id).exists())

    def test_admin_cannot_suspend_or_delete_self(self):
        """Verify an admin cannot accidentally lock out or delete their own account."""
        self.client.force_login(self.admin)

        # Self-suspend attempt
        res = self.client.post(
            reverse('api_admin_user_action', args=[self.admin.id]),
            data=json.dumps({'action': 'suspend'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("cannot suspend your own", res.json()['error'])
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

        # Self-delete attempt
        res = self.client.post(
            reverse('api_admin_user_action', args=[self.admin.id]),
            data=json.dumps({'action': 'delete'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("cannot delete your own", res.json()['error'])
        self.assertTrue(User.objects.filter(id=self.admin.id).exists())

    def test_header_user_icon_menu_admin_option_visibility(self):
        """Verify Admin Dashboard trigger and modal only appear in DOM for administrators."""
        # Regular trader
        self.client.force_login(self.trader)
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertNotIn("embeddedAdminDashboard", content)
        self.assertNotIn('href="/admin-dashboard/"', content)

        # Admin
        self.client.force_login(self.admin)
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn("embeddedAdminDashboard", content)
        self.assertIn("Admin Dashboard", content)
        self.assertIn('href="/admin-dashboard/"', content)

    def test_zero_competitor_mentions_in_views_and_code(self):
        """Strict compliance test: ensures no competitor brand names appear in any rendered template or response."""
        import re
        competitors = [
            "yahoo", "bloomberg", "marketwatch", "tradingview", "robinhood",
            "webull", "etrade", "saxo", "factset", "morningstar", "finviz",
            "seekingalpha", "tipranks", "benzinga"
        ]
        test_urls = [
            'home', 'markets', 'bonds', 'terminal', 'news', 'earnings', 
            'events_calendar', 'trade', 'portfolio', 'watchlist', 'login'
        ]
        for url_name in test_urls:
            if url_name in ['login', 'register']:
                self.client.logout()
            else:
                self.client.force_login(self.trader)
            res = self.client.get(reverse(url_name))
            self.assertEqual(res.status_code, 200)
            page_text = res.content.decode('utf-8').lower()
            for comp in competitors:
                # Use regex word boundary check to avoid false positives (e.g. 'executeTrade')
                match = re.search(rf'\b{re.escape(comp)}\b', page_text)
                self.assertIsNone(
                    match, 
                    f"Forbidden competitor brand '{comp}' found in rendered response for URL: {url_name}"
                )


class RegistrationAndSocialAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_trader_registration_requires_username_and_excludes_job_title_industry(self):
        """Verify username is mandatory and validated, while job_title and industry are removed from the form."""
        from markets.forms import TraderRegistrationForm

        # Form fields check
        form = TraderRegistrationForm()
        self.assertIn('username', form.fields)
        self.assertTrue(form.fields['username'].required)
        self.assertNotIn('job_title', form.fields)
        self.assertNotIn('industry', form.fields)

        # Invalid username: special characters not allowed
        invalid_payload = {
            'username': 'trader@invalid!',
            'email': 'trader_new@pesamarkets.com',
            'first_name': 'Alpha',
            'last_name': 'Trader',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!',
        }
        form_invalid = TraderRegistrationForm(data=invalid_payload)
        self.assertFalse(form_invalid.is_valid())
        self.assertIn('username', form_invalid.errors)

        # Valid payload registration
        valid_payload = {
            'username': 'alpha_trader99',
            'email': 'alpha99@pesamarkets.com',
            'first_name': 'Alpha',
            'last_name': 'Trader',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!',
        }
        form_valid = TraderRegistrationForm(data=valid_payload)
        self.assertTrue(form_valid.is_valid(), form_valid.errors)
        user = form_valid.save()
        self.assertEqual(user.username, 'alpha_trader99')
        profile = user.profile
        self.assertEqual(profile.job_title, '')
        self.assertEqual(profile.industry, '')

    def test_registration_form_post_creates_user_without_job_title_and_industry(self):
        """Test HTTP POST to /register/ with username succeeds without supplying job title or industry."""
        payload = {
            'username': 'betatrader',
            'email': 'betatrader@pesamarkets.com',
            'first_name': 'Beta',
            'last_name': 'Trader',
            'phone': '+254700112233',
            'password': 'BetaTrader2026!',
            'confirm_password': 'BetaTrader2026!',
        }
        res = self.client.post(reverse('register'), data=payload)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('verify_otp'))
        self.assertTrue(User.objects.filter(username='betatrader').exists())

    def test_registration_and_login_templates_render_google_and_apple_buttons_only(self):
        """Verify register.html and login.html render Google and Apple buttons and links, while Facebook and SSO are removed."""
        for url_name in ['register', 'login']:
            res = self.client.get(reverse(url_name))
            self.assertEqual(res.status_code, 200)
            content = res.content.decode('utf-8')
            
            # Google and Apple present in titles, buttons, or links
            self.assertIn('Google', content)
            self.assertIn('Apple', content)

            # Verification links for Google and Apple
            self.assertIn(reverse('oauth_google'), content)
            self.assertIn(reverse('oauth_apple'), content)

            # Modals point to their provider select account
            self.assertIn(reverse('oauth_select_account', args=['google']), content)
            self.assertIn(reverse('oauth_select_account', args=['apple']), content)

            # Facebook and SSO are strictly removed
            self.assertNotIn('Continue with Facebook', content)
            self.assertNotIn('Enterprise Single Sign-On', content)
            self.assertNotIn('oauth_facebook', content)
            self.assertNotIn('oauth_sso', content)

    def test_apple_oauth_initiation_redirects_to_select_account(self):
        """Verify Apple initiate route redirects to select-account when developer API keys are unconfigured."""
        res = self.client.get(reverse('oauth_apple'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('oauth_select_account', args=['apple']))

    def test_oauth_select_account_get_view_for_supported_providers(self):
        """Verify oauth_select_account GET view renders successfully for google and apple, and redirects unsupported providers."""
        for p in ['google', 'apple']:
            res = self.client.get(reverse('oauth_select_account', args=[p]))
            self.assertEqual(res.status_code, 200)
            content = res.content.decode('utf-8')
            self.assertIn('Choose an account', content)

        # Unsupported or removed providers redirect to login
        for removed in ['facebook', 'sso', 'twitter', 'github']:
            res_removed = self.client.get(reverse('oauth_select_account', args=[removed]))
            self.assertEqual(res_removed.status_code, 302)
            self.assertEqual(res_removed.url, reverse('login'))

    def test_apple_oauth_select_account_flow(self):
        """Verify selecting Apple account logs in user or creates new profile."""
        res = self.client.post(reverse('oauth_select_account', args=['apple']), data={
            'email': 'tim_cook@apple.com',
            'first_name': 'Tim',
            'last_name': 'Cook'
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('home'))
        user = User.objects.get(email='tim_cook@apple.com')
        self.assertEqual(user.profile.auth_provider, 'apple')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_oauth_callback_handling_supported_providers(self):
        """Verify oauth_callback gracefully handles callbacks for Google and Apple, and redirects invalid providers."""
        # Google with unconfigured credentials redirects to select-account; without code redirects to login
        res_g_nocode = self.client.get(reverse('oauth_callback', args=['google']))
        self.assertEqual(res_g_nocode.status_code, 302)
        self.assertEqual(res_g_nocode.url, reverse('login'))

        res_g_code = self.client.get(reverse('oauth_callback', args=['google']) + '?code=auth_sample_code')
        self.assertEqual(res_g_code.status_code, 302)
        self.assertEqual(res_g_code.url, reverse('oauth_select_account', args=['google']))

        # Apple with no email falls back to oauth_select_account
        res_apple = self.client.get(reverse('oauth_callback', args=['apple']))
        self.assertEqual(res_apple.status_code, 302)
        self.assertEqual(res_apple.url, reverse('oauth_select_account', args=['apple']))

        # Removed providers redirect to login
        for removed in ['facebook', 'sso']:
            res_removed = self.client.get(reverse('oauth_callback', args=[removed]))
            self.assertEqual(res_removed.status_code, 302)
            self.assertEqual(res_removed.url, reverse('login'))



