"""
Market Data Service for PesaMarkets
Provides comprehensive data for major US, Global, African (NSE), Crypto, and Commodity assets,
simulating Yahoo Finance features including real-time quotes, multi-timeframe charts,
key statistics, analyst ratings, news feeds, and market movers.
"""

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

# Comprehensive Asset Catalog with Yahoo Finance details
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
    }
}

# Curated Yahoo Finance News Stories
FINANCIAL_NEWS = [
    {
        "id": 1,
        "title": "Central Bank of Kenya Holds Key Rate Steady at 12.75% as Inflation Cools",
        "summary": "The Monetary Policy Committee retained the benchmark lending rate, citing foreign exchange stabilization and decelerating food and energy price pressures.",
        "content": "NAIROBI — The Central Bank of Kenya's Monetary Policy Committee (MPC) announced today that it will maintain the Central Bank Rate (CBR) unchanged at 12.75%. Central Bank Governor highlighted that overall inflation has stabilized well within the target range of 5.0% ± 2.5%, assisted by lower import fuel bills and resilient agricultural harvests. Commercial banking liquidity remains strong, and the Kenyan Shilling continues its stable performance against the US dollar.",
        "category": "East Africa",
        "source": "Business Daily Africa",
        "source_badge": "BDA",
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
        "source": "Reuters Financial",
        "source_badge": "Reuters",
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
        "source": "Yahoo Finance",
        "source_badge": "Yahoo",
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
        "source": "Bloomberg Markets",
        "source_badge": "Bloomberg",
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
        "source": "CNBC International",
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
        "source": "Financial Times",
        "source_badge": "FT",
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
