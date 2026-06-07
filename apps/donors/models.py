from django.db import models
from datetime import date


class DonorProfile(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending Review'),
        ('approved',  'Approved'),
        ('flagged',   'Flagged — High Risk'),
        ('suspended', 'Suspended'),
    ]

    user              = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='donor_profile')
    blood_type        = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    date_of_birth     = models.DateField()
    gender            = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')])
    national_id       = models.CharField(max_length=20, unique=True)
    address           = models.TextField()
    district          = models.CharField(max_length=100)
    profile_photo     = models.ImageField(upload_to='donors/photos/', blank=True, null=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations   = models.PositiveIntegerField(default=0)
    needs_transport   = models.BooleanField(default=False)
    transport_notes   = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_eligible_by_age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        return 25 <= age <= 65

    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def next_eligible_date(self):
        from datetime import timedelta
        if self.last_donation_date:
            return self.last_donation_date + timedelta(days=90)
        return None

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.blood_type}"


class EligibilityChecklist(models.Model):
    donor = models.OneToOneField(DonorProfile, on_delete=models.CASCADE, related_name='eligibility')

    # Disqualifying conditions
    hiv_positive            = models.BooleanField(default=False)
    hepatitis_b             = models.BooleanField(default=False)
    hepatitis_c             = models.BooleanField(default=False)
    malaria_last_3months    = models.BooleanField(default=False)
    tuberculosis_active     = models.BooleanField(default=False)
    recent_tattoo_6months   = models.BooleanField(default=False)
    recent_surgery_6months  = models.BooleanField(default=False)
    on_anticoagulants       = models.BooleanField(default=False)
    pregnancy_or_breastfeed = models.BooleanField(default=False)
    donated_last_3months    = models.BooleanField(default=False)
    weight_below_50kg       = models.BooleanField(default=False)

    feels_well_today        = models.BooleanField(default=True)
    no_alcohol_last_24h     = models.BooleanField(default=True)

    is_auto_flagged         = models.BooleanField(default=False)
    flagged_reason          = models.TextField(blank=True)
    completed_at            = models.DateTimeField(auto_now=True)

    DISQUALIFYING_FIELDS = [
        'hiv_positive', 'hepatitis_b', 'hepatitis_c', 'malaria_last_3months',
        'tuberculosis_active', 'on_anticoagulants', 'pregnancy_or_breastfeed',
        'donated_last_3months', 'weight_below_50kg',
    ]

    def compute_flag(self):
        reasons = []
        for field in self.DISQUALIFYING_FIELDS:
            if getattr(self, field):
                reasons.append(field.replace('_', ' ').title())
        self.is_auto_flagged = bool(reasons)
        self.flagged_reason  = ', '.join(reasons)

    def save(self, *args, **kwargs):
        self.compute_flag()
        super().save(*args, **kwargs)
        if self.is_auto_flagged:
            self.donor.status = 'flagged'
            self.donor.save(update_fields=['status'])

    def __str__(self):
        return f"Checklist for {self.donor}"


class DonationRecord(models.Model):
    donor       = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='donations')
    facility    = models.ForeignKey('accounts.Facility', on_delete=models.SET_NULL, null=True)
    donated_at  = models.DateField()
    blood_units = models.DecimalField(max_digits=4, decimal_places=2, default=0.45)
    notes       = models.TextField(blank=True)
    recorded_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='recorded_donations')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-donated_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update donor's total_donations count and last_donation_date
        self.donor.total_donations = self.donor.donations.count()
        self.donor.last_donation_date = self.donor.donations.first().donated_at if self.donor.donations.exists() else None
        self.donor.save(update_fields=['total_donations', 'last_donation_date'])

    def __str__(self):
        return f"{self.donor} donated {self.blood_units}L on {self.donated_at}"
