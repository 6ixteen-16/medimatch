from django.db import models
from django.utils import timezone
from datetime import timedelta


class SOSRequest(models.Model):
    URGENCY_CHOICES = [
        ('critical',  'Critical — Patient on table'),
        ('urgent',    'Urgent — Within 1 hour'),
        ('standard',  'Standard — Within 2 hours'),
    ]
    STATUS_CHOICES = [
        ('open',          'Open — Awaiting Response'),
        ('acknowledged',  'Acknowledged'),
        ('in_transit',    'Blood In Transit'),
        ('resolved',      'Resolved'),
        ('cancelled',     'Cancelled'),
    ]
    BLOOD_TYPE_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
        ('any','Any Available'),
    ]

    requesting_facility = models.ForeignKey('accounts.Facility', on_delete=models.CASCADE,
                                            related_name='sos_sent',
                                            limit_choices_to={'facility_type': 'clinic'})
    target_bank         = models.ForeignKey('accounts.Facility', on_delete=models.CASCADE,
                                            related_name='sos_received',
                                            limit_choices_to={'facility_type': 'blood_bank'},
                                            null=True, blank=True)
    blood_type_needed   = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES)
    units_needed        = models.PositiveSmallIntegerField(default=1)
    patient_condition   = models.TextField(help_text="Brief clinical context — no patient names")
    urgency             = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='urgent')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    requested_by        = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL,
                                            null=True, related_name='sos_requests')
    acknowledged_by     = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='sos_acknowledged')
    resolution_notes    = models.TextField(blank=True)
    resolved_at         = models.DateTimeField(null=True, blank=True)
    deadline            = models.DateTimeField(null=True, blank=True)
    is_overdue          = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "SOS Request"

    def save(self, *args, **kwargs):
        if not self.pk:
            delta = {'critical': 1, 'urgent': 2, 'standard': 4}
            self.deadline = timezone.now() + timedelta(hours=delta.get(self.urgency, 2))
        super().save(*args, **kwargs)

    def check_overdue(self):
        if self.status not in ('resolved', 'cancelled') and self.deadline:
            self.is_overdue = timezone.now() > self.deadline
            self.save(update_fields=['is_overdue'])

    def time_elapsed(self):
        delta = timezone.now() - self.created_at
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def __str__(self):
        return f"SOS #{self.pk} — {self.blood_type_needed} from {self.requesting_facility}"


class SOSStatusUpdate(models.Model):
    sos_request = models.ForeignKey(SOSRequest, on_delete=models.CASCADE, related_name='updates')
    updated_by  = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    old_status  = models.CharField(max_length=20)
    new_status  = models.CharField(max_length=20)
    note        = models.TextField(blank=True)
    updated_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SOS #{self.sos_request_id}: {self.old_status} → {self.new_status}"
