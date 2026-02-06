from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta



class Change_IN_OI_Increasing(models.Model):
    """
    Model to store Change in OI Increasing data.
    This model is used to track stocks with increasing change in open interest.
    """ 
    id = models.AutoField(primary_key=True)
    tradingsymbol = models.CharField(max_length=40)
    name = models.CharField(max_length=40, default='')
    previous_close = models.FloatField()
    current_price = models.FloatField()
    change_in_price = models.FloatField()
    change_in_price_percentage = models.FloatField()

    prev_oi = models.FloatField()
    oi = models.FloatField()
    change_in_oi = models.FloatField()
    change_in_oi_percentage = models.FloatField()

    oi_quantity = models.FloatField(default=0)
    change_in_oi_quantity = models.FloatField(default=0)
    prev_oi_quantity = models.FloatField(default=0)
    change_in_oi_percentage_quantity = models.FloatField(default=0)

    created_at = models.CharField(max_length=20, default=datetime.now().strftime("%Y-%m-%d %H:%M"))

    def __str__(self):
        return self.symbol

    class Meta:
        verbose_name_plural = "Change in OI Increasing Stocks"
        ordering = ['change_in_oi_percentage']

# Create your models here.

# class NSEOptionChainData(models.Model):
#     symbol = models.CharField(max_length=10)
#     expiry_date = models.CharField(max_length=10)
#     strike_price = models.FloatField()
#     call_volume = models.FloatField()
#     call_openInterest = models.FloatField()
#     call_changeinOpenInterest = models.FloatField()
#     call_impliedVolatility = models.FloatField()
#     call_lastPrice = models.FloatField()
#     call_change = models.FloatField()
#     call_bidqty = models.FloatField()
#     call_bid = models.FloatField()
#     call_ask = models.FloatField()
#     call_askqty = models.FloatField()

#     put_volume = models.FloatField()
#     put_openInterest = models.FloatField()
#     put_changeinOpenInterest = models.FloatField() 
#     put_impliedVolatility = models.FloatField()
#     put_lastPrice = models.FloatField()
#     put_change = models.FloatField()
#     put_bidqty = models.FloatField()
#     put_bid = models.FloatField()
#     put_ask = models.FloatField()
#     put_askqty = models.FloatField()

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         """
#         :return: the Category name
#         """
#         return self.symbol

#     class Meta:
#         """docstring for meta"""
#         ordering = ('id',)
#         verbose_name_plural = "NSE Option Chain"        



class ScaningStock(models.Model):   
    symbol = models.CharField(max_length=10)
    total_volume_call = models.FloatField()
    total_volume_put = models.FloatField()
    total_coi_call = models.FloatField()
    total_coi_put = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.symbol

class ScaningStockOI(models.Model):
    type = models.CharField(max_length=10, default='')   
    symbol = models.CharField(max_length=10)
    total_volume_call = models.FloatField()
    total_volume_put = models.FloatField()
    total_coi_call = models.FloatField()
    total_coi_put = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.symbol


class Scanner_ema(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=10)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    ema = models.FloatField()
    ema_type = models.CharField(max_length=10)
    date = models.DateTimeField()


    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.symbol
    

    
class CronJob(models.Model):
    """Model to track and manage cron jobs through Django Admin"""
    
    JOB_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    function_path = models.CharField(max_length=200, help_text="e.g., trading.cron.my_scheduled_job")
    cron_schedule = models.CharField(max_length=100, help_text="e.g., */30 * * * * for every 30 minutes")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='active')
    is_enabled = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cron Job"
        verbose_name_plural = "Cron Jobs"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CronJobExecution(models.Model):
    """Model to track individual cron job executions"""
    
    EXECUTION_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('running', 'Running'),
    ]
    
    job = models.ForeignKey(CronJob, on_delete=models.CASCADE, related_name='executions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES, default='running')
    duration = models.DurationField(null=True, blank=True)
    output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Cron Job Execution"
        verbose_name_plural = "Cron Job Executions"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.job.name} - {self.started_at}"
    
    def save(self, *args, **kwargs):
        if self.completed_at and self.started_at:
            self.duration = self.completed_at - self.started_at
        super().save(*args, **kwargs)




class Orders(models.Model):
    """Model """
    exchange = [
        ('NSE', 'NSE'),
        # ('BSE', 'BSE'),
        # ('MCX', 'MCX'),
        ('NFO', 'NFO'),
        # ('CDS', 'CDS'),
        # ('BFO', 'BFO'),
        # ('NSEFO', 'NSEFO'),
        # ('NSECDS', 'NSECDS'),
        # ('NSEBFO', 'NSEBFO'),
        # ('NSECM', 'NSECM'),
        # ('NSEEQ', 'NSEEQ'), 
        ]    
    id = models.AutoField(primary_key=True)
    strategy = models.CharField(max_length=50, blank=True, null=True,default='ATH')
    exchange = models.CharField(max_length=10, default='NSE',choices=exchange)
    
    ORDER_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell')
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('NRML', 'Normal')
        # ('MIS', 'MIS'),
        # ('CNC', 'CNC')
    ]
    
    ORDER_VARIANT_CHOICES = [
        ('MARKET', 'Market'),
        ('LIMIT', 'Limit'), 
        ('SL', 'Stop Loss'),
        ('SL-M', 'Stop Loss Market')
    ]

    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('OPEN', 'Open')
    ]
   
    

    
    symbol = models.CharField(max_length=50, blank=True, null=True, verbose_name='Symbol')
    #symbol_instrument_token = models.CharField(max_length=50, blank=False, null=False)

    #tradingsymbol = models.CharField(max_length=50)
    instrument_token = models.CharField('Ins-Token',max_length=50)


    transaction_type = models.CharField('T.Type',max_length=4, choices=ORDER_TYPE_CHOICES, default='BUY')
    quantity = models.IntegerField('Qty')
    product = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='NRML')
    order_type = models.CharField(max_length=10, choices=ORDER_VARIANT_CHOICES, default='LIMIT')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stoploss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trigger_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    order_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    filled_quantity = models.IntegerField('Fill Qty',default=0)
    pending_quantity = models.IntegerField('Pending Qty',default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    error_message = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response = models.TextField(blank=True, null=True)
    parent_symbol = models.CharField(max_length=50, blank=True, null=True, default='')
    parent_token = models.CharField(max_length=50, blank=True, null=True, default='')

    symbol_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    use_parent_symbol = models.CharField(max_length=1,default=1)
    option_type = models.CharField(max_length=2,default='CE')

    class Meta:
        db_table = "orders"
        verbose_name = "Orders"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.symbol}"



class OrdersDetail(models.Model):
    """Model """
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_details', verbose_name='Order ID')
    broker_order_id = models.CharField('B.OrdID',help_text='Broker order Id',max_length=30,null=True)
    strategy = models.CharField(max_length=50, blank=True, null=True,default='ATH')
    exchange = models.CharField(max_length=10,null=True,help_text='NSE or NFO')
    PRODUCT_TYPE_CHOICES = [
        ('NRML', 'Normal'),
        ('MIS', 'MIS'),
        ('CNC', 'CNC')
    ]
    
    ORDER_VARIANT_CHOICES = [
        ('MARKET', 'Market'),
        ('LIMIT', 'Limit'), 
        ('SL', 'Stop Loss'),
        ('SL-M', 'Stop Loss Market')
    ]

    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled')
    ]
    BOOL_CHOICES = ((True, 'Manual'), (False, 'Automatic'))

   
    symbol = models.CharField(max_length=50, blank=True, null=True)
    instrument_token = models.CharField('Token',help_text='Unique Instrument Token',max_length=50)


    transaction_type = models.CharField('T.Type',max_length=4, null=True)
    quantity = models.IntegerField('QTY')
    product = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='NRML')
    order_type = models.CharField(max_length=10, choices=ORDER_VARIANT_CHOICES, default='LIMIT')
    price = models.DecimalField('B. Price',max_digits=10, decimal_places=2, null=True, blank=True)
    stoploss_type = models.BooleanField('St.Type',choices=BOOL_CHOICES, default=True)
    stoploss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trigger_price = models.DecimalField('Target',max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    filled_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    parent_symbol = models.CharField(max_length=50, blank=True, null=True, default='')
    parent_token = models.CharField(max_length=50, blank=True, null=True, default='')
    symbol_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    error_message = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response = models.TextField(blank=True, null=True)
    option_type = models.CharField(max_length=2,default='CE')


    #ath_type = models.CharField(max_length=10,choice=[('up','up'),('down','down')] default='up', null=True, blank=True)


    class Meta:
        db_table = "orders_details"
        verbose_name = "Orders Details"
        verbose_name_plural = "Orders Details"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.symbol}"


class PreMarketStock(models.Model):
    """
    Model to store pre-market stock data.
    This model is used to track stocks that are active in the pre-market session.
    """
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=50)
    last_price = models.FloatField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    change = models.FloatField()
    change_percentage = models.FloatField()
   
    volume = models.FloatField()
    oi = models.FloatField()
    buy_quantity = models.FloatField(null=True)
    sell_quantity = models.FloatField(null=True)
    total_traded_value = models.FloatField(null=True)

    previous_close = models.FloatField(null=True)
    type = models.CharField(max_length=30, choices=[('PRE-MARKET', 'pre-market'), ('POST-MARKET', 'post-market'),('MARKET', 'market') ], default='PRE-MARKET', help_text='Type of pre-market data')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol

    class Meta:
        verbose_name_plural = "Pre-Market Stocks"
        ordering = ['-created_at']

class MostActiveSymbol(models.Model):
    """
    Model to store most active symbols data.
    This model is used to track stocks that are most active.
    """
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=50)
    # volume = models.FloatField()
    # change = models.FloatField()
    # change_percentage = models.FloatField()
    # oi = models.FloatField()
    type = models.CharField(max_length=30, choices=[('CAll', 'call'), ('PUT', 'put'),('FAVORITE', 'favorite'),('HATE', 'Hate'),('LOVELY', 'lovely') ], default='CAll', help_text='Type of most active data')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symbol

    class Meta:
        verbose_name_plural = "Most Active Symbols"
        ordering = ['-created_at']
        db_table = "most_active_symbol"

class COI(models.Model):
    """
    Model to store COI data.
    This model is used to track stocks that are active in the pre-market session.
    """
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=50,default='',db_index=True)
    instrument_token = models.CharField(max_length=50,default='')
    expiry_date = models.DateField(null=False, blank=False)
    strike = models.FloatField(default=0)
    current_price = models.FloatField(default=0)

    call_trading_symbol = models.CharField(max_length=50,default='')
    call_instrument_token = models.CharField(max_length=50,default='')
    call_oi = models.FloatField(default=0)
    call_coi = models.FloatField(default=0)
    call_coi_percentage = models.FloatField(default=0)
    call_volume = models.FloatField(default=0)
    call_last_price = models.FloatField(default=0)
    call_lots = models.FloatField(default=0)
    call_pre_oi = models.FloatField(default=0)
    call_current_price = models.FloatField(default=0)
    call_day_low = models.FloatField(default=0)
    call_day_high = models.FloatField(default=0)
    call_day_open = models.FloatField(default=0)

    put_trading_symbol = models.CharField(max_length=50,default='')
    put_instrument_token = models.CharField(max_length=50,default='')
    put_oi = models.FloatField(default=0)
    put_coi = models.FloatField(default=0)
    put_coi_percentage = models.FloatField(default=0)
    put_volume = models.FloatField(default=0)
    put_last_price = models.FloatField(default=0)
    put_lots = models.FloatField(default=0)
    put_pre_oi = models.FloatField(default=0)
    put_current_price = models.FloatField(default=0)
    put_day_low = models.FloatField(default=0)
    put_day_high = models.FloatField(default=0)
    put_day_open = models.FloatField(default=0)



    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    def __str__(self):
        return self.symbol

    class Meta:
        db_table = "coi_data"
        verbose_name_plural = "COI"
        ordering = ['-created_at']