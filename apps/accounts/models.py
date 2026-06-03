from django.contrib.auth.models import AbstractUser
from django.db import models


class Facility(models.Model):
    FACILITY_TYPE = [
        ('clinic',     'Community Health Centre'),
        ('blood_bank', 'Regional Blood Bank'),
    ]
    name          = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPE)
    address       = models.TextField()
    district      = models.CharField(max_length=100)
    phone         = models.CharField(max_length=20)
    email         = models.EmailField()
    latitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('donor',         'Donor'),
        ('clinic_admin',  'Clinic Administrator'),
        ('bank_admin',    'Blood Bank Administrator'),
        ('superadmin',    'Super Administrator'),
    ]
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=20, blank=True)
    facility     = models.ForeignKey(
        Facility, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='staff'
    )
    is_verified  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def is_clinic_admin(self):  return self.role == 'clinic_admin'
    def is_bank_admin(self):    return self.role == 'bank_admin'
    def is_donor(self):         return self.role == 'donor'
    def is_superadmin(self):    return self.role == 'superadmin'
    def is_staff_member(self):  return self.role in ('clinic_admin', 'bank_admin', 'superadmin')

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_role_display()})"
