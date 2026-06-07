import secrets
import string
from django.db import models


class TransportRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending Approval'),
        ('approved',  'Approved — Voucher Issued'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    FUNDING_SOURCE = [
        ('clinic_budget',  'Clinic Emergency Fund'),
        ('ngo_partner',    'NGO Partnership'),
        ('health_dept',    'Health Department'),
        ('pending_review', 'Pending Funding Review'),
    ]

    donor          = models.ForeignKey('donors.DonorProfile', on_delete=models.CASCADE, related_name='transport_requests')
    facility       = models.ForeignKey('accounts.Facility', on_delete=models.CASCADE)
    sos_request    = models.ForeignKey('sos.SOSRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='transport_requests')
    bulletin       = models.ForeignKey('bulletins.Bulletin', on_delete=models.SET_NULL, null=True, blank=True, related_name='transport_requests')
    pickup_address = models.TextField()
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    funding_source = models.CharField(max_length=30, choices=FUNDING_SOURCE, default='pending_review')
    voucher_code   = models.CharField(max_length=20, blank=True, null=True, default=None, unique=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by    = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='transport_approvals')
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def generate_voucher(self):
        if not self.voucher_code:
            chars = string.ascii_uppercase + string.digits
            self.voucher_code = 'MM-' + ''.join(secrets.choice(chars) for _ in range(8))

    def save(self, *args, **kwargs):
        if self.status == 'approved' and not self.voucher_code:
            self.generate_voucher()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transport #{self.pk} — {self.donor} ({self.status})"
