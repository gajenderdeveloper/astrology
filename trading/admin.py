from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, DateField
from django.db.models.functions import Trunc
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from django import forms
from dal import autocomplete
from .models import Orders,OrdersDetail
import importlib
import traceback
import threading
from django.forms import TextInput, Textarea

from django.db import models
from .autocomplete_views import instruments_df
#instruments = instruments_df[(instruments_df['exchange'] == 'NSE') & (instruments_df['segment'] == 'NSE')]
#symbol_list = instruments['tradingsymbol'].unique()
#symbol_choice = [(symbol, symbol) for symbol in symbol_list if isinstance(symbol, str) and len(symbol) > 0]

class UniqueDateFilter(admin.SimpleListFilter):
    title = _('created date')
    parameter_name = 'created_at__date'

    def lookups(self, request, model_admin):
        dates = model_admin.model.objects.annotate(
            date=Trunc('created_at', 'date', output_field=DateField())
        ).values('date').annotate(
            count=Count('pk')
        ).order_by('-date')
        return [(d['date'].strftime('%Y-%m-%d'), d['date'].strftime('%b %d, %Y')) for d in dates]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_at__date=self.value())
        return queryset

symbol_choice = []
class OrdersForm(forms.ModelForm):
    exchange = forms.ChoiceField(
        choices=[('NSE', 'NSE'), ('NFO', 'NFO')],  # Add your exchange options here
        widget=forms.Select(attrs={
            'onchange': 'updateSymbolChoices(this.value);'  # JavaScript to handle the change
        })
    )
    symbol = forms.ChoiceField(
        choices=symbol_choice,
        widget=autocomplete.ListSelect2(
            url='my_autocomplete',
            attrs={
                'data-minimum-input-length': 0,
                'data-allow-clear': 'false',
                'data-placeholder': 'Select a symbol...',
                'data-html': True,
                'data-depends-on': 'exchange',  # Indicates this field depends on exchange
                'onchange': 'updateSymbolChoices2(this.value);'  # JavaScript to handle the change
                
            },
            forward=['exchange']  # Forward the exchange value to the autocomplete view
        )
    )


    class Meta:
        model = Orders
        fields = '__all__'
        widgets = {
            'instrument_token': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing an existing instance, set the initial choices
        if self.instance and self.instance.pk:
            exchange = self.instance.exchange
            if exchange:
                if exchange == 'NFO':
                    segment = 'NFO-OPT'
                if exchange == 'NSE':
                    segment = 'NSE'
                filtered_instruments = instruments_df[
                    (instruments_df['exchange'] == exchange) & 
                    (instruments_df['segment'] == segment)
                ]
                filtered_symbols = filtered_instruments['tradingsymbol'].unique()
                self.fields['symbol'].choices = [
                    (symbol, symbol) for symbol in filtered_symbols 
                    if isinstance(symbol, str) and len(symbol) > 0
                ]
                # Set the current value
                self.fields['symbol'].initial = self.instance.symbol
        
        # Handle POST data for new submissions
        elif 'exchange' in self.data:
            try:
                exchange = self.data.get('exchange')
                if exchange == 'NFO':
                    segment = 'NFO-OPT'
                if exchange == 'NSE':
                    segment = 'NSE'
                filtered_instruments = instruments_df[
                    (instruments_df['exchange'] == exchange) & 
                    (instruments_df['segment'] == segment)
                ]
                filtered_symbols = filtered_instruments['tradingsymbol'].unique()
                self.fields['symbol'].choices = [
                    (symbol, symbol) for symbol in filtered_symbols 
                    if isinstance(symbol, str) and len(symbol) > 0
                ]
            except (ValueError, TypeError):
                pass
       


class OrdersAdmin(admin.ModelAdmin):
    # autocomplete_fields = ['symbol']
    list_display = ['strategy','symbol', 'price','status_colored','parent_symbol','symbol_price','stoploss','trigger_price',   'parent_token','order_id','exchange','transaction_type','quantity','product','order_type','average_price','error_message','created_at','updated_at']
    #list_filter = (UniqueDateFilter,  'status')
    search_fields = ('symbol', 'order_id', 'strategy','status')
    readonly_fields = ('parent_token', 'created_at', 'updated_at', 'filled_quantity', 'pending_quantity','response')
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return True
    
    form = OrdersForm
   
     # Add this to ensure the autocomplete media is loaded
    class Media:
        js = ('admin/js/jquery.init.js',)  # Ensure jQuery is loaded first

    def status_colored(self, obj):
        colors = {
            'PENDING': '#FFC0CB',
            'COMPLETE': '',
            'CLOSE': '',
            'OPEN': '',
            'REJECTED': '#ff7f7f',
            'CANCELLED': '#ff7f7f',
        }
        textcolors = {
            'PENDING':'<b style="background:{};">{}</b>',
            'COMPLETE':'<b style="background:{};">{}</b>',
            'OPEN':'<b style="background:{};">{}</b>',
            'CLOSE':'<b style="background:{};">{}</b>',
            'REJECTED': '<b style="background:{};">{}</b>',
            'CANCELLED': '<b style="background:{};">{}</b>',
        }
        return format_html(
            textcolors[obj.status],
            colors[obj.status],
            obj.status,
        )
    status_colored.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        # When a symbol is selected, update the instrument_token automatically
        if form.cleaned_data.get('symbol'):
            symbol = form.cleaned_data['symbol']
            exchange = form.cleaned_data['exchange']
            
            # Find the instrument token based on symbol and exchange
            instrument = instruments_df[
                (instruments_df['tradingsymbol'] == symbol) & 
                (instruments_df['exchange'] == exchange)
            ].iloc[0]
            
            obj.instrument_token = instrument['instrument_token']
            # You might also want to set other fields like tradingsymbol if needed
        
        super().save_model(request, obj, form, change)

admin.site.register(Orders,OrdersAdmin)

# class OrdersDetailForm(forms.ModelForm):
#     class Meta:
#         model = OrdersDetail
#         fields = '__all__'
#         widgets = {
#             'stoploss': forms.TextInput(attrs={'size': '2'}),
#         }

class OrdersDetailAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'broker_order_id', 'strategy', 'symbol', 'price', 'status_colored', 'symbol_price', 'stoploss', 'trigger_price','stoploss_type', 'transaction_type', 'quantity', 'order_type','filled_quantity', 'error_message', 'pending_quantity', 'average_price', 'product',  'instrument_token','exchange','strategy','created_at', 'updated_at']
    def status_colored(self, obj):
        colors = {
            'PENDING': '#FFC0CB',
            'OPEN': '#FFC0CB',
            'CLOSE': '#FFC0CB',
            'COMPLETE': '#90EE90',
            'REJECTED': '#ff7f7f',
            'CANCELLED': '#ff7f7f',
        }
        textcolors = {
            'PENDING':'<b style="background:{};">{}</b>',
            'OPEN':'<b style="background:{};">{}</b>',
            'CLOSE':'<b style="background:{};">{}</b>',
            'COMPLETE':'<b style="background:{};">{}</b>',
            'REJECTED': '<b style="background:{};">{}</b>',
            'CANCELLED': '<b style="background:{};">{}</b>',
        }
        return format_html(
            textcolors[obj.status],
            colors[obj.status],
            obj.status,
        )
    status_colored.short_description = 'Status'
    #list_editable = ('stoploss',)

    search_fields = ('order_id__order_id', 'broker_order_id', 'strategy', 'status', 'symbol')

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return True

    # formfield_overrides = {
    #         #models.CharField: {'widget': TextInput(attrs={'size': '20'})}, # For CharField
    #         #models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})}, # For TextField
    #     }
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
        
    #     # Only modify the widget for the specific field named 'my_field'
    #     if 'stoploss' in form.base_fields:
    #         form.base_fields['stoploss'].widget = TextInput(attrs={'size': '3'})
            
    #     return form


    # fieldsets = (
    #     ('Basic Information', {
    #         'fields': ('symbol', 'instrument_token', 'broker_order_id','status','exchange'),
    #         'classes': ('wide', 'extrapretty'),  # Add custom CSS classes
    #     }),

    #     ('Price Information', {
    #         'fields': ('price','quantity', 'stoploss', 'trigger_price', 'stoploss_type'),
            
    #     }),

    # )
    # class Media:
    #     css = {
    #         'all': ('admin/css/custom.css',)
    #     }
admin.site.register(OrdersDetail,OrdersDetailAdmin)
