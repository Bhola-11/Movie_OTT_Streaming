from django.contrib import admin
from .models import ContentReport

@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reason', 'status', 'reporter', 'created_at')
    list_filter = ('status', 'reason')
