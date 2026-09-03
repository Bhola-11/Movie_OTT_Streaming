import csv
from django.views.generic import ListView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from .models import AuditEntry

class AuditLogListView(UserPassesTestMixin, ListView):
    model = AuditEntry
    template_name = 'audit/log_list.html'
    context_object_name = 'audit_entries'
    paginate_by = 30

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == 'ADMIN')


class AuditExportCSVView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == 'ADMIN')

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="CineVerse_Audit_Logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Actor', 'Action', 'IP Address', 'Details'])

        for log in AuditEntry.objects.all()[:500]:
            actor_email = log.actor.email if log.actor else 'System'
            writer.writerow([log.timestamp, actor_email, log.action, log.ip_address, log.details])

        return response
