from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from KOTAK_NEO_API.models import (
    KotakNeoUserToken, KotakNeoInstrument, KotakNeoOrder, 
    KotakNeoMarketData, KotakNeoHolding, KotakNeoAlert,
    KotakNeoOptionChain, KotakNeoAPILog
)


# @admin.register(KotakNeoUserToken)
# class KotakNeoUserTokenAdmin(admin.ModelAdmin):
#     list_display = ['user_id', 'status', 'is_expired', 'is_valid', 'expires_at', 'created_at']
#     list_filter = ['status', 'created_at', 'updated_at']
#     search_fields = ['user_id']
#     readonly_fields = ['created_at', 'updated_at', 'is_expired', 'is_valid']
#     ordering = ['-updated_at']
    
#     fieldsets = (
#         ('User Information', {
#             'fields': ('user_id', 'status')
#         }),
#         ('Token Details', {
#             'fields': ('access_token', 'refresh_token', 'token_type', 'expires_at')
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#         ('Token Status', {
#             'fields': ('is_expired', 'is_valid'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def is_expired(self, obj):
#         try:
#             return obj.is_expired
#         except:
#             return True
#     is_expired.boolean = True
#     is_expired.short_description = 'Expired'
    
#     def is_valid(self, obj):
#         try:
#             return obj.is_valid
#         except:
#             return False
#     is_valid.boolean = True
#     is_valid.short_description = 'Valid'


# @admin.register(KotakNeoInstrument)
# class KotakNeoInstrumentAdmin(admin.ModelAdmin):
#     list_display = ['tradingsymbol', 'name', 'exchange', 'instrument_type', 'is_active', 'created_at']
#     list_filter = ['exchange', 'instrument_type', 'is_active', 'created_at']
#     search_fields = ['tradingsymbol', 'name', 'instrument_token']
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['tradingsymbol']
    
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('instrument_token', 'tradingsymbol', 'name', 'exchange'),
#             #'classes': ('wide', 'extrapretty'),  # Add custom CSS classes
#         }),
#         ('Instrument Details', {
#             'fields': ('instrument_type', 'segment', 'lot_size', 'tick_size', 'is_active')
#         }),
#         ('Derivative Details', {
#             'fields': ('expiry', 'strike_price'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#     class Media:
#         css = {
#             'all': ('admin/css/custom.css',)
#         }


# @admin.register(KotakNeoOrder)
# class KotakNeoOrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'order_id', 'user_token', 'instrument', 'transaction_type', 
#         'quantity', 'price', 'status', 'created_at'
#     ]
#     list_filter = [
#         'status', 'transaction_type', 'product', 'order_type', 
#         'created_at', 'user_token'
#     ]
#     search_fields = ['order_id', 'instrument__tradingsymbol', 'user_token__user_id']
#     readonly_fields = ['created_at', 'updated_at', 'order_id']
#     ordering = ['-created_at']
    
#     fieldsets = (
#         ('Order Information', {
#             'fields': ('order_id', 'user_token', 'instrument', 'status')
#         }),
#         ('Order Details', {
#             'fields': ('transaction_type', 'quantity', 'product', 'order_type', 'price', 'trigger_price')
#         }),
#         ('Execution Details', {
#             'fields': ('filled_quantity', 'pending_quantity', 'average_price'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('order_timestamp', 'exchange_timestamp', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#         ('Error Information', {
#             'fields': ('error_message', 'response_data'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user_token', 'instrument')


# @admin.register(KotakNeoMarketData)
# class KotakNeoMarketDataAdmin(admin.ModelAdmin):
#     list_display = [
#         'instrument', 'last_price', 'change_percentage', 'volume', 
#         'open_interest', 'timestamp'
#     ]
#     list_filter = ['instrument__exchange', 'instrument__instrument_type', 'timestamp']
#     search_fields = ['instrument__tradingsymbol', 'instrument__name']
#     readonly_fields = ['timestamp', 'raw_data']
#     ordering = ['-timestamp']
    
#     fieldsets = (
#         ('Instrument', {
#             'fields': ('instrument',)
#         }),
#         ('Price Data', {
#             'fields': ('open_price', 'high_price', 'low_price', 'close_price', 'last_price')
#         }),
#         ('Change Data', {
#             'fields': ('change', 'change_percentage', 'volume')
#         }),
#         ('Bid/Ask Data', {
#             'fields': ('bid_price', 'bid_quantity', 'ask_price', 'ask_quantity'),
#             'classes': ('collapse',)
#         }),
#         ('Options Data', {
#             'fields': ('open_interest', 'implied_volatility'),
#             'classes': ('collapse',)
#         }),
#         ('Raw Data', {
#             'fields': ('raw_data', 'timestamp'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('instrument')


# @admin.register(KotakNeoHolding)
# class KotakNeoHoldingAdmin(admin.ModelAdmin):
#     list_display = [
#         'user_token', 'instrument', 'quantity', 'average_price', 
#         'last_price', 'market_value', 'pnl_percentage', 'updated_at'
#     ]
#     list_filter = ['product', 'exchange', 'updated_at', 'user_token']
#     search_fields = ['instrument__tradingsymbol', 'user_token__user_id']
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['-updated_at']
    
#     fieldsets = (
#         ('Holding Information', {
#             'fields': ('user_token', 'instrument', 'quantity', 'product', 'exchange')
#         }),
#         ('Price Information', {
#             'fields': ('average_price', 'last_price', 'market_value')
#         }),
#         ('P&L Information', {
#             'fields': ('pnl', 'pnl_percentage'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user_token', 'instrument')


# @admin.register(KotakNeoAlert)
# class KotakNeoAlertAdmin(admin.ModelAdmin):
#     list_display = [
#         'name', 'user_token', 'instrument', 'alert_type', 'condition', 
#         'target_value', 'status', 'is_repeatable', 'created_at'
#     ]
#     list_filter = [
#         'alert_type', 'condition', 'status', 'is_repeatable', 
#         'created_at', 'user_token'
#     ]
#     search_fields = ['name', 'instrument__tradingsymbol', 'user_token__user_id']
#     readonly_fields = ['created_at', 'updated_at', 'triggered_at']
#     ordering = ['-created_at']
    
#     fieldsets = (
#         ('Alert Information', {
#             'fields': ('name', 'user_token', 'instrument', 'description')
#         }),
#         ('Alert Configuration', {
#             'fields': ('alert_type', 'condition', 'target_value', 'is_repeatable')
#         }),
#         ('Status Information', {
#             'fields': ('status', 'triggered_at', 'triggered_value'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user_token', 'instrument')


# @admin.register(KotakNeoOptionChain)
# class KotakNeoOptionChainAdmin(admin.ModelAdmin):
#     list_display = [
#         'symbol', 'expiry_date', 'strike_price', 'option_type', 
#         'last_price', 'volume', 'open_interest', 'implied_volatility'
#     ]
#     list_filter = [
#         'symbol', 'option_type', 'expiry_date', 'created_at'
#     ]
#     search_fields = ['symbol', 'strike_price']
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['symbol', 'strike_price', 'option_type']
    
#     fieldsets = (
#         ('Option Information', {
#             'fields': ('symbol', 'expiry_date', 'strike_price', 'option_type')
#         }),
#         ('Market Data', {
#             'fields': ('last_price', 'change', 'change_percentage', 'volume', 'open_interest', 'change_in_oi')
#         }),
#         ('Greeks', {
#             'fields': ('implied_volatility', 'delta', 'gamma', 'theta', 'vega'),
#             'classes': ('collapse',)
#         }),
#         ('Bid/Ask', {
#             'fields': ('bid_price', 'bid_quantity', 'ask_price', 'ask_quantity'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )


# @admin.register(KotakNeoAPILog)
# class KotakNeoAPILogAdmin(admin.ModelAdmin):
#     list_display = [
#         'endpoint', 'method', 'status_code', 'log_level', 
#         'user_token', 'response_time', 'created_at'
#     ]
#     list_filter = [
#         'log_level', 'method', 'status_code', 'created_at', 'user_token'
#     ]
#     search_fields = ['endpoint', 'message', 'user_token__user_id']
#     readonly_fields = ['created_at', 'request_data', 'response_data', 'error_details']
#     ordering = ['-created_at']
    
#     fieldsets = (
#         ('Request Information', {
#             'fields': ('user_token', 'endpoint', 'method', 'status_code', 'response_time')
#         }),
#         ('Log Details', {
#             'fields': ('log_level', 'message')
#         }),
#         ('Request/Response Data', {
#             'fields': ('request_data', 'response_data'),
#             'classes': ('collapse',)
#         }),
#         ('Error Details', {
#             'fields': ('error_details',),
#             'classes': ('collapse',)
#         }),
#         ('Timestamp', {
#             'fields': ('created_at',),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user_token')
    
#     def has_add_permission(self, request):
#         return False  # API logs should only be created by the system
    
#     def has_change_permission(self, request, obj=None):
#         return False  # API logs should not be modified
