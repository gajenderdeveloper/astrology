from django.contrib import admin
from django.urls import re_path as url
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

#from django.conf.urls import url
from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]


urlpatterns += [
    path('', include('django.contrib.auth.urls')),

    #path('<str:symbol_name>/options/', views.option_chain, name='oi_option'),
    # path('positions/', views.zerodha_positions, name='positions'),
   
   

]

