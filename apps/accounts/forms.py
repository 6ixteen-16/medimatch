from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'your@email.com', 'autocomplete': 'email'
    }))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+256 700 000 000'}))
    role = forms.ChoiceField(choices=[
        ('donor', 'Donor'),
        ('clinic_admin', 'Clinic Staff'),
        ('bank_admin', 'Blood Bank Staff'),
    ], widget=forms.HiddenInput())

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email    = self.cleaned_data['email']
        user.role     = self.cleaned_data['role']
        # Staff accounts need admin approval
        if user.role in ('clinic_admin', 'bank_admin'):
            user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'your@email.com', 'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False)
