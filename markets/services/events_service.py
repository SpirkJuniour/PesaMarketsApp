"""
Events and Reminders Service.
Provides comprehensive macroeconomic releases, central bank decisions,
and corporate earnings calendars with automated email reminder dispatch
to users' registered email addresses.
"""

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from markets.models import EventReminder

logger = logging.getLogger(__name__)

# Up-to-date schedule of macroeconomic and monetary policy events
MACRO_ECONOMIC_EVENTS = [
    {
        "id": "ev-ke-cbk-mpc",
        "title": "Central Bank of Kenya (CBK) MPC Key Rate Decision",
        "country": "Kenya",
        "country_code": "kenya",
        "country_flag": "🇰🇪",
        "category": "CENTRAL_BANK",
        "category_label": "Central Bank Policy",
        "date": "Today (Nov 17)",
        "date_iso": "2026-11-17",
        "time": "14:30 EAT",
        "impact": "High",
        "consensus": "12.00%",
        "previous": "12.75%",
        "symbol": "CBK-CBR",
        "description": "Monetary Policy Committee review of the Central Bank Rate (CBR) following inflation stabilization and foreign exchange reserve replenishment.",
        "trading_note": "A potential 75 bps easing cycle supports domestic treasury bond valuations (IFB10Y, FXD) and banking equity margins.",
    },
    {
        "id": "ev-us-claims-today",
        "title": "US Initial Jobless Claims",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "ECONOMIC",
        "category_label": "Labor Market Release",
        "date": "Today (Nov 17)",
        "date_iso": "2026-11-17",
        "time": "16:30 EAT",
        "impact": "High",
        "consensus": "218K",
        "previous": "221K",
        "symbol": "UST10Y",
        "description": "Weekly tracking of first-time applications for state unemployment benefits across the 50 US states.",
        "trading_note": "Key indicator for Federal Reserve interest rate trajectory and US Treasury 10-year note yield response.",
    },
    {
        "id": "ev-us-retail-sales",
        "title": "US Retail Sales MoM (Advance Monthly)",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "ECONOMIC",
        "category_label": "Consumer Spending",
        "date": "Today (Nov 17)",
        "date_iso": "2026-11-17",
        "time": "16:30 EAT",
        "impact": "High",
        "consensus": "+0.3%",
        "previous": "+0.4%",
        "symbol": "SP500",
        "description": "Total receipts at retail stores and food service providers, tracking consumer economic resilience.",
        "trading_note": "Impacts consumer discretionary equities (AMZN, HD, COST) and dollar index strength.",
    },
    {
        "id": "ev-us-fomc-minutes",
        "title": "FOMC Meeting Minutes Release",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "CENTRAL_BANK",
        "category_label": "Monetary Policy Minutes",
        "date": "Tomorrow (Nov 18)",
        "date_iso": "2026-11-18",
        "time": "22:00 EAT",
        "impact": "High",
        "consensus": "Neutral / Dovish Shift",
        "previous": "4.75%",
        "symbol": "UST10Y",
        "description": "Detailed record of Federal Reserve Open Market Committee discussions regarding neutral rate target and balance sheet roll-off.",
        "trading_note": "Crucial forward guidance on the benchmark fed funds rate for global sovereign yields and technology equity valuations.",
    },
    {
        "id": "ev-ke-nse-bond-auction",
        "title": "NSE Primary Corporate Bond Auction & Allocation",
        "country": "Kenya",
        "country_code": "kenya",
        "country_flag": "🇰🇪",
        "category": "ECONOMIC",
        "category_label": "Debt Capital Markets",
        "date": "Tomorrow (Nov 18)",
        "date_iso": "2026-11-18",
        "time": "11:00 EAT",
        "impact": "Medium",
        "consensus": "14.25% Coupon",
        "previous": "Over-subscribed 1.8x",
        "symbol": "IFB10Y",
        "description": "Primary dealer corporate debt auction book-build on the Nairobi Securities Exchange.",
        "trading_note": "Institutional liquidity indicators for high-yield frontier credit offerings.",
    },
    {
        "id": "ev-uk-cpi-inflation",
        "title": "UK Consumer Price Index (CPI) Inflation YoY",
        "country": "UK",
        "country_code": "uk",
        "country_flag": "🇬🇧",
        "category": "ECONOMIC",
        "category_label": "Inflation Print",
        "date": "Nov 19",
        "date_iso": "2026-11-19",
        "time": "10:00 EAT",
        "impact": "High",
        "consensus": "2.2%",
        "previous": "2.3%",
        "symbol": "UKG10Y",
        "description": "Office for National Statistics headline consumer price index measure of inflation.",
        "trading_note": "Directly guides Bank of England Monetary Policy Committee decision on December gilt yields.",
    },
    {
        "id": "ev-us-housing-starts",
        "title": "US Building Permits & Housing Starts",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "ECONOMIC",
        "category_label": "Real Estate / Macro",
        "date": "Nov 19",
        "date_iso": "2026-11-19",
        "time": "16:30 EAT",
        "impact": "Medium",
        "consensus": "1.34M",
        "previous": "1.35M",
        "symbol": "HD",
        "description": "Annualized number of new residential building projects commenced during the preceding month.",
        "trading_note": "Leading barometer of fixed private investment and building supply commodities (lumber, copper).",
    },
    {
        "id": "ev-ke-cbk-tbill-auction",
        "title": "CBK Treasury Bill Auction Results (T91, T182, T364)",
        "country": "Kenya",
        "country_code": "kenya",
        "country_flag": "🇰🇪",
        "category": "ECONOMIC",
        "category_label": "Sovereign Debt Auction",
        "date": "Nov 20",
        "date_iso": "2026-11-20",
        "time": "14:00 EAT",
        "impact": "High",
        "consensus": "15.75% (T91)",
        "previous": "15.84%",
        "symbol": "T91",
        "description": "Central Bank of Kenya weekly auction of KES 24 Billion in sovereign short-term bills.",
        "trading_note": "Benchmark yields dictating money market fund annualized returns and short-term interbank liquidity.",
    },
    {
        "id": "ev-jp-boj-summary",
        "title": "Bank of Japan Summary of Opinions & Policy Review",
        "country": "Japan",
        "country_code": "japan",
        "country_flag": "🇯🇵",
        "category": "CENTRAL_BANK",
        "category_label": "Central Bank Minutes",
        "date": "Nov 20",
        "date_iso": "2026-11-20",
        "time": "03:50 EAT",
        "impact": "High",
        "consensus": "0.25% - 0.50%",
        "previous": "0.25%",
        "symbol": "JGB10Y",
        "description": "Summary of deliberations by the Policy Board on monetary easing exit and yen carry-trade normalization.",
        "trading_note": "Crucial for USD/JPY exchange rates, Japanese 10-Year JGB yields, and Tokyo export equities (7203, Sony).",
    },
    {
        "id": "ev-us-flash-pmi",
        "title": "US S&P Global Flash Manufacturing & Services PMI",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "ECONOMIC",
        "category_label": "Business Activity",
        "date": "Nov 20",
        "date_iso": "2026-11-20",
        "time": "17:45 EAT",
        "impact": "High",
        "consensus": "52.8",
        "previous": "52.4",
        "symbol": "NVDA",
        "description": "Survey of private sector purchasing executives measuring output, new orders, and enterprise hiring.",
        "trading_note": "Leading indicator for GDP growth momentum and cloud infrastructure corporate procurement.",
    },
    {
        "id": "ev-ke-scom-h1-briefing",
        "title": "Safaricom PLC (SCOM) H1 FY27 Audited Results & M-PESA Declaration",
        "country": "Kenya",
        "country_code": "kenya",
        "country_flag": "🇰🇪",
        "category": "EARNINGS",
        "category_label": "Statutory Earnings",
        "date": "Nov 21",
        "date_iso": "2026-11-21",
        "time": "09:00 EAT",
        "impact": "High",
        "consensus": "KES 0.92 EPS",
        "previous": "KES 0.84",
        "symbol": "SCOM",
        "description": "Official Capital Markets Authority investor briefing covering M-PESA global remittances and Ethiopia subscriber profitability.",
        "trading_note": "Heavyweight stock accounting for ~48% of daily NSE trading volume and institutional foreign flows.",
    },
    {
        "id": "ev-uk-boe-policy",
        "title": "Bank of England Monetary Policy Review & Asset Targets",
        "country": "UK",
        "country_code": "uk",
        "country_flag": "🇬🇧",
        "category": "CENTRAL_BANK",
        "category_label": "Central Bank Policy",
        "date": "Nov 21",
        "date_iso": "2026-11-21",
        "time": "15:00 EAT",
        "impact": "High",
        "consensus": "4.75%",
        "previous": "5.00%",
        "symbol": "UKG10Y",
        "description": "Bank of England MPC decision on the Bank Rate and quantitative tightening gilt sale volumes.",
        "trading_note": "Drives British Pound Sterling valuations and FTSE 100 constituent financing costs.",
    },
    {
        "id": "ev-jp-core-cpi",
        "title": "Japan National Core CPI YoY (Ex-Fresh Food)",
        "country": "Japan",
        "country_code": "japan",
        "country_flag": "🇯🇵",
        "category": "ECONOMIC",
        "category_label": "Inflation Print",
        "date": "Nov 22",
        "date_iso": "2026-11-22",
        "time": "02:30 EAT",
        "impact": "High",
        "consensus": "2.4%",
        "previous": "2.5%",
        "symbol": "7203",
        "description": "Statistics Bureau nationwide inflation print excluding volatile fresh food components.",
        "trading_note": "Primary metric watched by Governor Ueda to determine the timing of the next rate hike.",
    },
    {
        "id": "ev-us-core-pce",
        "title": "US Core PCE Price Index MoM/YoY (Fed's Preferred Metric)",
        "country": "USA",
        "country_code": "usa",
        "country_flag": "🇺🇸",
        "category": "ECONOMIC",
        "category_label": "Inflation Print",
        "date": "Nov 26",
        "date_iso": "2026-11-26",
        "time": "16:30 EAT",
        "impact": "High",
        "consensus": "+0.2% MoM (+2.6% YoY)",
        "previous": "+0.3% MoM",
        "symbol": "UST10Y",
        "description": "Bureau of Economic Analysis personal consumption expenditures index, the Federal Reserve's primary gauge of underlying inflation.",
        "trading_note": "Direct determinant of FOMC rate trajectory; drives massive volatility across equity index futures and bond yields.",
    },
]

def get_macro_events(country=None, impact=None):
    """Filter macroeconomic events by country and impact."""
    events = list(MACRO_ECONOMIC_EVENTS)
    if country and country.lower() != 'all':
        c_clean = country.lower().strip()
        events = [e for e in events if e['country_code'] == c_clean or e['country'].lower() == c_clean]
    if impact and impact.lower() != 'all':
        i_clean = impact.lower().strip()
        events = [e for e in events if e['impact'].lower() == i_clean]
    return events

def get_dock_economic_events():
    """
    Format up-to-date events grouped by country for the Market Dock component.
    Matches Screenshots 1, 2, 3 with live up-to-date schedule.
    """
    kenya_events = [e for e in MACRO_ECONOMIC_EVENTS if e['country_code'] == 'kenya']
    usa_events = [e for e in MACRO_ECONOMIC_EVENTS if e['country_code'] == 'usa']
    uk_events = [e for e in MACRO_ECONOMIC_EVENTS if e['country_code'] == 'uk']
    japan_events = [e for e in MACRO_ECONOMIC_EVENTS if e['country_code'] == 'japan']

    return {
        "kenya": kenya_events,
        "usa": usa_events,
        "uk": uk_events,
        "japan": japan_events,
        "all": MACRO_ECONOMIC_EVENTS,
    }

def get_event_by_id(event_id):
    """Find event in either macroeconomic events or corporate earnings events."""
    for e in MACRO_ECONOMIC_EVENTS:
        if e['id'] == event_id:
            return e

    # Check corporate earnings events
    from .earnings_service import get_all_earnings_events
    for earn in get_all_earnings_events():
        if earn['id'] == event_id:
            return earn
    return None

def send_event_reminder_email(reminder):
    """
    Dispatches a dark-themed institutional HTML email notification
    to the user's registered email address with complete event details.
    """
    subject = f"[PesaMarkets Reminder] Upcoming Event: {reminder.event_title} ({reminder.event_date})"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'alerts@pesamarkets.com')
    recipient_list = [reminder.email]

    text_content = f"""PesaMarkets Event Alert & Reminder
========================================================================
Event: {reminder.event_title}
Scheduled Date: {reminder.event_date}
Scheduled Time: {reminder.event_time}
Country / Market: {reminder.country}
Category: {reminder.get_event_category_display()}
Impact Level: {reminder.impact}
Symbol / Ticker: {reminder.symbol or 'Macroeconomic'}
Notes: {reminder.notes or 'Scheduled macroeconomic / statutory release.'}

Log in to PesaMarkets to view live tick updates and debt auction order books.
Portal: https://pesamarkets.com/events/

This alert was delivered to your registered email address: {reminder.email}
========================================================================
PesaMarkets Financial Intelligence & Automated Trading
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PesaMarkets Event Reminder</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0F0F11; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #FFFFFF;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0F0F11; padding: 30px 15px;">
        <tr>
            <td align="center">
                <table width="100%" max-width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #18181B; border: 1px solid #27272A; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 35px; border-bottom: 1px solid #27272A; background-color: #121214;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td>
                                        <div style="font-size: 22px; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF;">
                                            Pesa<span style="color: #4169E1;">Markets</span>
                                        </div>
                                        <div style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #71717A; margin-top: 3px; letter-spacing: 0.8px;">
                                            Institutional Event Alert Desk
                                        </div>
                                    </td>
                                    <td align="right">
                                        <span style="display: inline-block; padding: 5px 12px; border-radius: 9999px; font-size: 11px; font-weight: 800; text-transform: uppercase; background-color: rgba(65, 105, 225, 0.15); color: #60A5FA; border: 1px solid rgba(65, 105, 225, 0.3);">
                                            🔔 REMINDER ACTIVE
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 35px 35px 25px 35px;">
                            <p style="margin: 0 0 8px 0; font-size: 13px; font-weight: 600; color: #A1A1AA; text-transform: uppercase; letter-spacing: 0.5px;">
                                Upcoming Scheduled Market Event
                            </p>
                            <h1 style="margin: 0 0 20px 0; font-size: 24px; font-weight: 800; line-height: 1.3; color: #FFFFFF; letter-spacing: -0.3px;">
                                {reminder.event_title}
                            </h1>

                            <!-- Event Details Card -->
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #202024; border: 1px solid #2E2E33; border-radius: 16px; margin-bottom: 25px;">
                                <tr>
                                    <td style="padding: 16px 20px; border-bottom: 1px solid #2E2E33;" width="50%">
                                        <div style="font-size: 11px; color: #71717A; font-weight: 600; text-transform: uppercase;">Scheduled Date</div>
                                        <div style="font-size: 15px; color: #FFFFFF; font-weight: 800; font-family: monospace; margin-top: 4px;">{reminder.event_date}</div>
                                    </td>
                                    <td style="padding: 16px 20px; border-bottom: 1px solid #2E2E33;" width="50%">
                                        <div style="font-size: 11px; color: #71717A; font-weight: 600; text-transform: uppercase;">Scheduled Time</div>
                                        <div style="font-size: 15px; color: #FFFFFF; font-weight: 800; font-family: monospace; margin-top: 4px;">{reminder.event_time}</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 16px 20px;" width="50%">
                                        <div style="font-size: 11px; color: #71717A; font-weight: 600; text-transform: uppercase;">Market / Country</div>
                                        <div style="font-size: 14px; color: #FFFFFF; font-weight: 700; margin-top: 4px;">{reminder.country}</div>
                                    </td>
                                    <td style="padding: 16px 20px;" width="50%">
                                        <div style="font-size: 11px; color: #71717A; font-weight: 600; text-transform: uppercase;">Expected Impact</div>
                                        <div style="font-size: 13px; color: #F59E0B; font-weight: 800; text-transform: uppercase; margin-top: 4px;">⚡ {reminder.impact} Impact</div>
                                    </td>
                                </tr>
                            </table>

                            <!-- Notes / Trading Context -->
                            <div style="padding: 18px 20px; background-color: rgba(65, 105, 225, 0.08); border: 1px solid rgba(65, 105, 225, 0.2); border-radius: 14px; margin-bottom: 30px;">
                                <div style="font-size: 12px; font-weight: 700; color: #60A5FA; margin-bottom: 4px;">
                                    Market Intelligence Brief
                                </div>
                                <div style="font-size: 13px; color: #D4D4D8; line-height: 1.5;">
                                    {reminder.notes or 'This release will impact volatility, sovereign yields, and asset valuations. Monitor order book flows closely.'}
                                </div>
                            </div>

                            <!-- CTA Button -->
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center">
                                        <a href="https://pesamarkets.com/events/" 
                                           style="display: inline-block; background-color: #4169E1; color: #FFFFFF; font-size: 14px; font-weight: 700; text-decoration: none; padding: 14px 32px; border-radius: 9999px; box-shadow: 0 4px 15px rgba(65, 105, 225, 0.4);">
                                            View Live Events Calendar & Market Data &rarr;
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 25px 35px; border-top: 1px solid #27272A; background-color: #121214; text-align: center;">
                            <p style="margin: 0 0 6px 0; font-size: 12px; color: #71717A;">
                                This alert was delivered to your registered email address: <strong style="color: #A1A1AA;">{reminder.email}</strong>
                            </p>
                            <p style="margin: 0; font-size: 11px; color: #52525B;">
                                &copy; 2026 PesaMarkets Financial Technologies Ltd. All rights reserved.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    try:
        send_mail(
            subject=subject,
            message=text_content,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_content,
            fail_silently=False,
        )
        reminder.email_sent = True
        reminder.email_sent_at = timezone.now()
        reminder.save(update_fields=['email_sent', 'email_sent_at'])
        return True
    except Exception as e:
        logger.error(f"Failed to send event reminder email to {reminder.email}: {e}")
        return False

def set_event_reminder(user, email, event_data):
    """
    Creates or activates an EventReminder for the given user/email,
    and immediately dispatches the notification email.
    """
    event_id = event_data.get('id') or event_data.get('event_id')
    event_title = event_data.get('title') or event_data.get('event_title', 'Market Event')
    event_category = event_data.get('category', 'ECONOMIC')
    event_date = event_data.get('date') or event_data.get('event_date', 'Upcoming')
    event_time = event_data.get('time') or event_data.get('event_time', '')
    country = event_data.get('country') or event_data.get('market', 'All')
    symbol = event_data.get('symbol', '')
    impact = event_data.get('impact', 'High')
    notes = event_data.get('description') or event_data.get('notes') or event_data.get('trading_note', '')

    reminder, created = EventReminder.objects.update_or_create(
        email=email.strip().lower(),
        event_id=event_id,
        defaults={
            "user": user if (user and user.is_authenticated) else None,
            "event_title": event_title,
            "event_category": event_category,
            "event_date": event_date,
            "event_time": event_time,
            "country": country,
            "symbol": symbol,
            "impact": impact,
            "notes": notes,
            "is_active": True,
        }
    )

    # Dispatch email reminder immediately
    email_success = send_event_reminder_email(reminder)

    return {
        "success": True,
        "created": created,
        "is_active": True,
        "email": reminder.email,
        "event_id": reminder.event_id,
        "event_title": reminder.event_title,
        "email_sent": email_success,
        "message": f"Reminder set successfully! Confirmation email dispatched to your registered address ({reminder.email}).",
    }

def toggle_event_reminder(user, email, event_id, event_data=None):
    """
    Toggles a reminder on or off. If turning off, marks inactive.
    If turning on or creating, saves and sends email.
    """
    clean_email = email.strip().lower()
    existing = EventReminder.objects.filter(email=clean_email, event_id=event_id).first()

    if existing and existing.is_active:
        existing.is_active = False
        existing.save(update_fields=['is_active'])
        return {
            "success": True,
            "is_active": False,
            "event_id": event_id,
            "email": clean_email,
            "message": f"Reminder for '{existing.event_title}' has been removed.",
        }

    # If not existing or was inactive, activate it
    full_data = event_data or get_event_by_id(event_id) or {"id": event_id, "title": "Market Event"}
    return set_event_reminder(user, clean_email, full_data)

def get_user_reminded_ids(email):
    """Return set of event IDs that this user/email currently has active reminders for."""
    if not email:
        return set()
    return set(
        EventReminder.objects.filter(
            email=email.strip().lower(),
            is_active=True
        ).values_list('event_id', flat=True)
    )
