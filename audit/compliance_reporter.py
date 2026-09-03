import json
from django.utils import timezone
from .models import AuditEntry

class ComplianceReportGenerator:
    """
    SOC2 / GDPR compliance log aggregator formatting audit trails for security reviews.
    """
    @classmethod
    def generate_json_compliance_export(cls, start_date=None, end_date=None):
        qs = AuditEntry.objects.select_related('actor').all()
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)

        records = []
        for item in qs[:1000]:
            records.append({
                'audit_id': str(item.id),
                'actor': item.actor.email if item.actor else 'SYSTEM',
                'action_type': item.action,
                'client_ip': item.ip_address or '0.0.0.0',
                'timestamp': item.timestamp.isoformat(),
                'payload_details': item.details
            })
        return json.dumps({'compliance_standard': 'SOC2_TYPE_II', 'total_records': len(records), 'logs': records}, indent=2)
