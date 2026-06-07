from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

from .models import DonorProfile, EligibilityChecklist
from .forms import DonorPersonalInfoForm, EligibilityChecklistForm, TransportConsentForm, DonorSearchForm


class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        if request.user.role not in self.allowed_roles:
            messages.error(request, "Access denied.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


DONOR_WIZARD_FORMS = [
    ('personal',    DonorPersonalInfoForm),
    ('eligibility', EligibilityChecklistForm),
    ('transport',   TransportConsentForm),
]

DONOR_WIZARD_TEMPLATES = {
    'personal':    'donors/wizard_step1.html',
    'eligibility': 'donors/wizard_step2.html',
    'transport':   'donors/wizard_step3.html',
}


class DonorRegistrationWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp'))

    def get_template_names(self):
        return [DONOR_WIZARD_TEMPLATES[self.steps.current]]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        if request.user.role != 'donor':
            messages.error(request, "Only donors can complete this form.")
            return redirect('dashboard:home')
        if hasattr(request.user, 'donor_profile'):
            messages.info(request, "You already have a donor profile.")
            return redirect('donors:my_profile')
        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        form_data = [f.cleaned_data for f in form_list]
        personal   = form_data[0]
        eligibility = form_data[1]
        transport  = form_data[2]

        profile = DonorProfile(
            user         = self.request.user,
            blood_type   = personal['blood_type'],
            date_of_birth = personal['date_of_birth'],
            gender       = personal['gender'],
            national_id  = personal['national_id'],
            address      = personal['address'],
            district     = personal['district'],
            needs_transport = transport.get('needs_transport', False),
            transport_notes = transport.get('transport_notes', ''),
        )
        if personal.get('profile_photo'):
            profile.profile_photo = personal['profile_photo']
        profile.save()

        checklist = EligibilityChecklist(donor=profile)
        for field in EligibilityChecklist._meta.fields:
            if field.name in eligibility:
                setattr(checklist, field.name, eligibility[field.name])
        checklist.save()

        # Send confirmation email
        try:
            from medimatch.utils.notifications import send_templated_email
            send_templated_email(
                subject='MediMatch — Donor Registration Received',
                template_name='donor_approved',
                context={'user': self.request.user, 'profile': profile},
                recipient_list=[self.request.user.email],
            )
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")

        if checklist.is_auto_flagged:
            messages.warning(self.request, "Your profile has been flagged for clinical review. A health officer will contact you.")
        else:
            messages.success(self.request, "Donor registration complete! Your profile is under review.")

        return redirect('donors:my_profile')


@login_required
def my_profile_view(request):
    try:
        profile = request.user.donor_profile
    except DonorProfile.DoesNotExist:
        return redirect('donors:register')
    donations = profile.donations.all()[:5]
    return render(request, 'donors/my_profile.html', {'profile': profile, 'donations': donations})


@login_required
def donor_list_view(request):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')

    form = DonorSearchForm(request.GET or None)
    donors = DonorProfile.objects.select_related('user').all()

    if form.is_valid():
        if form.cleaned_data.get('blood_type'):
            donors = donors.filter(blood_type=form.cleaned_data['blood_type'])
        if form.cleaned_data.get('district'):
            donors = donors.filter(district=form.cleaned_data['district'])
        if form.cleaned_data.get('status'):
            donors = donors.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('transport_needed'):
            donors = donors.filter(needs_transport=True)
        if form.cleaned_data.get('available'):
            cutoff = timezone.now().date() - timedelta(days=90)
            donors = donors.filter(last_donation_date__lt=cutoff) | donors.filter(last_donation_date__isnull=True)

    if request.htmx:
        return render(request, 'donors/_search_results.html', {'donors': donors})

    return render(request, 'donors/list.html', {'donors': donors, 'form': form})


@login_required
def donor_detail_view(request, pk):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    profile = get_object_or_404(DonorProfile, pk=pk)
    eligibility_fields = []
    if profile.eligibility:
        for f in EligibilityChecklist._meta.fields:
            if f.name not in ('id', 'donor', 'is_auto_flagged', 'flagged_reason', 'completed_at'):
                eligibility_fields.append({
                    'name': f.name,
                    'label': f.verbose_name,
                    'value': getattr(profile.eligibility, f.name)
                })
    return render(request, 'donors/detail.html', {
        'profile': profile,
        'eligibility_fields': eligibility_fields
    })


@login_required
@require_POST
def donor_approve_view(request, pk):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    profile = get_object_or_404(DonorProfile, pk=pk)
    # Check if donor has disqualifying conditions
    if hasattr(profile, 'eligibility') and profile.eligibility.is_auto_flagged:
        messages.error(request, "Cannot approve a donor with disqualifying conditions. Please review the eligibility checklist.")
        return redirect('donors:detail', pk=pk)
    profile.status = 'approved'
    profile.save()
    messages.success(request, f"{profile.user.get_full_name()} has been approved.")

    try:
        from medimatch.utils.notifications import send_sms, send_templated_email
        if profile.user.phone_number:
            send_sms([profile.user.phone_number], "[MediMatch] Your donor profile has been approved! You can now respond to blood drives. Thank you.")
        send_templated_email(
            subject='MediMatch — Donor Profile Approved',
            template_name='donor_approved',
            context={'user': profile.user, 'profile': profile},
            recipient_list=[profile.user.email],
        )
    except Exception as e:
        logger.error(f"Failed to send donor approval notifications: {e}")

    return redirect('donors:detail', pk=pk)


@login_required
@require_POST
def donor_flag_view(request, pk):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    profile = get_object_or_404(DonorProfile, pk=pk)
    profile.status = 'flagged'
    profile.save()
    messages.warning(request, f"{profile.user.get_full_name()} has been flagged.")
    return redirect('donors:detail', pk=pk)
