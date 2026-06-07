from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role in ('clinic_admin', 'bank_admin'):
                # Staff accounts are inactive until an administrator approves them.
                # Email verification is not required — admin approval is the only gate.
                messages.info(request, "Your account is pending administrator approval. You will be notified once your account is activated.")
                return redirect('accounts:login')
            # Donors are logged in immediately.
            # A verification notice is shown as a courtesy message only — it does not block access.
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            messages.info(request, "A verification email has been sent to your address. You may continue using the platform in the meantime.")
            messages.success(request, f"Welcome, {user.first_name}! Complete your donor profile to get started.")
            if user.role == 'donor':
                return redirect('donors:register')
            return redirect('dashboard:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Your account is pending approval.")
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            return redirect(request.GET.get('next', 'dashboard:home'))
        messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
