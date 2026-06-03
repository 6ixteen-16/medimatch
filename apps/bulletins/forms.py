from django import forms
from .models import Bulletin


class BulletinForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    event_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Bulletin
        fields = ['title', 'body', 'category', 'blood_types_needed', 'event_date', 'event_time', 'event_location', 'status']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5}),
            'blood_types_needed': forms.TextInput(attrs={'placeholder': 'e.g. O+, A-, B+'}),
            'event_location': forms.TextInput(attrs={'placeholder': 'Venue or address'}),
        }
