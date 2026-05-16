from django.contrib import admin
from .models import Sector,SectorSymbol

# Register your models here.

class SectorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(Sector,SectorAdmin)

class SectorSymbolAdmin(admin.ModelAdmin):
    list_display = ['symbol','sector']
    search_fields = ['symbol','sector__name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(SectorSymbol,SectorSymbolAdmin)
