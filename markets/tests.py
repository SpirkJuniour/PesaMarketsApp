from django.test import TestCase, Client
from django.urls import reverse
import json

class PesaMarketsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_yahoo_finance_mentions_in_templates(self):
        """Verify that Yahoo Finance is not mentioned anywhere across pages."""
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
            reverse('asset_detail', args=['BTC']),
            reverse('asset_detail', args=['T91']),
            reverse('asset_detail', args=['IFB10Y']),
        ]

        for u in urls_to_test:
            res = self.client.get(u)
            self.assertEqual(res.status_code, 200)
            content = res.content.decode('utf-8').lower()
            self.assertNotIn("yahoo", content, f"Yahoo found in response for URL: {u}")
            self.assertNotIn("yahoo finance", content, f"Yahoo Finance found in response for URL: {u}")

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

    def test_terminal_pro_page_renders_bloomberg_saxo_components(self):
        """Verify the Terminal Pro page renders with rich institutional components."""
        res = self.client.get(reverse('terminal'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        # Check Bloomberg & SaxoTraderGO elements
        self.assertIn("BLOOMBERG &bull; SAXOTRADERGO WORKSTATION", content)
        self.assertIn("OVERVIEW & LEVEL 2 DEPTH", content)
        self.assertIn("VALUATION & STATEMENTS (FA)", content)
        self.assertIn("SAXO TECHNICALS & SENTIMENT", content)
        self.assertIn("TIME & SALES / BLOCK TAPE", content)
        self.assertIn("MACRO CALENDAR & CBK/FED (ECO)", content)
        self.assertIn("SOVEREIGN YIELDS & CORR (YCRV)", content)
        self.assertIn("Level 2 Market Depth (Order Book)", content)

    def test_terminal_api_endpoints(self):
        """Verify the REST API returns valid JSON with all required institutional metrics."""
        for sym in ["SCOM", "NVDA", "BTC", "GOLD"]:
            res = self.client.get(reverse('api_terminal_data', args=[sym]))
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.content.decode('utf-8'))
            
            # Verify keys exist
            self.assertIn("asset", data)
            self.assertIn("level2", data)
            self.assertIn("valuation_fa", data)
            self.assertIn("technicals_saxo", data)
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

            # Check Saxo technicals
            self.assertIn("rsi_14", data["technicals_saxo"])
            self.assertIn("macd", data["technicals_saxo"])
            self.assertIn("sentiment", data["technicals_saxo"])
            self.assertIn("long_pct", data["technicals_saxo"]["sentiment"])

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
        """Verify the REST API accepts bond purchases and auction bids."""
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
        """Verify the standard /api/trade/execute/ endpoint seamlessly handles bond orders."""
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
        """Verify that invalid bond requests return HTTP 400 with an error description."""
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
