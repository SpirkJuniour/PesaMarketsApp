from django.urls import path
from . import views

urlpatterns = [
    # Web Pages
    path('', views.home, name='home'),
    path('markets/', views.markets_list, name='markets'),
    path('asset/<str:symbol>/', views.asset_detail, name='asset_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('trade/', views.trade, name='trade'),
    path('bonds/', views.bonds_page, name='bonds'),
    path('news/', views.news, name='news'),
    path('settings/', views.settings_page, name='settings'),
    path('support/', views.support, name='support'),
    path('profile/', views.profile, name='profile'),
    path('terminal/', views.terminal, name='terminal'),

    # REST APIs
    path('api/terminal/<str:symbol>/', views.api_terminal_data, name='api_terminal_data'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/quote/<str:symbol>/', views.api_quote, name='api_quote'),
    path('api/trade/execute/', views.api_trade_execute, name='api_trade_execute'),
    path('api/bonds/buy/', views.api_bonds_buy, name='api_bonds_buy'),
    path('api/news/', views.api_news, name='api_news'),
    path('api/watchlist/toggle/', views.api_watchlist_toggle, name='api_watchlist_toggle'),
]
