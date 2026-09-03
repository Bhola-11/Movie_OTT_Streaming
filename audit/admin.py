from django.contrib import admin
from .models import AuditEntry

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'ip_address')
    list_filter = ('action',)
    search_fields = ('actor__email', 'details')
