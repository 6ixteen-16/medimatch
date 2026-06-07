from django import forms
from .models import TransportRequest
from apps.accounts.models import Facility

class TransportRequestForm(forms.ModelForm):
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.all(),
        label="Facility (destination)",
        help_text="Which facility is the donor traveling to?"
    )
    
    class Meta:
        model = TransportRequest
        fields = ['facility', 'pickup_address', 'estimated_cost', 'funding_source', 'sos_request', 'bulletin', 'notes']
        widgets = {
            'pickup_address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
