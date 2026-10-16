import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .data import (
    MARKET_INDICES,
    ASSETS,
    FINANCIAL_NEWS,
    USER_PORTFOLIO,
    WATCHLISTS,
    EXCHANGE_RATES
)

def get_market_movers():
    """Calculates top gainers, top losers, and most active assets."""
    all_assets = list(ASSETS.values())
    sorted_by_change = sorted(all_assets, key=lambda x: x["change_percent"], reverse=True)
    top_gainers = [a for a in sorted_by_change if a["change_percent"] > 0][:5]
    top_losers = [a for a in sorted_by_change[::-1] if a["change_percent"] < 0][:5]
    trending = sorted(all_assets, key=lambda x: float(str(x["volume"]).replace("M", "").replace("K", "0.001").replace("B", "1000").split()[0]), reverse=True)[:5]
    return top_gainers, top_losers, trending

def home(request):
    top_gainers, top_losers, trending = get_market_movers()
    
    # Financial insights summary
    insights = [
        {"title": "Optimize Budget", "value": "+0.8% Monthly", "icon": "fa-chart-pie", "desc": "Reduced equity trading fees via bulk limit orders"},
        {"title": "Smart Saving", "value": "+1.8% Weekly", "icon": "fa-piggy-bank", "desc": "High yield treasury yield earning 12.5% annualized"},
        {"title": "Portfolio Alpha", "value": "+22.1% All-Time", "icon": "fa-award", "desc": "Outperforming benchmark NSE 20 Index by 14.8%"}
    ]
    
    context = {
        "indices": MARKET_INDICES,
        "portfolio": USER_PORTFOLIO,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "trending": trending,
        "news": FINANCIAL_NEWS[:4],
        "insights": insights,
        "assets": ASSETS,
        "rates": json.dumps(EXCHANGE_RATES),
        "page_title": "Dashboard",
        "active_tab": "home"
    }
    return render(request, 'markets/home.html', context)

def markets_list(request):
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '').strip().lower()
    
    all_assets = list(ASSETS.values())
    
    if category == 'equities':
        filtered = [a for a in all_assets if a['category'] == 'equities']
    elif category == 'crypto':
        filtered = [a for a in all_assets if a['category'] == 'crypto']
    elif category == 'commodities':
        filtered = [a for a in all_assets if a['category'] == 'commodities']
    elif category == 'gainers':
        filtered = sorted([a for a in all_assets if a['change_percent'] > 0], key=lambda x: x['change_percent'], reverse=True)
    elif category == 'losers':
        filtered = sorted([a for a in all_assets if a['change_percent'] < 0], key=lambda x: x['change_percent'])
    elif category == 'nse':
        filtered = [a for a in all_assets if a.get('market') == 'NSE']
    else:
        filtered = all_assets
        
    if search_query:
        filtered = [a for a in filtered if search_query in a['symbol'].lower() or search_query in a['name'].lower()]

    top_gainers, top_losers, trending = get_market_movers()

    context = {
        "indices": MARKET_INDICES,
        "assets_list": filtered,
        "current_category": category,
        "search_query": search_query,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "page_title": "Markets Overview",
        "active_tab": "markets"
    }
    return render(request, 'markets/markets.html', context)

def asset_detail(request, symbol):
    symbol_upper = symbol.upper()
    asset = ASSETS.get(symbol_upper)
    if not asset:
        # Fallback to SCOM if not found
        asset = ASSETS.get("SCOM")
    
    related_news = [n for n in FINANCIAL_NEWS if symbol_upper in n.get("tickers", [])]
    if not related_news:
        related_news = FINANCIAL_NEWS[:3]
        
    context = {
        "indices": MARKET_INDICES,
        "asset": asset,
        "asset_json": json.dumps(asset),
        "related_news": related_news,
        "portfolio": USER_PORTFOLIO,
        "page_title": f"{asset['symbol']} - {asset['name']}",
        "active_tab": "markets"
    }
    return render(request, 'markets/asset_detail.html', context)

def portfolio(request):
    total_val = USER_PORTFOLIO["total_value_usd"]
    cash_val = USER_PORTFOLIO["cash_balance_usd"]
    invested_val = total_val - cash_val
    
    # Calculate asset allocation slices
    allocation = []
    for h in USER_PORTFOLIO["holdings"]:
        allocation.append({
            "label": h["symbol"],
            "value": h["total_value_usd"],
            "percent": h["allocation_percent"]
        })
    allocation.append({
        "label": "Available Cash",
        "value": cash_val,
        "percent": round((cash_val / total_val) * 100, 1)
    })
    
    context = {
        "indices": MARKET_INDICES,
        "portfolio": USER_PORTFOLIO,
        "allocation": allocation,
        "allocation_json": json.dumps(allocation),
        "page_title": "Portfolio",
        "active_tab": "portfolio"
    }
    return render(request, 'markets/portfolio.html', context)

def watchlist(request):
    watchlist_id = request.GET.get('tab', 'default')
    symbols = WATCHLISTS.get(watchlist_id, WATCHLISTS['default'])
    watchlist_assets = [ASSETS[s] for s in symbols if s in ASSETS]
    
    context = {
        "indices": MARKET_INDICES,
        "watchlists": WATCHLISTS,
        "active_watchlist_id": watchlist_id,
        "watchlist_assets": watchlist_assets,
        "all_assets": list(ASSETS.values()),
        "page_title": "Watchlists",
        "active_tab": "watchlist"
    }
    return render(request, 'markets/watchlist.html', context)

def trade(request):
    symbol = request.GET.get('symbol', 'SCOM').upper()
    asset = ASSETS.get(symbol, ASSETS.get('SCOM'))
    
    context = {
        "indices": MARKET_INDICES,
        "asset": asset,
        "asset_json": json.dumps(asset),
        "all_assets": list(ASSETS.values()),
        "portfolio": USER_PORTFOLIO,
        "page_title": f"Trade {asset['symbol']}",
        "active_tab": "trade"
    }
    return render(request, 'markets/trade.html', context)

def news(request):
    category = request.GET.get('category', 'all')
    if category != 'all':
        filtered = [n for n in FINANCIAL_NEWS if n['category'].lower() == category.lower()]
    else:
        filtered = FINANCIAL_NEWS
        
    context = {
        "indices": MARKET_INDICES,
        "news_list": filtered,
        "current_category": category,
        "hero_news": FINANCIAL_NEWS[0] if FINANCIAL_NEWS else None,
        "page_title": "Market News",
        "active_tab": "news"
    }
    return render(request, 'markets/news.html', context)

def settings_page(request):
    context = {
        "rates": EXCHANGE_RATES,
        "page_title": "Settings",
        "active_tab": "settings"
    }
    return render(request, 'markets/settings.html', context)

def support(request):
    context = {
        "page_title": "Help & Support",
        "active_tab": "support"
    }
    return render(request, 'markets/support.html', context)

def profile(request):
    context = {
        "portfolio": USER_PORTFOLIO,
        "page_title": "My Account",
        "active_tab": "profile"
    }
    return render(request, 'markets/profile.html', context)

# --- AJAX / JSON REST APIs ---

def api_search(request):
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return JsonResponse({"results": []})
        
    matches = []
    for asset in ASSETS.values():
        if query in asset['symbol'].lower() or query in asset['name'].lower() or query in asset.get('sector', '').lower():
            matches.append({
                "symbol": asset["symbol"],
                "name": asset["name"],
                "price": asset["price"],
                "currency": asset["currency"],
                "change": asset["change"],
                "change_percent": asset["change_percent"],
                "category": asset["category"],
                "market": asset["market"]
            })
    return JsonResponse({"results": matches[:8]})

def api_quote(request, symbol):
    asset = ASSETS.get(symbol.upper())
    if not asset:
        return JsonResponse({"error": "Symbol not found"}, status=404)
    return JsonResponse(asset)

@csrf_exempt
def api_trade_execute(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper()
        action = data.get('action', 'BUY').upper()
        quantity = float(data.get('quantity', 0))
        order_type = data.get('order_type', 'MARKET')
        
        asset = ASSETS.get(symbol)
        if not asset or quantity <= 0:
            return JsonResponse({"error": "Invalid asset or quantity"}, status=400)
            
        unit_price = asset['price']
        total_amount = round(unit_price * quantity, 2)
        
        # Simulated execution
        new_tx = {
            "id": f"TX-{len(USER_PORTFOLIO['transactions']) + 9022}",
            "asset_symbol": symbol,
            "asset_name": asset['name'],
            "type": action,
            "shares": f"{quantity:g} {'Shares' if asset['category'] == 'equities' else symbol}",
            "price": f"{asset['currency']} {unit_price:,.2f}",
            "total": f"{asset['currency']} {total_amount:,.2f}",
            "date": "Just now",
            "status": "Completed"
        }
        USER_PORTFOLIO["transactions"].insert(0, new_tx)
        
        return JsonResponse({
            "success": True,
            "message": f"Successfully executed {action} order for {quantity:g} {symbol} at {asset['currency']} {unit_price:,.2f}",
            "transaction": new_tx
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def api_watchlist_toggle(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper()
        watchlist_name = data.get('watchlist', 'default')
        
        current_list = WATCHLISTS.setdefault(watchlist_name, [])
        if symbol in current_list:
            current_list.remove(symbol)
            is_in = False
        else:
            current_list.append(symbol)
            is_in = True
            
        return JsonResponse({
            "success": True,
            "symbol": symbol,
            "in_watchlist": is_in,
            "watchlist": watchlist_name
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
