from django.contrib import admin
from django.urls import re_path as url
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .autocomplete_views import MyAutocomplete
#from django.conf.urls import url

#from django.shortcuts import render, get_object_or_404
from . import views,api,scanner

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]


urlpatterns += [
    path('', include('django.contrib.auth.urls')),

    path('<str:symbol_name>/options/', views.option_chain, name='oi_option'),
    path('positions/', views.zerodha_positions, name='positions'),

    path('zerodha/zerodha_save_changein_oi', views.zerodha_save_changein_oi, name='zerodha_save_changein_oi'),



    path('nse/<str:stock_name>/options/', views.nse_option_2, name='nse_option_2'),


    # add new URL patterns for the trading app
    path('scanner/coi_increase/', scanner.scanner_increase_coi, name='scanner_increase_coi'),
    path('scanner/coi/', scanner.scanner_coi, name='scanner_coi'),
    path('scanner/200ma/', scanner.scanner_200ma, name='scanner_200ma'),
    path('scanner/background/', scanner.async_view, name='async_view'),

    path('scanner/pre_market/', scanner.pre_market, name='pre_market'),
    path('scanner/<str:symbol_name>/options/', scanner.option_chain_coi, name='option_chain_coi'),
    path('scanner/<str:symbol_name>/options/chart', scanner.option_chain_coi_chart, name='option_chain_coi_chart'),
    path('nse/market-data/most-active-contracts/', scanner.most_active_contracts, name='most_active_contracts'),

    path('api/v1/get_instrment/', api.get_instrment, name='get_instrment'),
    path('api/v1/get_quote/', api.get_quote, name='api_get_quote'),
    path('api/v1/place_order/', api.place_order, name='api_place_order'),

     path('ajax/nse/market-data/ajax_topGainers/', scanner.ajax_topGainers, name='ajax_topGainers'),
     path('ajax/nse/market-data/most-active-contracts/', scanner.ajax_most_active_contracts, name='ajax_most_active_contracts'),
    path('ajax/nse/market-data/ajax_chart/', scanner.ajax_chart, name='ajax_chart'),
    path('ajax/nse/market-data/ajax_api_get_oi_data/', scanner.api_get_oi_data, name='api_get_oi_data'),
    
     

    # Cron job management URLs
    path('cron/dashboard/', views.cron_job_dashboard, name='cron_dashboard'),
    path('cron/job/<int:job_id>/run/', views.run_cron_job, name='run_cron_job'),
    path('cron/status/', views.cron_job_status, name='cron_status'),

    #autocomplete
    path('my-autocomplete/', MyAutocomplete.as_view(), name='my_autocomplete'),
    
    path('order_atomic', views.order_atomic, name='order_atomic'),
    

]

