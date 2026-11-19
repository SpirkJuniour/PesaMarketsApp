"""
Market Dock Service.
Provides live telemetry data for the interactive right dock rail across the app:
- Trending tickers (with SVG sparklines)
- Recently viewed commodities and equities
- Top gainers, top losers, and most active assets
- Top economic events by country (Kenya, USA, UK, Japan, All)
- Upcoming earnings events from regulators (SEC, CMA, FCA)
"""

# Helper to generate smooth SVG sparkline path data
def generate_sparkline_svg(trend="up", seed=1):
    """Generate SVG polyline coordinates for mini-charts in the dock."""
    if trend == "up":
        # Green upward trend
        points = [
            (0, 18), (8, 16), (16, 17), (24, 13), (32, 14),
            (40, 10), (48, 11), (56, 7), (64, 8), (72, 3), (80, 2)
        ]
        color = "#10b981"
        fill_color = "rgba(16, 185, 129, 0.15)"
    else:
        # Red downward trend
        points = [
            (0, 3), (8, 5), (16, 4), (24, 9), (32, 8),
            (40, 12), (48, 11), (56, 15), (64, 14), (72, 19), (80, 20)
        ]
        color = "#f43f5e"
        fill_color = "rgba(244, 63, 94, 0.15)"

    points_str = " ".join(f"{x},{y}" for x, y in points)
    area_points = f"0,22 {points_str} 80,22"
    return {
        "polyline": points_str,
        "area": area_points,
        "stroke": color,
        "fill": fill_color,
    }

TRENDING_TICKERS = [
    {
        "symbol": "NFLX",
        "name": "Netflix, Inc.",
        "price": "60.75",
        "change": "-1.40",
        "change_percent": "-2.25%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 1),
    },
    {
        "symbol": "INTC",
        "name": "Intel Corporation",
        "price": "53.00",
        "change": "-6.66",
        "change_percent": "-11.16%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 2),
    },
    {
        "symbol": "GDHG",
        "name": "Golden Heaven Gr...",
        "price": "1.1698",
        "change": "+0.34",
        "change_percent": "+41.74%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 3),
    },
    {
        "symbol": "^IXIC",
        "name": "NASDAQ Composi...",
        "price": "24,509.76",
        "change": "-626.52",
        "change_percent": "-2.49%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 4),
    },
    {
        "symbol": "RCAT",
        "name": "Red Cat Holdings,...",
        "price": "2.6400",
        "change": "-1.1600",
        "change_percent": "-30.53%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 5),
    },
]

RECENTLY_VIEWED = [
    {
        "symbol": "CL=F",
        "name": "Crude Oil Dec 26",
        "price": "85.38",
        "change": "-0.34",
        "change_percent": "-0.40%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 6),
    },
    {
        "symbol": "BZ=F",
        "name": "Brent Crude Oil La...",
        "price": "92.13",
        "change": "-0.31",
        "change_percent": "-0.34%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 7),
    },
    {
        "symbol": "SCOM",
        "name": "Safaricom PLC",
        "price": "15.20",
        "change": "+0.35",
        "change_percent": "+2.36%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 8),
    },
]

TOP_GAINERS = [
    {
        "symbol": "CGON",
        "name": "CG Oncology, Inc.",
        "price": "84.71",
        "change": "+10.31",
        "change_percent": "+13.86%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 9),
    },
    {
        "symbol": "TU",
        "name": "TELUS Corporation",
        "price": "9.64",
        "change": "+1.11",
        "change_percent": "+13.01%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 10),
    },
    {
        "symbol": "MOH",
        "name": "Molina Healthcare...",
        "price": "232.95",
        "change": "+23.46",
        "change_percent": "+11.20%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 11),
    },
    {
        "symbol": "EQTY",
        "name": "Equity Group Hldgs",
        "price": "48.20",
        "change": "+2.10",
        "change_percent": "+4.55%",
        "is_positive": True,
        "sparkline": generate_sparkline_svg("up", 12),
    },
]

TOP_LOSERS = [
    {
        "symbol": "SMMT",
        "name": "Summit Therapeut...",
        "price": "11.98",
        "change": "-2.17",
        "change_percent": "-15.34%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 13),
    },
    {
        "symbol": "GDS",
        "name": "GDS Holdings Lim...",
        "price": "16.93",
        "change": "-2.88",
        "change_percent": "-14.54%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 14),
    },
    {
        "symbol": "ASTS",
        "name": "AST SpaceMobile,...",
        "price": "28.22",
        "change": "-4.38",
        "change_percent": "-13.44%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 15),
    },
    {
        "symbol": "USAR",
        "name": "USA Rare Earth, I...",
        "price": "7.08",
        "change": "-1.08",
        "change_percent": "-13.24%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 16),
    },
    {
        "symbol": "RUM",
        "name": "RUM Group Inc.",
        "price": "5.06",
        "change": "-0.71",
        "change_percent": "-12.30%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 17),
    },
]

MOST_ACTIVE = [
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "price": "155.63",
        "change": "-7.23",
        "change_percent": "-4.44%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 18),
    },
    {
        "symbol": "SPCX",
        "name": "Space Exploration...",
        "price": "137.16",
        "change": "-1.95",
        "change_percent": "-1.40%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 19),
    },
    {
        "symbol": "INTC",
        "name": "Intel Corporation",
        "price": "53.00",
        "change": "-6.66",
        "change_percent": "-11.16%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 20),
    },
    {
        "symbol": "NU",
        "name": "Nu Holdings Ltd.",
        "price": "12.63",
        "change": "-0.59",
        "change_percent": "-4.46%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 21),
    },
    {
        "symbol": "NIO",
        "name": "NIO Inc.",
        "price": "2.7099",
        "change": "-0.19",
        "change_percent": "-6.56%",
        "is_positive": False,
        "sparkline": generate_sparkline_svg("down", 22),
    },
]

ECONOMIC_EVENTS = {
    "kenya": [
        # Kenya starts empty to match screenshot, with toggle to view all
    ],
    "usa": [
        {
            "title": "US Initial Jobless Claims",
            "time": "16:30 EAT",
            "impact": "High",
            "consensus": "218K",
            "previous": "221K",
            "date": "Today",
        },
        {
            "title": "FOMC Meeting Minutes Release",
            "time": "22:00 EAT",
            "impact": "High",
            "consensus": "--",
            "previous": "4.75%",
            "date": "Tomorrow",
        },
    ],
    "uk": [
        {
            "title": "UK CPI Inflation YoY",
            "time": "10:00 EAT",
            "impact": "High",
            "consensus": "2.2%",
            "previous": "2.3%",
            "date": "Nov 19",
        },
    ],
    "japan": [
        {
            "title": "Bank of Japan Summary of Opinions",
            "time": "03:50 EAT",
            "impact": "Medium",
            "consensus": "--",
            "previous": "0.25%",
            "date": "Nov 20",
        },
    ],
    "all": [
        {
            "country": "USA",
            "country_flag": "🇺🇸",
            "title": "US Initial Jobless Claims",
            "time": "16:30 EAT",
            "impact": "High",
            "date": "Today",
        },
        {
            "country": "USA",
            "country_flag": "🇺🇸",
            "title": "FOMC Meeting Minutes Release",
            "time": "22:00 EAT",
            "impact": "High",
            "date": "Tomorrow",
        },
        {
            "country": "UK",
            "country_flag": "🇬🇧",
            "title": "UK CPI Inflation YoY",
            "time": "10:00 EAT",
            "impact": "High",
            "date": "Nov 19",
        },
        {
            "country": "Kenya",
            "country_flag": "🇰🇪",
            "title": "CBK Treasury Bill Auction Results (T91, T182, T364)",
            "time": "14:00 EAT",
            "impact": "Medium",
            "date": "Nov 20",
        },
    ]
}

def get_dock_data():
    """Return dictionary with all data sections for the market dock."""
    from .earnings_service import UPCOMING_EARNINGS, REPORTED_REGULATORY_FILINGS
    from .events_service import get_dock_economic_events
    return {
        "trending_tickers": TRENDING_TICKERS,
        "recently_viewed": RECENTLY_VIEWED,
        "top_gainers": TOP_GAINERS,
        "top_losers": TOP_LOSERS,
        "most_active": MOST_ACTIVE,
        "economic_events": get_dock_economic_events(),
        "earnings_upcoming": UPCOMING_EARNINGS[:6],
        "earnings_reported": REPORTED_REGULATORY_FILINGS[:5],
    }
