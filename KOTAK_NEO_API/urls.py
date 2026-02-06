from django.urls import path
from . import views

app_name = 'kotak_neo_api'

urlpatterns = [
    # Dashboard and Main Views
    path('dashboard/', views.kotak_dashboard, name='kotak_dashboard'),
    path('orders/', views.kotak_orders_view, name='kotak_orders'),
    path('holdings/', views.kotak_holdings_view, name='kotak_holdings'),
    path('market-data/', views.kotak_market_data_view, name='kotak_market_data'),
    path('alerts/', views.kotak_alerts_view, name='kotak_alerts'),
    
    # API Endpoints
    path('api/place-order/', views.kotak_api_place_order, name='kotak_api_place_order'),
    path('api/get-quote/', views.kotak_api_get_quote, name='kotak_api_get_quote'),
    path('api/get-holdings/', views.kotak_api_get_holdings, name='kotak_api_get_holdings'),
    path('api/get-option-chain/', views.kotak_api_get_option_chain, name='kotak_api_get_option_chain'),
    path('api/market-status/', views.kotak_market_status, name='kotak_market_status'),
    path('api/instrument-search/', views.kotak_instrument_search, name='kotak_instrument_search'),
    
    # Management Views
    path('token-management/', views.kotak_token_management, name='kotak_token_management'),
    path('api-logs/', views.kotak_api_logs_view, name='kotak_api_logs'),
    
    # Sync Views
    path('sync/holdings/', views.kotak_sync_holdings, name='kotak_sync_holdings'),
    path('sync/market-data/', views.kotak_sync_market_data, name='kotak_sync_market_data'),
    path('sync/instruments/', views.kotak_sync_instruments, name='kotak_sync_instruments'),
    
    # Alert Management
    path('alerts/create/', views.kotak_create_alert, name='kotak_create_alert'),
    path('alerts/<int:alert_id>/edit/', views.kotak_edit_alert, name='kotak_edit_alert'),
    path('alerts/<int:alert_id>/delete/', views.kotak_delete_alert, name='kotak_delete_alert'),
] 