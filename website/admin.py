from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = 'administration'

class HoroscopeAdmin(admin.ModelAdmin):
    list_display = ['name','slug', 'status']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(Horoscope,HoroscopeAdmin)

class PageContentAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(PageContent,PageContentAdmin)

class HomeAboutAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(HomeAbout,HomeAboutAdmin)


class HomePageServiceAdmin(admin.ModelAdmin):
    list_display = ['title','status']
    search_fields = ['title']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(HomePageService,HomePageServiceAdmin)


class TestimonialsAdmin(admin.ModelAdmin):
    list_display = ['name','designation','status']
    search_fields = ['title']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(Testimonials,TestimonialsAdmin)

class UsStockAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(UsStock,UsStockAdmin)