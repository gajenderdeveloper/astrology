from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path as url
#from website import views

urlpatterns = [
     #url(r'^your_app_start/', include('website.urls',namespace="website")),

    #url(r'^admin/login/', views.website),
    #url(r'^scheduler/', include('scheduler.urls')),
    url(r'^admin/', admin.site.urls),
    #path('api-auth/', include('rest_framework.urls')),
    #url(r'^api/', include('polls.urls')),

    url(r'^', include('website.urls')),
    url(r'^option-chain/', include('trading.urls')),
    url(r'^tradingview/', include('tradingview.urls')),
    url(r'^kotak/', include('KOTAK_NEO_API.urls')),
    #url(r'^zerodha/', include('zerodha.urls')),
    #url(r'^ckeditor/', include('ckeditor_uploader.urls')), # The CKEditor path

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)