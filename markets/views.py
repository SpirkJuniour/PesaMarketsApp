import json
import logging
import re
import secrets
import urllib.parse
import urllib.request
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.template import TemplateDoesNotExist
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

from .models import Market, Asset, UserProfile, OTPVerification, Portfolio, Order, Transaction, CashTransfer, Watchlist
from .forms import (
    LoginForm,
    TraderRegistrationForm,
    OTPVerificationForm,
    UserProfileUpdateForm,
    UserProfileDetailsForm,
    PasswordChangeCustomForm,
    TradeOrderForm,
    CashTransferForm,
    AssetSearchFilterForm,
)
from .services.notification_service import dispatch_user_verification
from .services.news_service import (
    get_agency_news,
    get_agency_news_for_asset,
    get_news_agencies,
    get_investor_categories,
    get_agency_story_by_id,
    NEWS_TRENDING_TOPICS,
)
from .data import (
    MARKET_INDICES,
    ASSETS,
    FINANCIAL_NEWS,
    USER_PORTFOLIO,
    WATCHLISTS,
    EXCHANGE_RATES,
    SUPPORTED_MARKETS,
    get_terminal_data,
    get_bonds_data,
    BONDS_CATALOG,
    BOND_PORTFOLIO,
    execute_bond_purchase,
    CBK_AUCTION_CALENDAR,
    CBK_RECENT_AUCTIONS,
    get_asset_logo,
    get_company_image,
    get_top_50_assets,
    get_underperforming_assets,
    get_contender_assets,
    rebalance_top_50
)

# --- Database & ORM Helper Methods ---

def get_or_create_market(symbol='NSE', name=None):
    """Ensures a Market instance exists in the database."""
    mkt = Market.objects.filter(symbol=symbol).first()
    if not mkt:
        default_names = {
            'NSE': 'Nairobi Securities Exchange',
            'NASDAQ': 'NASDAQ Stock Market',
            'NYSE': 'New York Stock Exchange',
            'LSE': 'London Stock Exchange',
            'TSE': 'Tokyo Stock Exchange',
            'CBK': 'Central Bank of Kenya',
            'US_TREASURY': 'United States Department of the Treasury',
            'UK_DMO': 'United Kingdom Debt Management Office',
            'MOF_JAPAN': 'Ministry of Finance Japan',
            'COMEX': 'Commodity Exchange (COMEX)',
            'NYMEX': 'New York Mercantile Exchange (NYMEX)',
            'ICE': 'Intercontinental Exchange (ICE)',
            'CBOT': 'Chicago Board of Trade (CBOT)'
        }
        mkt, _ = Market.objects.get_or_create(symbol=symbol, defaults={'name': name or default_names.get(symbol, symbol)})
    return mkt

def parse_volume(vol_str):
    parts = str(vol_str).strip().split()
    vol_str = parts[0] if parts else '0'
    vol_str = vol_str.replace('$', '').replace('£', '').replace('¥', '').replace('€', '').replace(',', '').strip()
    if vol_str.endswith('B'):
        return float(vol_str[:-1]) * 1_000_000_000
    elif vol_str.endswith('M'):
        return float(vol_str[:-1]) * 1_000_000
    elif vol_str.endswith('K'):
        return float(vol_str[:-1]) * 1_000
    try:
        return float(vol_str)
    except (ValueError, TypeError):
        return 0.0

def get_market_movers():
    """Calculates top gainers, top losers, and most active assets."""
    all_assets = list(ASSETS.values())
    sorted_by_change = sorted(all_assets, key=lambda x: x["change_percent"], reverse=True)
    top_gainers = [a for a in sorted_by_change if a["change_percent"] > 0][:5]
    top_losers = [a for a in sorted_by_change[::-1] if a["change_percent"] < 0][:5]
    trending = sorted(all_assets, key=lambda x: parse_volume(x["volume"]), reverse=True)[:5]
    return top_gainers, top_losers, trending

def get_user_portfolio_data(user):
    """
    Retrieves or calculates user portfolio, holdings, cash, and transactions directly from database records.
    Unauthenticated guests receive an empty guest structure with 0.0 balances and no fake transactions or holdings.
    """
    if not user or not user.is_authenticated:
        return {
            "is_guest": True,
            "total_value_usd": 0.0,
            "cash_balance_usd": 0.0,
            "invested_value_usd": 0.0,
            "day_profit_usd": 0.0,
            "day_profit_percent": 0.0,
            "total_profit_usd": 0.0,
            "total_profit_percent": 0.0,
            "holdings": [],
            "transactions": [],
            "watchlist_count": 0
        }

    portfolio_obj, _ = Portfolio.objects.get_or_create(
        user=user,
        defaults={'name': 'Growth & Dividend Portfolio', 'cash_balance_usd': Decimal('5212.17')}
    )

    db_txs = Transaction.objects.filter(portfolio=portfolio_obj).select_related('asset').order_by('-date')

    formatted_txs = []
    for tx in db_txs:
        formatted_txs.append({
            "id": tx.reference or f"TX-{tx.id}",
            "asset_symbol": tx.asset.symbol,
            "asset_name": tx.asset.name,
            "logo": get_asset_logo(tx.asset.symbol),
            "image": get_company_image(tx.asset.symbol),
            "type": tx.action,
            "shares": f"{float(tx.quantity):g} {'Shares' if tx.asset.category == 'equities' else tx.asset.symbol}",
            "price": f"{tx.asset.currency} {float(tx.price_at_transaction):,.2f}",
            "total": f"{tx.asset.currency} {float(tx.total_amount):,.2f}" if tx.total_amount else f"{tx.asset.currency} {(float(tx.price_at_transaction) * float(tx.quantity)):,.2f}",
            "date": tx.date.strftime("%b %d, %H:%M") if tx.date else "Just now",
            "status": tx.status
        })

    cash_balance = float(portfolio_obj.cash_balance_usd)

    # Compute live holdings from database transactions
    holdings_dict = {}
    for tx in db_txs:
        sym = tx.asset.symbol
        if sym not in holdings_dict:
            holdings_dict[sym] = {
                "symbol": sym,
                "name": tx.asset.name,
                "shares": 0.0,
                "total_invested": 0.0,
                "currency": tx.asset.currency,
                "current_price": float(tx.asset.current_price or 0.0)
            }
        qty = float(tx.quantity)
        price = float(tx.price_at_transaction or 0.0)
        if tx.action == 'BUY':
            holdings_dict[sym]["shares"] += qty
            holdings_dict[sym]["total_invested"] += price * qty
        elif tx.action == 'SELL':
            holdings_dict[sym]["shares"] = max(0.0, holdings_dict[sym]["shares"] - qty)

    holdings = []
    invested_total = 0.0
    for sym, h in holdings_dict.items():
        if h["shares"] > 0:
            asset_info = ASSETS.get(sym, {})
            curr_price = asset_info.get("price", h["current_price"])
            val = round(h["shares"] * curr_price, 2)
            fx_rate = EXCHANGE_RATES.get(h.get("currency", "USD"), 1.0)
            val_usd = round(val / fx_rate, 2)
            invested_total += val_usd
            cost_usd = round(h["total_invested"] / fx_rate, 2) if fx_rate else round(h["total_invested"], 2)
            unrealized_profit = round(val_usd - cost_usd, 2)
            profit_pct = round((unrealized_profit / cost_usd) * 100, 2) if cost_usd else 0.0
            holdings.append({
                "symbol": sym,
                "name": h["name"],
                "logo": get_asset_logo(sym),
                "image": get_company_image(sym),
                "shares": f"{h['shares']:g} Shares",
                "avg_buy_price": round(h["total_invested"] / h["shares"], 2) if h["shares"] else 0,
                "avg_price": round(h["total_invested"] / h["shares"], 2) if h["shares"] else 0,
                "current_price": curr_price,
                "currency": h["currency"],
                "total_value_usd": val_usd,
                "unrealized_profit_usd": unrealized_profit,
                "profit_usd": unrealized_profit,
                "profit_percent": profit_pct,
                "is_positive": profit_pct >= 0
            })

    total_value = round(invested_total + cash_balance, 2)
    for h in holdings:
        val_usd = h.get("total_value_usd", 0)
        h["allocation_percent"] = round((val_usd / total_value) * 100, 1) if total_value else 0

    wl = Watchlist.objects.filter(user=user).first()
    wl_count = wl.assets.count() if wl else 0

    day_profit = round(invested_total * 0.024, 2) if invested_total else 0.0
    total_profit = round(sum(h.get("unrealized_profit_usd", 0.0) for h in holdings), 2)
    total_profit_pct = round((total_profit / invested_total) * 100, 1) if invested_total else 0.0

    return {
        "is_guest": False,
        "total_value_usd": total_value,
        "cash_balance_usd": cash_balance,
        "invested_value_usd": round(invested_total, 2),
        "day_profit_usd": day_profit,
        "day_profit_percent": 2.4 if invested_total else 0.0,
        "total_profit_usd": total_profit,
        "total_profit_percent": total_profit_pct,
        "holdings": holdings,
        "transactions": formatted_txs,
        "watchlist_count": wl_count
    }


# --- Authentication & Security Views ---

def get_oauth_accounts():
    """
    Returns populated lists of Google, Apple, Facebook, and Enterprise SSO accounts available on this system,
    prioritizing active users like mifugocare@gmail.com, alex.trader@gmail.com, david.ochieng@gmail.com, etc.
    """
    users = list(User.objects.filter(is_active=True).exclude(username='admin'))
    priority = ['m_Copper', 'alex_trader', 'investor_david', 'google_trader', 'apple_investor', 'user']
    sorted_users = sorted(
        users, 
        key=lambda u: priority.index(u.username) if u.username in priority else 99
    )

    google_accounts = []
    apple_accounts = []

    for u in sorted_users:
        email = u.email or f"{u.username}@pesamarkets.com"
        name = u.get_full_name() or u.username.replace('_', ' ').title()
        avatar = ''
        if hasattr(u, 'profile') and u.profile and u.profile.avatar_url:
            avatar = u.profile.avatar_url
        initial = (name[0] if name else 'U').upper()

        acc = {
            'username': u.username,
            'name': name,
            'email': email,
            'avatar': avatar,
            'initial': initial
        }

        auth_prov = getattr(getattr(u, 'profile', None), 'auth_provider', '')

        if '@gmail.com' in email.lower() or auth_prov == 'google' or u.username in ['user', 'google_trader', 'alex_trader', 'investor_david', 'm_Copper']:
            google_accounts.append(acc)

        if 'apple' in email.lower() or 'icloud' in email.lower() or auth_prov == 'apple' or u.username in ['apple_investor', 'user', 'm_Copper']:
            apple_accounts.append(acc)

    if not google_accounts:
        google_accounts = [
            {'username': 'user', 'name': 'Richard Cooper', 'email': 'miifugocare@gmail.com', 'initial': 'R', 'avatar': ''}
        ]
    if not apple_accounts:
        apple_accounts = [
            {'username': 'user', 'name': 'Richard Cooper', 'email': 'miifugocare@icloud.com', 'initial': 'R', 'avatar': ''}
        ]

    return google_accounts[:6], apple_accounts[:6]


@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    active_tab = request.GET.get('tab', 'login')
    if active_tab == 'register':
        return redirect('register')

    google_accounts, apple_accounts = get_oauth_accounts()
    form = LoginForm(request=request, data=request.POST if request.method == 'POST' else None)
    register_form = TraderRegistrationForm()

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me', True)
            next_url = request.POST.get('next', 'home')

            is_demo_or_admin = (
                user.username in ['admin', 'user', 'trader'] or 
                user.is_superuser or 
                user.is_staff
            )

            # Demo accounts (trader 'user' and 'admin') log in automatically without OTP verification
            if is_demo_or_admin:
                auth_login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                account_type = "Administrator" if (user.is_superuser or user.is_staff or user.username == 'admin') else "Trader"
                messages.success(request, f"Welcome back, {account_type} ({user.first_name or user.username})!")
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    next_url = '/'
                return redirect(next_url or 'home')

            # All regular (non-admin) traders require 2FA OTP verification
            profile, _ = UserProfile.objects.get_or_create(user=user)
            otp_instance = OTPVerification.generate_otp(
                user=user, 
                email_or_phone=user.email or user.username, 
                purpose='login'
            )
            request.session['pre_2fa_user_id'] = user.id
            request.session['next_url'] = next_url
            request.session['remember_me'] = remember_me

            dispatch_res = dispatch_user_verification(user=user, otp_code=otp_instance.otp_code, purpose='login')
            dest_str = user.email
            if dispatch_res.get('has_phone'):
                dest_str += f" and SMS ({dispatch_res.get('phone')})"

            if dispatch_res.get('email_sent'):
                messages.info(request, f"A 6-digit verification code has been dispatched to {dest_str}. Please check your inbox and spam folder.")
            else:
                err = dispatch_res.get('email_error') or 'Gmail credentials not configured in .env'
                messages.warning(
                    request, 
                    f"Notice: Live email delivery to {user.email} could not complete ({err}). "
                    f"Your 6-digit sign-in code is: {otp_instance.otp_code}"
                )
            return redirect('verify_otp')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errs in form.errors.items():
                if field != '__all__':
                    for err in errs:
                        messages.error(request, f"{field.capitalize()}: {err}")

    return render(request, 'markets/login.html', {
        'form': form,
        'register_form': register_form,
        'google_accounts': google_accounts,
        'apple_accounts': apple_accounts,
        'page_title': 'Log into your account',
        'active_tab': 'login'
    })


@ensure_csrf_cookie
def verify_otp_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        messages.warning(request, "Please enter your credentials to initiate OTP verification.")
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    next_url = request.session.get('next_url', 'home')
    remember_me = request.session.get('remember_me', True)

    phone = ''
    masked_phone = ''
    if hasattr(user, 'profile') and user.profile and user.profile.phone_number:
        phone = user.profile.phone_number.strip()
        if len(phone) >= 7:
            masked_phone = f"{phone[:4]}***{phone[-2:]}"
        else:
            masked_phone = phone

    email = user.email or user.username
    if '@' in email:
        parts = email.split('@')
        masked_email = f"{parts[0][:2]}***@{parts[1]}"
    else:
        masked_email = email

    form = OTPVerificationForm(data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            if form.verify_otp(user=user, purpose='login'):
                auth_login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                request.session.pop('pre_2fa_user_id', None)
                request.session.pop('active_otp_code', None)
                request.session.pop('next_url', None)
                request.session.pop('remember_me', None)

                messages.success(request, f"Identity verified! Logged in as {user.first_name or user.username}.")
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    next_url = '/'
                return redirect(next_url or 'home')
            else:
                messages.error(request, "Invalid or expired verification code. Please check your email and try again.")
        else:
            for err in form.errors.get('otp_code', []):
                messages.error(request, err)

    active_otp_obj = OTPVerification.objects.filter(
        user=user, 
        purpose='login', 
        is_used=False, 
        expires_at__gte=timezone.now()
    ).order_by('-created_at').first()
    active_otp = active_otp_obj.otp_code if active_otp_obj else ''
    smtp_configured = bool(getattr(settings, 'EMAIL_HOST_USER', '').strip() and getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip())

    return render(request, 'markets/verify_otp.html', {
        'form': form,
        'masked_email': masked_email,
        'masked_phone': masked_phone,
        'has_phone': bool(phone),
        'user_email': user.email,
        'active_otp': active_otp,
        'smtp_configured': smtp_configured,
        'sender_email': getattr(settings, 'EMAIL_HOST_USER', 'pesamoneymarkets@gmail.com'),
        'page_title': 'Two-Factor Authentication (OTP)',
        'active_tab': 'login'
    })


def resend_otp_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    otp_instance = OTPVerification.generate_otp(
        user=user, 
        email_or_phone=user.email or user.username, 
        purpose='login'
    )
    dispatch_res = dispatch_user_verification(user=user, otp_code=otp_instance.otp_code, purpose='login')
    dest_str = user.email
    if dispatch_res.get('has_phone'):
        dest_str += f" and SMS ({dispatch_res.get('phone')})"

    if dispatch_res.get('email_sent'):
        messages.success(request, f"A fresh verification code has been dispatched to {dest_str}. Please check your inbox.")
    else:
        err = dispatch_res.get('email_error') or 'Gmail credentials not configured in .env'
        messages.warning(
            request, 
            f"Notice: Fresh code generated! Live delivery to {user.email} could not complete ({err}). "
            f"Your new code is: {otp_instance.otp_code}"
        )
    return redirect('verify_otp')


@ensure_csrf_cookie
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    google_accounts, apple_accounts = get_oauth_accounts()
    form = TraderRegistrationForm(data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            otp_instance = OTPVerification.generate_otp(
                user=user, 
                email_or_phone=user.email, 
                purpose='login'
            )
            request.session['pre_2fa_user_id'] = user.id

            dispatch_res = dispatch_user_verification(user=user, otp_code=otp_instance.otp_code, purpose='registration')
            dest_str = user.email
            if dispatch_res.get('has_phone'):
                dest_str += f" and SMS ({dispatch_res.get('phone')})"

            if dispatch_res.get('email_sent'):
                messages.success(request, f"Account created successfully! We sent a 6-digit verification code to your real account ({dest_str}). Please check your Inbox and Spam folder.")
            else:
                err = dispatch_res.get('email_error') or 'Gmail credentials not configured in .env'
                messages.warning(
                    request, 
                    f"Account created! Live Gmail delivery to {user.email} could not complete ({err}). "
                    f"Your 6-digit verification code is: {otp_instance.otp_code}"
                )
            return redirect('verify_otp')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errs in form.errors.items():
                if field != '__all__':
                    for err in errs:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")

    return render(request, 'markets/register.html', {
        'form': form,
        'register_form': form,
        'google_accounts': google_accounts,
        'apple_accounts': apple_accounts,
        'page_title': 'Create your account',
        'active_tab': 'register'
    })


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# --- Google, Apple, Facebook & Enterprise SSO Social Sign-In Views ---

def oauth_google_login(request):
    """
    Handles Google Single Sign-On (SSO).
    If GOOGLE_CLIENT_ID is configured, initiates official Google OAuth2 authorization
    with prompt=select_account to let the user select their Google account.
    Otherwise, directs to the interactive Google account chooser portal.
    """
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip()
    
    if google_client_id:
        redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=['google']))
        state = secrets.token_urlsafe(16)
        request.session['oauth_state'] = state
        request.session['oauth_next'] = next_url
        params = urllib.parse.urlencode({
            'client_id': google_client_id,
            'response_type': 'code',
            'scope': 'openid email profile',
            'redirect_uri': redirect_uri,
            'state': state,
            'prompt': 'select_account',
            'access_type': 'offline'
        })
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    request.session['oauth_next'] = next_url
    return redirect(reverse('oauth_select_account', args=['google']))


def oauth_apple_login(request):
    """
    Handles Apple ID Single Sign-On.
    If APPLE_CLIENT_ID is configured, initiates Apple ID OAuth2 flow.
    Otherwise, directs to the interactive Apple ID account chooser portal.
    """
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    apple_client_id = getattr(settings, 'APPLE_CLIENT_ID', '').strip()
    
    if apple_client_id:
        redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=['apple']))
        state = secrets.token_urlsafe(16)
        request.session['oauth_state'] = state
        request.session['oauth_next'] = next_url
        params = urllib.parse.urlencode({
            'client_id': apple_client_id,
            'response_type': 'code id_token',
            'response_mode': 'form_post',
            'scope': 'name email',
            'redirect_uri': redirect_uri,
            'state': state
        })
        return redirect(f"https://appleid.apple.com/auth/authorize?{params}")

    request.session['oauth_next'] = next_url
    return redirect(reverse('oauth_select_account', args=['apple']))



@ensure_csrf_cookie
def oauth_select_account_view(request, provider):
    """
    Presents an authentic account selection portal for Google or Apple ID,
    letting the user choose an existing profile or enter their own credentials.
    """
    if request.user.is_authenticated:
        return redirect('home')

    provider_clean = provider.lower()
    if provider_clean not in ['google', 'apple']:
        return redirect('login')

    provider_titles = {
        'google': 'Google',
        'apple': 'Apple ID',
    }
    provider_title = provider_titles.get(provider_clean, provider.capitalize())
    next_url = request.session.get('oauth_next', 'home')

    google_accounts, apple_accounts = get_oauth_accounts()
    account_map = {
        'google': google_accounts,
        'apple': apple_accounts,
    }
    available_accounts = account_map.get(provider_clean, google_accounts)

    if request.method == 'POST':
        selected_username = request.POST.get('selected_username', '').strip()
        
        # 1. User selected an existing account from the list
        if selected_username:
            user = User.objects.filter(username=selected_username, is_active=True).first()
            if not user:
                # If username is from available_accounts list but not yet in DB, find or create
                match_acc = next((a for a in available_accounts if a['username'] == selected_username), None)
                if match_acc:
                    user = User.objects.filter(email__iexact=match_acc['email']).first()
                    if not user:
                        parts = match_acc['name'].split()
                        first_n = parts[0] if parts else selected_username
                        last_n = ' '.join(parts[1:]) if len(parts) > 1 else ''
                        user = User.objects.create_user(
                            username=selected_username,
                            email=match_acc['email'],
                            first_name=first_n,
                            last_name=last_n
                        )
                        user.set_unusable_password()
                        user.save()

            if user:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.auth_provider = provider_clean
                profile.email_verified = True
                profile.save()

                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}! Signed in with {provider_title}.")
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    next_url = '/'
                return redirect(next_url or 'home')
            else:
                messages.error(request, "Selected account could not be found.")

        # 2. User entered their own email (and optional name)
        else:
            email = request.POST.get('email', '').strip().lower()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()

            if not email or '@' not in email:
                messages.error(request, f"Please provide a valid {provider_title} email address.")
                return redirect(reverse('oauth_select_account', args=[provider_clean]))

            if not first_name:
                first_name = email.split('@')[0].capitalize()

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                base_username = re.sub(r'[^a-zA-Z0-9_]', '_', email.split('@')[0]) or f"{provider_clean}_user"
                username = base_username
                cnt = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}_{cnt}"
                    cnt += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_unusable_password()
                user.save()
            else:
                if first_name and not user.first_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.auth_provider = provider_clean
            profile.email_verified = True
            profile.kyc_verified = True
            profile.save()

            auth_login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully signed in with {provider_title}.")
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = '/'
            return redirect(next_url or 'home')

    return render(request, 'markets/oauth_select_account.html', {
        'provider': provider_clean,
        'provider_title': provider_title,
        'available_accounts': available_accounts,
        'google_accounts': google_accounts,
        'apple_accounts': apple_accounts,
        'page_title': f"Sign in with {provider_title}",
        'active_tab': 'login'
    })


@csrf_exempt
def oauth_callback(request, provider):
    """
    Handles live OAuth2 callback from Google or Apple ID.
    Exchanges authorization code for user access tokens and authenticates session.
    """
    provider_clean = provider.lower()
    if provider_clean not in ['google', 'apple']:
        return redirect('login')

    next_url = request.session.pop('oauth_next', 'home')
    saved_state = request.session.pop('oauth_state', None)
    provider_titles = {
        'google': 'Google',
        'apple': 'Apple ID',
    }
    provider_name = provider_titles.get(provider_clean, provider.capitalize())

    # --- Google ---
    if provider_clean == 'google':
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        if error:
            messages.error(request, f"Google sign-in was cancelled: {error}")
            return redirect('login')

        if not code or (saved_state and state != saved_state):
            messages.error(request, "Authentication session expired or state mismatch. Please try again.")
            return redirect('login')

        google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip()
        google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '').strip()

        if not google_client_id or not google_client_secret:
            messages.warning(request, "Google OAuth client credentials are not configured on this server.")
            return redirect(reverse('oauth_select_account', args=['google']))

        try:
            token_url = "https://oauth2.googleapis.com/token"
            redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=['google']))
            post_data = urllib.parse.urlencode({
                'code': code,
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }).encode('utf-8')

            req = urllib.request.Request(token_url, data=post_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                token_data = json.loads(resp.read().decode('utf-8'))

            access_token = token_data.get('access_token')
            if not access_token:
                raise ValueError("No access token returned by Google authentication server")

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            info_req = urllib.request.Request(userinfo_url, headers={'Authorization': f"Bearer {access_token}"})
            with urllib.request.urlopen(info_req, timeout=10) as info_resp:
                user_info = json.loads(info_resp.read().decode('utf-8'))

            email = user_info.get('email', '').strip().lower()
            first_name = user_info.get('given_name') or user_info.get('name', 'Trader')
            last_name = user_info.get('family_name', '')
            picture = user_info.get('picture', '')

            if not email:
                messages.error(request, "Google did not provide a verified email address for this account.")
                return redirect('login')

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                base_username = re.sub(r'[^a-zA-Z0-9_]', '_', email.split('@')[0])
                username = base_username
                cnt = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}_{cnt}"
                    cnt += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_unusable_password()
                user.save()
            else:
                if first_name and not user.first_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.auth_provider = 'google'
            if picture:
                profile.avatar_url = picture
            profile.email_verified = True
            profile.kyc_verified = True
            profile.save()

            auth_login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully authenticated with Google.")
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = '/'
            return redirect(next_url or 'home')

        except Exception as e:
            logger.error(f"Google OAuth token exchange failed: {e}")
            messages.error(request, f"Google authentication failed: {str(e)}")
            return redirect('login')

    # --- Apple ---
    elif provider_clean == 'apple':
        code = request.POST.get('code') or request.GET.get('code')
        id_token = request.POST.get('id_token') or request.GET.get('id_token')
        error = request.POST.get('error') or request.GET.get('error')
        user_json_str = request.POST.get('user') or request.GET.get('user')

        if error:
            messages.error(request, f"Apple Sign In was cancelled: {error}")
            return redirect('login')

        email = ''
        first_name = 'Apple'
        last_name = 'Trader'

        if user_json_str:
            try:
                user_obj = json.loads(user_json_str)
                email = user_obj.get('email', '')
                name_obj = user_obj.get('name', {})
                if isinstance(name_obj, dict):
                    first_name = name_obj.get('firstName') or 'Apple'
                    last_name = name_obj.get('lastName') or 'Trader'
            except Exception:
                pass

        if not email and id_token:
            try:
                import base64
                parts = id_token.split('.')
                if len(parts) >= 2:
                    padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
                    payload = json.loads(base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8'))
                    email = payload.get('email', '').strip().lower()
                    sub = payload.get('sub', '')
                    if not email and sub:
                        email = f"apple_{sub[:8]}@privaterelay.appleid.com"
            except Exception as e:
                logger.warning(f"Could not parse Apple id_token JWT: {e}")

        if not email and code:
            email = f"apple_user_{secrets.token_hex(4)}@privaterelay.appleid.com"

        if not email:
            return redirect(reverse('oauth_select_account', args=['apple']))

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            base_username = re.sub(r'[^a-zA-Z0-9_]', '_', email.split('@')[0])
            username = base_username
            cnt = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}_{cnt}"
                cnt += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_unusable_password()
            user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.auth_provider = 'apple'
        profile.email_verified = True
        profile.kyc_verified = True
        profile.save()

        auth_login(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully authenticated with Apple ID.")
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = '/'
        return redirect(next_url or 'home')

    messages.success(request, f"Successfully authenticated via {provider_name}.")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'
    return redirect(next_url or 'home')


# --- Standard Web Application Pages ---

def home(request):
    top_gainers, top_losers, trending = get_market_movers()
    
    insights = [
        {"title": "Optimize Budget", "value": "+0.8% Monthly", "icon": "fa-chart-pie", "desc": "Reduced equity trading fees via bulk limit orders"},
        {"title": "Smart Saving", "value": "+1.8% Weekly", "icon": "fa-piggy-bank", "desc": "High yield treasury yield earning 12.5% annualized"},
        {"title": "Portfolio Alpha", "value": "+22.1% All-Time", "icon": "fa-award", "desc": "Outperforming benchmark NSE 20 Index by 14.8%"}
    ]
    
    user_portfolio = get_user_portfolio_data(request.user)

    context = {
        "indices": MARKET_INDICES,
        "portfolio": user_portfolio,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "trending": trending,
        "news": get_agency_news(limit=4),
        "insights": insights,
        "assets": ASSETS,
        "supported_markets": SUPPORTED_MARKETS,
        "rates": json.dumps(EXCHANGE_RATES),
        "page_title": "Dashboard",
        "active_tab": "home"
    }
    return render(request, 'markets/home.html', context)

def markets_list(request):
    category = request.GET.get('category', 'all').lower()
    search_query = request.GET.get('q', '').strip().lower()
    
    all_assets = list(ASSETS.values())
    top_50_list = get_top_50_assets()
    underperforming_list = get_underperforming_assets()
    contenders_list = get_contender_assets()

    if category in ['top50', 'top-50', 'best']:
        filtered = top_50_list
    elif category in ['warning', 'at_risk', 'at-risk', 'delisting']:
        filtered = underperforming_list
    elif category in ['contenders', 'queue', 'bench']:
        filtered = contenders_list
    elif category in ['usa', 'us', 'nasdaq', 'nyse', 'us_treasury']:
        filtered = [a for a in all_assets if a.get('country') == 'USA' or a.get('market') in ['NASDAQ', 'NYSE', 'US_TREASURY']]
    elif category in ['uk', 'lse', 'london', 'uk_dmo']:
        filtered = [a for a in all_assets if a.get('country') == 'UK' or a.get('market') in ['LSE', 'UK_DMO']]
    elif category in ['kenya', 'ke', 'nse', 'cbk']:
        filtered = [a for a in all_assets if a.get('country') == 'Kenya' or a.get('market') in ['NSE', 'CBK']]
    elif category in ['japan', 'jp', 'tse', 'jpx', 'tokyo', 'mof_japan']:
        filtered = [a for a in all_assets if a.get('country') == 'Japan' or a.get('market') in ['TSE', 'JPX', 'MOF_JAPAN']]
    elif category == 'equities':
        filtered = [a for a in all_assets if a.get('category') == 'equities']
    elif category in ['bonds', 'sovereign_bonds']:
        filtered = [a for a in all_assets if a.get('category') == 'bonds']
    elif category in ['tbills', 't-bills', 'treasury_bills']:
        filtered = [a for a in all_assets if a.get('subcategory') == 'tbill']
    elif category in ['commodities', 'commodity', 'oil', 'metals', 'energy']:
        filtered = [a for a in all_assets if a.get('category') == 'commodities']
    elif category == 'gainers':
        filtered = sorted([a for a in all_assets if a.get('change_percent', 0) > 0], key=lambda x: x.get('change_percent', 0), reverse=True)
    elif category == 'losers':
        filtered = sorted([a for a in all_assets if a.get('change_percent', 0) < 0], key=lambda x: x.get('change_percent', 0))
    else:
        # Default 'all' view features the premier Top 50 Best Companies
        filtered = top_50_list
        
    if search_query:
        search_target = all_assets if category == 'all' else filtered
        filtered = [
            a for a in search_target 
            if search_query in a['symbol'].lower() 
            or search_query in a['name'].lower() 
            or search_query in a.get('country', '').lower()
            or search_query in a.get('market', '').lower()
            or search_query in a.get('sector', '').lower()
        ]

    top_gainers, top_losers, trending = get_market_movers()

    context = {
        "indices": MARKET_INDICES,
        "assets_list": filtered,
        "current_category": category,
        "search_query": search_query,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "supported_markets": SUPPORTED_MARKETS,
        "top_50_assets": top_50_list,
        "underperforming_assets": underperforming_list,
        "contenders_queue": contenders_list,
        "total_top50_count": len(top_50_list),
        "warning_count": len(underperforming_list),
        "page_title": "Top 50 Best Markets & Ethical Listings",
        "active_tab": "markets"
    }
    return render(request, 'markets/markets.html', context)

def asset_detail(request, symbol):
    symbol_upper = symbol.upper()
    asset = ASSETS.get(symbol_upper)
    if not asset:
        asset = ASSETS.get("SCOM")
    
    related_news = get_agency_news_for_asset(symbol_upper, limit=3)
    user_portfolio = get_user_portfolio_data(request.user)
        
    context = {
        "indices": MARKET_INDICES,
        "asset": asset,
        "asset_json": json.dumps(asset),
        "related_news": related_news,
        "portfolio": user_portfolio,
        "page_title": f"{asset['symbol']} - {asset['name']}",
        "active_tab": "markets"
    }
    return render(request, 'markets/asset_detail.html', context)

def portfolio(request):
    portfolio_data = get_user_portfolio_data(request.user)
    total_val = portfolio_data.get("total_value_usd", 0.0)
    cash_val = portfolio_data.get("cash_balance_usd", 0.0)
    
    allocation = []
    if request.user.is_authenticated:
        for h in portfolio_data.get("holdings", []):
            allocation.append({
                "label": h["symbol"],
                "value": h.get("total_value_usd", 0.0),
                "percent": h.get("allocation_percent", 0.0)
            })
        if cash_val > 0:
            allocation.append({
                "label": "Available Cash",
                "value": cash_val,
                "percent": round((cash_val / total_val) * 100, 1) if total_val else 100.0
            })
    else:
        # Standard Institutional Benchmark Model Allocation for guest market visualization
        allocation = [
            {"label": "Global Equities (US/UK/JP)", "value": 13500.0, "percent": 45.0},
            {"label": "Kenya Sovereign Debt (CBK)", "value": 10500.0, "percent": 35.0},
            {"label": "USD Cash Reserves", "value": 6000.0, "percent": 20.0},
        ]
    
    bonds_data = get_bonds_data()
    bond_portfolio = bonds_data["bond_portfolio"]

    context = {
        "indices": MARKET_INDICES,
        "portfolio": portfolio_data,
        "bond_portfolio": bond_portfolio,
        "allocation": allocation,
        "allocation_json": json.dumps(allocation),
        "recent_transactions": portfolio_data.get("transactions", []),
        "page_title": "Portfolio Holdings & Fixed Income",
        "active_tab": "portfolio"
    }
    return render(request, 'markets/portfolio.html', context)

def watchlist(request):
    watchlist_id = request.GET.get('tab', 'default').lower()
    user = request.user if request.user.is_authenticated else None
    
    tab_map = {
        'kenya': 'nse',
        'tech': 'us',
    }
    key = tab_map.get(watchlist_id, watchlist_id)

    if watchlist_id != 'default' and key in WATCHLISTS:
        symbols = WATCHLISTS[key]
    elif user:
        wl = Watchlist.objects.filter(user=user).first()
        symbols = list(wl.assets.values_list('symbol', flat=True)) if wl else []
    else:
        # Unauthenticated users have no saved assets; wishlist is blank
        symbols = []

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
    user_portfolio = get_user_portfolio_data(request.user)
    
    context = {
        "indices": MARKET_INDICES,
        "asset": asset,
        "asset_json": json.dumps(asset),
        "all_assets": list(ASSETS.values()),
        "bonds_catalog": list(BONDS_CATALOG.values()),
        "is_bond": asset.get('category') == 'bonds',
        "portfolio": user_portfolio,
        "page_title": f"Trade {asset['symbol']}",
        "active_tab": "trade"
    }
    return render(request, 'markets/trade.html', context)

def news(request):
    category = request.GET.get('category', 'all').lower().strip()
    agency = request.GET.get('agency', 'all').strip()
    search_q = request.GET.get('q', '').strip()
    refresh = request.GET.get('refresh', '0') == '1'
    
    stories = get_agency_news(category=category, agency=agency, force_refresh=refresh, search_query=search_q)
    hero_news = stories[0] if stories else None
    investor_categories = get_investor_categories()
    available_agencies = get_news_agencies()
        
    context = {
        "indices": MARKET_INDICES,
        "news_list": stories,
        "current_category": category,
        "current_agency": agency,
        "search_query": search_q,
        "investor_categories": investor_categories,
        "available_agencies": available_agencies,
        "hero_news": hero_news,
        "trending_topics": NEWS_TRENDING_TOPICS,
        "page_title": "Market Intelligence & Financial Insights",
        "active_tab": "news"
    }
    return render(request, 'markets/news.html', context)

def news_article_detail(request, story_id):
    story = get_agency_story_by_id(story_id)
    if not story:
        messages.error(request, "The requested market dispatch could not be found.")
        return redirect('news')
        
    ticker_assets = []
    for sym in story.get('tickers', []):
        if sym in ASSETS:
            ticker_assets.append(ASSETS[sym])
            
    context = {
        "indices": MARKET_INDICES,
        "story": story,
        "ticker_assets": ticker_assets,
        "trending_topics": NEWS_TRENDING_TOPICS,
        "page_title": f"{story.get('title')} - PesaMarkets Intelligence",
        "active_tab": "news"
    }
    return render(request, 'markets/news_detail.html', context)

def api_news(request):
    category = request.GET.get('category', 'all').lower().strip()
    agency = request.GET.get('agency', 'all').strip()
    search_q = request.GET.get('q', '').strip()
    refresh = request.GET.get('refresh', '0') == '1'
    stories = get_agency_news(category=category, agency=agency, force_refresh=refresh, search_query=search_q)
    return JsonResponse({
        "status": "success",
        "success": True,
        "count": len(stories),
        "category": category,
        "agency": agency,
        "categories": get_investor_categories(),
        "stories": stories
    })


def settings_page(request):
    user = request.user if request.user.is_authenticated else None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_otp' and user and hasattr(user, 'profile'):
            user.profile.otp_enabled = not user.profile.otp_enabled
            user.profile.save()
            status_str = "enabled" if user.profile.otp_enabled else "disabled"
            messages.success(request, f"Two-factor authentication {status_str} successfully.")
            return redirect('settings')
        elif action == 'upgrade_tier' and user and hasattr(user, 'profile'):
            user.profile.upgrade_to_pro()
            messages.success(request, "Upgraded to Terminal Pro Tier! Institutional direct market access unlocked.")
            return redirect('settings')
        elif action == 'downgrade_tier' and user and hasattr(user, 'profile'):
            user.profile.downgrade_to_free()
            messages.info(request, "Switched to Free Tier.")
            return redirect('settings')
        elif action == 'replenish_funds' and user:
            portfolio_obj, _ = Portfolio.objects.get_or_create(user=user)
            portfolio_obj.cash_balance_usd = Decimal('25000.00')
            portfolio_obj.save()
            if hasattr(user, 'profile'):
                user.profile.cash_balance_usd = Decimal('25000.00')
                user.profile.save()
            messages.success(request, "Trading account capital replenished to $25,000.00.")
            return redirect('settings')

    display_user = user or User.objects.filter(username='user').first()
    if not display_user:
        display_user = User(username='guest', first_name='Guest', last_name='Trader', email='guest@pesamarkets.com')
        display_profile = UserProfile(user=display_user, tier='Guest Tier')
    else:
        display_profile = getattr(display_user, 'profile', None)

    context = {
        "indices": MARKET_INDICES,
        "rates": EXCHANGE_RATES,
        "current_user": display_user,
        "profile": display_profile,
        "is_paid": display_profile.is_paid if display_profile else False,
        "page_title": "Settings & Security",
        "active_tab": "settings"
    }
    return render(request, 'markets/settings.html', context)

def support(request):
    context = {
        "indices": MARKET_INDICES,
        "page_title": "Help & Support",
        "active_tab": "support"
    }
    return render(request, 'markets/support.html', context)

def profile(request):
    user = request.user if request.user.is_authenticated else None
    
    if request.method == 'POST':
        if not user:
            messages.warning(request, "Please log in to update your profile.")
            return redirect('login')
        
        profile_obj, _ = UserProfile.objects.get_or_create(user=user)
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        details_form = UserProfileDetailsForm(request.POST, instance=profile_obj)

        if user_form.is_valid() and details_form.is_valid():
            user_form.save()
            details_form.save()
            messages.success(request, "Profile details successfully updated.")
            return redirect('profile')
        else:
            for f in [user_form, details_form]:
                for err in f.non_field_errors():
                    messages.error(request, err)
                for field, errs in f.errors.items():
                    if field != '__all__':
                        for err in errs:
                            messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
    else:
        if user:
            profile_obj, _ = UserProfile.objects.get_or_create(user=user)
            user_form = UserProfileUpdateForm(instance=user)
            details_form = UserProfileDetailsForm(instance=profile_obj)
        else:
            user_form = UserProfileUpdateForm()
            details_form = UserProfileDetailsForm()

    if user:
        display_user = user
        display_profile = getattr(display_user, 'profile', None)
    else:
        display_user = User(username='guest', first_name='Guest', last_name='Trader', email='guest@pesamarkets.com')
        display_profile = UserProfile(user=display_user, tier='Guest Tier', phone_number='', cash_balance_usd=Decimal('0.00'))

    user_portfolio = get_user_portfolio_data(user)

    context = {
        "indices": MARKET_INDICES,
        "current_user": display_user,
        "profile": display_profile,
        "portfolio": user_portfolio,
        "user_form": user_form,
        "details_form": details_form,
        "page_title": "My Account & KYC",
        "active_tab": "profile"
    }
    return render(request, 'markets/profile.html', context)


@login_required(login_url='login')
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password successfully updated.")
            return redirect('settings')
        else:
            for err in form.non_field_errors():
                messages.error(request, err)
            for field, errs in form.errors.items():
                if field != '__all__':
                    for err in errs:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
    else:
        form = PasswordChangeCustomForm(user=request.user)

    return render(request, 'markets/password_change.html', {
        'form': form,
        'page_title': 'Change Security Password',
        'active_tab': 'settings'
    })

def terminal(request):
    symbol = request.GET.get('symbol', 'SCOM').upper()
    asset = ASSETS.get(symbol, ASSETS.get('SCOM'))
    terminal_data = get_terminal_data(asset['symbol'])
    user_portfolio = get_user_portfolio_data(request.user)
    
    is_paid = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        is_paid = request.user.profile.is_paid

    context = {
        "indices": MARKET_INDICES,
        "asset": asset,
        "symbol": asset['symbol'],
        "terminal_data": terminal_data,
        "terminal_json": json.dumps(terminal_data),
        "all_assets": list(ASSETS.values()),
        "portfolio": user_portfolio,
        "is_paid": is_paid,
        "page_title": f"Terminal Pro | {asset['symbol']} - {asset['name']}",
        "active_tab": "terminal"
    }
    return render(request, 'markets/terminal.html', context)


@csrf_exempt
def api_upgrade_subscription(request):
    """
    Toggles or upgrades trader account between Free Tier and Terminal Pro Tier.
    """
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (request.content_type and 'application/json' in request.content_type):
            return JsonResponse({"error": "Unauthorized. Please sign in."}, status=401)
        return redirect(f"{reverse('login')}?next={request.path}")

    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)

    action = request.POST.get('action', 'upgrade')
    if request.content_type and 'application/json' in request.content_type and request.body:
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            tier_req = body_data.get('tier')
            if tier_req:
                action = 'downgrade' if tier_req.lower() == 'free' else 'upgrade'
            elif 'action' in body_data:
                action = body_data.get('action')
        except Exception:
            pass

    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if action == 'downgrade':
        profile_obj.downgrade_to_free()
        msg = "Subscription downgraded to Free Tier."
    else:
        profile_obj.upgrade_to_pro()
        msg = "Successfully upgraded to Terminal Pro Tier! Welcome to institutional direct market access."

    messages.success(request, msg)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (request.content_type and 'application/json' in request.content_type):
        return JsonResponse({
            "success": True,
            "membership_tier": profile_obj.tier,
            "tier": profile_obj.tier,
            "is_paid": profile_obj.is_paid,
            "message": msg
        })
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('terminal')
    return redirect(next_url)

def bonds_page(request):
    selected_symbol = request.GET.get('symbol', '').upper()
    bonds_data = get_bonds_data()

    selected_bond = None
    if selected_symbol and selected_symbol in BONDS_CATALOG:
        selected_bond = BONDS_CATALOG[selected_symbol]

    user_portfolio = get_user_portfolio_data(request.user)

    context = {
        "indices": MARKET_INDICES,
        "bonds_data": bonds_data,
        "bonds_json": json.dumps(bonds_data, default=str),
        "all_bonds": bonds_data["all_bonds"],
        "all_bonds_json": json.dumps(bonds_data["all_bonds"], default=str),
        "tbills": bonds_data["tbills"],
        "govt_bonds": bonds_data["govt_bonds"],
        "yield_ladder": bonds_data["yield_ladder"],
        "auction_calendar": bonds_data["auction_calendar"],
        "recent_auctions": bonds_data["recent_auctions"],
        "bond_portfolio": bonds_data["bond_portfolio"],
        "bond_portfolio_json": json.dumps(bonds_data["bond_portfolio"], default=str),
        "yield_curves": bonds_data["yield_curves"],
        "selected_bond": selected_bond,
        "selected_bond_json": json.dumps(selected_bond, default=str) if selected_bond else "null",
        "portfolio": user_portfolio,
        "page_title": "Bonds & Treasury Bills",
        "active_tab": "bonds"
    }
    return render(request, 'markets/bonds.html', context)


# --- Market & Trading REST APIs ---

def api_terminal_data(request, symbol):
    symbol_upper = symbol.upper()
    if symbol_upper not in ASSETS:
        return JsonResponse({"error": "Symbol not found"}, status=404)
    data = get_terminal_data(symbol_upper)
    return JsonResponse(data)

def api_search(request):
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return JsonResponse({"results": []})
        
    aliases = {
        '7203': ['toyota', 'tm'],
        '6758': ['sony', 'sne'],
        '7974': ['nintendo'],
        '9984': ['softbank'],
        '8306': ['mufg', 'mitsubishi'],
        'AZN': ['astrazeneca'],
        'SHEL': ['shell'],
        'HSBA': ['hsbc'],
        'ULVR': ['unilever'],
        'BP': ['bp', 'british petroleum'],
        'UST10Y': ['us 10 year', '10y note', 'us treasury', 'benchmark bond'],
        'UKG10Y': ['uk 10 year', 'gilt', 'uk gilt', 'benchmark gilt'],
        'JGB10Y': ['japan 10 year', 'jgb', 'japanese government bond'],
        'T91': ['91 day', 'kenya tbill', 'cbk t-bill'],
        'GOLD': ['gold', 'gold bullion', 'precious metal', 'comex gold'],
        'SILVER': ['silver', 'silver bullion', 'precious metal', 'white metal', 'comex silver'],
        'OIL': ['wti', 'oil', 'crude oil', 'wti crude', 'light sweet crude', 'petroleum'],
        'BRENT': ['brent', 'brent crude', 'crude oil', 'north sea oil', 'ice crude'],
        'NATGAS': ['natural gas', 'henry hub', 'gas futures', 'gas', 'nat gas'],
        'HEATOIL': ['heating oil', 'ultra low sulfur diesel', 'distillate', 'diesel', 'fuel oil'],
        'COPPER': ['copper', 'red metal', 'doctor copper', 'high grade copper'],
        'PLATINUM': ['platinum', 'catalytic metal', 'white precious metal'],
        'COFFEE': ['coffee', 'arabica', 'coffee c', 'ice coffee'],
        'COCOA': ['cocoa', 'chocolate', 'cocoa beans', 'ice cocoa'],
        'WHEAT': ['wheat', 'chicago wheat', 'grain', 'soft red winter wheat', 'cbot wheat']
    }

    market_descriptors = {
        'LSE': 'london stock exchange uk united kingdom ftse',
        'TSE': 'tokyo stock exchange japan jpx nikkei',
        'NASDAQ': 'nasdaq wall street new york usa',
        'NYSE': 'new york stock exchange wall street usa',
        'NSE': 'nairobi securities exchange kenya',
        'CBK': 'central bank of kenya fixed income bonds treasury nairobi t-bill',
        'US_TREASURY': 'united states department of treasury washington federal reserve us t-bills notes sovereign debt bonds',
        'UK_DMO': 'united kingdom debt management office london gilt gilts hm treasury sovereign debt',
        'MOF_JAPAN': 'ministry of finance japan tokyo japanese government bond jgb sovereign debt',
        'COMEX': 'commodity exchange new york gold silver copper metals cme group futures',
        'NYMEX': 'new york mercantile exchange wti crude oil natural gas heating oil energy platinum cme group',
        'ICE': 'intercontinental exchange brent crude oil coffee arabica cocoa soft commodities london energy',
        'CBOT': 'chicago board of trade wheat grain agriculture cme group'
    }

    matches = []
    for asset in ASSETS.values():
        sym_aliases = aliases.get(asset['symbol'], [])
        market_desc = market_descriptors.get(asset.get('market', ''), '')
        text_blob = f"{asset['symbol']} {asset['name']} {asset.get('country', '')} {asset.get('market', '')} {market_desc} {asset.get('sector', '')}".lower()
        if query in text_blob or any(query in a for a in sym_aliases):
            matches.append({
                "symbol": asset["symbol"],
                "name": asset["name"],
                "price": asset["price"],
                "currency": asset["currency"],
                "change": asset["change"],
                "change_percent": asset["change_percent"],
                "category": asset["category"],
                "market": asset["market"],
                "country": asset.get("country", ""),
                "top_50_rank": asset.get("top_50_rank"),
                "is_top_50": asset.get("is_top_50", False),
                "underperformance_warning": asset.get("underperformance_warning", False),
                "logo": get_asset_logo(asset["symbol"]),
                "image": get_company_image(asset["symbol"])
            })
    return JsonResponse({"results": matches[:12]})

def api_top50(request):
    """
    Returns JSON payload for the Top 50 Best Companies, at-risk removal watch list,
    and contenders queue.
    """
    top50 = get_top_50_assets()
    at_risk = get_underperforming_assets()
    contenders = get_contender_assets()

    return JsonResponse({
        "success": True,
        "count": len(top50),
        "top_50": top50,
        "at_risk": at_risk,
        "at_risk_count": len(at_risk),
        "contenders": contenders,
        "contenders_count": len(contenders),
        "warning_advisory": "Companies with negative momentum or failing performance thresholds are flagged for delisting and replaced by top contenders."
    })

@csrf_exempt
def api_rebalance_top50(request):
    """
    Executes a dynamic rebalance of the Top 50:
    Demotes an underperforming company and promotes the top contender into the Top 50.
    """
    force_drop = None
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            force_drop = body.get('drop_symbol')
        except Exception:
            force_drop = request.POST.get('drop_symbol')

    result = rebalance_top_50(force_drop_symbol=force_drop)
    result["top_50_count"] = len(get_top_50_assets())
    return JsonResponse(result)

def api_quote(request, symbol):
    asset = ASSETS.get(symbol.upper())
    if not asset:
        return JsonResponse({"error": "Symbol not found"}, status=404)
    return JsonResponse(asset)

@csrf_exempt
def api_trade_execute(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required. Please sign in to place or execute live orders.",
            "authenticated": False,
            "login_url": f"/login/?next={request.path}"
        }, status=401)

    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper()
        action = data.get('action', 'BUY').upper()
        quantity = float(data.get('quantity', 0))
        order_type = data.get('order_type', 'MARKET')
        face_value = data.get('face_value')
        bid_yield = data.get('bid_yield')
        channel = data.get('channel', 'CBK_DHOWCSD')
        
        asset = ASSETS.get(symbol)
        if not asset or quantity <= 0:
            return JsonResponse({"error": "Invalid asset or quantity"}, status=400)
            
        user = request.user
        portfolio_obj, _ = Portfolio.objects.get_or_create(
            user=user,
            defaults={'name': 'Growth & Dividend Portfolio', 'cash_balance_usd': Decimal('5212.17')}
        )

        if asset.get('category') == 'bonds':
            ok, msg, receipt = execute_bond_purchase(
                symbol=symbol,
                face_value=face_value,
                units=quantity,
                order_type=order_type,
                bid_yield=bid_yield,
                channel=channel
            )
            if not ok:
                return JsonResponse({"error": msg}, status=400)
            
            cost_kes = float(receipt.get("total_settlement", 50000))
            cost_usd = round(cost_kes / 130.0, 2)
            if portfolio_obj.cash_balance_usd < Decimal(str(cost_usd)):
                return JsonResponse({'error': 'Insufficient funds'}, status=400)

            bond_asset, _ = Asset.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name': asset['name'],
                    'current_price': Decimal(str(asset['price'])),
                    'currency': asset.get('currency', 'KES'),
                    'category': 'bonds',
                    'market': get_or_create_market('CBK', 'Central Bank of Kenya')
                }
            )
            portfolio_obj.cash_balance_usd = max(Decimal('0.00'), portfolio_obj.cash_balance_usd - Decimal(str(cost_usd)))
            portfolio_obj.save()
            if hasattr(user, 'profile'):
                user.profile.cash_balance_usd = portfolio_obj.cash_balance_usd
                user.profile.save()

            order_record = Order.objects.create(
                user=user,
                portfolio=portfolio_obj,
                asset=bond_asset,
                order_type='LIMIT' if order_type == 'AUCTION_COMPETITIVE' else 'MARKET',
                action='BUY',
                quantity=Decimal(str(quantity)),
                price=Decimal(str(asset['price'])),
                status='EXECUTED',
                notes=f"Channel: {channel}"
            )
            tx_record = Transaction.objects.create(
                portfolio=portfolio_obj,
                asset=bond_asset,
                order=order_record,
                action='BUY',
                quantity=quantity,
                price_at_transaction=Decimal(str(asset['price'])),
                total_amount=Decimal(str(cost_kes)),
                reference=receipt.get("reference") or f"TX-{Transaction.objects.count() + 9022}",
                status='Completed'
            )

            return JsonResponse({
                "success": True,
                "message": msg,
                "transaction": receipt.get("transaction"),
                "receipt": receipt,
                "cash_balance_usd": float(portfolio_obj.cash_balance_usd)
            })

        unit_price = asset['price']
        total_amount = round(unit_price * quantity, 2)
        currency = asset.get('currency', 'USD')
        fx_rate = EXCHANGE_RATES.get(currency, 1.0)
        cost_usd = round(total_amount / fx_rate, 2)

        if action == 'BUY':
            if portfolio_obj.cash_balance_usd < Decimal(str(cost_usd)):
                return JsonResponse({'error': 'Insufficient funds'}, status=400)
            portfolio_obj.cash_balance_usd = max(Decimal('0.00'), portfolio_obj.cash_balance_usd - Decimal(str(cost_usd)))
        elif action == 'SELL':
            user_txs = Transaction.objects.filter(portfolio=portfolio_obj, asset__symbol=symbol)
            shares_bought = sum(Decimal(str(t.quantity)) for t in user_txs if t.action == 'BUY')
            shares_sold = sum(Decimal(str(t.quantity)) for t in user_txs if t.action == 'SELL')
            owned_shares = shares_bought - shares_sold
            if owned_shares < Decimal(str(quantity)):
                return JsonResponse({'error': 'Insufficient holdings to sell'}, status=400)
            portfolio_obj.cash_balance_usd = portfolio_obj.cash_balance_usd + Decimal(str(cost_usd))
        
        portfolio_obj.save()
        if hasattr(user, 'profile'):
            user.profile.cash_balance_usd = portfolio_obj.cash_balance_usd
            user.profile.save()

        db_asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': asset['name'],
                'current_price': Decimal(str(unit_price)),
                'currency': currency,
                'category': asset.get('category', 'equities'),
                'market': get_or_create_market(asset.get('market', 'NASDAQ'))
            }
        )
        order_record = Order.objects.create(
            user=user,
            portfolio=portfolio_obj,
            asset=db_asset,
            order_type=order_type,
            action=action,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(unit_price)),
            status='EXECUTED'
        )
        new_tx_obj = Transaction.objects.create(
            portfolio=portfolio_obj,
            asset=db_asset,
            order=order_record,
            action=action,
            quantity=quantity,
            price_at_transaction=Decimal(str(unit_price)),
            total_amount=Decimal(str(total_amount)),
            status='Completed'
        )

        new_tx = {
            "id": new_tx_obj.reference,
            "asset_symbol": symbol,
            "asset_name": asset['name'],
            "logo": asset.get('logo', ''),
            "image": asset.get('image', ''),
            "type": action,
            "shares": f"{quantity:g} {'Shares' if asset['category'] == 'equities' else symbol}",
            "price": f"{asset['currency']} {unit_price:,.2f}",
            "total": f"{asset['currency']} {total_amount:,.2f}",
            "date": "Just now",
            "status": "Completed"
        }
        
        return JsonResponse({
            "success": True,
            "message": f"Successfully executed {action} order for {quantity:g} {symbol} at {asset['currency']} {unit_price:,.2f}",
            "transaction": new_tx,
            "cash_balance_usd": float(portfolio_obj.cash_balance_usd)
        })
    except Exception as e:
        logger.exception("Error in api_trade_execute: %s", e)
        return JsonResponse({"error": "An internal error occurred"}, status=500)

@csrf_exempt
def api_cash_transfer(request):
    """
    Handles Cash Deposits and Withdrawals into User Portfolios using CashTransferForm.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required. Please sign in to manage account deposits and withdrawals.",
            "authenticated": False,
            "login_url": "/login/?next=/portfolio/"
        }, status=401)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        else:
            data = request.POST.dict()

        user = request.user
        portfolio_obj, _ = Portfolio.objects.get_or_create(
            user=user,
            defaults={'name': 'Growth & Dividend Portfolio', 'cash_balance_usd': Decimal('5212.17')}
        )

        form = CashTransferForm(portfolio=portfolio_obj, data=data)
        if form.is_valid():
            transfer = form.execute()
            if hasattr(user, 'profile'):
                user.profile.cash_balance_usd = portfolio_obj.cash_balance_usd
                user.profile.save()
            return JsonResponse({
                "success": True,
                "message": f"Successfully executed {transfer.get_transfer_type_display()} of ${transfer.amount} via {transfer.get_method_display()}",
                "transfer": {
                    "id": transfer.id,
                    "reference": transfer.reference,
                    "type": transfer.transfer_type,
                    "amount": float(transfer.amount),
                    "status": transfer.status,
                    "new_cash_balance_usd": float(portfolio_obj.cash_balance_usd)
                }
            })
        else:
            errors = []
            for err in form.non_field_errors():
                errors.append(str(err))
            for f, errs in form.errors.items():
                if f != '__all__':
                    errors.extend([f"{f}: {e}" for e in errs])
            return JsonResponse({"error": '; '.join(errors), "errors": form.errors}, status=400)
    except Exception as e:
        logger.exception("Error in api_cash_transfer: %s", e)
        return JsonResponse({"error": "An internal error occurred"}, status=500)

@csrf_exempt
def api_bonds_buy(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required. Please sign in to purchase sovereign bonds or submit CBK auction bids.",
            "authenticated": False,
            "login_url": "/login/?next=/bonds/"
        }, status=401)

    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper()
        face_value = data.get('face_value')
        units = data.get('units') or data.get('quantity')
        order_type = data.get('order_type', 'AUCTION_NON_COMPETITIVE')
        bid_yield = data.get('bid_yield')
        channel = data.get('channel', 'CBK_DHOWCSD')
        
        ok, msg, receipt = execute_bond_purchase(
            symbol=symbol,
            face_value=face_value,
            units=units,
            order_type=order_type,
            bid_yield=bid_yield,
            channel=channel
        )
        if not ok:
            return JsonResponse({"error": msg}, status=400)
            
        user = request.user
        portfolio_obj, _ = Portfolio.objects.get_or_create(user=user)
        cost_kes = float(receipt.get("total_settlement", 50000))
        cost_usd = round(cost_kes / 130.0, 2)
        if portfolio_obj.cash_balance_usd < Decimal(str(cost_usd)):
            return JsonResponse({'error': 'Insufficient funds'}, status=400)

        asset_info = ASSETS.get(symbol, {})
        bond_asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': asset_info.get('name', symbol),
                'current_price': Decimal(str(asset_info.get('price', 100.0))),
                'currency': 'KES',
                'category': 'bonds',
                'market': get_or_create_market('CBK', 'Central Bank of Kenya')
            }
        )
        portfolio_obj.cash_balance_usd = max(Decimal('0.00'), portfolio_obj.cash_balance_usd - Decimal(str(cost_usd)))
        portfolio_obj.save()
        if hasattr(user, 'profile'):
            user.profile.cash_balance_usd = portfolio_obj.cash_balance_usd
            user.profile.save()

        order_record = Order.objects.create(
            user=user,
            portfolio=portfolio_obj,
            asset=bond_asset,
            order_type='LIMIT' if order_type == 'AUCTION_COMPETITIVE' else 'MARKET',
            action='BUY',
            quantity=Decimal(str(units or 1)),
            price=Decimal(str(asset_info.get('price', 100.0))),
            status='EXECUTED',
            notes=f"Channel: {channel}"
        )
        tx_obj = Transaction.objects.create(
            portfolio=portfolio_obj,
            asset=bond_asset,
            order=order_record,
            action='BUY',
            quantity=float(units or 1),
            price_at_transaction=Decimal(str(asset_info.get('price', 100.0))),
            total_amount=Decimal(str(cost_kes)),
            reference=receipt.get("reference") or f"TX-{Transaction.objects.count() + 9022}",
            status='Completed'
        )

        return JsonResponse({
            "success": True,
            "message": msg,
            "receipt": receipt,
            "transaction": receipt.get("transaction"),
            "cash_balance_usd": float(portfolio_obj.cash_balance_usd)
        })
    except Exception as e:
        logger.exception("Error in api_bonds_buy: %s", e)
        return JsonResponse({"error": "An internal error occurred"}, status=500)

@csrf_exempt
def api_watchlist_toggle(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required. Please sign in to manage your watchlist.",
            "authenticated": False,
            "login_url": "/login/?next=/watchlist/"
        }, status=401)
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper()
        watchlist_name = data.get('watchlist', 'default')
        
        user = request.user
        is_in = False
        if user.is_authenticated:
            wl_obj, _ = Watchlist.objects.get_or_create(user=user, name="Primary Watchlist")
            db_asset = Asset.objects.filter(symbol=symbol).first()
            if not db_asset and symbol in ASSETS:
                a_info = ASSETS[symbol]
                mkt = get_or_create_market(a_info.get('market', 'NSE'))
                db_asset = Asset.objects.create(
                    symbol=symbol,
                    name=a_info['name'],
                    current_price=Decimal(str(a_info['price'])),
                    market=mkt
                )
            if db_asset:
                if db_asset in wl_obj.assets.all():
                    wl_obj.assets.remove(db_asset)
                    is_in = False
                else:
                    wl_obj.assets.add(db_asset)
                    is_in = True

        current_list = WATCHLISTS.setdefault(watchlist_name, [])
        if symbol in current_list:
            current_list.remove(symbol)
        else:
            current_list.append(symbol)
            
        return JsonResponse({
            "success": True,
            "symbol": symbol,
            "in_watchlist": is_in,
            "watchlist": watchlist_name
        })
    except Exception as e:
        logger.exception("Error in api_watchlist_toggle: %s", e)
        return JsonResponse({"error": "An internal error occurred"}, status=500)


def earnings_calendar(request):
    """
    Corporate Earnings and Regulatory Filings Hub.
    Provides upcoming schedules and reported statutory disclosures (SEC, CMA, FCA, FSA).
    """
    from .services.earnings_service import get_upcoming_earnings, get_reported_filings
    from .data import MARKET_INDICES

    upcoming = get_upcoming_earnings()
    reported = get_reported_filings()

    context = {
        "indices": MARKET_INDICES,
        "upcoming_list": upcoming,
        "reported_list": reported,
        "page_title": "Earnings Reports & SEC Filings",
        "active_tab": "earnings"
    }
    return render(request, 'markets/earnings.html', context)


def earnings_filing_detail(request, filing_id):
    """
    Detailed in-app reader for statutory regulatory earnings report (SEC EDGAR, CMA, etc.).
    """
    from .services.earnings_service import get_filing_by_id
    from .data import MARKET_INDICES

    filing = get_filing_by_id(filing_id)
    if not filing:
        messages.error(request, "The requested regulatory filing could not be found.")
        return redirect('earnings')

    context = {
        "indices": MARKET_INDICES,
        "filing": filing,
        "page_title": f"{filing.get('company_name')} {filing.get('filing_type')} - Regulatory Filing",
        "active_tab": "earnings"
    }
    return render(request, 'markets/earnings_detail.html', context)


def earnings_download_file(request, filing_id, file_type):
    """
    Direct in-app download for regulatory statutory filings (PDF, Excel, CSV).
    Generates verified institutional disclosure documents directly on the server
    without sending or redirecting users to external regulators.
    """
    from .services.earnings_service import get_filing_by_id
    from .services.filing_export_service import (
        generate_filing_pdf,
        generate_filing_excel,
        generate_filing_csv
    )

    filing = get_filing_by_id(filing_id)
    if not filing:
        messages.error(request, "The requested regulatory filing could not be found.")
        return redirect('earnings')

    symbol = str(filing.get('symbol', 'ASSET')).upper()
    filing_type = str(filing.get('filing_type', 'REPORT')).replace(' ', '_').replace('/', '_')
    period = str(filing.get('fiscal_period', 'PERIOD')).replace(' ', '_').replace('/', '_')
    base_name = f"PesaMarkets_{symbol}_{filing_type}_{period}"

    ft = file_type.lower()
    if ft == 'pdf':
        content = generate_filing_pdf(filing)
        content_type = 'application/pdf'
        filename = f"{base_name}.pdf"
    elif ft in ['excel', 'xlsx']:
        content = generate_filing_excel(filing)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f"{base_name}.xlsx"
    elif ft == 'csv':
        content = generate_filing_csv(filing)
        content_type = 'text/csv; charset=utf-8'
        filename = f"{base_name}.csv"
    else:
        messages.error(request, f"Unsupported download format: {file_type}")
        return redirect('earnings_filing_detail', filing_id=filing_id)

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def api_earnings(request):
    """
    REST API endpoint returning upcoming earnings and statutory filings.
    """
    from .services.earnings_service import get_upcoming_earnings, get_reported_filings

    regulator = request.GET.get('regulator', 'all')
    upcoming = get_upcoming_earnings()
    reported = get_reported_filings(regulator=regulator)

    return JsonResponse({
        "success": True,
        "status": "success",
        "upcoming_count": len(upcoming),
        "reported_count": len(reported),
        "upcoming": upcoming,
        "reported": reported
    })


def events_calendar(request):
    """
    Macroeconomic and corporate earnings events calendar.
    Allows viewing all upcoming economic releases, listed companies earnings reports,
    and setting email reminders delivered to the user's registered email address.
    """
    import json
    from .services.events_service import get_macro_events, get_user_reminded_ids
    from .services.earnings_service import get_upcoming_earnings, get_reported_filings, get_all_earnings_events
    from .data import MARKET_INDICES

    country = request.GET.get('country', 'all')
    impact = request.GET.get('impact', 'all')
    category = request.GET.get('category', 'all')
    session = request.GET.get('session', 'all')

    economic_events = get_macro_events(country=country, impact=impact)
    upcoming_earnings = get_upcoming_earnings()
    reported_filings = get_reported_filings()
    corporate_earnings = get_all_earnings_events(market=country, session=session)

    # Combined unified list
    combined_events = list(economic_events) + list(corporate_earnings)

    user_email = request.user.email if (request.user.is_authenticated and request.user.email) else ''
    reminded_ids = list(get_user_reminded_ids(user_email))

    stats = {
        "total_events": len(combined_events),
        "earnings_count": len(corporate_earnings),
        "macro_count": len(economic_events),
        "bmo_count": len([e for e in corporate_earnings if e.get('session_code') == 'BMO']),
        "amc_count": len([e for e in corporate_earnings if e.get('session_code') == 'AMC']),
    }

    context = {
        "indices": MARKET_INDICES,
        "economic_events": economic_events,
        "upcoming_earnings": upcoming_earnings,
        "corporate_earnings": corporate_earnings,
        "reported_filings": reported_filings,
        "combined_events": combined_events,
        "economic_events_json": json.dumps(economic_events),
        "corporate_earnings_json": json.dumps(corporate_earnings),
        "combined_events_json": json.dumps(combined_events),
        "selected_country": country,
        "selected_impact": impact,
        "selected_category": category,
        "selected_session": session,
        "user_email": user_email,
        "reminded_ids": reminded_ids,
        "stats": stats,
        "page_title": "Economic & Corporate Events Calendar | PesaMarkets",
        "active_tab": "events"
    }
    return render(request, 'markets/events.html', context)


def api_events(request):
    """
    REST API endpoint returning upcoming economic events and earnings schedule.
    """
    from .services.events_service import get_macro_events
    from .services.earnings_service import get_upcoming_earnings, get_all_earnings_events

    country = request.GET.get('country', 'all')
    impact = request.GET.get('impact', 'all')
    session = request.GET.get('session', 'all')

    events = get_macro_events(country=country, impact=impact)
    earnings = get_upcoming_earnings()
    corporate_earnings = get_all_earnings_events(market=country, session=session)
    combined = list(events) + list(corporate_earnings)

    return JsonResponse({
        "success": True,
        "count": len(events),
        "events": events,
        "earnings": earnings,
        "corporate_earnings": corporate_earnings,
        "all_events": combined,
        "earnings_count": len(corporate_earnings),
        "macro_count": len(events),
        "total_count": len(combined)
    })


@csrf_exempt
@require_POST
def api_set_event_reminder(request):
    """
    API endpoint to set or toggle an event reminder.
    Dispatches reminder notification to user's registered email address.
    """
    import json
    from .services.events_service import toggle_event_reminder, get_event_by_id

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()
    except Exception:
        data = request.POST.dict()

    event_id = data.get('event_id') or data.get('id')
    if not event_id:
        return JsonResponse({"success": False, "error": "Event ID is required."}, status=400)

    # Determine email address: prefer registered email if authenticated
    if request.user.is_authenticated and request.user.email:
        email = request.user.email
    else:
        email = data.get('email', '').strip()

    if not email:
        return JsonResponse({
            "success": False,
            "requires_email": True,
            "error": "Please provide an email address or sign in to use your registered account email."
        }, status=400)

    event_data = get_event_by_id(event_id) or data
    result = toggle_event_reminder(
        user=request.user if request.user.is_authenticated else None,
        email=email,
        event_id=event_id,
        event_data=event_data
    )
    return JsonResponse(result)


def api_my_event_reminders(request):
    """
    Return active reminders for authenticated user or provided email.
    """
    from .services.events_service import get_user_reminded_ids
    from .models import EventReminder

    email = ''
    if request.user.is_authenticated and request.user.email:
        email = request.user.email
    elif request.GET.get('email'):
        email = request.GET.get('email').strip().lower()

    if not email:
        return JsonResponse({"success": True, "reminded_ids": [], "reminders": []})

    reminders = list(EventReminder.objects.filter(email=email, is_active=True).values(
        'event_id', 'event_title', 'event_date', 'event_time', 'country', 'impact', 'email_sent', 'created_at'
    ))
    return JsonResponse({
        "success": True,
        "email": email,
        "count": len(reminders),
        "reminded_ids": list(get_user_reminded_ids(email)),
        "reminders": reminders
    })


def custom_404(request, exception=None):
    try:
        return render(request, '404.html', status=404)
    except TemplateDoesNotExist:
        return HttpResponseNotFound('<h1>404 Not Found</h1>')


def custom_500(request):
    try:
        return render(request, '500.html', status=500)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>500 Server Error</h1>')


# ========================================================
# ADMIN DASHBOARD & USER MANAGEMENT (ADMIN ONLY)
# ========================================================

def is_admin_user(user):
    """Check if the user is an authenticated administrator."""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or user.username == 'admin'


def admin_dashboard_view(request):
    """
    Real-time Admin Dashboard for viewing and managing all user accounts.
    Accessible exclusively to administrators.
    """
    if not is_admin_user(request.user):
        messages.error(request, "Access restricted. Administrator privileges required to access the Admin Dashboard.")
        return redirect('home')

    users_qs = User.objects.all().select_related('profile').order_by('-date_joined')
    
    total_users = users_qs.count()
    active_users = users_qs.filter(is_active=True).count()
    inactive_users = users_qs.filter(is_active=False).count()
    flagged_users = UserProfile.objects.filter(is_flagged=True).count()
    verified_users = UserProfile.objects.filter(email_verified=True).count()
    pro_users = UserProfile.objects.filter(tier__icontains='Pro').count()

    initial_users_data = []
    for u in users_qs[:100]:
        prof = getattr(u, 'profile', None)
        initial_users_data.append({
            "id": u.id,
            "username": u.username,
            "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
            "email": u.email,
            "phone": prof.phone_number if prof else '',
            "is_active": u.is_active,
            "is_flagged": prof.is_flagged if prof else False,
            "flag_reason": prof.flag_reason if prof else '',
            "email_verified": prof.email_verified if prof else False,
            "phone_verified": prof.phone_verified if prof else False,
            "tier": prof.tier if prof else 'Free Tier',
            "is_admin": u.is_superuser or u.is_staff or u.username == 'admin',
            "date_joined": u.date_joined.strftime("%b %d, %Y %H:%M") if u.date_joined else 'N/A',
            "last_login": u.last_login.strftime("%b %d, %Y %H:%M") if u.last_login else 'Never',
            "avatar_url": prof.avatar_url if prof else 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80',
        })

    import json
    context = {
        "page_title": "Admin Dashboard | PesaMarkets",
        "active_tab": "admin_dashboard",
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "flagged_users": flagged_users,
        "verified_users": verified_users,
        "pro_users": pro_users,
        "users": users_qs[:100],
        "initial_users_json": json.dumps(initial_users_data),
        "indices": MARKET_INDICES,
        "rates": EXCHANGE_RATES,
    }
    return render(request, 'markets/admin_dashboard.html', context)


def api_admin_users(request):
    """
    Real-time REST API returning user accounts, activity states, and live metrics.
    Exclusively accessible to administrators.
    """
    if not is_admin_user(request.user):
        return JsonResponse({"success": False, "error": "Access denied. Administrator privileges required."}, status=403)

    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').lower()

    users_qs = User.objects.all().select_related('profile').order_by('-date_joined')

    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(profile__phone_number__icontains=q)
        )

    if status_filter == 'active':
        users_qs = users_qs.filter(is_active=True)
    elif status_filter in ['inactive', 'suspended']:
        users_qs = users_qs.filter(is_active=False)
    elif status_filter == 'flagged':
        users_qs = users_qs.filter(profile__is_flagged=True)
    elif status_filter == 'verified':
        users_qs = users_qs.filter(profile__email_verified=True)

    users_data = []
    for u in users_qs:
        prof = getattr(u, 'profile', None)
        users_data.append({
            "id": u.id,
            "username": u.username,
            "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
            "email": u.email,
            "phone": prof.phone_number if prof else '',
            "is_active": u.is_active,
            "is_flagged": prof.is_flagged if prof else False,
            "flag_reason": prof.flag_reason if prof else '',
            "email_verified": prof.email_verified if prof else False,
            "phone_verified": prof.phone_verified if prof else False,
            "tier": prof.tier if prof else 'Free Tier',
            "is_admin": u.is_superuser or u.is_staff or u.username == 'admin',
            "cash_balance": float(prof.cash_balance_usd) if prof else 0.0,
            "date_joined": u.date_joined.strftime("%b %d, %Y %H:%M") if u.date_joined else 'N/A',
            "last_login": u.last_login.strftime("%b %d, %Y %H:%M") if u.last_login else 'Never',
            "avatar_url": prof.avatar_url if prof else 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80',
        })

    all_users = User.objects.all()
    stats = {
        "total": all_users.count(),
        "active": all_users.filter(is_active=True).count(),
        "inactive": all_users.filter(is_active=False).count(),
        "flagged": UserProfile.objects.filter(is_flagged=True).count(),
        "verified": UserProfile.objects.filter(email_verified=True).count(),
        "pro": UserProfile.objects.filter(tier__icontains='Pro').count(),
    }

    return JsonResponse({
        "success": True,
        "stats": stats,
        "users": users_data,
        "count": len(users_data)
    })


@csrf_exempt
@require_POST
def api_admin_user_action(request, user_id):
    """
    Real-time REST API to suspend, activate, flag, unflag, delete, or toggle tier for a user.
    Exclusively accessible to administrators.
    """
    if not is_admin_user(request.user):
        return JsonResponse({"success": False, "error": "Access denied. Administrator privileges required."}, status=403)

    try:
        import json
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()
    except Exception:
        data = request.POST.dict()

    action = data.get('action', '').strip().lower()
    target_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if action == 'suspend':
        if target_user.id == request.user.id:
            return JsonResponse({"success": False, "error": "You cannot suspend your own administrative account."}, status=400)
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])
        return JsonResponse({
            "success": True,
            "message": f"Account @{target_user.username} has been suspended.",
            "user_id": target_user.id,
            "is_active": False
        })

    elif action == 'activate':
        target_user.is_active = True
        target_user.save(update_fields=['is_active'])
        return JsonResponse({
            "success": True,
            "message": f"Account @{target_user.username} has been reactivated.",
            "user_id": target_user.id,
            "is_active": True
        })

    elif action == 'flag':
        reason = data.get('reason', '').strip() or 'Flagged for administrative risk review'
        profile.is_flagged = True
        profile.flag_reason = reason
        profile.save(update_fields=['is_flagged', 'flag_reason'])
        return JsonResponse({
            "success": True,
            "message": f"Account @{target_user.username} flagged for review ({reason}).",
            "user_id": target_user.id,
            "is_flagged": True,
            "flag_reason": reason
        })

    elif action == 'unflag':
        profile.is_flagged = False
        profile.flag_reason = ''
        profile.save(update_fields=['is_flagged', 'flag_reason'])
        return JsonResponse({
            "success": True,
            "message": f"Flag removed from account @{target_user.username}.",
            "user_id": target_user.id,
            "is_flagged": False,
            "flag_reason": ''
        })

    elif action == 'delete':
        if target_user.id == request.user.id:
            return JsonResponse({"success": False, "error": "You cannot delete your own account."}, status=400)
        if target_user.username == 'admin' and request.user.username != 'admin':
            return JsonResponse({"success": False, "error": "Cannot delete master administrator account."}, status=400)

        del_username = target_user.username
        target_user.delete()
        return JsonResponse({
            "success": True,
            "message": f"Account @{del_username} was permanently deleted.",
            "user_id": user_id,
            "deleted": True
        })

    elif action == 'toggle_tier':
        if 'Pro' in profile.tier:
            profile.tier = 'Free Tier'
        else:
            profile.tier = 'Terminal Pro Tier'
        profile.save(update_fields=['tier'])
        return JsonResponse({
            "success": True,
            "message": f"Tier for @{target_user.username} updated to {profile.tier}.",
            "user_id": target_user.id,
            "tier": profile.tier
        })

    return JsonResponse({"success": False, "error": f"Unknown action: {action}"}, status=400)

