from django import forms
from .models import DonorProfile, EligibilityChecklist

BLOOD_TYPES = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]


class DonorPersonalInfoForm(forms.Form):
    blood_type    = forms.ChoiceField(choices=BLOOD_TYPES)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender        = forms.ChoiceField(choices=[('male','Male'),('female','Female'),('other','Other')])
    national_id   = forms.CharField(max_length=20)
    address       = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    district      = forms.CharField(max_length=100)
    profile_photo = forms.ImageField(required=False)

    def clean_national_id(self):
        nid = self.cleaned_data['national_id']
        if DonorProfile.objects.filter(national_id=nid).exists():
            raise forms.ValidationError("A donor with this National ID already exists.")
        return nid


class YesNoRadioWidget(forms.RadioSelect):
    def __init__(self):
        super().__init__(choices=[(True, 'Yes'), (False, 'No')])


class EligibilityChecklistForm(forms.ModelForm):
    BOOL_CHOICES = [(True, 'Yes'), (False, 'No')]

    hiv_positive            = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    hepatitis_b             = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    hepatitis_c             = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    malaria_last_3months    = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    tuberculosis_active     = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    recent_tattoo_6months   = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    recent_surgery_6months  = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    on_anticoagulants       = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    pregnancy_or_breastfeed = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    donated_last_3months    = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    weight_below_50kg       = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    feels_well_today        = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)
    no_alcohol_last_24h     = forms.TypedChoiceField(choices=BOOL_CHOICES, coerce=lambda x: x == 'True', widget=forms.RadioSelect)

    class Meta:
        model = EligibilityChecklist
        exclude = ['donor', 'is_auto_flagged', 'flagged_reason', 'completed_at']


class TransportConsentForm(forms.Form):
    needs_transport  = forms.BooleanField(required=False, label="I need transport assistance to reach the donation centre")
    transport_notes  = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Transport details (pickup location, distance, special needs)")
    consent          = forms.BooleanField(required=True, label="I confirm that all information I have provided is accurate and I consent to being contacted by registered health facilities in cases of blood emergency.")


class DonorSearchForm(forms.Form):
    DISTRICT_CHOICES = [('', 'All Districts')] + [(d, d) for d in [
        'Kampala', 'Wakiso', 'Mukono', 'Jinja', 'Mbale', 'Gulu', 'Mbarara',
        'Fort Portal', 'Arua', 'Lira', 'Masaka', 'Entebbe'
    ]]
    blood_type        = forms.ChoiceField(choices=[('', 'All Blood Types')] + BLOOD_TYPES, required=False)
    district          = forms.ChoiceField(choices=DISTRICT_CHOICES, required=False)
    status            = forms.ChoiceField(choices=[('','All Statuses'),('approved','Approved'),('pending','Pending'),('flagged','Flagged')], required=False)
    transport_needed  = forms.BooleanField(required=False, label="Needs transport only")
    available         = forms.BooleanField(required=False, label="Available now (no donation in 90 days)")
