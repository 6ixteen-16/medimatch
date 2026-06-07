from django.db import models


class Bulletin(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
        ('expired',   'Expired'),
    ]
    CATEGORY_CHOICES = [
        ('blood_drive',    'Scheduled Blood Drive'),
        ('urgent_appeal',  'Urgent Blood Appeal'),
        ('awareness',      'Awareness Campaign'),
        ('general',        'General Announcement'),
    ]

    title              = models.CharField(max_length=255)
    body               = models.TextField()
    category           = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='blood_drive')
    blood_types_needed = models.CharField(max_length=100, blank=True, help_text="Comma-separated, e.g. O+,A-,B+")
    facility           = models.ForeignKey('accounts.Facility', on_delete=models.CASCADE, related_name='bulletins')
    posted_by          = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='bulletins')
    event_date         = models.DateField(null=True, blank=True)
    event_time         = models.TimeField(null=True, blank=True)
    event_location     = models.CharField(max_length=255, blank=True)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sms_sent           = models.BooleanField(default=False)
    email_sent         = models.BooleanField(default=False)
    sms_sent_at        = models.DateTimeField(null=True, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def blood_type_list(self):
        return [bt.strip() for bt in self.blood_types_needed.split(',') if bt.strip()]
