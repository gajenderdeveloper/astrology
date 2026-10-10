from django.contrib import admin

# Register your models here.


from .models import *

# Register your models here.
admin.site.site_header = 'administration'

class PreMarketActivitiesAdmin(admin.ModelAdmin):
    list_display = ['created_at','meditation', 'feel_now','over_confident','daily']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(PreMarketActivities,PreMarketActivitiesAdmin)

class RulesAndComplienceAdmin(admin.ModelAdmin):
    list_display = ['created_at','trade_before', 'take_only']
    search_fields = ['name']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(RulesAndComplience,RulesAndComplienceAdmin)

class PostmarketActivitiesAdmin(admin.ModelAdmin):
    list_display = ['created_at','best_trade', 'worst_trade','missed_trade']
    search_fields = ['best_trade']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(PostmarketActivities,PostmarketActivitiesAdmin)


class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['created_at','discpline_today']
    search_fields = ['discpline_today']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(Discipline,DisciplineAdmin)

class TradeJournalAdmin(admin.ModelAdmin):
    list_display = ['created_at','symbol']
    search_fields = ['symbol']
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
admin.site.register(TradeJournal,TradeJournalAdmin)