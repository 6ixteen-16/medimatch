from django import forms
from .models import SOSRequest
from apps.accounts.models import Facility


class SOSRequestForm(forms.ModelForm):
    class Meta:
        model = SOSRequest
        fields = ['blood_type_needed', 'units_needed', 'patient_condition', 'urgency', 'target_bank']
        widgets = {
            'patient_condition': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief clinical context only — do not include patient names or personal identifiers.'}),
            'urgency': forms.HiddenInput(),
            'blood_type_needed': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_bank'].queryset = Facility.objects.filter(facility_type='blood_bank', is_active=True)
        self.fields['target_bank'].empty_label = "Broadcast to all blood banks"
        self.fields['target_bank'].required = False


class SOSResolveForm(forms.Form):
    resolution_notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Resolution notes")
