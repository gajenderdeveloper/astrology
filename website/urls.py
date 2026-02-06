from django.contrib import admin
from django.urls import re_path as url
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
#from django.conf.urls import url

#from django.shortcuts import render, get_object_or_404
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', include('django.contrib.auth.urls')),
    url(r'^$', views.home, name='home'),
    url(r'horoscope/(?P<horoscope_slug>\w+)$', views.horoscope, name='horoscope'),
    #url(r'quote/(?P<stock_name>\w+)/options/$', views.option_chain, name='option_chain'),
    path('quote/<str:stock_name>/options/', views.option_chain, name='option_chain'),
    url(r'nse/(?P<stock_name>\w+)/options/$', views.nse_option, name='nse_option'),
    # static pages
    url(r'about-us$', views.page_content, name='about-us'),
    #url(r'anil$', views.anil_page, name='anil'),
    url(r'privacy-policy$', views.page_content, name='privacy-policy'),
    url(r'refund-policy$', views.page_content, name='refund-policy'),
    url(r'terms-and-Conditions$', views.page_content, name='terms-and-Conditions'),

    url(r'price$', views.price, name='price'),
    url(r'appointment$', views.appointment, name='appointment'),
    url(r'basic-details$', views.basic_details, name='basic-details'),
    url(r'summary$', views.summary, name='summary'),


    url(r'^loginpage$', views.login, name='login_new'),
    
    url(r'signup$', views.signup, name='signup'),
    


    #url(r'(?P<page_name>\w+)/)$', views.page_content, name='page_content'),

    #path('<page_name>', views.page_content, name='page_content'),

    #url(r'(?P<category_slug>\w+)/)$', views.categoryProductList, name='category_url'),


     path('get-time/', views.get_current_time, name='get_current_time'),

]

