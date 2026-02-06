from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json


class KotakNeoUserToken(models.Model):
    """Model to store user authentication tokens for Kotak Neo API"""
    
    TOKEN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('invalid', 'Invalid'),
    ]
    
    user_id = models.CharField(max_length=50, unique=True, help_text="Kotak Neo User ID")
    access_token = models.TextField(help_text="Access token for API authentication")
    refresh_token = models.TextField(help_text="Refresh token for token renewal")
    token_type = models.CharField(max_length=20, default='Bearer')
    expires_at = models.DateTimeField(help_text="Token expiration timestamp")
    status = models.CharField(max_length=20, choices=TOKEN_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'KOTAK_NEO_API'
        verbose_name = "Kotak Neo User Token"
        verbose_name_plural = "Kotak Neo User Tokens"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure expires_at is set"""
        if self.expires_at is None:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        if self.expires_at is None:
            return True
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid and not expired"""
        if self.expires_at is None:
            return False
        return self.status == 'active' and not self.is_expired


class KotakNeoInstrument(models.Model):
    """Model to store Kotak Neo instruments data"""
    
    INSTRUMENT_TYPE_CHOICES = [
        ('EQ', 'Equity'),
        ('FUT', 'Future'),
        ('OPT', 'Option'),
        ('CE', 'Call Option'),
        ('PE', 'Put Option'),
        ('INDEX', 'Index'),
    ]
    
    instrument_token = models.CharField(max_length=50, unique=True, help_text="Unique instrument token")
    tradingsymbol = models.CharField(max_length=50, help_text="Trading symbol")
    name = models.CharField(max_length=100, help_text="Instrument name")
    exchange = models.CharField(max_length=10, help_text="Exchange (NSE, NFO, etc.)")
    instrument_type = models.CharField(max_length=10, choices=INSTRUMENT_TYPE_CHOICES, help_text="Type of instrument")
    segment = models.CharField(max_length=20, help_text="Market segment")
    expiry = models.DateField(blank=True, null=True, help_text="Expiry date for derivatives")
    strike_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Strike price for options")
    lot_size = models.IntegerField(default=1, help_text="Lot size")
    tick_size = models.DecimalField(max_digits=10, decimal_places=2, default=0.05, help_text="Tick size")
    is_active = models.BooleanField(default=True, help_text="Whether instrument is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kotak Neo Instrument"
        verbose_name_plural = "Kotak Neo Instruments"
        ordering = ['tradingsymbol']
    
    def __str__(self):
        return f"{self.tradingsymbol} ({self.exchange})"


class KotakNeoOrder(models.Model):
    """Model to store Kotak Neo orders"""
    
    ORDER_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('NRML', 'Normal'),
        ('MIS', 'MIS'),
        ('CNC', 'CNC'),
    ]
    
    ORDER_VARIANT_CHOICES = [
        ('MARKET', 'Market'),
        ('LIMIT', 'Limit'),
        ('SL', 'Stop Loss'),
        ('SL-M', 'Stop Loss Market'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('OPEN', 'Open'),
    ]
    
    order_id = models.CharField(max_length=50, unique=True, help_text="Kotak Neo order ID")
    user_token = models.ForeignKey(KotakNeoUserToken, on_delete=models.CASCADE, related_name='orders')
    instrument = models.ForeignKey(KotakNeoInstrument, on_delete=models.CASCADE, related_name='orders')
    
    transaction_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES, help_text="Buy or Sell")
    quantity = models.IntegerField(help_text="Order quantity")
    product = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='NRML', help_text="Product type")
    order_type = models.CharField(max_length=10, choices=ORDER_VARIANT_CHOICES, default='LIMIT', help_text="Order variant")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Order price")
    trigger_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Trigger price for SL orders")
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING', help_text="Order status")
    filled_quantity = models.IntegerField(default=0, help_text="Filled quantity")
    pending_quantity = models.IntegerField(default=0, help_text="Pending quantity")
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Average fill price")
    
    order_timestamp = models.DateTimeField(help_text="Order timestamp from broker")
    exchange_timestamp = models.DateTimeField(null=True, blank=True, help_text="Exchange timestamp")
    
    error_message = models.TextField(blank=True, null=True, help_text="Error message if order failed")
    response_data = models.JSONField(default=dict, help_text="Full response from Kotak Neo API")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kotak Neo Order"
        verbose_name_plural = "Kotak Neo Orders"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.transaction_type} {self.instrument.tradingsymbol}"


class KotakNeoMarketData(models.Model):
    """Model to store real-time market data from Kotak Neo"""
    
    instrument = models.ForeignKey(KotakNeoInstrument, on_delete=models.CASCADE, related_name='market_data')
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Data timestamp")
    
    # OHLCV data
    open_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    
    # Additional market data
    last_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Bid/Ask data
    bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_quantity = models.IntegerField(null=True, blank=True)
    ask_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ask_quantity = models.IntegerField(null=True, blank=True)
    
    # For options
    open_interest = models.BigIntegerField(null=True, blank=True)
    implied_volatility = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    raw_data = models.JSONField(default=dict, help_text="Raw market data from API")
    
    class Meta:
        verbose_name = "Kotak Neo Market Data"
        verbose_name_plural = "Kotak Neo Market Data"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['instrument', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.instrument.tradingsymbol} - {self.timestamp}"


class KotakNeoHolding(models.Model):
    """Model to store user holdings from Kotak Neo"""
    
    user_token = models.ForeignKey(KotakNeoUserToken, on_delete=models.CASCADE, related_name='holdings')
    instrument = models.ForeignKey(KotakNeoInstrument, on_delete=models.CASCADE, related_name='holdings')
    
    quantity = models.IntegerField(help_text="Holding quantity")
    average_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average purchase price")
    last_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Last traded price")
    market_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Current market value")
    pnl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Profit/Loss")
    pnl_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="P&L percentage")
    
    product = models.CharField(max_length=10, default='NRML', help_text="Product type")
    exchange = models.CharField(max_length=10, help_text="Exchange")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kotak Neo Holding"
        verbose_name_plural = "Kotak Neo Holdings"
        ordering = ['-updated_at']
        unique_together = ['user_token', 'instrument', 'product']
    
    def __str__(self):
        return f"{self.instrument.tradingsymbol} - {self.quantity}"


class KotakNeoAlert(models.Model):
    """Model to store trading alerts and notifications"""
    
    ALERT_TYPE_CHOICES = [
        ('PRICE', 'Price Alert'),
        ('VOLUME', 'Volume Alert'),
        ('OI', 'Open Interest Alert'),
        ('CUSTOM', 'Custom Alert'),
    ]
    
    ALERT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    CONDITION_CHOICES = [
        ('ABOVE', 'Above'),
        ('BELOW', 'Below'),
        ('EQUALS', 'Equals'),
        ('CROSSES_ABOVE', 'Crosses Above'),
        ('CROSSES_BELOW', 'Crosses Below'),
    ]
    
    name = models.CharField(max_length=100, help_text="Alert name")
    user_token = models.ForeignKey(KotakNeoUserToken, on_delete=models.CASCADE, related_name='alerts')
    instrument = models.ForeignKey(KotakNeoInstrument, on_delete=models.CASCADE, related_name='alerts')
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, help_text="Type of alert")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, help_text="Alert condition")
    target_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Target value for alert")
    
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='ACTIVE', help_text="Alert status")
    is_repeatable = models.BooleanField(default=False, help_text="Whether alert can be triggered multiple times")
    
    triggered_at = models.DateTimeField(null=True, blank=True, help_text="When alert was triggered")
    triggered_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Value when triggered")
    
    description = models.TextField(blank=True, help_text="Alert description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kotak Neo Alert"
        verbose_name_plural = "Kotak Neo Alerts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.instrument.tradingsymbol}"


class KotakNeoOptionChain(models.Model):
    """Model to store option chain data"""
    
    OPTION_TYPE_CHOICES = [
        ('CE', 'Call'),
        ('PE', 'Put'),
    ]
    
    symbol = models.CharField(max_length=20, help_text="Underlying symbol")
    expiry_date = models.DateField(help_text="Expiry date")
    strike_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Strike price")
    option_type = models.CharField(max_length=2, choices=OPTION_TYPE_CHOICES, help_text="Call or Put")
    
    # Market data
    last_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Volume and OI
    volume = models.BigIntegerField(null=True, blank=True)
    open_interest = models.BigIntegerField(null=True, blank=True)
    change_in_oi = models.BigIntegerField(null=True, blank=True)
    
    # Greeks
    implied_volatility = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    delta = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    gamma = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    theta = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    vega = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    # Bid/Ask
    bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_quantity = models.IntegerField(null=True, blank=True)
    ask_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ask_quantity = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kotak Neo Option Chain"
        verbose_name_plural = "Kotak Neo Option Chains"
        ordering = ['symbol', 'strike_price', 'option_type']
        unique_together = ['symbol', 'expiry_date', 'strike_price', 'option_type']
        indexes = [
            models.Index(fields=['symbol', 'expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.symbol} {self.strike_price} {self.option_type} {self.expiry_date}"


class KotakNeoAPILog(models.Model):
    """Model to log API calls and responses for debugging"""
    
    LOG_LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('DEBUG', 'Debug'),
    ]
    
    user_token = models.ForeignKey(KotakNeoUserToken, on_delete=models.CASCADE, related_name='api_logs', null=True, blank=True)
    endpoint = models.CharField(max_length=200, help_text="API endpoint called")
    method = models.CharField(max_length=10, help_text="HTTP method")
    status_code = models.IntegerField(null=True, blank=True, help_text="HTTP status code")
    response_time = models.DurationField(null=True, blank=True, help_text="API response time")
    
    request_data = models.JSONField(default=dict, help_text="Request data sent")
    response_data = models.JSONField(default=dict, help_text="Response data received")
    
    log_level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='INFO')
    message = models.TextField(blank=True, help_text="Log message")
    error_details = models.TextField(blank=True, help_text="Error details if any")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kotak Neo API Log"
        verbose_name_plural = "Kotak Neo API Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_token', '-created_at']),
            models.Index(fields=['log_level', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.endpoint} - {self.status_code} - {self.created_at}"
