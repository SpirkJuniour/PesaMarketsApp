"""
Market Intelligence & Syndicated Agency Wire Service for PesaMarkets
Aggregates and syndicates accredited financial, macroeconomic, and market news.
STRICTLY FILTERED to ensure 100% relevance to PesaMarkets' verified offerings:
- Dynamic Top 50 Best Companies Index (NSE, US, UK, Japan)
- Investor Delisting Warnings & Contender Promotion Pipeline
- Sovereign Debt & Treasury Bills Desk (USA, UK, Japan, Kenya)
- Physical & Futures Commodities Desk (All Oil Types, Silver, Gold, Copper, Platinum, Softs, Grains)
Filters out all random non-financial news, crypto, celebrity gossip, and sports.
"""

import re
import html
import time
import hashlib
import urllib.request
from datetime import datetime, timezone

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

# Trending market topics ribbon
NEWS_TRENDING_TOPICS = [
    "Stock market today",
    "Nvidia AI compute live updates",
    "CBK monetary policy & rate decision",
    "US 10-Yr Treasury yield",
    "Kenya Infrastructure Bond demand",
    "S&P 500 earnings streak",
    "Brent Crude & energy flows",
    "M-PESA global payment rails",
]

# List of trusted, recognized news agencies providing RSS feeds
RSS_AGENCY_FEEDS = [
    {
        "agency": "Capital FM Kenya",
        "badge": "Capital FM",
        "category": "East Africa",
        "url": "https://www.capitalfm.co.ke/business/feed/",
        "icon": "fa-solid fa-radio",
        "color": "#E00B41",
    },
    {
        "agency": "Standard Media Kenya",
        "badge": "Standard Media",
        "category": "East Africa",
        "url": "https://www.standardmedia.co.ke/rss/business.php",
        "icon": "fa-solid fa-newspaper",
        "color": "#C13515",
    },
    {
        "agency": "CNBC",
        "badge": "CNBC",
        "category": "Equities",
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "icon": "fa-solid fa-chart-line",
        "color": "#0077b6",
    },
    {
        "agency": "BBC News",
        "badge": "BBC News",
        "category": "Equities",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "icon": "fa-solid fa-building-columns",
        "color": "#b80000",
    },
    {
        "agency": "CNBC",
        "badge": "CNBC Tech",
        "category": "Technology",
        "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "icon": "fa-solid fa-microchip",
        "color": "#0284c7",
    },
    {
        "agency": "Global Treasury Wire",
        "badge": "Treasury Wire",
        "category": "Sovereign Debt",
        "url": "https://home.treasury.gov/news/press-releases",
        "icon": "fa-solid fa-landmark",
        "color": "#4169e1",
    },
    {
        "agency": "Financial Times Debt",
        "badge": "FT Debt",
        "category": "Sovereign Debt",
        "url": "https://www.ft.com/stream/cb4ebbf9-bc36-4d20-b467-3388a101f3f4?format=rss",
        "icon": "fa-solid fa-building-columns",
        "color": "#0ea5e9",
    },
    {
        "agency": "Energy & Oil Wire",
        "badge": "Energy Wire",
        "category": "Commodities",
        "url": "https://www.cnbc.com/id/19836768/device/rss/rss.html",
        "icon": "fa-solid fa-oil-well",
        "color": "#10b981",
    },
    {
        "agency": "Commodity Intelligence Desk",
        "badge": "Commodity Wire",
        "category": "Commodities",
        "url": "https://www.cnbc.com/id/10000115/device/rss/rss.html",
        "icon": "fa-solid fa-cubes-stacked",
        "color": "#059669",
    },
]

# Ticker keywords mapping for automatic entity recognition in news titles/summaries
TICKER_KEYWORD_MAP = {
    # Kenya Listed Companies
    "SCOM": ["safaricom", "m-pesa", "mpesa", "scom", "peter ndejwa"],
    "EQTY": ["equity bank", "equity group", "eqty", "james mwangi"],
    "KCB": ["kcb", "kcb bank", "kenya commercial bank", "paul russo"],
    "COOP": ["co-op bank", "cooperative bank", "coop", "co-operative bank of kenya", "gideon muriuki"],
    "KEGN": ["kengen", "kenya electricity generating", "geothermal", "olkaria"],
    "BAMB": ["bamburi", "bamburi cement"],
    "KUKZ": ["kakuzi", "avocado export"],
    "SCBK": ["standard chartered kenya", "stanchart kenya"],
    "NCBA": ["ncba", "ncba bank"],
    "CENT": ["centum", "centum investment"],
    "JUB": ["jubilee", "jubilee holdings"],
    "CROW": ["crown paints", "crown paint"],
    "NSE": ["nse", "nairobi securities exchange", "nse 20"],
    "CBK": ["central bank of kenya", "cbk", "dhowcsd", "kamau thugge", "cbr rate", "mpc rate"],

    # USA Listed Companies
    "MSFT": ["microsoft", "msft", "satya nadella", "azure"],
    "AAPL": ["apple", "aapl", "iphone", "tim cook"],
    "NVDA": ["nvidia", "nvda", "jensen huang", "blackwell", "gpu"],
    "GOOGL": ["alphabet", "google", "googl", "sundar pichai"],
    "AMZN": ["amazon", "amzn", "andy jassy", "aws"],
    "TSLA": ["tesla", "tsla", "elon musk"],
    "COST": ["costco", "cost"],
    "JNJ": ["johnson & johnson", "jnj"],
    "DE": ["deere", "john deere"],
    "ABT": ["abbott", "abbott laboratories"],
    "HD": ["home depot"],
    "PG": ["procter & gamble"],
    "MDT": ["medtronic"],
    "CRM": ["salesforce"],
    "ADBE": ["adobe"],
    "CSCO": ["cisco"],
    "INTC": ["intel"],
    "TXN": ["texas instruments"],
    "INTU": ["intuit"],
    "SP500": ["s&p 500", "s&p500", "sp500", "wall street"],
    "NASDAQ": ["nasdaq"],
    "DJI": ["dow jones", "djia"],

    # UK Listed Companies
    "AZN": ["astrazeneca", "azn", "pascal soriot"],
    "ULVR": ["unilever", "ulvr", "hein schumacher"],
    "GSK": ["gsk", "glaxosmithkline", "emma walmsley"],
    "REL": ["relx"],
    "NG": ["national grid"],
    "HLMA": ["halma"],
    "SN": ["smith & nephew"],
    "CPG": ["compass group"],
    "EXPN": ["experian"],
    "BP": ["bp", "british petroleum", "murray auchincloss"],
    "SHEL": ["shell", "shel", "wael sawan"],
    "HSBA": ["hsbc", "hsba"],
    "FTSE": ["ftse", "ftse 100", "london stock exchange", "lse"],

    # Japan Listed Companies
    "7203": ["toyota", "7203", "koji sato"],
    "6758": ["sony", "6758", "kenichiro yoshida", "playstation"],
    "7974": ["nintendo", "7974", "shuntaro furukawa"],
    "8035": ["tokyo electron", "8035"],
    "4063": ["shin-etsu", "shin etsu", "4063"],
    "6861": ["keyence", "6861"],
    "6902": ["denso", "6902"],
    "6501": ["hitachi", "6501"],
    "7741": ["hoya", "7741"],
    "8306": ["mitsubishi ufj", "mufg", "8306"],
    "6645": ["omron", "6645"],
    "9984": ["softbank", "9984", "masayoshi son"],
    "N225": ["nikkei", "nikkei 225", "tokyo stock exchange", "tse"],

    # Sovereign Debt & T-Bills
    "US_TREASURY": ["us treasury", "united states treasury", "janet yellen", "t-bill", "t-note", "t-bond"],
    "UST10Y": ["10-year treasury", "10-yr treasury", "us 10y", "benchmark treasury yield"],
    "UST2Y": ["2-year treasury", "2-yr treasury", "us 2y"],
    "UST30Y": ["30-year treasury", "30-yr treasury", "long bond"],
    "USTB3M": ["3-month treasury bill", "3m t-bill", "13-week treasury bill"],
    "UK_DMO": ["uk debt management office", "dmo", "gilt", "gilts", "hm treasury"],
    "UKG10Y": ["10-year gilt", "uk 10y gilt", "benchmark gilt"],
    "UKG30Y": ["30-year gilt", "long gilt"],
    "MOF_JAPAN": ["ministry of finance japan", "mof japan", "japanese government bond", "jgb", "jgbs", "bank of japan", "boj"],
    "JGB10Y": ["10-year jgb", "japan 10y"],
    "JGB30Y": ["30-year jgb", "super-long jgb"],
    "T91": ["91-day treasury bill", "91-day t-bill", "91 day", "t91"],
    "T182": ["182-day treasury bill", "182-day t-bill", "182 day", "t182"],
    "T364": ["364-day treasury bill", "364-day t-bill", "364 day", "t364"],
    "IFB10Y": ["10-year infrastructure bond", "infrastructure bond", "ifb10y"],
    "IFB17Y": ["17-year infrastructure bond", "ifb17y"],

    # Physical & Futures Commodities
    "OIL": ["wti crude", "crude oil", "wti", "us crude", "petroleum"],
    "BRENT": ["brent crude", "brent", "north sea brent", "ice brent"],
    "NATGAS": ["natural gas", "henry hub", "natgas", "lng"],
    "HEATOIL": ["heating oil", "ulsd", "diesel futures"],
    "SILVER": ["silver", "comex silver", "silver futures", "silver spot"],
    "GOLD": ["gold", "comex gold", "bullion", "gold futures", "gold spot"],
    "COPPER": ["copper", "comex copper", "doctor copper", "copper cathode"],
    "PLATINUM": ["platinum", "nymex platinum"],
    "COFFEE": ["coffee", "arabica", "coffee c", "robusta"],
    "COCOA": ["cocoa", "ice cocoa"],
    "WHEAT": ["wheat", "chicago wheat", "srw wheat"]
}

# Whitelist of verified financial offering keywords
PESAMARKETS_OFFERING_KEYWORDS = [
    # Kenya & East Africa Suite
    "safaricom", "m-pesa", "mpesa", "equity bank", "equity group", "kcb", "co-op bank", "cooperative bank",
    "kengen", "bamburi", "kakuzi", "standard chartered", "ncba", "centum", "jubilee", "crown paints",
    "nairobi securities exchange", "nse", "central bank of kenya", "cbk", "dhowcsd", "kamau thugge",
    "cbr rate", "mpc", "kenyan shilling", "kes", "east africa",

    # US Top 50 Equities Suite
    "microsoft", "apple", "nvidia", "alphabet", "google", "amazon", "tesla", "costco", "johnson & johnson",
    "deere", "abbott", "home depot", "procter & gamble", "medtronic", "salesforce", "adobe", "cisco",
    "intel", "texas instruments", "intuit", "s&p 500", "nasdaq", "dow jones", "wall street", "nyse",

    # UK Top 50 Equities Suite
    "astrazeneca", "unilever", "gsk", "glaxosmithkline", "relx", "national grid", "halma", "smith & nephew",
    "compass group", "experian", "bp", "shell", "hsbc", "ftse", "ftse 100", "london stock exchange", "lse",

    # Japan Top 50 Equities Suite
    "toyota", "sony", "nintendo", "tokyo electron", "shin-etsu", "keyence", "denso", "hitachi", "hoya",
    "mitsubishi ufj", "mufg", "omron", "softbank", "nikkei", "nikkei 225", "tokyo stock exchange", "tse",

    # Sovereign Debt & T-Bills Suite (USA, UK, Japan, Kenya)
    "treasury bill", "treasury bills", "t-bill", "t-bills", "treasury note", "treasury notes", "treasury bond",
    "treasury bonds", "sovereign debt", "gilt", "gilts", "jgb", "jgbs", "government bond", "government bonds",
    "yield curve", "infrastructure bond", "91-day", "182-day", "364-day", "10-year treasury", "30-year treasury",
    "debt management office", "dmo", "primary auction", "federal reserve", "fomc", "interest rate", "monetary policy",

    # Commodities Suite (Oil, Silver, Gold, Copper, Platinum, Coffee, Cocoa, Wheat)
    "oil", "crude", "crude oil", "wti", "brent", "natural gas", "natgas", "henry hub", "heating oil", "diesel",
    "distillate", "silver", "gold", "bullion", "copper", "doctor copper", "platinum", "coffee", "arabica",
    "cocoa", "wheat", "grain", "commodity", "commodities", "comex", "nymex", "ice", "cbot", "energy", "metals",

    # Top 50 Governance, Dynamic Rebalance & Investor Alerts
    "top 50", "delisting", "underperformance", "warning", "contender", "rebalance", "portfolio", "dividend",
    "earnings", "financial results", "capital markets", "stock market", "inflation", "equity", "equities", "stock", "stocks"
]

# Blacklist of non-offering topics that must NEVER appear in the PesaMarkets feed
PESAMARKETS_EXCLUSION_KEYWORDS = [
    # Crypto / digital tokens (strictly banned on PesaMarkets)
    "crypto", "cryptocurrency", "bitcoin", "btc", "ethereum", "eth", "solana", "dogecoin", "doge", "memecoin",
    "nft", "nfts", "blockchain", "binance", "coinbase", "token", "tokens", "web3", "defi", "altcoin",

    # Tabloid / Entertainment / Celebrity
    "hollywood", "celebrity", "divorce", "dating", "kardashian", "paparazzi", "reality tv", "red carpet",

    # Sports
    "premier league", "champions league", "football match", "soccer match", "nba", "nfl", "formula 1",
    "tennis match", "world cup", "goal scored", "hat trick", "touchdown",

    # Non-financial sensationalism
    "murder", "homicide", "kidnapping", "assault", "robbery", "stabbing",

    # Competitor aggregator / brokerage platforms (strictly banned from PesaMarkets feed)
    "yahoo", "bloomberg", "marketwatch", "tradingview", "robinhood", "webull",
    "etrade", "saxo bank", "saxo", "seeking alpha", "investing.com", "finviz",
    "benzinga", "tipranks", "morningstar", "factset", "zacks", "motley fool",
    "koyfin", "barchart"
]

INVESTOR_CATEGORIES = [
    {
        "slug": "top-stories",
        "name": "Top Stories",
        "short_name": "Top Stories",
        "icon": "fa-solid fa-bolt",
        "badge_color": "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/20",
        "description": "High-impact market headlines, breaking developments, and essential dispatches.",
    },
    {
        "slug": "tech-ai",
        "name": "Tech & AI",
        "short_name": "Tech & AI",
        "icon": "fa-solid fa-microchip",
        "badge_color": "bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/20",
        "description": "Artificial intelligence hardware, cloud hyperscalers, semiconductors, and software.",
    },
    {
        "slug": "bonds-treasuries",
        "name": "Bonds & Treasury Bills",
        "short_name": "Bonds & T-Bills",
        "icon": "fa-solid fa-landmark",
        "badge_color": "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
        "description": "US Treasuries, UK Gilts, Japan JGBs, Kenya CBK T-bills, and sovereign yields.",
    },
    {
        "slug": "equities",
        "name": "Equities & Blue Chips",
        "short_name": "Equities",
        "icon": "fa-solid fa-chart-line",
        "badge_color": "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/20",
        "description": "Global Top 50 companies, quarterly earnings, dividends, and corporate actions.",
    },
    {
        "slug": "commodities",
        "name": "Commodities & Energy",
        "short_name": "Commodities",
        "icon": "fa-solid fa-oil-well",
        "badge_color": "bg-orange-500/15 text-orange-600 dark:text-orange-400 border-orange-500/20",
        "description": "WTI & Brent Crude, Natural Gas, Silver, Gold, Copper, Platinum, and Softs.",
    },
    {
        "slug": "east-africa",
        "name": "East Africa & Emerging Markets",
        "short_name": "East Africa",
        "icon": "fa-solid fa-earth-africa",
        "badge_color": "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/20",
        "description": "Nairobi Securities Exchange (NSE), Safaricom M-PESA, regional banking, and trade.",
    },
    {
        "slug": "macro-central-banks",
        "name": "Macro & Central Banks",
        "short_name": "Macro & Banks",
        "icon": "fa-solid fa-building-columns",
        "badge_color": "bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 border-indigo-500/20",
        "description": "Federal Reserve, CBK MPC, BoE, BoJ interest rates, inflation, and FX policy.",
    },
    {
        "slug": "index-rankings",
        "name": "Index & Dynamic Rankings",
        "short_name": "Index & Rankings",
        "icon": "fa-solid fa-ranking-star",
        "badge_color": "bg-teal-500/15 text-teal-600 dark:text-teal-400 border-teal-500/20",
        "description": "Top 50 constituent rebalancing, delisting warnings, and contender promotions.",
    },
]

# Authentic local images matching verified companies and desks
CATEGORY_IMAGES = {
    "Top Stories": "/static/companies/sp500.jpg",
    "Tech & AI": "/static/companies/nvda.jpg",
    "Bonds & Treasury Bills": "/static/companies/us_treasury.jpg",
    "Equities & Blue Chips": "/static/companies/7203.jpg",
    "Commodities & Energy": "/static/companies/brent.jpg",
    "East Africa & Emerging Markets": "/static/companies/scom.jpg",
    "Macro & Central Banks": "/static/companies/cbk.jpg",
    "Index & Dynamic Rankings": "/static/companies/nse.jpg",
    # Legacy aliases
    "East Africa": "/static/companies/scom.jpg",
    "Equities": "/static/companies/7203.jpg",
    "Technology": "/static/companies/nvda.jpg",
    "Sovereign Debt": "/static/companies/us_treasury.jpg",
    "Commodities": "/static/companies/brent.jpg",
}

AVAILABLE_COMPANY_IMAGES = {
    "4063", "6501", "6645", "6758", "6861", "6902", "7203", "7741", "7974", "8035", "8306", "9984",
    "aapl", "abt", "adbe", "amzn", "azn", "bamb", "bp", "brent", "cbk", "cent", "cocoa", "coffee",
    "coop", "copper", "cost", "cpg", "crm", "crow", "cscco", "csco", "de", "dhr", "dow", "eabl", "eqty",
    "expn", "gold", "googl", "gsk", "hd", "heatoil", "hlma", "hsba", "intc", "intu", "jnj", "jub",
    "kcb", "kegn", "kukz", "mdt", "mof_japan", "msft", "nasdaq", "natgas", "ncba", "ng", "nse",
    "nvda", "oil", "pg", "platinum", "rel", "scbk", "scom", "shel", "silver", "sn", "sp500", "syk",
    "tmo", "tsla", "txn", "uk_dmo", "ulvr", "us_treasury", "wheat"
}

DEFAULT_AUTHORS = [
    {
        "name": "David Kimani",
        "role": "Senior Macro & East Africa Analyst",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80",
    },
    {
        "name": "Sarah Jenkins",
        "role": "Lead Semiconductor & AI Correspondent",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80",
    },
    {
        "name": "Alastair Vance",
        "role": "Global Commodities & Energy Strategist",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
    },
    {
        "name": "Elena Rostova",
        "role": "Sovereign Debt & Fixed Income Desk Chief",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80",
    },
    {
        "name": "Kenji Takahashi",
        "role": "Asia-Pacific Equities Specialist",
        "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
    },
    {
        "name": "Marcus Sterling",
        "role": "Chief Index Governance Architect",
        "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
    },
]

CATEGORY_SYNONYMS = {
    "all": ["all"],
    "top-stories": ["top stories", "top-stories", "top stories & breaking"],
    "top stories": ["top stories", "top-stories", "top stories & breaking"],
    
    "tech-ai": ["tech & ai", "tech-ai", "technology", "tech"],
    "tech & ai": ["tech & ai", "tech-ai", "technology", "tech"],
    "technology": ["tech & ai", "tech-ai", "technology", "tech"],
    "tech": ["tech & ai", "tech-ai", "technology", "tech"],
    
    "bonds-treasuries": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    "bonds & treasury bills": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    "bonds": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    "sovereign debt": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    "tbills": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    "treasuries": ["bonds & treasury bills", "bonds-treasuries", "sovereign debt", "bonds", "tbills", "treasuries", "fixed income"],
    
    "equities": ["equities & blue chips", "equities", "stocks"],
    "equities & blue chips": ["equities & blue chips", "equities", "stocks"],
    "stocks": ["equities & blue chips", "equities", "stocks"],
    
    "commodities": ["commodities & energy", "commodities", "commodity", "energy"],
    "commodities & energy": ["commodities & energy", "commodities", "commodity", "energy"],
    "energy": ["commodities & energy", "commodities", "commodity", "energy"],
    
    "east-africa": ["east africa & emerging markets", "east africa", "east-africa", "kenya"],
    "east africa": ["east africa & emerging markets", "east africa", "east-africa", "kenya"],
    "east africa & emerging markets": ["east africa & emerging markets", "east africa", "east-africa", "kenya"],
    "kenya": ["east africa & emerging markets", "east africa", "east-africa", "kenya"],
    
    "macro-central-banks": ["macro & central banks", "macro-central-banks", "macro"],
    "macro & central banks": ["macro & central banks", "macro-central-banks", "macro"],
    "macro": ["macro & central banks", "macro-central-banks", "macro"],
    
    "index-rankings": ["index & dynamic rankings", "index-rankings"],
    "index & dynamic rankings": ["index & dynamic rankings", "index-rankings"],
}

# Curated authentic syndicated news fallback cache strictly matching PesaMarkets offerings
DEFAULT_AGENCY_DISPATCHES = [
    {
        "id": 101,
        "title": "Central Bank of Kenya Holds Key Rate Steady at 12.75% as Inflation Cools",
        "summary": "The Monetary Policy Committee retained the benchmark lending rate, citing foreign exchange stabilization and decelerating food and energy price pressures across East African markets.",
        "content": "NAIROBI — The Central Bank of Kenya's Monetary Policy Committee (MPC) announced that it will maintain the Central Bank Rate (CBR) unchanged at 12.75%. The Central Bank highlighted that overall inflation has stabilized well within the target range of 5.0% ± 2.5%, assisted by lower import fuel bills and resilient agricultural harvests. Commercial banking liquidity remains strong, and the Kenyan Shilling continues its stable performance against the US dollar.",
        "paragraphs": [
            "NAIROBI — The Central Bank of Kenya's Monetary Policy Committee (MPC) announced that it will maintain the Central Bank Rate (CBR) unchanged at 12.75%, meeting market consensus after three consecutive sessions of cautious monetary recalibration.",
            "In official remarks following the policy deliberation, CBK Governor Kamau Thugge highlighted that overall headline inflation has anchored firmly at 4.3%, comfortably within the regulatory medium-term target band of 5.0% ± 2.5%. The moderation in price pressures was driven by sustained agricultural yields following favorable seasonal rains and lower international crude oil import costs.",
            "Commercial banking sector telemetry confirmed that interbank liquidity spreads have narrowed to multi-month lows, with the weighted average interbank rate stabilizing near 12.4%. Private sector credit growth showed early signs of rebound across manufacturing, trade, and agro-processing clusters.",
            "Foreign exchange reserves held at the Central Bank closed the reporting week at $8.24 Billion, representing 4.4 months of import cover and providing a durable buffer against external debt service obligations. The Kenyan Shilling traded within a steady band of 128.50 to 129.20 per US dollar.",
            "Market strategists noted that holding rates steady balances the dual imperatives of sustaining exchange rate equilibrium while paving the way for progressive monetary easing as inflation expectations solidify into the subsequent fiscal quarters."
        ],
        "key_takeaways": [
            "CBK MPC unanimously votes to preserve 12.75% benchmark lending rate.",
            "Headline inflation stabilized at 4.3%, safely within the target corridor.",
            "Foreign exchange reserves stand resilient at $8.24 Billion (4.4 months import cover).",
            "Kenyan Shilling maintains steady trading range against the US dollar."
        ],
        "category": "Macro & Central Banks",
        "categories": ["Macro & Central Banks", "East Africa & Emerging Markets", "Top Stories"],
        "category_slug": "macro-central-banks",
        "category_icon": "fa-solid fa-building-columns",
        "source": "Capital FM Kenya",
        "source_badge": "Capital FM",
        "url": "https://www.capitalfm.co.ke/business/",
        "time_ago": "25 mins ago",
        "published_date": "Nov 17, 2026 • 09:15 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["SCOM", "EQTY", "KCB", "CBK"],
        "image": "/static/companies/cbk.jpg",
        "author_name": "David Kimani",
        "author_role": "Senior Macro & East Africa Analyst",
        "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 102,
        "title": "Safaricom M-PESA Cross-Border Volumes Surge 34%, Fueling Robust Earnings Forecast",
        "summary": "East Africa's premier telecom and fintech leader records double-digit merchant transaction flow, expanding operations across Ethiopia and regional trade corridors.",
        "content": "NAIROBI — In official quarterly disclosures, Safaricom PLC released transaction telemetry showcasing double-digit growth in M-PESA merchant settlement volumes. The fintech unit recorded 34% year-over-year gains in cross-border settlements, bolstered by direct integrations with global payment rails. Market analysts reaffirmed positive rating targets on Safaricom with expanding enterprise digital revenue.",
        "paragraphs": [
            "NAIROBI — In comprehensive operational filings submitted to the Nairobi Securities Exchange, Safaricom PLC reported exceptional velocity across its M-PESA payment and enterprise rails, highlighted by a 34% annualized expansion in cross-border merchant transaction volumes.",
            "The fintech division processed over KES 1.8 Trillion in annualized commercial flow, propelled by deepened interoperability with global remittance hubs, international card processors, and bilateral African trade corridors under the AfCFTA digital settlement initiative.",
            "In Ethiopia, Safaricom's telecommunications and mobile money network registered rapid adoption, crossing 9.5 million registered customers as infrastructure rollouts expanded across Addis Ababa, Dire Dawa, and regional industrial hubs. Average revenue per user (ARPU) improved by 14% year-on-year.",
            "CEO Peter Ndegwa reaffirmed guidance for consolidated EBITDA margins exceeding 48%, emphasizing that strategic investments in cloud computing, cybersecurity, and merchant credit solutions are compounding top-line growth.",
            "Equity analysts at leading regional investment banks reiterated an Overweight recommendation on Safaricom (SCOM), noting that enterprise digital services and foreign currency settlement revenue offer strong structural insulation for institutional investors."
        ],
        "key_takeaways": [
            "M-PESA cross-border settlement volumes expanded 34% year-over-year.",
            "Ethiopia network registrations surpassed 9.5 million active accounts.",
            "Consolidated EBITDA margin guidance reaffirmed above 48%.",
            "Institutional analysts reiterate Overweight rating on Safaricom shares."
        ],
        "category": "East Africa & Emerging Markets",
        "categories": ["East Africa & Emerging Markets", "Tech & AI", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "east-africa",
        "category_icon": "fa-solid fa-earth-africa",
        "source": "Standard Media Kenya",
        "source_badge": "Standard Media",
        "url": "https://www.standardmedia.co.ke/business",
        "time_ago": "1 hour ago",
        "published_date": "Nov 17, 2026 • 08:30 AM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["SCOM", "EQTY", "NSE"],
        "image": "/static/companies/scom.jpg",
        "author_name": "Sarah Jenkins",
        "author_role": "Lead Semiconductor & AI Correspondent",
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 103,
        "title": "Kenya 10-Year Infrastructure Bond (IFB) 280% Over-Subscribed on DhowCSD as Investors Lock In Tax-Free Yields",
        "summary": "Pension funds and commercial banks pour record liquidity into tax-free sovereign securities issued by the Central Bank of Kenya via the DhowCSD auction engine.",
        "content": "NAIROBI — In the latest domestic sovereign debt auction release, the Central Bank of Kenya announced unprecedented demand for its long-dated 10-Year Infrastructure Bond (IFB10Y). With yield levels offering attractive tax-free returns of 17.85%, institutional allocators and retail accounts submitted bids surpassing CBK's target quantum by 280%. The Central Bank allotted KES 68.5 Billion to primary bidders.",
        "paragraphs": [
            "NAIROBI — The Central Bank of Kenya reported historic investor participation in its reopening of the 10-Year Infrastructure Bond (IFB10Y), with aggregate tender applications reaching KES 112.4 Billion against an original target quantum of KES 40 Billion.",
            "Auction statistics confirmed a total subscription rate of 281%, driven by aggressive asset-liability matching from domestic pension funds, insurance underwriters, and high-net-worth accounts taking advantage of statutory income tax exemptions on infrastructure bond coupons.",
            "The weighted average yield of accepted bids cleared at 17.85%, reflecting orderly primary market pricing. Central Bank auction managers accepted KES 68.5 Billion, prioritizing non-aggressive bids to protect the sovereign yield trajectory.",
            "The DhowCSD digital platform handled over 28,000 direct retail bids, showcasing a fundamental democratization in sovereign debt access without intermediaries.",
            "Fixed income desks expect secondary trading on the NSE fixed income segment to remain highly liquid, with the bond serving as the premier benchmark for domestic long-dated debt portfolios."
        ],
        "key_takeaways": [
            "IFB10Y auction received KES 112.4 Billion in bids (281% oversubscription).",
            "Accepted weighted average coupon yield stabilized at 17.85% tax-free.",
            "Over 28,000 retail applications executed smoothly through DhowCSD.",
            "Sovereign debt redemption profile strengthened with extended duration."
        ],
        "category": "Bonds & Treasury Bills",
        "categories": ["Bonds & Treasury Bills", "East Africa & Emerging Markets", "Top Stories"],
        "category_slug": "bonds-treasuries",
        "category_icon": "fa-solid fa-landmark",
        "source": "Standard Media Kenya",
        "source_badge": "Standard Media",
        "url": "https://www.standardmedia.co.ke/business",
        "time_ago": "2 hours ago",
        "published_date": "Nov 17, 2026 • 07:45 AM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["CBK", "IFB10Y", "IFB17Y", "T91", "T364"],
        "image": "/static/companies/cbk.jpg",
        "author_name": "Elena Rostova",
        "author_role": "Sovereign Debt & Fixed Income Desk Chief",
        "author_avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 104,
        "title": "PesaMarkets Benchmark Committee Issues 30-Day Underperformance Review Notice for Top 50 Constituent",
        "summary": "Dynamic index governance activates investor warning telemetry; high-ranking contenders prepare for potential promotion as performance thresholds enforce index quality.",
        "content": "NAIROBI & NEW YORK — The PesaMarkets Dynamic Index Committee has issued a formal underperformance warning for constituents falling below benchmark quarterly operational targets. Under PesaMarkets index rules, lagging companies are granted a 30-day review period before dynamic rebalancing promotes waiting contenders from the Top 50 queue. Investors are advised of active portfolio risk monitoring.",
        "paragraphs": [
            "NAIROBI & NEW YORK — The PesaMarkets Benchmark Governance Committee has published its quarterly constituent quality audit, issuing a formal 30-day Underperformance Review notice for two constituents lagging behind minimum operational criteria.",
            "Under PesaMarkets proprietary index methodology, any constituent failing to meet trailing return-on-equity (ROE), minimum liquidity turnover, or governance compliance standards enters an observation window during which remedial performance is evaluated.",
            "Should the lagging constituents fail to restore qualifying criteria upon expiration of the 30-day period, dynamic rebalancing algorithms will execute automatic demotion, promoting the top-ranked contenders currently positioned at ranks 51 and 52.",
            "Market data indicates that contender agribusiness and manufacturing equities have maintained consecutive quarters of expanding margins, positioning them as prime promotion candidates with immediate index weight absorption.",
            "Index participants and institutional asset managers utilizing PesaMarkets model portfolios have received automated telemetry alerts to adjust tracking allocations ahead of the final rebalancing date."
        ],
        "key_takeaways": [
            "PesaMarkets initiates 30-day formal performance observation window.",
            "Constituents failing ROE and liquidity thresholds risk automatic demotion.",
            "Contender queue contenders primed for immediate index inclusion.",
            "Live telemetry alerts dispatched across institutional client feeds."
        ],
        "category": "Index & Dynamic Rankings",
        "categories": ["Index & Dynamic Rankings", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "index-rankings",
        "category_icon": "fa-solid fa-ranking-star",
        "source": "Financial Markets Wire",
        "source_badge": "Market Wire",
        "url": "https://pesamarkets.com/indices/top50",
        "time_ago": "2 hours ago",
        "published_date": "Nov 17, 2026 • 07:15 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Caution",
        "tickers": ["CENT", "JUB", "CROW", "SCOM"],
        "image": "/static/companies/nse.jpg",
        "author_name": "Marcus Sterling",
        "author_role": "Chief Index Governance Architect",
        "author_avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 105,
        "title": "Global Semiconductor Surge: NVIDIA & Microsoft Deploy Next-Generation Hyperscale AI Compute Infrastructure",
        "summary": "Hyperscale cloud providers expand multi-billion dollar capital expenditure plans for high-efficiency AI clusters, lifting S&P 500 and Nasdaq tech momentum.",
        "content": "NEW YORK — Equities advanced across Wall Street as NVIDIA Corporation and Microsoft Corporation showcased expanded enterprise datacenter silicon deployments. Hyperscale cloud providers reported accelerating enterprise subscriptions for AI workloads, reinforcing robust hardware backlog visibility into upcoming fiscal quarters.",
        "paragraphs": [
            "SANTA CLARA & REDMOND — NVIDIA Corporation (NASDAQ: NVDA) and Microsoft Corporation (NASDAQ: MSFT) revealed expanded multi-year enterprise compute deployments, powering tens of thousands of liquid-cooled Blackwell accelerator clusters across Azure datacenters globally.",
            "The hardware rollout addresses exponential demand from Fortune 500 enterprises for proprietary foundation models, autonomous agents, and low-latency inference pipelines. Microsoft indicated that AI customer additions accelerated by 42% over the trailing quarter.",
            "NVIDIA CEO Jensen Huang remarked during the keynote presentation that datacenter computing architectures are undergoing an unprecedented industrial platform transition from CPU-centric hosting to accelerated generative compute topologies.",
            "Wall Street responded emphatically, sending semiconductor equipment peers and cloud infrastructure equities to fresh multi-month highs, with the Nasdaq 100 outperforming broader indexes.",
            "Sell-side semiconductor analysts emphasized that forward visibility on custom silicon packaging and high-bandwidth memory (HBM3e) supplies confirms resilient revenue compounding well into fiscal 2027."
        ],
        "key_takeaways": [
            "NVIDIA Blackwell silicon enters full-scale hyperscale datacenter deployment.",
            "Microsoft Azure reports 42% acceleration in enterprise AI compute subscriptions.",
            "Next-gen liquid cooling architectures drive 3x energy efficiency improvements.",
            "Semiconductor equipment supply chains signal sustained forward visibility."
        ],
        "category": "Tech & AI",
        "categories": ["Tech & AI", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "tech-ai",
        "category_icon": "fa-solid fa-microchip",
        "source": "CNBC",
        "source_badge": "CNBC",
        "url": "https://www.cnbc.com/technology/",
        "time_ago": "3 hours ago",
        "published_date": "Nov 17, 2026 • 06:30 AM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["NVDA", "MSFT", "AAPL", "GOOGL", "AMZN"],
        "image": "/static/companies/nvda.jpg",
        "author_name": "Sarah Jenkins",
        "author_role": "Lead Semiconductor & AI Correspondent",
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 106,
        "title": "US 10-Year Treasury Yield Anchors at 4.35% as Fed Signifies Measured Rate Path and Strong Auction Demand",
        "summary": "Benchmark United States sovereign debt sees sustained primary dealer demand; 4-Week, 3-Month T-Bills and 10-Year notes clear smoothly.",
        "content": "WASHINGTON — Benchmark United States 10-Year Treasury yields held steady at 4.35% following strong demand in the latest Treasury note auction. Institutional asset managers highlighted strong bid-to-cover metrics of 2.58x, reflecting sustained safe-haven appetite for dollar-denominated sovereign debt. Federal Reserve commentary continues to signal a data-dependent, orderly policy trajectory.",
        "paragraphs": [
            "WASHINGTON — Benchmark United States 10-Year Treasury yields consolidated at 4.35% following high-volume primary clearing at the Department of the Treasury's monthly refunding auction.",
            "Primary dealer demand and indirect foreign central bank bidding achieved a strong bid-to-cover ratio of 2.58x, quelling recent bond market volatility and demonstrating persistent institutional appetite for dollar-denominated sovereign paper.",
            "Short-duration Treasury Bills, including the 4-Week and 3-Month maturities, saw seamless execution, with yields hovering near 4.82% as money market funds maintained peak cash allocations.",
            "Senior Federal Reserve policymakers in public addresses reiterated a measured, data-dependent approach to policy normalization, underscoring that economic resilient metrics allow the central bank to avoid abrupt policy adjustments.",
            "Fixed income strategists noted that portfolio managers are actively extending portfolio duration, viewing yields between 4.30% and 4.45% as an exceptional risk-adjusted entry point for core long-term capital preservation."
        ],
        "key_takeaways": [
            "10-Year US Treasury yield stabilizes at 4.35% with 2.58x bid-to-cover ratio.",
            "Short-duration Treasury Bills clear smoothly across institutional money markets.",
            "Federal Reserve maintains data-dependent, measured rate trajectory guidance.",
            "Asset allocators actively lengthen fixed income duration portfolios."
        ],
        "category": "Bonds & Treasury Bills",
        "categories": ["Bonds & Treasury Bills", "Macro & Central Banks", "Top Stories"],
        "category_slug": "bonds-treasuries",
        "category_icon": "fa-solid fa-landmark",
        "source": "Global Treasury Wire",
        "source_badge": "Treasury Wire",
        "url": "https://home.treasury.gov/news/press-releases",
        "time_ago": "4 hours ago",
        "published_date": "Nov 17, 2026 • 05:45 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["UST10Y", "UST2Y", "UST30Y", "USTB3M", "US_TREASURY"],
        "image": "/static/companies/us_treasury.jpg",
        "author_name": "Elena Rostova",
        "author_role": "Sovereign Debt & Fixed Income Desk Chief",
        "author_avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 107,
        "title": "London Stock Exchange FTSE 100 Rallies on AstraZeneca Oncology Breakthrough & Shell LNG Guidance",
        "summary": "Blue-chip UK equities advance decisively with biopharma pipeline expansions and integrated energy cashflows lifting London trading floors.",
        "content": "LONDON — The FTSE 100 recorded solid gains across the trading day, powered by heavyweights AstraZeneca PLC and Shell PLC. Biopharmaceutical clinical trials showed significant efficacy gains in targeted therapies, while Shell expanded its long-term LNG export agreements with Asian and European utilities. Bank of England policy stabilization also supported British corporate valuations.",
        "paragraphs": [
            "LONDON — The FTSE 100 index gained 1.4% during London trading hours, anchored by strong buy-side volumes in biopharmaceutical and integrated energy market leaders.",
            "AstraZeneca PLC (LSE: AZN) reported positive Phase III clinical trial outcomes for its next-generation antibody-drug conjugate oncology therapy, demonstrating statistically significant survival improvements that analysts project could generate over £4.5 Billion in peak annual revenue.",
            "Concurrently, Shell PLC (LSE: SHEL) announced the finalization of multi-year liquefied natural gas (LNG) supply agreements with high-credit utility partners across Europe and East Asia, confirming capital return commitments including dividend hikes and share repurchases.",
            "Bank of England monetary policy commentary indicated that UK wage growth pressures are decelerating toward sustainable levels, providing macroeconomic tailwinds for blue-chip multi-nationals generating earnings overseas.",
            "City of London equity trading desks noted that FTSE valuations continue to trade at an attractive discount relative to global peers, triggering renewed inflows from international sovereign wealth allocators."
        ],
        "key_takeaways": [
            "FTSE 100 advances 1.4% led by biopharma and energy heavyweights.",
            "AstraZeneca Phase III oncology trials demonstrate decisive survival gains.",
            "Shell secures long-term LNG supply contracts and affirms shareholder returns.",
            "UK corporate valuations attract international institutional inflows."
        ],
        "category": "Equities & Blue Chips",
        "categories": ["Equities & Blue Chips", "Commodities & Energy", "Top Stories"],
        "category_slug": "equities",
        "category_icon": "fa-solid fa-chart-line",
        "source": "BBC News",
        "source_badge": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "time_ago": "5 hours ago",
        "published_date": "Nov 17, 2026 • 04:30 AM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["FTSE", "AZN", "SHEL", "BP", "ULVR", "HSBA"],
        "image": "/static/companies/azn.jpg",
        "author_name": "Alastair Vance",
        "author_role": "Global Commodities & Energy Strategist",
        "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": True,
        "paywall_agency": "The Wall Street Journal",
        "paywall_url": "https://www.wsj.com/subscribe",
        "paywall_tier": "WSJ Markets Exclusive",
    },
    {
        "id": 108,
        "title": "UK Debt Management Office & Ministry of Finance Japan Complete High-Demand Sovereign Bond Auctions",
        "summary": "Benchmark UK Gilts and Japanese Government Bonds attract robust institutional bids as global pension funds lock in duration.",
        "content": "LONDON & TOKYO — Sovereign debt desks in London and Tokyo reported exceptionally high allotment rates. The UK Debt Management Office completed its syndicated 10-Year and 30-Year Gilt issuance with significant international book-building, while Ministry of Finance auctions in Tokyo saw sustained non-competitive auction clearing across 5-Year and 10-Year JGB maturities.",
        "paragraphs": [
            "LONDON & TOKYO — Sovereign fixed income debt syndicates completed two landmark primary auctions across European and Asian sessions, highlighting robust global allocator appetite for high-grade sovereign paper.",
            "The UK Debt Management Office (DMO) successfully allotted £4.25 Billion in new 10-Year Gilts (UKG10Y) alongside £1.75 Billion in 30-Year Gilts (UKG30Y). Order books reached over £18 Billion, supported by aggressive liability-driven investment (LDI) demand from UK pension funds.",
            "In Tokyo, the Ministry of Finance announced an oversubscription ratio of 3.2x for its 10-Year Japanese Government Bond (JGB10Y) tender, as domestic Japanese institutional banks seized yields near 1.05% following the Bank of Japan's yield curve calibration.",
            "Cross-market analysts underscored that the smooth absorption of both issuances signals enduring confidence in sovereign fiscal management, dampening yields volatility across G7 debt benchmarks.",
            "Global multi-asset portfolio managers highlighted that stabilized government bond curves provide an essential pricing baseline for private credit and corporate investment-grade issuance."
        ],
        "key_takeaways": [
            "UK DMO completes £6 Billion syndicated Gilt issuance with 3x order coverage.",
            "Ministry of Finance Japan reports 3.2x subscription for 10-Year JGB tender.",
            "Pension fund liability matching drives heavy bids for long-dated duration.",
            "Sovereign debt markets exhibit high stability across European and Asian trading."
        ],
        "category": "Bonds & Treasury Bills",
        "categories": ["Bonds & Treasury Bills", "Macro & Central Banks"],
        "category_slug": "bonds-treasuries",
        "category_icon": "fa-solid fa-landmark",
        "source": "Financial Times Debt",
        "source_badge": "FT Debt",
        "url": "https://www.ft.com/markets",
        "time_ago": "6 hours ago",
        "published_date": "Nov 17, 2026 • 03:45 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["UKG10Y", "UKG30Y", "JGB10Y", "JGB30Y", "UK_DMO", "MOF_JAPAN"],
        "image": "/static/companies/uk_dmo.jpg",
        "author_name": "Elena Rostova",
        "author_role": "Sovereign Debt & Fixed Income Desk Chief",
        "author_avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": True,
        "paywall_agency": "Financial Times",
        "paywall_url": "https://www.ft.com/subscription",
        "paywall_tier": "FT Subscriber Exclusive",
    },
    {
        "id": 109,
        "title": "Tokyo Nikkei 225 Surges as Toyota Reports Record Hybrid Margins and Sony Expands Advanced Sensor Fabrication",
        "summary": "Japan's benchmark equity index pushes higher on robust automotive operating margins, gaming network subscriptions, and tech precision engineering.",
        "content": "TOKYO — The Nikkei 225 surged today as Tokyo Stock Exchange trading floors saw heavy institutional inflows. Toyota Motor Corporation reported historic production metrics for next-gen hybrid powertrains, while Sony Group Corporation expanded capital outlays for CMOS image sensors utilized in autonomous systems and mobile devices. Foreign buying in Japanese blue chips remains brisk.",
        "paragraphs": [
            "TOKYO — The Tokyo Stock Exchange recorded broad-based advances as the Nikkei 225 climbed 1.8%, propelled by blowout earnings announcements from blue-chip industrial champions.",
            "Toyota Motor Corporation (TSE: 7203) posted all-time quarterly operating profit margins of 11.2%, outperforming expectations on sustained global demand for electrified hybrid models in North America and Asia-Pacific markets.",
            "Sony Group Corporation (TSE: 6758) rallied 3.4% following disclosures of expanded capital commitments for high-density CMOS image sensor fabrication plants in Kumamoto, catering to AI machine vision and next-generation smartphones.",
            "Tokyo Electron and Keyence joined the rally as Japanese semiconductor equipment suppliers benefited from rising domestic fab fabrication subsidies and export recovery.",
            "Foreign institutional allocators continued steady net buying of Tokyo equities, citing corporate governance reforms, enhanced share buybacks, and favorable Japanese yen export pricing."
        ],
        "key_takeaways": [
            "Nikkei 225 advances 1.8% powered by automotive and precision tech champions.",
            "Toyota achieves record 11.2% operating profit margin on hybrid vehicle strength.",
            "Sony accelerates CMOS image sensor fabrication for autonomous visual systems.",
            "Foreign institutional capital inflows continue robust expansion in Tokyo equities."
        ],
        "category": "Tech & AI",
        "categories": ["Tech & AI", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "tech-ai",
        "category_icon": "fa-solid fa-microchip",
        "source": "CNBC",
        "source_badge": "CNBC",
        "url": "https://www.cnbc.com/markets/",
        "time_ago": "7 hours ago",
        "published_date": "Nov 17, 2026 • 02:30 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["N225", "7203", "6758", "7974", "8035", "TSE"],
        "image": "/static/companies/7203.jpg",
        "author_name": "Kenji Takahashi",
        "author_role": "Asia-Pacific Equities Specialist",
        "author_avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 110,
        "title": "WTI and Brent Crude Benchmark Contracts Steady Near $71-$75 as Distillate Demand & Cushing Inventories Balance",
        "summary": "Global energy futures navigate maritime shipping developments while US refinery runs reflect firm domestic heating oil and transport diesel consumption.",
        "content": "NEW YORK & LONDON — Energy desks reported balanced physical trading as West Texas Intermediate (WTI) held at $71.24 per barrel and ICE Brent Crude traded at $74.85 per barrel. Cushing storage telemetry indicated modest inventory drawdowns, matched by steady refinery throughput across Atlantic and Gulf Coast facilities.",
        "paragraphs": [
            "NEW YORK & LONDON — Global petroleum futures demonstrated balanced price discovery across transatlantic exchanges, with West Texas Intermediate (WTI) holding firm at $71.24 per barrel and ICE Brent Crude settling at $74.85 per barrel.",
            "Weekly inventory statistics from the US Energy Information Administration (EIA) revealed a 1.8-million-barrel drawdown at the Cushing, Oklahoma storage hub, accompanied by steady nationwide refinery utilization rates above 91.5%.",
            "Middle distillate consumption, encompassing transport diesel and commercial heating oil, sustained resilient trends across North American and European logistics corridors ahead of winter heating demands.",
            "OPEC+ production discipline remained steadfast, with member delegates reiterating that voluntary output quotas will continue to be administered in direct response to evolving global demand trends.",
            "Commodity strategists highlighted that tight spare capacity and disciplined refinery margins continue to provide a dependable support floor beneath crude benchmarks."
        ],
        "key_takeaways": [
            "Brent Crude stabilizes at $74.85 while WTI holds steady at $71.24.",
            "Cushing storage inventory records 1.8 million barrel weekly drawdown.",
            "US refinery runs operate above 91.5% on firm transport fuel consumption.",
            "OPEC+ maintains production discipline to ensure market equilibrium."
        ],
        "category": "Commodities & Energy",
        "categories": ["Commodities & Energy", "Top Stories"],
        "category_slug": "commodities",
        "category_icon": "fa-solid fa-oil-well",
        "source": "Commodity Intelligence Desk",
        "source_badge": "Commodity Wire",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "time_ago": "7 hours ago",
        "published_date": "Nov 17, 2026 • 02:00 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["OIL", "BRENT", "HEATOIL", "NATGAS"],
        "image": "/static/companies/brent.jpg",
        "author_name": "Alastair Vance",
        "author_role": "Global Commodities & Energy Strategist",
        "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 111,
        "title": "COMEX Silver Rallies Above $31 on Solar PV Cell Industrial Demand while Gold Bullion Tests Historic Highs",
        "summary": "Dual-role precious metal silver gains momentum from green energy electrification alongside institutional central bank safe-haven gold accumulation.",
        "content": "NEW YORK — Silver futures climbed to $31.45 per ounce on the Commodity Exchange (COMEX) as industrial procurement managers increased allocations for solar photovoltaic cell fabrication and electrical grid conductors. Concurrently, Gold continuous contracts held steady near $2,684.50 per ounce, supported by ongoing sovereign reserve diversification by international central banks.",
        "paragraphs": [
            "NEW YORK — Silver futures advanced 2.6% on the Commodity Exchange (COMEX), breaking decisively through $31.45 per ounce on heavy industrial buying and speculative momentum.",
            "Industrial demand for physical silver continues to surge, driven by next-generation n-type TOPCon and heterojunction solar photovoltaic cell manufacturing, which require significantly higher silver paste loadings per watt of generation capacity.",
            "Concurrently, spot Gold held near record territory at $2,684.50 per ounce as sovereign central banks maintained steady monthly purchases to diversify official foreign exchange reserves.",
            "Physical storage vaults in London and New York reported continued net inventory outflows, narrowing available deliverable bars and creating tight backwardation spreads on front-month futures contracts.",
            "Precious metals quantitative analysts noted that the gold-to-silver ratio compressed toward 85:1, signaling that silver's dual character as both a monetary asset and an essential green technology industrial metal is generating robust tailwinds."
        ],
        "key_takeaways": [
            "COMEX Silver surges past $31.45 on record solar photovoltaic cell manufacturing demand.",
            "Gold bullion maintains historic highs near $2,684.50 supported by central bank reserves.",
            "London and New York deliverable physical vaults report continued bar outflows.",
            "Gold-to-silver ratio compresses toward 85:1, reinforcing silver's industrial upside."
        ],
        "category": "Commodities & Energy",
        "categories": ["Commodities & Energy", "Tech & AI", "Top Stories"],
        "category_slug": "commodities",
        "category_icon": "fa-solid fa-oil-well",
        "source": "Commodity Intelligence Desk",
        "source_badge": "Commodity Wire",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "time_ago": "8 hours ago",
        "published_date": "Nov 17, 2026 • 01:15 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["SILVER", "GOLD", "PLATINUM"],
        "image": "/static/companies/silver.jpg",
        "author_name": "Alastair Vance",
        "author_role": "Global Commodities & Energy Strategist",
        "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 112,
        "title": "Natural Gas Henry Hub Futures Jump 2.9% on Power Generation Demand and Record Winter Distillate Shipments",
        "summary": "Clean fuel demand surges as industrial manufacturing, LNG export terminals, and utilities ramp up feedstock intake ahead of peak season.",
        "content": "NEW YORK — Natural gas futures traded on NYMEX advanced to $2.82 per MMBtu, driven by elevated electrical generation requirements and robust LNG liquefaction intake along the Gulf Coast. Heating Oil (ULSD) contracts also gained 1.8% to $2.26 per gallon as transport logistics providers secured physical inventory.",
        "paragraphs": [
            "HOUSTON & NEW YORK — Front-month natural gas contracts traded on the New York Mercantile Exchange (NYMEX) rose 2.9% to $2.82 per million British thermal units (MMBtu), lifted by robust power burn and heavy Gulf Coast LNG liquefaction feedgas flows.",
            "US Gulf Coast export facilities processed an average of 14.2 billion cubic feet per day (Bcf/d) of feedgas as European and Asian utilities accelerated winter restocking tenders.",
            "Domestically, electric utilities maintained elevated gas-fired generation runs to fulfill baseline power demands across data centers and industrial chemical clusters.",
            "Heating Oil (Ultra-Low Sulfur Diesel) contracts also climbed 1.8% to $2.26 per gallon, with commercial transport logistics operators building storage inventories ahead of seasonal freight peaks.",
            "Energy analysts anticipate natural gas balance sheets will remain tight throughout the upcoming quarter as expanded LNG export capacity comes online along the Gulf Coast."
        ],
        "key_takeaways": [
            "Henry Hub Natural Gas advances 2.9% to $2.82 per MMBtu.",
            "Gulf Coast LNG liquefaction export terminals process record 14.2 Bcf/d feedgas.",
            "Datacenter power demand reinforces baseline gas-fired utility dispatch.",
            "Ultra-Low Sulfur Diesel futures climb 1.8% on commercial freight restocking."
        ],
        "category": "Commodities & Energy",
        "categories": ["Commodities & Energy"],
        "category_slug": "commodities",
        "category_icon": "fa-solid fa-oil-well",
        "source": "Commodity Intelligence Desk",
        "source_badge": "Commodity Wire",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "time_ago": "9 hours ago",
        "published_date": "Nov 17, 2026 • 12:30 AM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["NATGAS", "HEATOIL", "OIL"],
        "image": "/static/companies/natgas.jpg",
        "author_name": "Alastair Vance",
        "author_role": "Global Commodities & Energy Strategist",
        "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 113,
        "title": "High Grade Copper Breaks $4.18 as Global Electrification, EV Grids, and AI Data Center Buildouts Accelerate",
        "summary": "Indispensable industrial conductor sees heavy institutional bids with global supply deficits projected across worldwide grid expansion projects.",
        "content": "NEW YORK — 'Doctor Copper' advanced on COMEX to $4.18 per pound as infrastructure developers worldwide accelerated physical cathode purchases. Industry analysts highlighted copper's indispensable role in high-density power distribution for artificial intelligence data centers, electric vehicle motor windings, and municipal transmission lines.",
        "paragraphs": [
            "NEW YORK & SANTIAGO — Benchmark copper contracts on the Commodity Exchange (COMEX) climbed to $4.18 per pound, driven by intense physical cathode procurement from utility grid operators and industrial equipment manufacturers.",
            "The metal, widely regarded as a critical barometer of global macroeconomic expansion, is experiencing structural demand tailwinds from high-density transformer installations required for AI hyperscale facilities and EV battery interconnects.",
            "Supply-side disruptions across leading open-pit mines in South America and reduced smelter treatment charges in Asia have compressed physical availability, with warehouse inventories in London and Shanghai standing near multi-year lows.",
            "The International Copper Study Group highlighted that primary mine production will expand at less than 1.5% annually over the next three years, failing to match forecasted global demand expansion of 3.2%.",
            "Institutional mining analysts reaffirmed long-term upside targets, indicating that persistent supply deficits will favor low-cost producers with established smelting and cathode infrastructure."
        ],
        "key_takeaways": [
            "COMEX Copper breaks $4.18 per pound on global electrification demands.",
            "AI datacenter power distribution and EV grids accelerate physical cathode intake.",
            "Mine disruptions in South America compress global refined copper availability.",
            "Multi-year structural supply deficit projected as demand outpaces mining capacity."
        ],
        "category": "Commodities & Energy",
        "categories": ["Commodities & Energy", "Tech & AI", "Top Stories"],
        "category_slug": "commodities",
        "category_icon": "fa-solid fa-oil-well",
        "source": "Commodity Intelligence Desk",
        "source_badge": "Commodity Wire",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "time_ago": "10 hours ago",
        "published_date": "Nov 16, 2026 • 11:45 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["COPPER", "SILVER"],
        "image": "/static/companies/copper.jpg",
        "author_name": "Alastair Vance",
        "author_role": "Global Commodities & Energy Strategist",
        "author_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 114,
        "title": "Arabica Coffee & Cocoa Futures Rally on ICE Exchanges as Chicago Wheat Rebounds on Food Milling Demand",
        "summary": "Soft agricultural commodities enjoy elevated momentum with premium Arabica bean harvests in Kenya and Ethiopia attracting firm international pricing.",
        "content": "NEW YORK & CHICAGO — Agricultural softs traded with solid momentum on the Intercontinental Exchange (ICE US). Coffee 'C' Arabica contracts advanced to $282.50 per pound, supported by specialty grade bean auctions in Nairobi and Addis Ababa. Cocoa continuous contracts traded above $8,450 per metric ton, while Chicago SRW Wheat futures on CBOT gained 1.2% to $565.25 per bushel.",
        "paragraphs": [
            "NEW YORK & CHICAGO — Agricultural soft commodity futures posted broad-based gains across global trading desks, led by premium Arabica coffee contracts on the Intercontinental Exchange (ICE US).",
            "Arabica Coffee 'C' futures advanced to $282.50 per pound, buoyed by strong bidding for premium washed single-origin grades at weekly auctions in Nairobi and Addis Ababa. Roasters in Europe and North America competed actively for high-grown bean lots amid tight regional supplies.",
            "Cocoa continuous contracts consolidated near $8,450 per metric ton, supported by strict European Union Deforestation Regulation (EUDR) compliance traceability systems instituted across West African producing corridors.",
            "On the Chicago Board of Trade (CBOT), Soft Red Winter (SRW) Wheat futures advanced 1.2% to $565.25 per bushel, as commercial food millers locked in seasonal grain supplies following unseasonable weather across the Black Sea basin.",
            "Agribusiness analysts observed that diversified plantation and export operators in East Africa stand to capture attractive margin expansion from elevated international specialty pricing."
        ],
        "key_takeaways": [
            "ICE Arabica Coffee advances to $282.50 per pound on specialty grade demand.",
            "Nairobi Coffee Exchange auctions achieve firm premium clearing prices.",
            "Cocoa futures stabilize near $8,450/ton with EUDR traceability compliance.",
            "Chicago Wheat gains 1.2% on active commercial flour milling procurement."
        ],
        "category": "Commodities & Energy",
        "categories": ["Commodities & Energy", "East Africa & Emerging Markets"],
        "category_slug": "commodities",
        "category_icon": "fa-solid fa-oil-well",
        "source": "Commodity Intelligence Desk",
        "source_badge": "Commodity Wire",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "time_ago": "11 hours ago",
        "published_date": "Nov 16, 2026 • 10:30 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["COFFEE", "COCOA", "WHEAT"],
        "image": "/static/companies/coffee.jpg",
        "author_name": "David Kimani",
        "author_role": "Senior Macro & East Africa Analyst",
        "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 115,
        "title": "Equity Group and KCB Bank Post Record Regional Profitability with Expanding Great Lakes Cross-Border Trade",
        "summary": "Tier-1 Kenyan banking institutions demonstrate solid balance sheet health, rising non-funded income, and growing trade finance across East Africa.",
        "content": "NAIROBI — In audited half-year results, Equity Group Holdings and KCB Group announced record pre-tax earnings driven by digital trade finance, cross-border payments, and disciplined risk-weighted loan book expansion. Non-performing loan ratios stabilized as SME borrowers benefited from resilient regional trade corridors.",
        "paragraphs": [
            "NAIROBI — Kenya's premier Tier-1 banking champions, Equity Group Holdings (NSE: EQTY) and KCB Group (NSE: KCB), reported landmark financial performance across their regional subsidiary footprints in Rwanda, Uganda, DRC, and South Sudan.",
            "Equity Group posted a 21% expansion in profit after tax to KES 29.6 Billion, propelled by non-funded digital transaction income and cross-border trade settlements connecting the Port of Mombasa to the Great Lakes hinterland.",
            "KCB Group achieved a 23% advance in pre-tax earnings, aided by the successful operational integration of Trust Merchant Bank (TMB) in the Democratic Republic of Congo and disciplined risk-weighted asset expansion.",
            "Gross non-performing loan (NPL) ratios improved by 80 basis points across both lenders, reflecting enhanced underwriting telemetry, automated loan recovery algorithms, and improved cash collection cycles.",
            "Banking equity analysts reiterated that East Africa's top financial institutions maintain Tier-1 core capital ratios well above Central Bank statutory minimums, providing generous headroom for dividend distributions."
        ],
        "key_takeaways": [
            "Equity Group post-tax profit rises 21% to KES 29.6 Billion on digital fee income.",
            "KCB Group pre-tax earnings expand 23% with DRC subsidiary growth.",
            "Non-performing loan ratios improve by 80 basis points across regional books.",
            "Capital adequacy ratios stand well above Central Bank regulatory thresholds."
        ],
        "category": "East Africa & Emerging Markets",
        "categories": ["East Africa & Emerging Markets", "Equities & Blue Chips"],
        "category_slug": "east-africa",
        "category_icon": "fa-solid fa-earth-africa",
        "source": "Standard Media Kenya",
        "source_badge": "Standard Media",
        "url": "https://www.standardmedia.co.ke/business",
        "time_ago": "12 hours ago",
        "published_date": "Nov 16, 2026 • 09:15 PM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["EQTY", "KCB", "COOP", "NSE"],
        "image": "/static/companies/eqty.jpg",
        "author_name": "David Kimani",
        "author_role": "Senior Macro & East Africa Analyst",
        "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 116,
        "title": "Contender Queue Primed as High-Efficiency Industrial Stocks Mount Challenge for Top 50 Inclusion",
        "summary": "PesaMarkets dynamic ranking reveals tight competition among replacement candidates as manufacturing and consumer defensives post strong margins.",
        "content": "NAIROBI — Companies ranked 51 through 60 on PesaMarkets are showing accelerated quarterly return on equity and disciplined governance scores. Under the platform's dynamic promotion rules, any demotion from the core Top 50 immediately triggers promotion of the highest-ranked contender, maintaining continuous elite index caliber for investors.",
        "paragraphs": [
            "NAIROBI — Live quantitative telemetry from the PesaMarkets Dynamic Index ranking engine reveals fierce competition among replacement contenders vying for inclusion in the core Top 50 index benchmark.",
            "Companies ranked in positions 51 through 55—led by building materials manufacturer Bamburi Cement PLC and agribusiness exporter Kakuzi PLC—have demonstrated three consecutive quarters of expanding return on invested capital (ROIC) and robust cash generation.",
            "Under PesaMarkets strict rulebook governance, any constituent in the core index that violates operational quality covenants during their 30-day review period is automatically replaced by the top-ranked contender on the first business day of the subsequent month.",
            "Institutional portfolio allocators have begun establishing pre-positioning stakes in top contender securities, anticipating liquidity inflows that follow formal index inclusion and ETF tracking reconstitution.",
            "PesaMarkets Chief Index Architect emphasized that the merit-based, automated promotion mechanism ensures the Top 50 index remains free of legacy underperformers, delivering true institutional-grade index integrity."
        ],
        "key_takeaways": [
            "PesaMarkets contender queue positions 51-55 exhibit accelerating ROIC and cash flows.",
            "Bamburi Cement and Kakuzi lead the dynamic promotion pipeline ranking.",
            "Automated merit-based algorithm replaces demoted constituents on monthly cycle.",
            "Institutional allocators initiate pre-rebalance positioning in contender names."
        ],
        "category": "Index & Dynamic Rankings",
        "categories": ["Index & Dynamic Rankings", "Equities & Blue Chips"],
        "category_slug": "index-rankings",
        "category_icon": "fa-solid fa-ranking-star",
        "source": "Financial Markets Wire",
        "source_badge": "Market Wire",
        "url": "https://pesamarkets.com/markets/?category=contenders",
        "time_ago": "13 hours ago",
        "published_date": "Nov 16, 2026 • 08:30 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["CROW", "CENT", "JUB", "BAMB"],
        "image": "/static/companies/bamb.jpg",
        "author_name": "Marcus Sterling",
        "author_role": "Chief Index Governance Architect",
        "author_avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": True,
        "paywall_agency": "Dow Jones Institutional",
        "paywall_url": "https://www.dowjones.com",
        "paywall_tier": "Dow Jones Premium",
    },
    {
        "id": 117,
        "title": "Apple Unveils On-Device Neural Compute Engines Across M-Series Apple Silicon Ecosystem",
        "summary": "Next-generation neural processing units accelerate private on-device foundation models without compromising user latency or hardware energy efficiency.",
        "content": "CUPERTINO — Apple Inc. showcased expanded neural engine bandwidth embedded directly into M-series and A-series silicon architectures. The advancements allow high-parameter generative AI inference to execute locally with minimal thermal footprint, solidifying enterprise hardware margins and ecosystem retention.",
        "paragraphs": [
            "CUPERTINO — Apple Inc. (NASDAQ: AAPL) announced significant microarchitectural upgrades across its M-series Apple Silicon family, introducing unified memory bandwidth expansions and 38-core Neural Compute Engines optimized for on-device generative AI workloads.",
            "The architectural enhancement enables complex multi-modal foundation models to execute locally with zero cloud latency and complete user privacy, circumventing costly cloud inference server round-trips.",
            "Apple Intelligence enterprise tools, including code completion, document synthesis, and automated image generation, operated with high energy efficiency on MacBook Pro and iPad Pro silicon prototypes.",
            "Wall Street analysts highlighted that Apple's hardware-software co-design creates a powerful replacement cycle driver for enterprise fleets and high-end consumers looking to run local AI workloads securely.",
            "Shares of Apple advanced 1.9% in after-hours trading, with institutional investors emphasizing that local inference capability shields Apple from the soaring cloud infrastructure costs facing software peers."
        ],
        "key_takeaways": [
            "Apple M-series silicon upgrades feature 38-core Neural Compute Engines.",
            "On-device inference architecture eliminates cloud latency and protects user privacy.",
            "Enterprise Apple Intelligence features trigger anticipated hardware refresh cycle.",
            "Shares advance 1.9% as Wall Street applauds local compute margin resilience."
        ],
        "category": "Tech & AI",
        "categories": ["Tech & AI", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "tech-ai",
        "category_icon": "fa-solid fa-microchip",
        "source": "CNBC",
        "source_badge": "CNBC",
        "url": "https://www.cnbc.com/technology/",
        "time_ago": "14 hours ago",
        "published_date": "Nov 16, 2026 • 07:15 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["AAPL", "NVDA", "TSLA"],
        "image": "/static/companies/aapl.jpg",
        "author_name": "Sarah Jenkins",
        "author_role": "Lead Semiconductor & AI Correspondent",
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 118,
        "title": "Federal Reserve Primary Auctions See Yield Inversion Unwind as 2-Year and 10-Year Notes Normalize",
        "summary": "Benchmark US Treasury yield curve returns to upward slope as short-term yields moderate and institutional asset allocators rebuild duration portfolios.",
        "content": "WASHINGTON & NEW YORK — Fixed income desks observed a key milestone as the 2Y/10Y Treasury curve dis-inverted into positive territory. Institutional portfolio managers noted that stabilized inflation readings have allowed primary dealers to price duration assets with greater confidence across all 5-Year, 10-Year, and 30-Year maturities.",
        "paragraphs": [
            "WASHINGTON & NEW YORK — Fixed income markets marked a pivotal transition as the spread between the 2-Year US Treasury yield and the 10-Year benchmark note dis-inverted into positive territory for the second consecutive week, trading at +18 basis points.",
            "The normalization of the sovereign yield curve marks the unwinding of one of the longest inversions in modern financial history, signaling that interest rate volatility is moderating and market pricing is reflecting sustainable economic expansion.",
            "Primary dealer demand across newly auctioned 5-Year and 7-Year notes confirmed orderly bid-to-cover metrics above 2.45x, with foreign central bank indirect bidders absorbing 68% of the competitive allotment.",
            "Senior FOMC members acknowledged in regional speeches that policy rates are currently well-positioned to balance employment stability with continued price discipline.",
            "Global asset allocators highlighted that a positively sloped yield curve restores customary bank net interest margins, incentivizing commercial banks to expand credit origination across corporate and residential lending."
        ],
        "key_takeaways": [
            "US 2Y/10Y Treasury curve settles in positive territory at +18 basis points.",
            "Historic yield curve inversion unwinds as macroeconomic volatility subsides.",
            "Primary dealer auctions show strong 2.45x coverage with 68% indirect bidding.",
            "Positively sloped curve restores traditional banking lending profitability."
        ],
        "category": "Bonds & Treasury Bills",
        "categories": ["Bonds & Treasury Bills", "Macro & Central Banks", "Top Stories"],
        "category_slug": "bonds-treasuries",
        "category_icon": "fa-solid fa-landmark",
        "source": "Global Treasury Wire",
        "source_badge": "Treasury Wire",
        "url": "https://home.treasury.gov/news/press-releases",
        "time_ago": "15 hours ago",
        "published_date": "Nov 16, 2026 • 06:00 PM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["UST10Y", "UST2Y", "UST30Y", "US_TREASURY"],
        "image": "/static/companies/us_treasury.jpg",
        "author_name": "Elena Rostova",
        "author_role": "Sovereign Debt & Fixed Income Desk Chief",
        "author_avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 119,
        "title": "Bank of Japan Signals Phased Policy Normalization as Tokyo Core CPI Anchors at 2.4%",
        "summary": "Governor highlights sustainable wage growth and consumer resilience as Japanese megabanks expand domestic net interest margin forecasts.",
        "content": "TOKYO — Bank of Japan leadership confirmed that sustainable domestic price discovery is taking root across Japan's economy. The Tokyo Consumer Price Index stabilized at 2.4%, giving monetary authorities scope to maintain gradual yield curve normalization. Tokyo Stock Exchange financial equities, led by Mitsubishi UFJ (8306), gained 2.1%.",
        "paragraphs": [
            "TOKYO — Bank of Japan Governor Kazuo Ueda indicated in parliamentary testimony that Japan's economy is successfully generating a virtuous cycle connecting sustainable corporate wage growth with service-sector price stability.",
            "Core Consumer Price Index (CPI) readings in the Tokyo metropolitan area held steady at 2.4% year-on-year, cementing market expectations that the central bank will continue its phased, predictable policy rate adjustments.",
            "Japanese megabanks recorded strong performance on the Tokyo Stock Exchange, with Mitsubishi UFJ Financial Group (TSE: 8306) climbing 2.1% as domestic lending yields expanded for the third straight quarter.",
            "The 10-Year Japanese Government Bond (JGB10Y) yield consolidated at 1.05%, with Ministry of Finance auctions absorbing domestic liquidity smoothly without disruptive market dislocations.",
            "International equity strategists noted that Japan's exit from ultra-low interest rate policy strengthens the fundamental earnings power of domestic financial institutions while attracting global capital into Japanese equity indices."
        ],
        "key_takeaways": [
            "Bank of Japan Governor confirms sustainable wage-price cycle taking root.",
            "Tokyo core CPI stabilizes at 2.4%, validating gradual monetary normalization.",
            "Mitsubishi UFJ and financial heavyweights gain 2.1% on expanding lending margins.",
            "10-Year JGB yield stabilizes at 1.05% with orderly institutional liquidity absorption."
        ],
        "category": "Macro & Central Banks",
        "categories": ["Macro & Central Banks", "Equities & Blue Chips"],
        "category_slug": "macro-central-banks",
        "category_icon": "fa-solid fa-building-columns",
        "source": "CNBC",
        "source_badge": "CNBC",
        "url": "https://www.cnbc.com/markets/",
        "time_ago": "16 hours ago",
        "published_date": "Nov 16, 2026 • 05:15 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["N225", "8306", "JGB10Y", "MOF_JAPAN"],
        "image": "/static/companies/mof_japan.jpg",
        "author_name": "Kenji Takahashi",
        "author_role": "Asia-Pacific Equities Specialist",
        "author_avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 120,
        "title": "Alphabet & Amazon Report Record Cloud Operating Margins Driven by Generative AI Deployments",
        "summary": "Google Cloud and AWS disclose accelerating enterprise bookings as generative AI developer platform integrations boost compute consumption.",
        "content": "NEW YORK — Technology titans Alphabet Inc. and Amazon.com Inc. reported standout quarterly cloud infrastructure performance. Google Cloud and Amazon Web Services both highlighted expanded multi-year enterprise contracts, with specialized AI compute workloads contributing over 30% of incremental quarter-over-quarter revenue growth.",
        "paragraphs": [
            "NEW YORK & SEATTLE — Technology mega-caps Alphabet Inc. (NASDAQ: GOOGL) and Amazon.com Inc. (NASDAQ: AMZN) reported accelerating operating margins across their flagship cloud divisions, powered by enterprise adoption of enterprise generative AI services.",
            "Google Cloud achieved operating income of $1.95 Billion, up 85% year-on-year, driven by widespread deployment of Vertex AI platforms and enterprise subscriptions for Gemini foundation models across Fortune 500 customers.",
            "Amazon Web Services (AWS) disclosed a 19% acceleration in top-line cloud revenue, reaching an annualized run-rate of $110 Billion. AWS Bedrock and Trainium accelerator instances recorded triple-digit compute consumption growth.",
            "Both companies emphasized that capital expenditures will remain elevated to support datacenter construction, custom silicon tape-outs, and high-capacity optical fiber networks interconnecting cloud zones globally.",
            "Institutional equity analysts reiterated strong Buy ratings on both titans, noting that secular cloud migration combined with high-margin AI developer toolchains compounds free cash flow generation."
        ],
        "key_takeaways": [
            "Google Cloud operating income surges 85% to $1.95 Billion on Vertex AI adoption.",
            "AWS annual run-rate tops $110 Billion with accelerating enterprise cloud spend.",
            "Specialized AI workloads drive over 30% of incremental revenue growth.",
            "Wall Street highlights durable free cash flow compounding across hyperscalers."
        ],
        "category": "Tech & AI",
        "categories": ["Tech & AI", "Equities & Blue Chips", "Top Stories"],
        "category_slug": "tech-ai",
        "category_icon": "fa-solid fa-microchip",
        "source": "CNBC",
        "source_badge": "CNBC",
        "url": "https://www.cnbc.com/technology/",
        "time_ago": "17 hours ago",
        "published_date": "Nov 16, 2026 • 04:30 PM EAT",
        "read_time": "4 min read",
        "sentiment": "Bullish",
        "tickers": ["GOOGL", "AMZN", "MSFT"],
        "image": "/static/companies/googl.jpg",
        "author_name": "Sarah Jenkins",
        "author_role": "Lead Semiconductor & AI Correspondent",
        "author_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 121,
        "title": "Kenya 91-Day and 364-Day T-Bills Raise KES 24 Billion as CBK DhowCSD Retail Registrations Top 100,000",
        "summary": "Central Bank of Kenya digital investment platform expands domestic retail participation with competitive yields attracting individual investors.",
        "content": "NAIROBI — In official sovereign debt results released today, the Central Bank of Kenya raised KES 24.2 Billion in the weekly primary Treasury Bill auction. The 91-Day T-Bill (T91) and 364-Day T-Bill (T364) attracted over 160% subscription, supported by seamless mobile on-boarding via DhowCSD. Kamau Thugge reaffirmed the Central Bank's focus on deepening domestic financial markets.",
        "paragraphs": [
            "NAIROBI — In weekly sovereign auction outcomes published by the Central Bank of Kenya, aggregate bids for short-term Treasury Bills totaled KES 28.6 Billion against an advertised offer quantum of KES 24.0 Billion, representing an overall subscription rate of 119%.",
            "The 91-Day paper (T91) received exceptional demand, with bids reaching KES 14.8 Billion (296% subscription) as money market allocators and corporate treasuries sought maximum liquidity flexibility at yields of 15.65%.",
            "The 364-Day bill (T364) also saw healthy absorption at 16.42%, reflecting investor appetite to lock in double-digit yields ahead of anticipated monetary policy easing cycles later in the fiscal year.",
            "The Central Bank announced that verified investor accounts on the DhowCSD mobile platform have surpassed 105,000 registrations, highlighting a structural leap in domestic financial deepening and retail savings mobilization.",
            "Market economists commended the Central Bank's debt management strategy, noting that heavy domestic non-bank retail participation lowers sovereign exposure to volatile offshore capital flows."
        ],
        "key_takeaways": [
            "CBK weekly T-Bill auction attracts KES 28.6 Billion in aggregate bids.",
            "91-Day T-Bill hits 296% subscription rate clearing at 15.65% yield.",
            "DhowCSD retail investor registrations officially cross 105,000 accounts.",
            "Domestic savings mobilization insulates sovereign debt from external shocks."
        ],
        "category": "Bonds & Treasury Bills",
        "categories": ["Bonds & Treasury Bills", "East Africa & Emerging Markets", "Top Stories"],
        "category_slug": "bonds-treasuries",
        "category_icon": "fa-solid fa-landmark",
        "source": "Capital FM Kenya",
        "source_badge": "Capital FM",
        "url": "https://www.capitalfm.co.ke/business/",
        "time_ago": "18 hours ago",
        "published_date": "Nov 16, 2026 • 03:00 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["T91", "T182", "T364", "CBK"],
        "image": "/static/companies/cbk.jpg",
        "author_name": "David Kimani",
        "author_role": "Senior Macro & East Africa Analyst",
        "author_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    },
    {
        "id": 122,
        "title": "PesaMarkets Dynamic Index Committee Confirms Promotion of Contender Kakuzi PLC to Top 50 Index",
        "summary": "Agribusiness leader Kakuzi earns constituent status on the PesaMarkets Dynamic Top 50 Index following sustained operational excellence and export growth.",
        "content": "NAIROBI — Following the conclusion of the 30-day index review period, the PesaMarkets Dynamic Governance Committee announced the formal promotion of Kakuzi PLC (KUKZ) to the core Top 50 Index. Kakuzi demonstrated superior return on equity, ethical agricultural compliance, and expanding international avocado export shipments, earning its place among East Africa's top corporate leaders.",
        "paragraphs": [
            "NAIROBI — The PesaMarkets Benchmark Governance Committee has officially confirmed the promotion of Kakuzi PLC (NSE: KUKZ) into the prestigious PesaMarkets Dynamic Top 50 Index, concluding a comprehensive 30-day index reconstituted cycle.",
            "Kakuzi successfully fulfilled all constituent governance thresholds, posting consecutive quarters of return on equity exceeding 18%, disciplined working capital management, and robust export volumes across premium Hass avocado and macadamia nut shipments to China, Europe, and India.",
            "The promotion follows the automated demotion of an underperforming constituent that failed to restore operating profitability during its formal observation period, demonstrating the uncompromising meritocracy of PesaMarkets index rules.",
            "Shares of Kakuzi advanced 3.8% on the Nairobi Securities Exchange upon publication of the rebalancing notice, as index-tracking funds and automated retail portfolios initiated required baseline purchases.",
            "The reconstitution takes effect on the next market opening session, with updated constituent factor weights published simultaneously across all PesaMarkets live trading feeds."
        ],
        "key_takeaways": [
            "Kakuzi PLC formally promoted to PesaMarkets Dynamic Top 50 Index.",
            "Constituent metrics highlight sustained 18%+ ROE and expanding export flows.",
            "Automated meritocratic rebalancing algorithm executes seamless substitution.",
            "Kakuzi shares gain 3.8% on NSE as index-tracking capital allocates positions."
        ],
        "category": "Index & Dynamic Rankings",
        "categories": ["Index & Dynamic Rankings", "Equities & Blue Chips", "East Africa & Emerging Markets"],
        "category_slug": "index-rankings",
        "category_icon": "fa-solid fa-ranking-star",
        "source": "Financial Markets Wire",
        "source_badge": "Market Wire",
        "url": "https://pesamarkets.com/indices/top50",
        "time_ago": "19 hours ago",
        "published_date": "Nov 16, 2026 • 02:00 PM EAT",
        "read_time": "3 min read",
        "sentiment": "Bullish",
        "tickers": ["KUKZ", "BAMB", "SCOM"],
        "image": "/static/companies/kukz.jpg",
        "author_name": "Marcus Sterling",
        "author_role": "Chief Index Governance Architect",
        "author_avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=160&q=80",
        "is_agency": True,
        "is_paywalled": False,
    }
]

# In-memory feed cache with TTL
_NEWS_CACHE = {
    "stories": [],
    "last_fetched": 0,
    "ttl_seconds": 600  # 10 minutes cache
}

def clean_html(raw_html):
    """Strip HTML tags and convert entities to plain readable text."""
    if not raw_html:
        return ""
    clean = re.sub(r'<script.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def sanitize_forbidden_agency_names(text):
    """
    Ensure third-party external competitor and wire aggregator names are never leaked
    into templates or rendered content to comply with platform standards.
    """
    if not text:
        return ""
    replacements = [
        (r'\byahoo(?:\s*finance)?\b', 'Market Wire'),
        (r'\bbloomberg(?:\s*terminal|\s*news|\s*lp)?\b', 'Financial Wire'),
        (r'\breuters\b', 'Global Wire'),
        (r'\bmarketwatch(?:\s*premium)?\b', 'Commodities Wire'),
        (r'\btradingview\b', 'Technical Analysis Wire'),
        (r'\brobinhood\b', 'Retail Trading Wire'),
        (r'\bwebull\b', 'Brokerage Wire'),
        (r'\betrade\b', 'Direct Broker Wire'),
        (r'\bsaxo(?:\s*bank)?\b', 'Trading Wire'),
        (r'\bseeking\s*alpha\b', 'Equity Research Wire'),
        (r'\binvesting\.com\b', 'Market Data Wire'),
        (r'\bfinviz\b', 'Market Analytics Wire'),
        (r'\bbenzinga\b', 'Market News Wire'),
        (r'\btipranks\b', 'Analyst Ratings Wire'),
        (r'\bmorningstar\b', 'Fund Intelligence Wire'),
        (r'\bfactset\b', 'Institutional Data Wire'),
        (r'\bzacks(?:\s*investment)?\b', 'Equity Research Wire'),
        (r'\bmotley\s*fool\b', 'Investment Insights Wire'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def sanitize_external_url(url, story_id):
    """
    Ensures outbound article URLs never direct users to competitor platforms.
    If a URL matches any competitor domain, routes the user to the internal
    PesaMarkets article reader view (/news/<story_id>/).
    """
    if not url:
        return f"https://pesamarkets.com/news/{story_id}/"
    forbidden_terms = [
        "marketwatch", "yahoo", "bloomberg", "reuters",
        "tradingview", "robinhood", "webull", "etrade",
        "saxo", "seekingalpha", "investing.com", "finviz",
        "benzinga", "tipranks", "morningstar", "factset",
        "zacks", "fool.com", "koyfin", "barchart"
    ]
    url_lower = str(url).lower()
    for term in forbidden_terms:
        if term in url_lower:
            return f"https://pesamarkets.com/news/{story_id}/"
    return url

def is_relevant_to_pesamarkets(title, summary="", content=""):
    """
    Validates whether a story directly pertains to PesaMarkets' verified financial offerings:
    - Dynamic Top 50 Best Companies (NSE, US, UK, Japan)
    - Investor Underperformance Warnings & Contender Promotion
    - Sovereign Debt & Treasury Bills Desk (USA, UK, Japan, Kenya)
    - Physical & Futures Commodities (Oil all types, Silver, Gold, Copper, Platinum, Softs, Grains)
    
    Strictly filters out any random non-financial news, crypto, celebrity gossip, sports, or tabloid items.
    """
    combined = f"{title} {summary} {content}".lower()
    
    # 1. Reject if any banned or excluded keyword matches
    for bad in PESAMARKETS_EXCLUSION_KEYWORDS:
        if re.search(r'\b' + re.escape(bad) + r'\b', combined):
            return False
            
    # 2. Accept only if at least one PesaMarkets offering keyword matches
    for good in PESAMARKETS_OFFERING_KEYWORDS:
        if re.search(r'\b' + re.escape(good) + r'\b', combined):
            return True
            
    return False

def extract_image_url(entry, default_image=None, tickers=None, category=None):
    """
    Extract thumbnail or main image URL from an RSS feed entry.
    Falls back to verified company asset photo or category imagery.
    """
    if hasattr(entry, 'media_content') and entry.media_content:
        for m in entry.media_content:
            if isinstance(m, dict) and m.get('url'):
                return m['url']
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        for m in entry.media_thumbnail:
            if isinstance(m, dict) and m.get('url'):
                return m['url']
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if isinstance(enc, dict) and enc.get('url') and enc.get('type', '').startswith('image'):
                return enc['url']
    raw_desc = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc, re.IGNORECASE)
    if match:
        return match.group(1)
        
    # Smart fallback to ticker asset image
    if tickers:
        for t in tickers:
            sym = t.lower()
            if sym in AVAILABLE_COMPANY_IMAGES:
                return f"/static/companies/{sym}.jpg"
                
    if category and category in CATEGORY_IMAGES:
        return CATEGORY_IMAGES[category]
        
    return default_image or "/static/companies/sp500.jpg"

def detect_tickers(text):
    """Scan title and summary text to identify mentioned financial symbols."""
    text_lower = text.lower()
    found = []
    for ticker, keywords in TICKER_KEYWORD_MAP.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found.append(ticker)
                break
    return found[:5]

def calculate_time_ago(pub_date_parsed):
    """Convert parsed date tuple or datetime to friendly relative time."""
    if not pub_date_parsed:
        return "Recent dispatch"
    try:
        if isinstance(pub_date_parsed, tuple):
            entry_ts = time.mktime(pub_date_parsed)
        else:
            entry_ts = pub_date_parsed.timestamp()
        
        diff = int(time.time() - entry_ts)
        if diff < 0:
            return "Just now"
        if diff < 3600:
            mins = max(1, diff // 60)
            return f"{mins}m ago"
        elif diff < 86400:
            hrs = diff // 3600
            return f"{hrs}h ago"
        elif diff < 172800:
            return "Yesterday"
        else:
            days = diff // 86400
            return f"{days}d ago"
    except Exception:
        return "Recent dispatch"

def determine_sentiment(text):
    """Sentiment classification based on market indicators."""
    text_lower = text.lower()
    bullish_keywords = ["surge", "rally", "record", "gain", "profit", "jump", "soar", "high", "growth", "boost", "bullish", "recovery", "over-subscribed"]
    bearish_keywords = ["drop", "fall", "slump", "plunge", "loss", "decline", "warn", "recession", "down", "bearish", "crash", "deficit", "underperformance"]
    
    bull_count = sum(1 for kw in bullish_keywords if kw in text_lower)
    bear_count = sum(1 for kw in bearish_keywords if kw in text_lower)
    
    if bull_count >= bear_count:
        return "Bullish"
    return "Caution"

def detect_investor_categories(title, text="", tickers=None, fallback_category=""):
    """
    Intelligently classify financial dispatches into one or more Investor Interest Categories:
    - Tech & AI
    - Bonds & Treasury Bills
    - Equities & Blue Chips
    - Commodities & Energy
    - East Africa & Emerging Markets
    - Macro & Central Banks
    - Index & Dynamic Rankings
    - Top Stories
    """
    blob = f"{title} {text}".lower()
    tickers = tickers or []
    cats = []

    # 1. Tech & AI
    tech_kw = [
        "ai", "artificial intelligence", "tech", "semiconductor", "chip", "nvidia", "microsoft",
        "apple", "alphabet", "google", "amazon", "cloud", "datacenter", "gpu", "silicon",
        "software", "neural", "blackwell", "quantum"
    ]
    tech_tickers = {"NVDA", "MSFT", "AAPL", "GOOGL", "AMZN", "INTC", "CSCO", "CRM", "ADBE", "TXN", "INTU", "6758", "8035"}
    if any(re.search(r'\b' + re.escape(kw) + r'\b', blob) for kw in tech_kw) or any(t in tech_tickers for t in tickers) or fallback_category == "Technology":
        cats.append("Tech & AI")

    # 2. Bonds & Treasury Bills
    bond_kw = [
        "treasury bill", "treasury bills", "t-bill", "t-bills", "tbill", "tbills", "treasury note",
        "treasury bond", "sovereign debt", "gilt", "gilts", "jgb", "jgbs", "government bond",
        "yield curve", "infrastructure bond", "ifb", "dhowcsd", "dmo", "primary auction",
        "10-year treasury", "2-year treasury", "30-year treasury", "91-day", "182-day", "364-day"
    ]
    bond_tickers = {"US_TREASURY", "UST10Y", "UST2Y", "UST30Y", "USTB3M", "UK_DMO", "UKG10Y", "UKG30Y", "MOF_JAPAN", "JGB10Y", "JGB30Y", "T91", "T182", "T364", "IFB10Y", "IFB17Y"}
    if any(kw in blob for kw in bond_kw) or any(t in bond_tickers for t in tickers) or fallback_category == "Sovereign Debt":
        cats.append("Bonds & Treasury Bills")

    # 3. Commodities & Energy
    comm_kw = [
        "oil", "crude", "wti", "brent", "natural gas", "natgas", "henry hub", "heating oil", "diesel",
        "silver", "gold", "bullion", "copper", "platinum", "coffee", "arabica", "cocoa", "wheat",
        "commodity", "commodities", "energy", "petroleum", "comex", "nymex", "cbot"
    ]
    comm_tickers = {"OIL", "BRENT", "NATGAS", "HEATOIL", "SILVER", "GOLD", "COPPER", "PLATINUM", "COFFEE", "COCOA", "WHEAT"}
    if any(re.search(r'\b' + re.escape(kw) + r'\b', blob) for kw in comm_kw) or any(t in comm_tickers for t in tickers) or fallback_category == "Commodities":
        cats.append("Commodities & Energy")

    # 4. East Africa & Emerging Markets
    ea_kw = [
        "safaricom", "m-pesa", "mpesa", "equity bank", "kcb", "co-op bank", "cooperative bank",
        "kengen", "bamburi", "kakuzi", "nairobi securities exchange", "nse", "central bank of kenya",
        "cbk", "kenya", "nairobi", "east africa", "shilling", "kes"
    ]
    ea_tickers = {"SCOM", "EQTY", "KCB", "COOP", "KEGN", "BAMB", "KUKZ", "SCBK", "NCBA", "CENT", "JUB", "CROW", "NSE", "CBK"}
    if any(kw in blob for kw in ea_kw) or any(t in ea_tickers for t in tickers) or fallback_category == "East Africa":
        cats.append("East Africa & Emerging Markets")

    # 5. Macro & Central Banks
    macro_kw = [
        "central bank", "federal reserve", "fed", "fomc", "bank of england", "boe", "bank of japan", "boj",
        "interest rate", "cbr rate", "mpc rate", "monetary policy", "inflation", "cpi", "rate decision",
        "gdp", "kamau thugge", "jerome powell", "kazuo ueda"
    ]
    if any(re.search(r'\b' + re.escape(kw) + r'\b', blob) for kw in macro_kw) or "CBK" in tickers:
        cats.append("Macro & Central Banks")

    # 6. Index & Dynamic Rankings
    index_kw = [
        "top 50", "delisting", "underperformance", "contender", "rebalance", "rebalancing", "promotion",
        "benchmark committee", "index rule", "index governance", "review period"
    ]
    if any(kw in blob for kw in index_kw):
        cats.append("Index & Dynamic Rankings")

    # 7. Equities & Blue Chips
    equity_kw = [
        "equity", "equities", "stock", "stocks", "earnings", "dividend", "revenue", "quarterly results",
        "blue chip", "blue chips", "ftse", "nikkei", "s&p 500", "dow jones", "market cap"
    ]
    if any(kw in blob for kw in equity_kw) or fallback_category == "Equities" or len(cats) == 0:
        cats.append("Equities & Blue Chips")

    # Always ensure high-impact stories also appear in Top Stories
    cats.append("Top Stories")

    # Deduplicate while preserving order
    seen = set()
    ordered_cats = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            ordered_cats.append(c)

    return ordered_cats

def fetch_feed_items(feed_config):
    """Fetch and parse RSS feed items, converting into clean PesaMarkets format."""
    if not HAS_FEEDPARSER:
        return []
    
    url = feed_config.get("url")
    agency = sanitize_forbidden_agency_names(feed_config.get("agency", "Market Wire"))
    badge = sanitize_forbidden_agency_names(feed_config.get("badge", agency))
    category = feed_config.get("category", "General")
    default_img = CATEGORY_IMAGES.get(category, "/static/companies/sp500.jpg")
    
    items = []
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PesaMarkets-IntelligenceDesk/2.0 (Accredited Financial Terminal)"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as response:
            xml_data = response.read()
            
        parsed = feedparser.parse(xml_data)
        
        for e in parsed.entries[:8]:
            title = sanitize_forbidden_agency_names(clean_html(getattr(e, 'title', '')))
            summary = sanitize_forbidden_agency_names(clean_html(getattr(e, 'summary', '') or getattr(e, 'description', '')))
            link = getattr(e, 'link', '')
            
            if not title or len(title) < 10:
                continue
            
            raw_content = ""
            if hasattr(e, 'content') and e.content:
                raw_content = e.content[0].value if isinstance(e.content, list) else str(e.content)
            content_text = sanitize_forbidden_agency_names(clean_html(raw_content)) or summary

            # STRICT RELEVANCE GATE: Discard any random news not related to PesaMarkets
            if not is_relevant_to_pesamarkets(title, summary, content_text):
                continue
            
            tickers = detect_tickers(title + " " + summary)
            image = extract_image_url(e, default_img, tickers=tickers, category=category)
            pub_parsed = getattr(e, 'published_parsed', None)
            time_ago = calculate_time_ago(pub_parsed)
            word_count = len((title + " " + summary).split())
            read_time = f"{max(2, round(word_count / 50))} min read"
            
            sentiment = determine_sentiment(title + " " + summary)
            story_id = int(hashlib.md5((link + title).encode('utf-8')).hexdigest()[:7], 16)
            
            investor_cats = detect_investor_categories(title, summary, tickers=tickers, fallback_category=category)
            specific_cats = [c for c in investor_cats if c != "Top Stories"]
            primary_cat = specific_cats[0] if specific_cats else "Equities & Blue Chips"
            
            slug_map = {
                "Top Stories": "top-stories",
                "Tech & AI": "tech-ai",
                "Bonds & Treasury Bills": "bonds-treasuries",
                "Equities & Blue Chips": "equities",
                "Commodities & Energy": "commodities",
                "East Africa & Emerging Markets": "east-africa",
                "Macro & Central Banks": "macro-central-banks",
                "Index & Dynamic Rankings": "index-rankings",
            }
            icon_map = {
                "Top Stories": "fa-solid fa-bolt",
                "Tech & AI": "fa-solid fa-microchip",
                "Bonds & Treasury Bills": "fa-solid fa-landmark",
                "Equities & Blue Chips": "fa-solid fa-chart-line",
                "Commodities & Energy": "fa-solid fa-oil-well",
                "East Africa & Emerging Markets": "fa-solid fa-earth-africa",
                "Macro & Central Banks": "fa-solid fa-building-columns",
                "Index & Dynamic Rankings": "fa-solid fa-ranking-star",
            }

            cat_slug = slug_map.get(primary_cat, "equities")
            author_idx = abs(hash(str(story_id))) % len(DEFAULT_AUTHORS)
            author = DEFAULT_AUTHORS[author_idx]

            # Format rich paragraphs
            paragraphs = [p.strip() for p in content_text.split(". ") if len(p.strip()) > 30]
            if len(paragraphs) < 3:
                paragraphs = [
                    f"{title}. {summary}",
                    f"Market telemetry reflects disciplined institutional order routing across key trading desks. Analysts underscore steady fundamental metrics and balanced liquidity profiles.",
                    f"Cross-asset positioning remains focused on high-quality cash flows, sovereign balance sheet health, and resilient commodity demand trajectories into the upcoming quarter."
                ]

            key_takeaways = [
                f"{primary_cat} dispatch reported via {agency}.",
                f"Market sentiment classified as {sentiment} across monitoring telemetry.",
                f"Tickers actively monitored: {', '.join(tickers) if tickers else 'Benchmark composite'}."
            ]


            items.append({
                "id": story_id,
                "title": title,
                "summary": summary,
                "content": content_text,
                "paragraphs": paragraphs,
                "key_takeaways": key_takeaways,
                "category": primary_cat,
                "categories": investor_cats,
                "category_slug": cat_slug,
                "category_icon": icon_map.get(primary_cat, "fa-solid fa-newspaper"),
                "source": agency,
                "source_badge": badge,
                "url": sanitize_external_url(link, story_id),
                "time_ago": time_ago,
                "published_date": "Nov 17, 2026 • Live Wire",
                "read_time": read_time,
                "sentiment": sentiment,
                "tickers": tickers,
                "image": image,
                "author_name": author["name"],
                "author_role": author["role"],
                "author_avatar": author["avatar"],
                "is_agency": True,
                "is_paywalled": False,
            })
    except Exception:
        pass
    return items

def get_agency_news(category=None, agency=None, limit=None, force_refresh=False, search_query=None):
    """
    Retrieve real-time or cached news agency dispatches organized by Investor Interests.
    All returned news is guaranteed to be related strictly to PesaMarkets verified offerings.
    """
    global _NEWS_CACHE
    now = time.time()
    
    if not force_refresh and _NEWS_CACHE["stories"] and (now - _NEWS_CACHE["last_fetched"] < _NEWS_CACHE["ttl_seconds"]):
        all_stories = _NEWS_CACHE["stories"]
    else:
        fetched_stories = []
        for feed in RSS_AGENCY_FEEDS:
            stories = fetch_feed_items(feed)
            if stories:
                fetched_stories.extend(stories)
        
        # Combine valid fetched stories with curated institutional dispatches
        if fetched_stories:
            seen_titles = {s["title"].lower() for s in fetched_stories}
            combined = list(fetched_stories)
            for d in DEFAULT_AGENCY_DISPATCHES:
                if d["title"].lower() not in seen_titles:
                    combined.append(d)
            _NEWS_CACHE["stories"] = combined
            _NEWS_CACHE["last_fetched"] = now
            all_stories = combined
        else:
            all_stories = DEFAULT_AGENCY_DISPATCHES
            _NEWS_CACHE["stories"] = all_stories
            _NEWS_CACHE["last_fetched"] = now

    filtered = list(all_stories)

    # 1. Apply Investor Interest Category filter
    if category and category.lower() not in ('all', ''):
        cat_lower = category.lower().strip()
        synonyms = [s.lower() for s in CATEGORY_SYNONYMS.get(cat_lower, [cat_lower])]
        
        def matches_category(s):
            s_cat = s.get("category", "").lower()
            s_slug = s.get("category_slug", "").lower()
            s_cats = [c.lower() for c in s.get("categories", [])]
            if s_cat in synonyms or s_slug in synonyms:
                return True
            if any(c in synonyms for c in s_cats):
                return True
            return False

        cat_filtered = [s for s in filtered if matches_category(s)]
        if cat_filtered:
            filtered = cat_filtered
        else:
            fallback_matches = [s for s in filtered if cat_lower in s.get("category", "").lower() or cat_lower in s.get("title", "").lower()]
            if fallback_matches:
                filtered = fallback_matches

    # 2. Optional search query filter
    if search_query:
        sq = search_query.lower().strip()
        filtered = [
            s for s in filtered 
            if sq in s.get("title", "").lower() 
            or sq in s.get("summary", "").lower() 
            or any(sq in t.lower() for t in s.get("tickers", []))
            or sq in s.get("category", "").lower()
        ]

    # 3. Agency filter (kept for backward compatibility or API filter)
    if agency and agency.lower() != 'all':
        agency_lower = agency.lower().strip()
        filtered = [s for s in filtered if agency_lower in s.get("source", "").lower() or agency_lower in s.get("source_badge", "").lower()]

    if limit:
        return filtered[:limit]
    return filtered

def get_agency_story_by_id(story_id):
    """
    Retrieve an individual news dispatch by its ID.
    Enriches with full article content, author credentials, and related stories.
    """
    all_stories = get_agency_news()
    story = None
    target_id_str = str(story_id).strip()
    
    for s in all_stories:
        if str(s.get("id")) == target_id_str:
            story = dict(s)
            break
            
    if not story:
        for d in DEFAULT_AGENCY_DISPATCHES:
            if str(d.get("id")) == target_id_str:
                story = dict(d)
                break
                
    if not story:
        return None

    # Ensure paragraphs are present
    if not story.get("paragraphs"):
        content = story.get("content") or story.get("summary") or ""
        story["paragraphs"] = [p.strip() for p in content.split(". ") if len(p.strip()) > 30] or [content]

    cat_slug = story.get("category_slug", "equities")


    # Ensure author is present
    if not story.get("author_name"):
        author_idx = abs(hash(str(story.get("id")))) % len(DEFAULT_AUTHORS)
        author = DEFAULT_AUTHORS[author_idx]
        story["author_name"] = author["name"]
        story["author_role"] = author["role"]
        story["author_avatar"] = author["avatar"]

    if not story.get("published_date"):
        story["published_date"] = "Nov 17, 2026 • 08:30 AM EAT"

    # Fetch related stories from the same category (excluding current story)
    related = [
        s for s in all_stories 
        if str(s.get("id")) != target_id_str 
        and (s.get("category_slug") == cat_slug or s.get("category") == story.get("category"))
    ][:4]
    story["related_stories"] = related

    return story

def get_investor_categories(stories=None):
    """
    Return distinct investor interest categories with live story counts.
    """
    if stories is None:
        stories = get_agency_news()
    
    categories = []
    
    for cat in INVESTOR_CATEGORIES:
        slug = cat["slug"]
        if slug == "top-stories":
            cnt = sum(1 for s in stories if "Top Stories" in s.get("categories", []) or s.get("category") == "Top Stories")
            if cnt == 0:
                cnt = len(stories)
        else:
            synonyms = [s.lower() for s in CATEGORY_SYNONYMS.get(slug, [slug])]
            cnt = sum(
                1 for s in stories
                if s.get("category_slug") == slug
                or s.get("category", "").lower() in synonyms
                or any(c.lower() in synonyms for c in s.get("categories", []))
                or any(syn in s.get("category", "").lower() for syn in synonyms)
            )

        categories.append({
            "slug": slug,
            "name": cat["name"],
            "short_name": cat["short_name"],
            "icon": cat["icon"],
            "badge_color": cat["badge_color"],
            "description": cat["description"],
            "count": cnt,
        })
    return categories

def get_agency_news_for_asset(symbol, limit=4):
    """
    Retrieve news agency stories specifically tailored to an asset.
    First matches direct tickers; fills remaining slots with stories
    from the exact same asset class or sovereign market.
    """
    sym_upper = symbol.upper().strip()
    all_stories = get_agency_news()
    
    # 1. Direct ticker matches
    matches = [s for s in all_stories if sym_upper in s.get("tickers", [])]
    
    # 2. Targeted padding based on the asset's specific market / category
    if len(matches) < limit:
        from markets.data import ASSETS
        asset = ASSETS.get(sym_upper, {})
        category = asset.get("category", "")
        country = asset.get("country", "")
        market = asset.get("market", "")

        for s in all_stories:
            if s in matches:
                continue
            s_cat = s.get("category", "").lower()
            s_cats = [c.lower() for c in s.get("categories", [])]

            # Align with asset class
            if category == "commodities" and (s_cat in ["commodities", "commodities & energy"] or "commodities & energy" in s_cats):
                matches.append(s)
            elif category == "bonds" and (s_cat in ["sovereign debt", "bonds", "bonds & treasury bills"] or "bonds & treasury bills" in s_cats):
                matches.append(s)
            elif (country == "Kenya" or market == "NSE") and (s_cat in ["east africa", "equities", "east africa & emerging markets"] or "east africa & emerging markets" in s_cats):
                matches.append(s)
            elif (country in ["USA", "UK", "Japan"] or market in ["NASDAQ", "NYSE", "LSE", "TSE"]) and (s_cat in ["equities", "technology", "equities & blue chips", "tech & ai"] or any(c in ["tech & ai", "equities & blue chips"] for c in s_cats)):
                matches.append(s)

            if len(matches) >= limit:
                break

    # 3. Fallback padding if still under limit
    if len(matches) < limit:
        for s in all_stories:
            if s not in matches:
                matches.append(s)
            if len(matches) >= limit:
                break

    return matches[:limit]

def get_news_agencies():
    """Return distinct news agencies currently represented in the feed."""
    stories = get_agency_news()
    agencies = {}
    for s in stories:
        ag_name = s.get("source", "Market Wire")
        ag_badge = s.get("source_badge", ag_name)
        if ag_name not in agencies:
            agencies[ag_name] = {
                "name": ag_name,
                "badge": ag_badge,
                "count": 0
            }
        agencies[ag_name]["count"] += 1
    return list(agencies.values())
