"""
Market Data Service for PesaMarkets
Provides comprehensive data for major US, Global, African (NSE), Crypto, and Commodity assets,
providing institutional market terminal features including real-time quotes, multi-timeframe charts,
key statistics, analyst ratings, news feeds, and market movers.
"""

# Official Vector SVG Brand Logos Mapping for Listed Companies & Assets
LOGO_MAP = {
    "SCOM": "/static/logos/scom.svg",
    "EQTY": "/static/logos/eqty.svg",
    "KCB": "/static/logos/kcb.svg",
    "EABL": "/static/logos/eabl.svg",
    "AAPL": "/static/logos/aapl.svg",
    "NVDA": "/static/logos/nvda.svg",
    "TSLA": "/static/logos/tsla.svg",
    "MSFT": "/static/logos/msft.svg",
    "BTC": "/static/logos/btc.svg",
    "BTC-USD": "/static/logos/btc.svg",
    "ETH": "/static/logos/eth.svg",
    "ETH-USD": "/static/logos/eth.svg",
    "SOL": "/static/logos/sol.svg",
    "SOL-USD": "/static/logos/sol.svg",
    "GOLD": "/static/logos/gold.svg",
    "GC=F": "/static/logos/gold.svg",
    "CL=F": "/static/logos/oil.svg",
    "CRUDE": "/static/logos/oil.svg",
    "OIL": "/static/logos/oil.svg",
    "^GSPC": "/static/logos/sp500.svg",
    "SP500": "/static/logos/sp500.svg",
    "^IXIC": "/static/logos/nasdaq.svg",
    "NASDAQ": "/static/logos/nasdaq.svg",
    "^DJI": "/static/logos/dow.svg",
    "DJI": "/static/logos/dow.svg",
    "^NSE20": "/static/logos/nse.svg",
    "NSE20": "/static/logos/nse.svg",
    "NSE": "/static/logos/nse.svg",
    "T91": "/static/logos/cbk.svg",
    "T182": "/static/logos/cbk.svg",
    "T364": "/static/logos/cbk.svg",
    "FXD2Y": "/static/logos/cbk.svg",
    "FXD5Y": "/static/logos/cbk.svg",
    "IFB10Y": "/static/logos/cbk.svg",
}

def get_asset_logo(symbol):
    clean = str(symbol).upper().strip()
    if clean in LOGO_MAP:
        return LOGO_MAP[clean]
    base = clean.split('-')[0].replace('^', '')
    if base in LOGO_MAP:
        return LOGO_MAP[base]
    if clean.startswith(('T9', 'T1', 'T3', 'FXD', 'IFB', 'BOND')):
        return "/static/logos/cbk.svg"
    return "/static/logos/nse.svg"

# Real Company Headquarters, Facilities, and Authentic Corporate Images
COMPANY_IMAGES = {
    "SCOM": "/static/companies/scom.jpg",
    "EQTY": "/static/companies/eqty.jpg",
    "KCB": "/static/companies/kcb.jpg",
    "EABL": "/static/companies/eabl.jpg",
    "AAPL": "/static/companies/aapl.jpg",
    "NVDA": "/static/companies/nvda.jpg",
    "TSLA": "/static/companies/tsla.jpg",
    "MSFT": "/static/companies/msft.jpg",
    "BTC": "/static/companies/btc.jpg",
    "BTC-USD": "/static/companies/btc.jpg",
    "ETH": "/static/companies/eth.jpg",
    "ETH-USD": "/static/companies/eth.jpg",
    "SOL": "/static/companies/sol.jpg",
    "SOL-USD": "/static/companies/sol.jpg",
    "GOLD": "/static/companies/gold.jpg",
    "GC=F": "/static/companies/gold.jpg",
    "CL=F": "/static/companies/oil.jpg",
    "CRUDE": "/static/companies/oil.jpg",
    "OIL": "/static/companies/oil.jpg",
    "^GSPC": "/static/companies/sp500.jpg",
    "SP500": "/static/companies/sp500.jpg",
    "^IXIC": "/static/companies/nasdaq.jpg",
    "NASDAQ": "/static/companies/nasdaq.jpg",
    "^DJI": "/static/companies/dow.jpg",
    "DJI": "/static/companies/dow.jpg",
    "^NSE20": "/static/companies/nse.jpg",
    "NSE20": "/static/companies/nse.jpg",
    "NSE": "/static/companies/nse.jpg",
    "T91": "/static/companies/cbk.jpg",
    "T182": "/static/companies/cbk.jpg",
    "T364": "/static/companies/cbk.jpg",
    "FXD2Y": "/static/companies/cbk.jpg",
    "FXD5Y": "/static/companies/cbk.jpg",
    "IFB10Y": "/static/companies/cbk.jpg",
}

def get_company_image(symbol):
    clean = str(symbol).upper().strip()
    if clean in COMPANY_IMAGES:
        return COMPANY_IMAGES[clean]
    base = clean.split('-')[0].replace('^', '')
    if base in COMPANY_IMAGES:
        return COMPANY_IMAGES[base]
    if clean.startswith(('T9', 'T1', 'T3', 'FXD', 'IFB', 'BOND')):
        return "/static/companies/cbk.jpg"
    return "/static/companies/scom.jpg"

# Major Market Indices for the Ticker Tape / Header Ribbon
MARKET_INDICES = [
    {
        "symbol": "^GSPC",
        "name": "S&P 500",
        "price": 5864.67,
        "change": 44.82,
        "change_percent": 0.77,
        "is_positive": True,
        "sparkline": [5820, 5828, 5840, 5835, 5852, 5860, 5864.67]
    },
    {
        "symbol": "^IXIC",
        "name": "Nasdaq",
        "price": 18518.61,
        "change": 115.80,
        "change_percent": 0.63,
        "is_positive": True,
        "sparkline": [18400, 18430, 18460, 18440, 18490, 18510, 18518.61]
    },
    {
        "symbol": "^DJI",
        "name": "Dow Jones",
        "price": 42863.86,
        "change": 409.74,
        "change_percent": 0.97,
        "is_positive": True,
        "sparkline": [42450, 42520, 42680, 42610, 42790, 42840, 42863.86]
    },
    {
        "symbol": "^NSE20",
        "name": "NSE 20 Share",
        "price": 1542.30,
        "change": 18.25,
        "change_percent": 1.20,
        "is_positive": True,
        "sparkline": [1524, 1528, 1535, 1532, 1538, 1540, 1542.30]
    },
    {
        "symbol": "BTC-USD",
        "name": "Bitcoin",
        "price": 64850.00,
        "change": 1820.00,
        "change_percent": 2.89,
        "is_positive": True,
        "sparkline": [63000, 63400, 64100, 63800, 64500, 64700, 64850]
    },
    {
        "symbol": "ETH-USD",
        "name": "Ethereum",
        "price": 3480.00,
        "change": 65.50,
        "change_percent": 1.92,
        "is_positive": True,
        "sparkline": [3410, 3425, 3450, 3435, 3465, 3470, 3480]
    },
    {
        "symbol": "CL=F",
        "name": "Crude Oil",
        "price": 75.56,
        "change": -0.29,
        "change_percent": -0.38,
        "is_positive": False,
        "sparkline": [76.2, 75.9, 76.1, 75.8, 75.6, 75.7, 75.56]
    },
    {
        "symbol": "GC=F",
        "name": "Gold",
        "price": 2657.40,
        "change": 29.30,
        "change_percent": 1.12,
        "is_positive": True,
        "sparkline": [2628, 2635, 2642, 2639, 2650, 2654, 2657.40]
    },
    {
        "symbol": "SCOM",
        "name": "Safaricom",
        "price": 14.85,
        "change": 0.35,
        "change_percent": 2.41,
        "is_positive": True,
        "sparkline": [14.4, 14.5, 14.65, 14.55, 14.75, 14.8, 14.85]
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA",
        "price": 138.25,
        "change": 5.80,
        "change_percent": 4.38,
        "is_positive": True,
        "sparkline": [132.5, 133.8, 135.2, 134.9, 137.0, 137.8, 138.25]
    },
    {
        "symbol": "AAPL",
        "name": "Apple",
        "price": 232.15,
        "change": 3.65,
        "change_percent": 1.60,
        "is_positive": True,
        "sparkline": [228.5, 229.4, 230.8, 230.1, 231.5, 232.0, 232.15]
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "price": 154.60,
        "change": 8.40,
        "change_percent": 5.75,
        "is_positive": True,
        "sparkline": [146.2, 148.0, 151.2, 149.8, 153.1, 154.0, 154.6]
    }
]

# Comprehensive Asset Catalog with market intelligence
ASSETS = {
    "SCOM": {
        "symbol": "SCOM",
        "name": "Safaricom PLC",
        "category": "equities",
        "market": "NSE",
        "currency": "KES",
        "price": 14.85,
        "change": 0.35,
        "change_percent": 2.41,
        "previous_close": 14.50,
        "open": 14.55,
        "day_low": 14.40,
        "day_high": 15.00,
        "year_low": 11.80,
        "year_high": 18.50,
        "volume": "14.2M",
        "avg_volume": "12.8M",
        "market_cap": "594.8B",
        "pe_ratio": 11.2,
        "eps": 1.33,
        "dividend_yield": "7.4%",
        "beta": 0.85,
        "target_est": 18.20,
        "sector": "Communication Services",
        "industry": "Telecom Services",
        "ceo": "Peter Ndegwa",
        "description": "Safaricom PLC is the leading telecommunications service provider in Kenya and operator of M-PESA, the world's most successful mobile money platform with over 32 million active users.",
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.6,
            "buy": 78,
            "hold": 18,
            "sell": 4
        },
        "sparkline": [14.4, 14.5, 14.65, 14.55, 14.75, 14.8, 14.85],
        "history": {
            "1D": [14.50, 14.55, 14.60, 14.50, 14.70, 14.80, 14.85],
            "1W": [14.20, 14.30, 14.45, 14.40, 14.60, 14.75, 14.85],
            "1M": [13.80, 13.95, 14.10, 14.35, 14.50, 14.65, 14.85],
            "1Y": [12.00, 12.80, 13.50, 14.10, 13.80, 14.30, 14.85],
            "ALL": [9.50, 11.20, 13.00, 15.50, 13.80, 14.20, 14.85]
        }
    },
    "EQTY": {
        "symbol": "EQTY",
        "name": "Equity Group Holdings",
        "category": "equities",
        "market": "NSE",
        "currency": "KES",
        "price": 38.80,
        "change": 0.55,
        "change_percent": 1.44,
        "previous_close": 38.25,
        "open": 38.30,
        "day_low": 38.10,
        "day_high": 39.00,
        "year_low": 33.50,
        "year_high": 46.00,
        "volume": "4.8M",
        "avg_volume": "4.1M",
        "market_cap": "146.4B",
        "pe_ratio": 4.8,
        "eps": 8.08,
        "dividend_yield": "10.3%",
        "beta": 1.12,
        "target_est": 48.00,
        "sector": "Financial Services",
        "industry": "Banks - Regional",
        "ceo": "James Mwangi",
        "description": "Equity Group Holdings is a top-tier financial services conglomerate across East and Central Africa, providing commercial banking, digital payments, and investment services to over 18 million customers.",
        "rating": {
            "consensus": "Buy",
            "score": 4.3,
            "buy": 65,
            "hold": 28,
            "sell": 7
        },
        "sparkline": [38.2, 38.3, 38.5, 38.4, 38.65, 38.75, 38.8],
        "history": {
            "1D": [38.25, 38.30, 38.45, 38.40, 38.60, 38.75, 38.80],
            "1W": [37.80, 37.90, 38.10, 38.25, 38.50, 38.70, 38.80],
            "1M": [36.50, 36.80, 37.20, 37.90, 38.10, 38.40, 38.80],
            "1Y": [34.00, 35.50, 37.00, 38.20, 36.80, 38.00, 38.80],
            "ALL": [28.00, 32.50, 36.00, 42.00, 37.50, 38.20, 38.80]
        }
    },
    "KCB": {
        "symbol": "KCB",
        "name": "KCB Group PLC",
        "category": "equities",
        "market": "NSE",
        "currency": "KES",
        "price": 22.80,
        "change": 0.70,
        "change_percent": 3.17,
        "previous_close": 22.10,
        "open": 22.20,
        "day_low": 22.00,
        "day_high": 23.00,
        "year_low": 17.50,
        "year_high": 32.00,
        "volume": "3.5M",
        "avg_volume": "2.9M",
        "market_cap": "73.3B",
        "pe_ratio": 3.6,
        "eps": 6.33,
        "dividend_yield": "8.8%",
        "beta": 1.25,
        "target_est": 29.50,
        "sector": "Financial Services",
        "industry": "Banks - Regional",
        "ceo": "Paul Russo",
        "description": "KCB Group is one of East Africa's oldest and largest commercial banking networks, operating in Kenya, Tanzania, South Sudan, Rwanda, Uganda, and the DRC.",
        "rating": {
            "consensus": "Buy",
            "score": 4.1,
            "buy": 60,
            "hold": 32,
            "sell": 8
        },
        "sparkline": [22.1, 22.25, 22.4, 22.3, 22.6, 22.7, 22.8],
        "history": {
            "1D": [22.10, 22.25, 22.40, 22.35, 22.55, 22.70, 22.80],
            "1W": [21.50, 21.80, 22.00, 22.10, 22.40, 22.65, 22.80],
            "1M": [20.00, 20.60, 21.20, 21.80, 22.10, 22.50, 22.80],
            "1Y": [18.20, 19.50, 20.80, 21.50, 20.20, 22.10, 22.80],
            "ALL": [16.00, 21.00, 25.00, 30.00, 22.00, 22.40, 22.80]
        }
    },
    "EABL": {
        "symbol": "EABL",
        "name": "East African Breweries",
        "category": "equities",
        "market": "NSE",
        "currency": "KES",
        "price": 142.50,
        "change": -1.25,
        "change_percent": -0.87,
        "previous_close": 143.75,
        "open": 144.00,
        "day_low": 141.50,
        "day_high": 144.50,
        "year_low": 125.00,
        "year_high": 170.00,
        "volume": "420K",
        "avg_volume": "510K",
        "market_cap": "112.7B",
        "pe_ratio": 12.8,
        "eps": 11.13,
        "dividend_yield": "5.6%",
        "beta": 0.72,
        "target_est": 165.00,
        "sector": "Consumer Defensive",
        "industry": "Beverages - Brewers",
        "ceo": "Jane Karuku",
        "description": "East African Breweries Limited (EABL) is a leading branded alcohol beverage company and subsidiary of Diageo, with operations in Kenya, Uganda, and Tanzania.",
        "rating": {
            "consensus": "Hold",
            "score": 3.7,
            "buy": 45,
            "hold": 45,
            "sell": 10
        },
        "sparkline": [144.0, 143.8, 143.2, 143.5, 142.8, 142.6, 142.5],
        "history": {
            "1D": [143.75, 144.00, 143.50, 143.20, 142.90, 142.60, 142.50],
            "1W": [145.00, 144.50, 144.00, 143.75, 143.00, 142.80, 142.50],
            "1M": [140.00, 141.50, 143.00, 145.00, 144.00, 143.50, 142.50],
            "1Y": [130.00, 138.00, 148.00, 155.00, 146.00, 144.00, 142.50],
            "ALL": [120.00, 135.00, 150.00, 165.00, 145.00, 143.00, 142.50]
        }
    },
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "category": "equities",
        "market": "NASDAQ",
        "currency": "USD",
        "price": 232.15,
        "change": 3.65,
        "change_percent": 1.60,
        "previous_close": 228.50,
        "open": 229.10,
        "day_low": 228.40,
        "day_high": 233.00,
        "year_low": 164.08,
        "year_high": 237.23,
        "volume": "48.5M",
        "avg_volume": "54.2M",
        "market_cap": "3.54T",
        "pe_ratio": 34.6,
        "eps": 6.70,
        "dividend_yield": "0.43%",
        "beta": 1.08,
        "target_est": 250.00,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "ceo": "Tim Cook",
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories, and sells a variety of related services including Apple Intelligence, iCloud, and Apple Pay.",
        "rating": {
            "consensus": "Moderate Buy",
            "score": 4.4,
            "buy": 72,
            "hold": 24,
            "sell": 4
        },
        "sparkline": [228.5, 229.4, 230.8, 230.1, 231.5, 232.0, 232.15],
        "history": {
            "1D": [228.50, 229.20, 230.50, 230.10, 231.40, 231.90, 232.15],
            "1W": [224.00, 226.50, 227.00, 228.50, 230.00, 231.50, 232.15],
            "1M": [215.00, 218.00, 222.00, 225.50, 228.00, 230.50, 232.15],
            "1Y": [170.00, 182.00, 195.00, 210.00, 220.00, 228.00, 232.15],
            "ALL": [130.00, 150.00, 175.00, 195.00, 215.00, 225.00, 232.15]
        }
    },
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "category": "equities",
        "market": "NASDAQ",
        "currency": "USD",
        "price": 138.25,
        "change": 5.80,
        "change_percent": 4.38,
        "previous_close": 132.45,
        "open": 133.50,
        "day_low": 133.10,
        "day_high": 139.10,
        "year_low": 39.23,
        "year_high": 140.76,
        "volume": "62.4M",
        "avg_volume": "58.1M",
        "market_cap": "3.39T",
        "pe_ratio": 58.2,
        "eps": 2.38,
        "dividend_yield": "0.03%",
        "beta": 1.68,
        "target_est": 155.00,
        "sector": "Technology",
        "industry": "Semiconductors",
        "ceo": "Jensen Huang",
        "description": "NVIDIA Corporation pioneer of GPU computing, dominating AI chip architectures including Blackwell and Hopper GPUs powering artificial intelligence enterprise data centers worldwide.",
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.8,
            "buy": 89,
            "hold": 9,
            "sell": 2
        },
        "sparkline": [132.5, 133.8, 135.2, 134.9, 137.0, 137.8, 138.25],
        "history": {
            "1D": [132.45, 133.50, 135.10, 134.80, 136.90, 137.60, 138.25],
            "1W": [128.00, 130.50, 132.00, 133.50, 135.00, 137.00, 138.25],
            "1M": [115.00, 120.00, 126.00, 130.00, 133.00, 136.00, 138.25],
            "1Y": [45.00, 60.00, 85.00, 110.00, 125.00, 132.00, 138.25],
            "ALL": [20.00, 35.00, 55.00, 80.00, 110.00, 128.00, 138.25]
        }
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla, Inc.",
        "category": "equities",
        "market": "NASDAQ",
        "currency": "USD",
        "price": 242.80,
        "change": 14.20,
        "change_percent": 6.21,
        "previous_close": 228.60,
        "open": 230.50,
        "day_low": 229.80,
        "day_high": 244.50,
        "year_low": 138.80,
        "year_high": 271.00,
        "volume": "85.2M",
        "avg_volume": "74.8M",
        "market_cap": "775.1B",
        "pe_ratio": 62.4,
        "eps": 3.89,
        "dividend_yield": "N/A",
        "beta": 2.45,
        "target_est": 265.00,
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "ceo": "Elon Musk",
        "description": "Tesla, Inc. designs, develops, manufactures, sells, and leases fully electric vehicles, energy generation and storage systems, and autonomous robotaxi technologies.",
        "rating": {
            "consensus": "Hold",
            "score": 3.6,
            "buy": 42,
            "hold": 40,
            "sell": 18
        },
        "sparkline": [228.6, 231.0, 235.4, 234.2, 239.5, 241.8, 242.8],
        "history": {
            "1D": [228.60, 231.00, 235.20, 234.00, 239.20, 241.50, 242.80],
            "1W": [218.00, 222.00, 225.00, 228.60, 234.00, 239.00, 242.80],
            "1M": [205.00, 210.00, 218.00, 225.00, 230.00, 238.00, 242.80],
            "1Y": [195.00, 175.00, 160.00, 190.00, 220.00, 232.00, 242.80],
            "ALL": [120.00, 160.00, 210.00, 250.00, 210.00, 230.00, 242.80]
        }
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "category": "equities",
        "market": "NASDAQ",
        "currency": "USD",
        "price": 421.50,
        "change": 4.10,
        "change_percent": 0.98,
        "previous_close": 417.40,
        "open": 418.00,
        "day_low": 417.20,
        "day_high": 423.00,
        "year_low": 326.93,
        "year_high": 468.35,
        "volume": "21.5M",
        "avg_volume": "23.8M",
        "market_cap": "3.13T",
        "pe_ratio": 35.8,
        "eps": 11.77,
        "dividend_yield": "0.79%",
        "beta": 0.91,
        "target_est": 490.00,
        "sector": "Technology",
        "industry": "Software - Infrastructure",
        "ceo": "Satya Nadella",
        "description": "Microsoft develops and supports software, services, devices and cloud solutions, including Azure, Windows, Microsoft 365, Copilot AI, and LinkedIn.",
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.7,
            "buy": 86,
            "hold": 12,
            "sell": 2
        },
        "sparkline": [417.4, 418.5, 419.8, 419.2, 420.5, 421.2, 421.5],
        "history": {
            "1D": [417.40, 418.20, 419.60, 419.10, 420.70, 421.10, 421.50],
            "1W": [412.00, 414.50, 416.00, 417.40, 419.00, 420.50, 421.50],
            "1M": [405.00, 408.00, 412.00, 416.00, 418.00, 420.00, 421.50],
            "1Y": [340.00, 365.00, 395.00, 420.00, 435.00, 425.00, 421.50],
            "ALL": [280.00, 310.00, 350.00, 390.00, 410.00, 418.00, 421.50]
        }
    },
    "BTC": {
        "symbol": "BTC",
        "name": "Bitcoin (BTC-USD)",
        "category": "crypto",
        "market": "CRYPTO",
        "currency": "USD",
        "price": 64850.00,
        "change": 1820.00,
        "change_percent": 2.89,
        "previous_close": 63030.00,
        "open": 63100.00,
        "day_low": 62900.00,
        "day_high": 65150.00,
        "year_low": 26800.00,
        "year_high": 73750.00,
        "volume": "32.4B",
        "avg_volume": "28.9B",
        "market_cap": "1.28T",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "N/A",
        "beta": 2.10,
        "target_est": 85000.00,
        "sector": "Digital Assets",
        "industry": "Cryptocurrency",
        "ceo": "Satoshi Nakamoto",
        "description": "Bitcoin is a decentralized digital cryptocurrency pioneered in 2009. It utilizes proof-of-work blockchain consensus with a hard cap limit of 21 million coins.",
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.7,
            "buy": 82,
            "hold": 14,
            "sell": 4
        },
        "sparkline": [63030, 63400, 64100, 63800, 64500, 64700, 64850],
        "history": {
            "1D": [63030, 63400, 64100, 63800, 64500, 64700, 64850],
            "1W": [61200, 61900, 62500, 63100, 63900, 64400, 64850],
            "1M": [57500, 59200, 61000, 62800, 63500, 64200, 64850],
            "1Y": [28000, 36000, 44000, 62000, 68000, 63000, 64850],
            "ALL": [19000, 28000, 42000, 60000, 65000, 62000, 64850]
        }
    },
    "ETH": {
        "symbol": "ETH",
        "name": "Ethereum (ETH-USD)",
        "category": "crypto",
        "market": "CRYPTO",
        "currency": "USD",
        "price": 3480.00,
        "change": 65.50,
        "change_percent": 1.92,
        "previous_close": 3414.50,
        "open": 3420.00,
        "day_low": 3400.00,
        "day_high": 3510.00,
        "year_low": 1520.00,
        "year_high": 4090.00,
        "volume": "18.1B",
        "avg_volume": "16.4B",
        "market_cap": "418.5B",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "3.2% (Staking)",
        "beta": 2.35,
        "target_est": 4500.00,
        "sector": "Digital Assets",
        "industry": "Smart Contracts Layer 1",
        "ceo": "Vitalik Buterin",
        "description": "Ethereum is an open-source decentralized computing platform with smart contract functionality, powering decentralized finance (DeFi), NFTs, and global Web3 protocols.",
        "rating": {
            "consensus": "Buy",
            "score": 4.4,
            "buy": 74,
            "hold": 20,
            "sell": 6
        },
        "sparkline": [3414, 3430, 3455, 3440, 3465, 3475, 3480],
        "history": {
            "1D": [3414, 3430, 3455, 3440, 3465, 3475, 3480],
            "1W": [3280, 3320, 3360, 3410, 3440, 3465, 3480],
            "1M": [3100, 3180, 3260, 3350, 3410, 3450, 3480],
            "1Y": [1600, 1950, 2400, 3300, 3700, 3400, 3480],
            "ALL": [1200, 1650, 2200, 3100, 3500, 3350, 3480]
        }
    },
    "SOL": {
        "symbol": "SOL",
        "name": "Solana (SOL-USD)",
        "category": "crypto",
        "market": "CRYPTO",
        "currency": "USD",
        "price": 154.60,
        "change": 8.40,
        "change_percent": 5.75,
        "previous_close": 146.20,
        "open": 147.00,
        "day_low": 145.80,
        "day_high": 156.20,
        "year_low": 21.10,
        "year_high": 209.90,
        "volume": "4.8B",
        "avg_volume": "3.9B",
        "market_cap": "72.4B",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "6.8% (Staking)",
        "beta": 2.75,
        "target_est": 220.00,
        "sector": "Digital Assets",
        "industry": "High-Throughput Layer 1",
        "ceo": "Anatoly Yakovenko",
        "description": "Solana is an ultra-fast proof-of-stake blockchain designed for high transaction throughput and minimal sub-cent gas fees, widely adopted for decentralized trading and consumer applications.",
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.6,
            "buy": 80,
            "hold": 15,
            "sell": 5
        },
        "sparkline": [146.2, 148.0, 151.2, 149.8, 153.1, 154.0, 154.6],
        "history": {
            "1D": [146.2, 148.0, 151.2, 149.8, 153.1, 154.0, 154.6],
            "1W": [136.0, 140.0, 143.5, 146.2, 149.0, 152.0, 154.6],
            "1M": [124.0, 129.0, 135.0, 142.0, 148.0, 151.0, 154.6],
            "1Y": [24.0, 45.0, 95.0, 145.0, 175.0, 148.0, 154.6],
            "ALL": [18.0, 32.0, 75.0, 120.0, 160.0, 140.0, 154.6]
        }
    },
    "GOLD": {
        "symbol": "GOLD",
        "name": "Gold Spot / Comex (GC=F)",
        "category": "commodities",
        "market": "COMMODITIES",
        "currency": "USD",
        "price": 2657.40,
        "change": 29.30,
        "change_percent": 1.12,
        "previous_close": 2628.10,
        "open": 2630.00,
        "day_low": 2625.00,
        "day_high": 2662.00,
        "year_low": 1810.00,
        "year_high": 2685.00,
        "volume": "185K contracts",
        "avg_volume": "160K contracts",
        "market_cap": "17.2T (Physical)",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "N/A",
        "beta": 0.15,
        "target_est": 2800.00,
        "sector": "Commodities",
        "industry": "Precious Metals",
        "ceo": "Market Asset",
        "description": "Gold is the world's premier monetary reserve and safe-haven store of value asset, traded actively on the New York Mercantile Exchange (COMEX) and global bullion hubs.",
        "rating": {
            "consensus": "Buy",
            "score": 4.5,
            "buy": 75,
            "hold": 22,
            "sell": 3
        },
        "sparkline": [2628, 2635, 2642, 2639, 2650, 2654, 2657.4],
        "history": {
            "1D": [2628, 2635, 2642, 2639, 2650, 2654, 2657.4],
            "1W": [2610, 2618, 2625, 2628, 2640, 2651, 2657.4],
            "1M": [2540, 2565, 2590, 2615, 2630, 2645, 2657.4],
            "1Y": [1980, 2050, 2180, 2350, 2480, 2580, 2657.4],
            "ALL": [1820, 1920, 2080, 2240, 2450, 2580, 2657.4]
        }
    },
    # ===================================================================
    # KENYA GOVERNMENT TREASURY BILLS (CBK Primary Auction Market)
    # ===================================================================
    "T91": {
        "symbol": "T91",
        "name": "91-Day Treasury Bill",
        "category": "bonds",
        "subcategory": "tbill",
        "market": "CBK",
        "currency": "KES",
        "price": 96.18,
        "change": 0.03,
        "change_percent": 0.03,
        "previous_close": 96.15,
        "open": 96.15,
        "day_low": 96.10,
        "day_high": 96.22,
        "year_low": 95.20,
        "year_high": 97.10,
        "volume": "12.8B",
        "avg_volume": "11.4B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "15.72%",
        "beta": 0.02,
        "target_est": 96.50,
        "sector": "Government Securities",
        "industry": "Treasury Bills",
        "ceo": "Central Bank of Kenya",
        "description": "91-Day Kenya Government Treasury Bill issued by the Central Bank of Kenya (CBK). Auctioned weekly on Wednesdays, these are zero-coupon discount instruments with a face value of KES 100,000 minimum. Currently yielding 15.72% annualized.",
        "face_value": 100000,
        "coupon_rate": 0.0,
        "yield_to_maturity": 15.72,
        "maturity_days": 91,
        "maturity_date": "2027-01-18",
        "issue_date": "2026-10-19",
        "issue_number": "T91/2435",
        "auction_date": "2026-10-16",
        "amount_offered": "24.0B",
        "amount_received": "38.6B",
        "amount_accepted": "24.0B",
        "weighted_avg_yield": 15.72,
        "subscription_rate": 160.8,
        "rating": {
            "consensus": "Safe Haven",
            "score": 4.9,
            "buy": 92,
            "hold": 7,
            "sell": 1
        },
        "sparkline": [96.08, 96.10, 96.12, 96.14, 96.16, 96.17, 96.18],
        "history": {
            "1D": [96.15, 96.14, 96.16, 96.15, 96.17, 96.18, 96.18],
            "1W": [96.05, 96.08, 96.10, 96.12, 96.15, 96.17, 96.18],
            "1M": [95.80, 95.88, 95.95, 96.02, 96.08, 96.14, 96.18],
            "1Y": [95.20, 95.45, 95.65, 95.90, 96.00, 96.10, 96.18],
            "ALL": [94.80, 95.10, 95.50, 95.80, 96.00, 96.12, 96.18]
        }
    },
    "T182": {
        "symbol": "T182",
        "name": "182-Day Treasury Bill",
        "category": "bonds",
        "subcategory": "tbill",
        "market": "CBK",
        "currency": "KES",
        "price": 92.45,
        "change": 0.05,
        "change_percent": 0.05,
        "previous_close": 92.40,
        "open": 92.40,
        "day_low": 92.38,
        "day_high": 92.50,
        "year_low": 91.20,
        "year_high": 93.50,
        "volume": "8.4B",
        "avg_volume": "7.2B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "16.18%",
        "beta": 0.03,
        "target_est": 92.80,
        "sector": "Government Securities",
        "industry": "Treasury Bills",
        "ceo": "Central Bank of Kenya",
        "description": "182-Day Kenya Government Treasury Bill. Semi-annual zero-coupon instrument auctioned fortnightly by CBK. Face value KES 100,000 minimum. Currently yielding 16.18% annualized.",
        "face_value": 100000,
        "coupon_rate": 0.0,
        "yield_to_maturity": 16.18,
        "maturity_days": 182,
        "maturity_date": "2027-04-19",
        "issue_date": "2026-10-19",
        "issue_number": "T182/1218",
        "auction_date": "2026-10-16",
        "amount_offered": "10.0B",
        "amount_received": "14.2B",
        "amount_accepted": "10.0B",
        "weighted_avg_yield": 16.18,
        "subscription_rate": 142.0,
        "rating": {
            "consensus": "Safe Haven",
            "score": 4.8,
            "buy": 88,
            "hold": 10,
            "sell": 2
        },
        "sparkline": [92.30, 92.33, 92.36, 92.38, 92.41, 92.43, 92.45],
        "history": {
            "1D": [92.40, 92.38, 92.41, 92.40, 92.43, 92.44, 92.45],
            "1W": [92.20, 92.25, 92.30, 92.35, 92.38, 92.42, 92.45],
            "1M": [91.80, 91.95, 92.05, 92.15, 92.28, 92.38, 92.45],
            "1Y": [91.20, 91.50, 91.80, 92.00, 92.15, 92.30, 92.45],
            "ALL": [90.50, 91.00, 91.40, 91.80, 92.10, 92.30, 92.45]
        }
    },
    "T364": {
        "symbol": "T364",
        "name": "364-Day Treasury Bill",
        "category": "bonds",
        "subcategory": "tbill",
        "market": "CBK",
        "currency": "KES",
        "price": 86.15,
        "change": 0.08,
        "change_percent": 0.09,
        "previous_close": 86.07,
        "open": 86.07,
        "day_low": 86.02,
        "day_high": 86.20,
        "year_low": 84.80,
        "year_high": 87.50,
        "volume": "6.2B",
        "avg_volume": "5.5B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "16.45%",
        "beta": 0.04,
        "target_est": 86.50,
        "sector": "Government Securities",
        "industry": "Treasury Bills",
        "ceo": "Central Bank of Kenya",
        "description": "364-Day Kenya Government Treasury Bill. Annual zero-coupon discount instrument auctioned fortnightly by CBK. Face value KES 100,000 minimum. Currently yielding 16.45% annualized.",
        "face_value": 100000,
        "coupon_rate": 0.0,
        "yield_to_maturity": 16.45,
        "maturity_days": 364,
        "maturity_date": "2027-10-18",
        "issue_date": "2026-10-19",
        "issue_number": "T364/608",
        "auction_date": "2026-10-16",
        "amount_offered": "10.0B",
        "amount_received": "15.8B",
        "amount_accepted": "10.0B",
        "weighted_avg_yield": 16.45,
        "subscription_rate": 158.0,
        "rating": {
            "consensus": "Safe Haven",
            "score": 4.7,
            "buy": 85,
            "hold": 12,
            "sell": 3
        },
        "sparkline": [85.95, 85.98, 86.02, 86.05, 86.08, 86.12, 86.15],
        "history": {
            "1D": [86.07, 86.05, 86.08, 86.06, 86.10, 86.13, 86.15],
            "1W": [85.85, 85.90, 85.95, 86.00, 86.05, 86.10, 86.15],
            "1M": [85.40, 85.55, 85.70, 85.85, 85.95, 86.08, 86.15],
            "1Y": [84.80, 85.10, 85.40, 85.70, 85.90, 86.05, 86.15],
            "ALL": [84.00, 84.50, 85.00, 85.40, 85.80, 86.00, 86.15]
        }
    },
    # ===================================================================
    # KENYA GOVERNMENT BONDS (CBK Fixed Coupon & Infrastructure Bonds)
    # ===================================================================
    "FXD2Y": {
        "symbol": "FXD2Y",
        "name": "2-Year Fixed Coupon Bond",
        "category": "bonds",
        "subcategory": "bond",
        "market": "CBK",
        "currency": "KES",
        "price": 98.45,
        "change": -0.12,
        "change_percent": -0.12,
        "previous_close": 98.57,
        "open": 98.55,
        "day_low": 98.35,
        "day_high": 98.60,
        "year_low": 96.50,
        "year_high": 100.20,
        "volume": "4.8B",
        "avg_volume": "4.1B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "16.85%",
        "beta": 0.05,
        "target_est": 99.00,
        "sector": "Government Securities",
        "industry": "Treasury Bonds",
        "ceo": "Central Bank of Kenya",
        "description": "2-Year Kenya Government Fixed Coupon Treasury Bond (FXD1/2026/002). Pays semi-annual coupons at 16.50% per annum. Face value KES 50,000 minimum. Current yield to maturity: 16.85%.",
        "face_value": 50000,
        "coupon_rate": 16.50,
        "yield_to_maturity": 16.85,
        "maturity_days": 730,
        "maturity_date": "2028-10-18",
        "issue_date": "2026-10-19",
        "issue_number": "FXD1/2026/002",
        "auction_date": "2026-10-14",
        "amount_offered": "30.0B",
        "amount_received": "52.4B",
        "amount_accepted": "30.0B",
        "coupon_frequency": "Semi-Annual",
        "next_coupon_date": "2027-04-19",
        "weighted_avg_yield": 16.85,
        "subscription_rate": 174.7,
        "rating": {
            "consensus": "Buy",
            "score": 4.5,
            "buy": 80,
            "hold": 16,
            "sell": 4
        },
        "sparkline": [98.50, 98.52, 98.55, 98.48, 98.50, 98.47, 98.45],
        "history": {
            "1D": [98.57, 98.55, 98.50, 98.48, 98.46, 98.44, 98.45],
            "1W": [98.70, 98.65, 98.60, 98.55, 98.50, 98.48, 98.45],
            "1M": [99.20, 99.00, 98.85, 98.70, 98.60, 98.50, 98.45],
            "1Y": [96.50, 97.00, 97.50, 98.00, 98.30, 98.40, 98.45],
            "ALL": [95.00, 96.00, 97.00, 98.00, 98.50, 98.50, 98.45]
        }
    },
    "FXD5Y": {
        "symbol": "FXD5Y",
        "name": "5-Year Fixed Coupon Bond",
        "category": "bonds",
        "subcategory": "bond",
        "market": "CBK",
        "currency": "KES",
        "price": 97.20,
        "change": -0.18,
        "change_percent": -0.18,
        "previous_close": 97.38,
        "open": 97.35,
        "day_low": 97.10,
        "day_high": 97.45,
        "year_low": 94.80,
        "year_high": 99.50,
        "volume": "3.5B",
        "avg_volume": "3.0B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "17.10%",
        "beta": 0.08,
        "target_est": 97.80,
        "sector": "Government Securities",
        "industry": "Treasury Bonds",
        "ceo": "Central Bank of Kenya",
        "description": "5-Year Kenya Government Fixed Coupon Treasury Bond (FXD1/2026/005). Pays semi-annual coupons at 16.80% per annum. Face value KES 50,000 minimum. Current yield to maturity: 17.10%.",
        "face_value": 50000,
        "coupon_rate": 16.80,
        "yield_to_maturity": 17.10,
        "maturity_days": 1825,
        "maturity_date": "2031-10-18",
        "issue_date": "2026-10-19",
        "issue_number": "FXD1/2026/005",
        "auction_date": "2026-10-14",
        "amount_offered": "25.0B",
        "amount_received": "41.2B",
        "amount_accepted": "25.0B",
        "coupon_frequency": "Semi-Annual",
        "next_coupon_date": "2027-04-19",
        "weighted_avg_yield": 17.10,
        "subscription_rate": 164.8,
        "rating": {
            "consensus": "Buy",
            "score": 4.3,
            "buy": 74,
            "hold": 20,
            "sell": 6
        },
        "sparkline": [97.30, 97.32, 97.35, 97.28, 97.25, 97.22, 97.20],
        "history": {
            "1D": [97.38, 97.35, 97.30, 97.25, 97.22, 97.21, 97.20],
            "1W": [97.60, 97.55, 97.48, 97.40, 97.35, 97.28, 97.20],
            "1M": [98.20, 98.00, 97.80, 97.60, 97.45, 97.30, 97.20],
            "1Y": [94.80, 95.50, 96.20, 96.80, 97.10, 97.25, 97.20],
            "ALL": [93.50, 94.50, 95.50, 96.50, 97.00, 97.20, 97.20]
        }
    },
    "IFB10Y": {
        "symbol": "IFB10Y",
        "name": "10-Year Infrastructure Bond",
        "category": "bonds",
        "subcategory": "bond",
        "market": "CBK",
        "currency": "KES",
        "price": 95.80,
        "change": -0.25,
        "change_percent": -0.26,
        "previous_close": 96.05,
        "open": 96.00,
        "day_low": 95.65,
        "day_high": 96.10,
        "year_low": 92.40,
        "year_high": 98.00,
        "volume": "5.2B",
        "avg_volume": "4.6B",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "17.85%",
        "beta": 0.12,
        "target_est": 96.50,
        "sector": "Government Securities",
        "industry": "Infrastructure Bonds",
        "ceo": "Central Bank of Kenya",
        "description": "10-Year Kenya Government Infrastructure Bond (IFB1/2026/010). Tax-exempt coupon payments at 17.50% per annum make IFBs the most attractive fixed-income instrument for retail and institutional investors. Proceeds fund national infrastructure: roads, energy, and water projects.",
        "face_value": 50000,
        "coupon_rate": 17.50,
        "yield_to_maturity": 17.85,
        "maturity_days": 3650,
        "maturity_date": "2036-10-18",
        "issue_date": "2026-10-19",
        "issue_number": "IFB1/2026/010",
        "auction_date": "2026-10-14",
        "amount_offered": "50.0B",
        "amount_received": "98.5B",
        "amount_accepted": "50.0B",
        "coupon_frequency": "Semi-Annual",
        "next_coupon_date": "2027-04-19",
        "tax_exempt": True,
        "weighted_avg_yield": 17.85,
        "subscription_rate": 197.0,
        "rating": {
            "consensus": "Strong Buy",
            "score": 4.7,
            "buy": 88,
            "hold": 10,
            "sell": 2
        },
        "sparkline": [95.90, 95.92, 95.95, 95.88, 95.85, 95.82, 95.80],
        "history": {
            "1D": [96.05, 96.00, 95.95, 95.90, 95.85, 95.82, 95.80],
            "1W": [96.30, 96.25, 96.15, 96.05, 95.95, 95.88, 95.80],
            "1M": [97.00, 96.75, 96.50, 96.25, 96.05, 95.90, 95.80],
            "1Y": [92.40, 93.50, 94.50, 95.20, 95.60, 95.75, 95.80],
            "ALL": [90.00, 91.50, 93.00, 94.50, 95.50, 95.70, 95.80]
        }
    }
}

# Comprehensive Bonds & Treasury Bills Catalog for the Fixed Income Desk
BONDS_CATALOG = {sym: data for sym, data in ASSETS.items() if data.get("category") == "bonds"}

# Upcoming CBK Auction Calendar
CBK_AUCTION_CALENDAR = [
    {"date": "2026-10-23", "day": "Wednesday", "instrument": "91-Day T-Bill", "symbol": "T91", "amount": "KES 24.0B", "status": "Upcoming"},
    {"date": "2026-10-23", "day": "Wednesday", "instrument": "182-Day T-Bill", "symbol": "T182", "amount": "KES 10.0B", "status": "Upcoming"},
    {"date": "2026-10-23", "day": "Wednesday", "instrument": "364-Day T-Bill", "symbol": "T364", "amount": "KES 10.0B", "status": "Upcoming"},
    {"date": "2026-10-28", "day": "Monday", "instrument": "2-Year FXD Bond", "symbol": "FXD2Y", "amount": "KES 30.0B", "status": "Upcoming"},
    {"date": "2026-11-04", "day": "Monday", "instrument": "10-Year IFB Bond", "symbol": "IFB10Y", "amount": "KES 50.0B", "status": "Upcoming"},
    {"date": "2026-11-11", "day": "Monday", "instrument": "5-Year FXD Bond", "symbol": "FXD5Y", "amount": "KES 25.0B", "status": "Upcoming"},
]

# Historical CBK Auction Results
CBK_RECENT_AUCTIONS = [
    {"date": "2026-10-16", "instrument": "91-Day T-Bill", "symbol": "T91", "offered": "24.0B", "received": "38.6B", "accepted": "24.0B", "wav_yield": 15.72, "subscription": 160.8, "cut_off": 15.85},
    {"date": "2026-10-16", "instrument": "182-Day T-Bill", "symbol": "T182", "offered": "10.0B", "received": "14.2B", "accepted": "10.0B", "wav_yield": 16.18, "subscription": 142.0, "cut_off": 16.30},
    {"date": "2026-10-16", "instrument": "364-Day T-Bill", "symbol": "T364", "offered": "10.0B", "received": "15.8B", "accepted": "10.0B", "wav_yield": 16.45, "subscription": 158.0, "cut_off": 16.60},
    {"date": "2026-10-14", "instrument": "2-Year FXD Bond", "symbol": "FXD2Y", "offered": "30.0B", "received": "52.4B", "accepted": "30.0B", "wav_yield": 16.85, "subscription": 174.7, "cut_off": 17.00},
    {"date": "2026-10-14", "instrument": "10-Year IFB", "symbol": "IFB10Y", "offered": "50.0B", "received": "98.5B", "accepted": "50.0B", "wav_yield": 17.85, "subscription": 197.0, "cut_off": 18.00},
    {"date": "2026-10-07", "instrument": "5-Year FXD Bond", "symbol": "FXD5Y", "offered": "25.0B", "received": "41.2B", "accepted": "25.0B", "wav_yield": 17.10, "subscription": 164.8, "cut_off": 17.25},
]


# Simulated Fixed Income & Government Securities Portfolio State
BOND_PORTFOLIO = {
    "total_invested": 2362650.00,
    "total_face_value": 2500000.00,
    "unrealized_pnl": 42500.00,
    "avg_yield": 16.72,
    "next_coupon_payment": "KES 218,750",
    "next_coupon_date": "2027-04-19",
    "holdings": [
        {
            "symbol": "T91",
            "name": "91-Day Treasury Bill",
            "face_value": 500000.00,
            "units": 5,
            "cost": 480900.00,
            "current_value": 480900.00,
            "yield": 15.72,
            "coupon": 0.0,
            "maturity": "2027-01-18",
            "tax_exempt": False,
            "category": "tbill"
        },
        {
            "symbol": "T364",
            "name": "364-Day Treasury Bill",
            "face_value": 500000.00,
            "units": 5,
            "cost": 430750.00,
            "current_value": 430750.00,
            "yield": 16.45,
            "coupon": 0.0,
            "maturity": "2027-10-18",
            "tax_exempt": False,
            "category": "tbill"
        },
        {
            "symbol": "IFB10Y",
            "name": "10-Year Infrastructure Bond",
            "face_value": 1000000.00,
            "units": 20,
            "cost": 958000.00,
            "current_value": 958000.00,
            "yield": 17.85,
            "coupon": 17.50,
            "maturity": "2036-10-18",
            "tax_exempt": True,
            "category": "bond"
        },
        {
            "symbol": "FXD2Y",
            "name": "2-Year Fixed Coupon Bond",
            "face_value": 500000.00,
            "units": 10,
            "cost": 492250.00,
            "current_value": 492250.00,
            "yield": 16.85,
            "coupon": 16.50,
            "maturity": "2028-10-18",
            "tax_exempt": False,
            "category": "bond"
        }
    ]
}


def execute_bond_purchase(symbol, face_value=None, units=None, order_type="AUCTION_NON_COMPETITIVE", bid_yield=None, channel="CBK_DHOWCSD"):
    """
    Executes a simulated purchase or auction bid for Kenya Government Bonds / Treasury Bills,
    updating the fixed income portfolio and recording the CSD transaction.
    """
    sym_clean = symbol.upper()
    asset = BONDS_CATALOG.get(sym_clean, ASSETS.get(sym_clean))
    if not asset or asset.get("category") != "bonds":
        return False, f"Invalid government security symbol: {symbol}", None

    unit_face_value = float(asset.get("face_value", 100000 if asset.get("subcategory") == "tbill" else 50000))
    
    # Calculate units and total face value
    if face_value and float(face_value) > 0:
        total_face_value = float(face_value)
        calculated_units = max(1, int(round(total_face_value / unit_face_value)))
        total_face_value = calculated_units * unit_face_value
        units = calculated_units
    elif units and int(units) > 0:
        units = int(units)
        total_face_value = units * unit_face_value
    else:
        units = 1
        total_face_value = unit_face_value

    price_pct = float(asset["price"])
    cost_kes = round(total_face_value * (price_pct / 100.0), 2)
    cost_usd = round(cost_kes / 130.0, 2)

    # Calculate return metrics
    is_tbill = asset.get("subcategory") == "tbill"
    is_tax_exempt = asset.get("tax_exempt", False)
    wht_rate = 0.0 if is_tax_exempt else 0.15

    if is_tbill:
        gross_interest = round(total_face_value - cost_kes, 2)
        tax_amount = round(gross_interest * wht_rate, 2)
        net_return = round(gross_interest - tax_amount, 2)
        annual_coupon = 0.0
        semi_annual_coupon = 0.0
    else:
        coupon_rate = float(asset.get("coupon_rate", 0))
        annual_coupon = round(total_face_value * (coupon_rate / 100.0), 2)
        semi_annual_coupon = round(annual_coupon / 2.0, 2)
        tax_amount = round(annual_coupon * wht_rate, 2)
        gross_interest = annual_coupon
        net_return = round(annual_coupon - tax_amount, 2)

    # Check and update cash balance in USER_PORTFOLIO
    if USER_PORTFOLIO.get("cash_balance_usd", 0) >= cost_usd:
        USER_PORTFOLIO["cash_balance_usd"] = max(0.0, round(USER_PORTFOLIO["cash_balance_usd"] - cost_usd, 2))

    # Transaction details
    tx_num = len(USER_PORTFOLIO.get("transactions", [])) + 9025
    order_type_clean = order_type.upper()
    if "AUCTION" in order_type_clean:
        tx_id = f"CSD-AUCT-{tx_num}"
        channel_name = "CBK Primary Auction (DhowCSD)"
        status_label = "Auction Bid Accepted & Allotted"
    else:
        tx_id = f"CSD-OTC-{tx_num}"
        channel_name = "NSE Secondary Fixed Income OTC"
        status_label = "Settled & Registered in CSD"

    new_tx = {
        "id": tx_id,
        "asset_symbol": sym_clean,
        "asset_name": asset["name"],
        "logo": get_asset_logo(sym_clean),
        "image": get_company_image(sym_clean),
        "type": f"BUY ({channel_name})",
        "shares": f"KES {total_face_value:,.0f} Face Value ({units} Units)",
        "price": f"{price_pct:.2f}% (YTM: {asset.get('yield_to_maturity')}%)",
        "total": f"KES {cost_kes:,.2f}",
        "date": "Just now",
        "status": status_label
    }
    USER_PORTFOLIO.setdefault("transactions", []).insert(0, new_tx)

    # Update BOND_PORTFOLIO holdings
    existing = next((h for h in BOND_PORTFOLIO["holdings"] if h["symbol"] == sym_clean), None)
    if existing:
        existing["units"] += units
        existing["face_value"] += total_face_value
        existing["cost"] = round(existing["cost"] + cost_kes, 2)
        existing["current_value"] = round(existing["current_value"] + cost_kes, 2)
    else:
        BOND_PORTFOLIO["holdings"].append({
            "symbol": sym_clean,
            "name": asset["name"],
            "logo": get_asset_logo(sym_clean),
            "image": get_company_image(sym_clean),
            "face_value": total_face_value,
            "units": units,
            "cost": cost_kes,
            "current_value": cost_kes,
            "yield": float(asset.get("yield_to_maturity", 0)),
            "coupon": float(asset.get("coupon_rate", 0)),
            "maturity": asset.get("maturity_date", "N/A"),
            "tax_exempt": is_tax_exempt,
            "category": asset.get("subcategory", "bond")
        })

    # Recalculate portfolio metrics
    BOND_PORTFOLIO["total_invested"] = round(sum(h["cost"] for h in BOND_PORTFOLIO["holdings"]), 2)
    BOND_PORTFOLIO["total_face_value"] = round(sum(h["face_value"] for h in BOND_PORTFOLIO["holdings"]), 2)
    if BOND_PORTFOLIO["total_face_value"] > 0:
        w_yield = sum(h["yield"] * h["face_value"] for h in BOND_PORTFOLIO["holdings"]) / BOND_PORTFOLIO["total_face_value"]
        BOND_PORTFOLIO["avg_yield"] = round(w_yield, 2)

    receipt = {
        "csd_reference": tx_id,
        "symbol": sym_clean,
        "name": asset["name"],
        "face_value_kes": total_face_value,
        "units": units,
        "settlement_cost_kes": cost_kes,
        "settlement_cost_usd": cost_usd,
        "price_pct": price_pct,
        "yield_to_maturity": asset.get("yield_to_maturity"),
        "coupon_rate": asset.get("coupon_rate", 0),
        "semi_annual_coupon": semi_annual_coupon,
        "maturity_date": asset.get("maturity_date", "N/A"),
        "channel": channel_name,
        "status": status_label,
        "tax_exempt": is_tax_exempt,
        "estimated_return": net_return,
        "transaction": new_tx
    }

    msg = f"Successfully placed order for KES {total_face_value:,.0f} in {asset['name']} at {price_pct:.2f}% clean price. Settlement cost: KES {cost_kes:,.2f}."
    return True, msg, receipt


def get_bonds_data():
    """
    Returns comprehensive fixed-income desk data for the bonds & treasury bills page,
    including the full catalog, yield curve, auction calendar, and portfolio analytics.
    """
    bonds = list(BONDS_CATALOG.values())
    tbills = [b for b in bonds if b.get("subcategory") == "tbill"]
    govt_bonds = [b for b in bonds if b.get("subcategory") == "bond"]

    # Yield ladder for display
    yield_ladder = []
    for b in sorted(bonds, key=lambda x: x.get("maturity_days", 0)):
        yield_ladder.append({
            "symbol": b["symbol"],
            "name": b["name"],
            "tenor": f"{b['maturity_days']}D",
            "yield": b.get("yield_to_maturity", 0),
            "coupon": b.get("coupon_rate", 0),
            "price": b["price"],
            "change": b["change"],
            "maturity_date": b.get("maturity_date", "N/A"),
            "tax_exempt": b.get("tax_exempt", False),
        })

    return {
        "all_bonds": bonds,
        "tbills": tbills,
        "govt_bonds": govt_bonds,
        "yield_ladder": yield_ladder,
        "auction_calendar": CBK_AUCTION_CALENDAR,
        "recent_auctions": CBK_RECENT_AUCTIONS,
        "bond_portfolio": BOND_PORTFOLIO,
        "yield_curves": SOVEREIGN_YIELD_CURVES,
    }


# Curated Institutional Financial News Stories (Syndicated from Accredited News Agencies)
FINANCIAL_NEWS = [
    {
        "id": 1,
        "title": "Central Bank of Kenya Holds Key Rate Steady at 12.75% as Inflation Cools",
        "summary": "The Monetary Policy Committee retained the benchmark lending rate, citing foreign exchange stabilization and decelerating food and energy price pressures.",
        "content": "NAIROBI — The Central Bank of Kenya's Monetary Policy Committee (MPC) announced today that it will maintain the Central Bank Rate (CBR) unchanged at 12.75%. Central Bank Governor highlighted that overall inflation has stabilized well within the target range of 5.0% ± 2.5%, assisted by lower import fuel bills and resilient agricultural harvests. Commercial banking liquidity remains strong, and the Kenyan Shilling continues its stable performance against the US dollar.",
        "category": "East Africa",
        "source": "Capital FM Kenya",
        "source_badge": "Capital FM",
        "time_ago": "18 minutes ago",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["SCOM", "EQTY", "KCB"],
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 2,
        "title": "Safaricom Cross-Border M-PESA Volumes Surge 34%, Fueling Robust H1 Earnings Forecast",
        "summary": "East Africa's most valuable tech telco sees exponential merchant transaction flow, expanding operations across Ethiopia and regional corridors.",
        "content": "NAIROBI — Safaricom PLC (NSE: SCOM) released quarterly transaction telemetry showcasing double-digit growth in M-PESA merchant settlement volumes. The fintech subsidiary recorded 34% year-over-year gains in cross-border settlements, bolstered by direct integrations with global payment rails. Analysts from Renaissance Capital reaffirmed their 'Strong Buy' rating on Safaricom with a 12-month price objective of KES 18.20.",
        "category": "Equities",
        "source": "Standard Media Kenya",
        "source_badge": "Standard Media",
        "time_ago": "1 hour ago",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["SCOM"],
        "image": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 3,
        "title": "NVIDIA Blackwell AI Server Deployments Accelerate; Enterprise Demand 'Off The Charts'",
        "summary": "CEO Jensen Huang noted that production capacity for next-generation B200 AI clusters is sold out through mid-2027 amid cloud infrastructure buildouts.",
        "content": "SANTA CLARA, Calif. — NVIDIA Corporation (NASDAQ: NVDA) saw shares rally over 4% after leadership confirmed that hyperscale cloud providers—including Microsoft, Meta, and Alphabet—have expanded their capital deployment for Blackwell AI accelerator architectures. Analysts project datacenter revenues will maintain exceptional gross margins above 75% through the upcoming fiscal year.",
        "category": "Technology",
        "source": "CNBC",
        "source_badge": "CNBC",
        "time_ago": "2 hours ago",
        "read_time": "5 min read",
        "sentiment": "Bullish",
        "tickers": ["NVDA", "MSFT", "AAPL"],
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 4,
        "title": "Bitcoin Flirts With $65,000 as Institutional ETF Inflows Top $800M in Single Session",
        "summary": "Digital asset markets experience a broad-based rally as institutional allocations hit new monthly highs ahead of global rate cut cycles.",
        "content": "NEW YORK — Bitcoin climbed past $64,800 today backed by renewed spot ETF inflows from institutional custody managers. Major investment houses recorded cumulative net purchases of 12,400 BTC over 48 hours. Altcoins also benefited, with Ethereum clearing $3,480 and Solana leaping 5.7% to $154.60.",
        "category": "Crypto",
        "source": "CoinDesk",
        "source_badge": "CoinDesk",
        "time_ago": "3 hours ago",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["BTC", "ETH", "SOL"],
        "image": "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 5,
        "title": "Tesla Announces Autonomous Robotaxi Commercial Fleet Roadmap and Cybercab Production Target",
        "summary": "Wall Street responds favorably to updated autonomous vehicle manufacturing timeline and proprietary end-to-end neural network driving demonstrations.",
        "content": "AUSTIN, Texas — Tesla Inc. (NASDAQ: TSLA) shares gained 6.2% following the detailed rollout strategy for its driverless ride-hailing app in Texas and California. Management reiterated targets for volume Cybercab production beginning in 2026 with vehicle cost estimates under $30,000.",
        "category": "Automotive",
        "source": "CNBC",
        "source_badge": "CNBC",
        "time_ago": "4 hours ago",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["TSLA"],
        "image": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 6,
        "title": "Gold Reaches Historic Territory as Global Central Banks Bolster Gold Reserves",
        "summary": "Bullion prices touch $2,657 an ounce as investors seek structural diversification against sovereign debt expansion and currency realignments.",
        "content": "LONDON — Gold sustained record-high trading levels in COMEX and London OTC settlement sessions today. Official central bank buying led by emerging market monetary authorities accounted for over 480 metric tonnes of physical gold bullion purchases year-to-date, according to the World Gold Council.",
        "category": "Commodities",
        "source": "MarketWatch",
        "source_badge": "MarketWatch",
        "time_ago": "5 hours ago",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["GOLD"],
        "image": "https://images.unsplash.com/photo-1610375461246-83df859d849d?auto=format&fit=crop&w=800&q=80"
    }
]

# User Simulated Portfolio State
USER_PORTFOLIO = {
    "total_value_usd": 27450.50,
    "cash_balance_usd": 5212.17,
    "day_profit_usd": 1546.80,
    "day_profit_percent": 5.96,
    "total_profit_usd": 4972.20,
    "total_profit_percent": 22.12,
    "holdings": [
        {
            "symbol": "SCOM",
            "name": "Safaricom PLC",
            "shares": 50000,
            "avg_buy_price": 12.40,
            "current_price": 14.85,
            "currency": "KES",
            "total_value": 742500.00, # KES
            "total_value_usd": 5711.53, # @ 130 KES/USD
            "profit_usd": 942.30,
            "profit_percent": 19.75,
            "allocation_percent": 20.8,
            "sparkline": [14.4, 14.5, 14.65, 14.55, 14.75, 14.8, 14.85]
        },
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "shares": 30,
            "avg_buy_price": 210.00,
            "current_price": 232.15,
            "currency": "USD",
            "total_value": 6964.50,
            "total_value_usd": 6964.50,
            "profit_usd": 664.50,
            "profit_percent": 10.55,
            "allocation_percent": 25.4,
            "sparkline": [228.5, 229.4, 230.8, 230.1, 231.5, 232.0, 232.15]
        },
        {
            "symbol": "NVDA",
            "name": "NVIDIA Corporation",
            "shares": 35,
            "avg_buy_price": 115.00,
            "current_price": 138.25,
            "currency": "USD",
            "total_value": 4838.75,
            "total_value_usd": 4838.75,
            "profit_usd": 813.75,
            "profit_percent": 20.21,
            "allocation_percent": 17.6,
            "sparkline": [132.5, 133.8, 135.2, 134.9, 137.0, 137.8, 138.25]
        },
        {
            "symbol": "BTC",
            "name": "Bitcoin (BTC)",
            "shares": 0.0728,
            "avg_buy_price": 58500.00,
            "current_price": 64850.00,
            "currency": "USD",
            "total_value": 4721.08,
            "total_value_usd": 4721.08,
            "profit_usd": 462.28,
            "profit_percent": 10.85,
            "allocation_percent": 17.2,
            "sparkline": [63030, 63400, 64100, 63800, 64500, 64700, 64850]
        }
    ],
    "transactions": [
        {
            "id": "TX-9021",
            "asset_symbol": "BTC",
            "asset_name": "Bitcoin",
            "type": "BUY",
            "shares": "0.025 BTC",
            "price": "$63,800.00",
            "total": "$1,595.00",
            "date": "Today, 14:22",
            "status": "Completed"
        },
        {
            "id": "TX-9020",
            "asset_symbol": "NVDA",
            "asset_name": "NVIDIA Corp",
            "type": "BUY",
            "shares": "10 Shares",
            "price": "$134.50",
            "total": "$1,345.00",
            "date": "Yesterday, 16:05",
            "status": "Completed"
        },
        {
            "id": "TX-9019",
            "asset_symbol": "SCOM",
            "asset_name": "Safaricom PLC",
            "type": "BUY",
            "shares": "10,000 Shares",
            "price": "KES 14.50",
            "total": "KES 145,000",
            "date": "Oct 09, 2026",
            "status": "Completed"
        },
        {
            "id": "TX-9018",
            "asset_symbol": "AAPL",
            "asset_name": "Apple Inc.",
            "type": "SELL",
            "shares": "5 Shares",
            "price": "$229.00",
            "total": "$1,145.00",
            "date": "Oct 08, 2026",
            "status": "Completed"
        }
    ]
}

# Watchlists Collection
WATCHLISTS = {
    "default": ["SCOM", "EQTY", "AAPL", "NVDA", "BTC", "ETH"],
    "tech": ["AAPL", "NVDA", "MSFT", "TSLA"],
    "kenya": ["SCOM", "EQTY", "KCB", "EABL"],
    "crypto": ["BTC", "ETH", "SOL"]
}

# Currency Exchange Rates relative to USD
EXCHANGE_RATES = {
    "USD": 1.0,
    "KES": 130.0,
    "EUR": 0.92,
    "GBP": 0.77
}

# Automatically associate official logos and real company images with all assets, indices, and portfolio records
for _item in MARKET_INDICES:
    _item["logo"] = get_asset_logo(_item["symbol"])
    _item["image"] = get_company_image(_item["symbol"])

for _sym, _asset in ASSETS.items():
    _asset["logo"] = get_asset_logo(_sym)
    _asset["image"] = get_company_image(_sym)

for _holding in USER_PORTFOLIO.get("holdings", []):
    _holding["logo"] = get_asset_logo(_holding["symbol"])
    _holding["image"] = get_company_image(_holding["symbol"])

for _tx in USER_PORTFOLIO.get("transactions", []):
    _tx["logo"] = get_asset_logo(_tx["asset_symbol"])
    _tx["image"] = get_company_image(_tx["asset_symbol"])

for _bh in BOND_PORTFOLIO.get("holdings", []):
    _bh["logo"] = get_asset_logo(_bh["symbol"])
    _bh["image"] = get_company_image(_bh["symbol"])


def generate_asset_ohlc(asset):
    """
    Generates realistic OHLC (Open, High, Low, Close, Volume, SMA) candlestick data
    for 1D, 1W, 1M, 1Y, and ALL timeframes with 20-26 high-resolution intervals.
    """
    timeframe_configs = {
        "1D": [
            "09:30", "09:45", "10:00", "10:15", "10:30", "10:45",
            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:15", "14:30", "14:45", "15:00", "15:15",
            "15:30", "15:45", "16:00"
        ],
        "1W": [
            "Mon AM", "Mon PM", "Tue AM", "Tue PM", "Wed AM",
            "Wed PM", "Thu AM", "Thu PM", "Fri AM", "Fri PM"
        ],
        "1M": [
            f"D{i+1}" for i in range(22)
        ],
        "1Y": [
            "Jan", "Jan 15", "Feb", "Feb 15", "Mar", "Mar 15", "Apr", "Apr 15",
            "May", "May 15", "Jun", "Jun 15", "Jul", "Jul 15", "Aug", "Aug 15",
            "Sep", "Sep 15", "Oct", "Oct 15", "Nov", "Nov 15", "Dec", "Current"
        ],
        "ALL": [
            "Q1 '22", "Q2 '22", "Q3 '22", "Q4 '22",
            "Q1 '23", "Q2 '23", "Q3 '23", "Q4 '23",
            "Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24",
            "Q1 '25", "Q2 '25", "Q3 '25", "Q4 '25",
            "Q1 '26", "Q2 '26", "Q3 '26", "Current"
        ]
    }
    
    price_base = float(asset["price"])
    prev_close = float(asset.get("previous_close", price_base * 0.98))
    history = asset.get("history", {})
    
    ohlc_data = {}
    for tf, labels in timeframe_configs.items():
        base_series = history.get(tf, [price_base * 0.95, price_base * 0.98, price_base])
        n = len(labels)
        
        # Interpolate points from base_series across n labels
        m = len(base_series)
        points = []
        for i in range(n):
            if m == 1:
                points.append(float(base_series[0]))
            else:
                pos = (i / (n - 1)) * (m - 1)
                idx = int(pos)
                frac = pos - idx
                if idx >= m - 1:
                    v = float(base_series[-1])
                else:
                    v = float(base_series[idx]) * (1 - frac) + float(base_series[idx + 1]) * frac
                # Add slight realistic micro-volatility
                jitter = ((i * 17 + 7) % 11 - 5) * 0.0015 * price_base
                points.append(v + jitter)
        
        # Anchor endpoints
        points[-1] = price_base
        if tf == "1D":
            points[0] = prev_close
            
        candles = []
        running_closes = []
        for i, label in enumerate(labels):
            close_val = round(points[i], 2)
            if i == 0:
                open_val = round(prev_close if tf == "1D" else close_val * 0.995, 2)
            else:
                open_val = candles[i - 1]["close"]
            
            delta = close_val - open_val
            spread = max(abs(delta), close_val * 0.003)
            
            # Realistic wicks
            wick_high = ((i * 13 + 3) % 7) * 0.001 * close_val
            wick_low = ((i * 19 + 5) % 7) * 0.001 * close_val
            high_val = round(max(open_val, close_val) + spread * 0.5 + wick_high, 2)
            low_val = round(max(0.01, min(open_val, close_val) - spread * 0.5 - wick_low), 2)
            
            if tf == "1D" and i == n - 1:
                close_val = price_base
                high_val = max(high_val, float(asset.get("day_high", high_val)))
                low_val = min(low_val, float(asset.get("day_low", low_val)))
                
            running_closes.append(close_val)
            # 5-period moving average for local trend, or expanding
            window = running_closes[-7:] if len(running_closes) >= 7 else running_closes
            sma_val = round(sum(window) / len(window), 2)
            
            vol_base = 850000
            vol_factor = 0.8 + ((abs(close_val - open_val) / max(0.01, close_val)) * 25) + ((i % 5) * 0.15)
            volume_val = int(vol_base * vol_factor)
            
            candles.append({
                "time": label,
                "open": open_val,
                "high": high_val,
                "low": low_val,
                "close": close_val,
                "volume": volume_val,
                "sma": sma_val,
                "is_bullish": close_val >= open_val
            })
            
        ohlc_data[tf] = candles
        
    return ohlc_data

# Attach OHLC series to every asset in catalog
for _sym, _a in ASSETS.items():
    _a["ohlc"] = generate_asset_ohlc(_a)


# =====================================================================
# PESAMARKETS PRO INSTITUTIONAL TERMINAL SERVICE
# =====================================================================

CENTRAL_BANK_RATES = [
    {"bank": "Central Bank of Kenya (CBK)", "rate": 12.75, "change": 0.0, "stance": "Neutral", "currency": "KES", "inflation": 4.2},
    {"bank": "US Federal Reserve (Fed)", "rate": 4.875, "change": -0.25, "stance": "Easing", "currency": "USD", "inflation": 2.4},
    {"bank": "European Central Bank (ECB)", "rate": 3.25, "change": -0.25, "stance": "Accommodative", "currency": "EUR", "inflation": 1.7},
    {"bank": "Bank of England (BoE)", "rate": 5.00, "change": 0.0, "stance": "Restrictive", "currency": "GBP", "inflation": 2.2},
    {"bank": "Bank of Japan (BoJ)", "rate": 0.25, "change": 0.0, "stance": "Normalizing", "currency": "JPY", "inflation": 2.5},
]

ECONOMIC_CALENDAR = [
    {"time": "09:00 EAT", "country": "KE", "event": "CBK Monetary Policy Committee Benchmark Decision", "period": "Q4", "actual": "12.75%", "forecast": "12.75%", "prior": "12.75%", "impact": "HIGH"},
    {"time": "10:30 EAT", "country": "KE", "event": "KNBS Headline Consumer Price Index (CPI YoY)", "period": "Sep", "actual": "4.20%", "forecast": "4.35%", "prior": "4.40%", "impact": "HIGH"},
    {"time": "13:30 EAT", "country": "US", "event": "US Core PCE Price Index (MoM / YoY)", "period": "Sep", "actual": "2.70%", "forecast": "2.60%", "prior": "2.70%", "impact": "HIGH"},
    {"time": "15:30 EAT", "country": "US", "event": "Non-Farm Payrolls (NFP) Net Job Additions", "period": "Sep", "actual": "142K", "forecast": "145K", "prior": "142K", "impact": "HIGH"},
    {"time": "16:00 EAT", "country": "KE", "event": "Treasury Bond Auction: 10-Yr IFB Infrastructure Bond", "period": "Issue", "actual": "17.85%", "forecast": "17.90%", "prior": "18.10%", "impact": "MED"},
    {"time": "17:00 EAT", "country": "EU", "event": "Eurozone HCOB Manufacturing PMI Final", "period": "Sep", "actual": "45.0", "forecast": "44.8", "prior": "44.8", "impact": "MED"},
]

SOVEREIGN_YIELD_CURVES = {
    "kenya": [
        {"tenor": "91D T-Bill", "yield": 15.72, "change": -0.08, "type": "T-Bill"},
        {"tenor": "182D T-Bill", "yield": 16.18, "change": -0.12, "type": "T-Bill"},
        {"tenor": "364D T-Bill", "yield": 16.45, "change": -0.15, "type": "T-Bill"},
        {"tenor": "2-Yr FXD", "yield": 16.85, "change": -0.10, "type": "Benchmark"},
        {"tenor": "5-Yr FXD", "yield": 17.10, "change": -0.05, "type": "Benchmark"},
        {"tenor": "10-Yr IFB", "yield": 17.85, "change": +0.02, "type": "Infrastructure"},
        {"tenor": "15-Yr FXD", "yield": 18.20, "change": +0.04, "type": "Long Bond"},
        {"tenor": "Eurobond '31", "yield": 9.42, "change": -0.18, "type": "Sovereign USD"},
    ],
    "us_treasuries": [
        {"tenor": "1-Month", "yield": 4.65, "change": -0.02},
        {"tenor": "3-Month", "yield": 4.58, "change": -0.03},
        {"tenor": "6-Month", "yield": 4.42, "change": -0.04},
        {"tenor": "1-Year", "yield": 4.18, "change": -0.05},
        {"tenor": "2-Year", "yield": 3.95, "change": -0.06},
        {"tenor": "5-Year", "yield": 3.98, "change": -0.04},
        {"tenor": "10-Year", "yield": 4.08, "change": -0.02},
        {"tenor": "30-Year", "yield": 4.38, "change": +0.01},
    ],
    "curve_spread_2_10": "+13 bps"
}

def get_terminal_data(symbol):
    """
    Returns an information-dense institutional payload featuring
    Financial Analysis (FA), Economic Calendar (ECO), Yield Curves (YCRV),
    Level 2 Market Depth, Technical Indicators, Client Sentiment, and Block Tape.
    """
    symbol_clean = symbol.upper()
    asset = ASSETS.get(symbol_clean, ASSETS.get("SCOM"))
    price = float(asset["price"])
    category = asset.get("category", "equities")
    market = asset.get("market", "NSE")
    currency = asset.get("currency", "KES")

    # Tick size & depth calculation
    if category == "crypto":
        tick = 5.0 if price > 1000 else (0.25 if price > 10 else 0.01)
        base_lot = 0.5 if price > 10000 else 12.0
        venues = ["BINANCE-MM", "COINBASE-PRIME", "KRAKEN-OTC", "OKX-ALGO", "BYBIT-DEPTH", "DERIBIT-INST", "WINTERMUTE", "JUMP-CRYPTO"]
    elif category == "commodities":
        tick = 0.20
        base_lot = 50.0
        venues = ["COMEX-MATCH", "LBMA-OTC", "CME-GLBX", "UBS-PRECIOUS", "HSBC-GOLD", "BARCLAYS-MET", "SCOTIA-MOC", "BMO-METALS"]
    elif market == "NSE":
        tick = 0.05 if price < 50 else 0.25
        base_lot = 8500.0
        venues = ["NSE-DMA", "SBG-SEC", "KCB-CAP", "DYER-BLR", "FAIDA-IB", "GENAFRICA", "AIB-AXYS", "APEX-AFR"]
    else:
        tick = 0.01 if price < 200 else 0.05
        base_lot = 450.0
        venues = ["ARCA", "INET", "BATS", "CITADEL", "VIRTU", "JPM-X", "TWO-SIGMA", "MORGAN-STANLEY"]

    # 1. Level 2 Order Book (8 Bids & 8 Asks)
    bids = []
    asks = []
    cum_bid = 0
    cum_ask = 0

    for i in range(8):
        # Bids
        b_price = round(max(0.01, price - (i + 1) * tick), 2)
        b_orders = int(12 + ((i * 7 + 3) % 19))
        b_size = int(base_lot * (1.2 + ((i * 11 + 5) % 13) * 0.15))
        cum_bid += b_size
        bids.append({
            "level": i + 1,
            "orders": b_orders,
            "size": b_size,
            "price": b_price,
            "venue": venues[i % len(venues)],
            "depth_pct": min(100, int((b_size / (base_lot * 3.5)) * 100))
        })

        # Asks
        a_price = round(price + (i + 1) * tick, 2)
        a_orders = int(9 + ((i * 5 + 4) % 17))
        a_size = int(base_lot * (0.95 + ((i * 13 + 7) % 11) * 0.14))
        cum_ask += a_size
        asks.append({
            "level": i + 1,
            "orders": a_orders,
            "size": a_size,
            "price": a_price,
            "venue": venues[(i + 3) % len(venues)],
            "depth_pct": min(100, int((a_size / (base_lot * 3.5)) * 100))
        })

    spread = round(asks[0]["price"] - bids[0]["price"], 4)
    spread_bps = round((spread / max(0.01, price)) * 10000, 1)
    tot_depth = max(1, cum_bid + cum_ask)
    bid_pressure = round((cum_bid / tot_depth) * 100, 1)
    ask_pressure = round(100 - bid_pressure, 1)
    micro_price = round(((bids[0]["price"] * asks[0]["size"]) + (asks[0]["price"] * bids[0]["size"])) / max(1, (bids[0]["size"] + asks[0]["size"])), 2)
    vwap = round(price * (0.9985 if price > 10 else 0.995), 2)

    level2 = {
        "bids": bids,
        "asks": asks,
        "total_bid_size": f"{cum_bid:,}",
        "total_ask_size": f"{cum_ask:,}",
        "bid_pressure_pct": bid_pressure,
        "ask_pressure_pct": ask_pressure,
        "spread": spread,
        "spread_bps": spread_bps,
        "micro_price": micro_price,
        "vwap": vwap
    }

    # 2. Fundamental Valuation & Financial Statements (FA / DES)
    pe_raw = asset.get("pe_ratio")
    try:
        pe_val = float(pe_raw) if pe_raw not in [None, "N/A", ""] else None
    except (ValueError, TypeError):
        pe_val = None

    eps_raw = asset.get("eps")
    try:
        eps_val = float(eps_raw) if eps_raw not in [None, "N/A", ""] else (round(price / (pe_val if pe_val else 15), 2) if category == "equities" else "N/A")
    except (ValueError, TypeError):
        eps_val = "N/A"

    div_yield = asset.get("dividend_yield", "N/A")
    beta_val = asset.get("beta", 1.05)

    if category == "crypto" or category == "commodities":
        fa = {
            "market_cap": asset.get("market_cap", "N/A"),
            "enterprise_value": asset.get("market_cap", "N/A"),
            "pe_ttm": "N/A (Store of Value)",
            "pe_fwd": "N/A",
            "peg_ratio": "N/A",
            "pb_ratio": "N/A",
            "ps_ratio": "N/A",
            "ev_ebitda": "N/A",
            "ev_fcf": "N/A",
            "fcf_yield": "N/A",
            "roe": "N/A",
            "roic": "N/A",
            "roa": "N/A",
            "gross_margin": "N/A",
            "operating_margin": "N/A",
            "net_margin": "N/A",
            "altman_z": 9.99,
            "altman_status": "Non-Applicable (Commodity / Digital Asset)",
            "piotroski_f": "N/A",
            "current_ratio": "N/A",
            "quick_ratio": "N/A",
            "debt_to_equity": "0.00",
            "interest_coverage": "N/A",
            "div_yield": "0.00%",
            "payout_ratio": "0.00%",
            "shares_out": "21.0M Cap" if symbol_clean == "BTC" else "Circulating Supply"
        }
    else:
        is_tech = symbol_clean in ["AAPL", "NVDA", "TSLA", "MSFT"]
        is_bank = symbol_clean in ["EQTY", "KCB"]
        
        fa = {
            "market_cap": asset.get("market_cap", "N/A"),
            "enterprise_value": f"{currency} {asset.get('market_cap', 'N/A')}",
            "pe_ttm": f"{pe_val:.1f}x" if pe_val else "N/A",
            "pe_fwd": f"{(pe_val * 0.86):.1f}x" if pe_val else "N/A",
            "peg_ratio": "1.35x" if is_tech else ("0.68x" if is_bank else "1.12x"),
            "pb_ratio": "38.2x" if symbol_clean == "AAPL" else ("48.6x" if symbol_clean == "NVDA" else ("0.85x" if is_bank else "2.40x")),
            "ps_ratio": "28.5x" if symbol_clean == "NVDA" else ("8.2x" if is_tech else "1.65x"),
            "ev_ebitda": "34.2x" if symbol_clean == "NVDA" else ("18.5x" if is_tech else "5.8x"),
            "ev_fcf": "41.5x" if is_tech else "7.4x",
            "fcf_yield": "2.4%" if is_tech else ("14.8%" if is_bank else "11.2%"),
            "roe": "115.6%" if symbol_clean == "NVDA" else ("147.2%" if symbol_clean == "AAPL" else ("22.4%" if is_bank else "28.4%")),
            "roic": "64.8%" if symbol_clean == "NVDA" else ("56.2%" if is_tech else "18.5%"),
            "roa": "48.1%" if symbol_clean == "NVDA" else ("28.4%" if is_tech else ("3.1%" if is_bank else "14.2%")),
            "gross_margin": "75.1%" if symbol_clean == "NVDA" else ("46.2%" if is_tech else "58.4%"),
            "operating_margin": "62.4%" if symbol_clean == "NVDA" else ("31.2%" if is_tech else "34.1%"),
            "net_margin": "55.8%" if symbol_clean == "NVDA" else ("24.5%" if is_tech else ("26.8%" if is_bank else "22.5%")),
            "altman_z": 18.42 if symbol_clean == "NVDA" else (8.95 if symbol_clean == "AAPL" else 3.82),
            "altman_status": "Safe Zone (Low Default Probability)",
            "piotroski_f": "9 / 9 (Superior Quality)" if is_tech else "8 / 9 (High Quality Value)",
            "current_ratio": 4.12 if symbol_clean == "NVDA" else (1.45 if not is_bank else 1.25),
            "quick_ratio": 3.45 if symbol_clean == "NVDA" else (1.28 if not is_bank else 1.15),
            "debt_to_equity": 0.18 if is_tech else (0.62 if not is_bank else 0.82),
            "interest_coverage": "48.2x" if is_tech else ("14.5x" if not is_bank else "7.2x"),
            "div_yield": str(div_yield),
            "payout_ratio": "1.8%" if is_tech else ("42.5%" if is_bank else "72.4%"),
            "shares_out": "24.55B" if symbol_clean == "NVDA" else ("15.12B" if symbol_clean == "AAPL" else ("40.06B" if symbol_clean == "SCOM" else "3.77B"))
        }

    # 3. Technical Scanner & Client Sentiment
    rsi_val = 68.4 if symbol_clean in ["NVDA", "BTC", "GOLD"] else (58.2 if symbol_clean == "SCOM" else 52.8)
    rsi_status = "Overbought Momentum" if rsi_val > 70 else ("Bullish Expansion" if rsi_val > 55 else "Neutral")
    
    technicals = {
        "rsi_14": rsi_val,
        "rsi_status": rsi_status,
        "macd": {
            "line": round(price * 0.015, 2),
            "signal": round(price * 0.011, 2),
            "hist": round(price * 0.004, 2),
            "status": "Bullish Divergence / Positive Acceleration"
        },
        "bollinger": {
            "upper": round(price * 1.045, 2),
            "mid": round(price * 0.998, 2),
            "lower": round(price * 0.952, 2),
            "bandwidth": "9.3%",
            "pct_b": 0.68
        },
        "moving_averages": [
            {"period": "EMA 20", "value": round(price * 0.985, 2), "status": "BULLISH", "signal": "Strong Buy", "pct": "+1.5%"},
            {"period": "SMA 50", "value": round(price * 0.958, 2), "status": "BULLISH", "signal": "Strong Buy", "pct": "+4.2%"},
            {"period": "SMA 100", "value": round(price * 0.915, 2), "status": "BULLISH", "signal": "Bullish Trend", "pct": "+8.5%"},
            {"period": "SMA 200", "value": round(price * 0.862, 2), "status": "BULLISH", "signal": "Golden Cross", "pct": "+13.8%"},
        ],
        "pivots": {
            "r3": round(price * 1.058, 2),
            "r2": round(price * 1.036, 2),
            "r1": round(price * 1.018, 2),
            "pp": round(price * 0.995, 2),
            "s1": round(price * 0.978, 2),
            "s2": round(price * 0.962, 2),
            "s3": round(price * 0.942, 2)
        },
        "atr_14": round(price * 0.024, 2),
        "adx_14": {"value": 29.8, "trend": "Strong Directional Trend"},
        "stochastic": {"k": 68.2, "d": 63.4, "signal": "Bullish Continuous"},
        "sentiment": {
            "long_pct": 78 if symbol_clean in ["SCOM", "NVDA", "BTC"] else 64,
            "short_pct": 22 if symbol_clean in ["SCOM", "NVDA", "BTC"] else 36,
            "shift_24h": "+3.4% Net Buying",
            "positioning": "Strong Institutional Overweight",
            "put_call_ratio": 0.62,
            "retail_inst_divergence": "Institutional: 84% Long vs Retail: 59% Long"
        }
    }

    # 4. Institutional Block Tape (Time & Sales)
    tape = []
    times = [
        "16:28:14", "16:26:50", "16:24:12", "16:21:45",
        "16:18:02", "16:14:38", "16:10:19", "16:05:44",
        "16:01:20", "15:58:05", "15:52:40", "15:48:15"
    ]
    sides = ["BUY", "BUY", "SELL", "BUY", "BUY", "CROSS", "BUY", "SELL", "BUY", "BUY", "SELL", "BUY"]
    for idx, tm in enumerate(times):
        side = sides[idx]
        t_price = round(price + ((idx % 3 - 1) * tick), 2)
        t_qty = int(base_lot * (2.5 + ((idx * 7 + 1) % 9) * 0.8))
        is_block = t_qty > (base_lot * 4.5)
        tot_val = t_price * t_qty
        
        tape.append({
            "time": tm,
            "side": side,
            "price": f"{currency} {t_price:,.2f}",
            "size": f"{t_qty:,}",
            "total": f"{currency} {tot_val:,.2f}",
            "venue": venues[idx % len(venues)],
            "condition": "INST BLOCK" if is_block else ("CROSS" if side == "CROSS" else "REGULAR")
        })

    block_data = {
        "tape": tape,
        "cvd": f"+{currency} {int(base_lot * 45 * price):,} Net Accumulation",
        "inst_block_ratio": "72.4% Institutional Volume Share"
    }

    # 5. Intermarket Correlations with this asset
    correlations = [
        {"asset": "Benchmark Index (NSE 20 / S&P 500)", "corr": 0.84, "direction": "Strong Positive", "beta": beta_val},
        {"asset": "Local FX (USD/KES Exchange Rate)", "corr": -0.42, "direction": "Inverse Hedge", "beta": -0.35},
        {"asset": "10-Yr Sovereign Benchmark Yield", "corr": -0.38, "direction": "Moderate Inverse", "beta": -0.28},
        {"asset": "Gold Bullion (COMEX GC=F)", "corr": 0.28, "direction": "Mild Diversification", "beta": 0.22},
        {"asset": "Crude Oil (WTI CL=F)", "corr": -0.15, "direction": "Low Correlation", "beta": -0.12},
    ]

    return {
        "asset": asset,
        "level2": level2,
        "valuation_fa": fa,
        "technicals": technicals,
        "block_data": block_data,
        "correlations": correlations,
        "central_banks": CENTRAL_BANK_RATES,
        "economic_calendar": ECONOMIC_CALENDAR,
        "yield_curves": SOVEREIGN_YIELD_CURVES,
        "all_assets": list(ASSETS.values())
    }

