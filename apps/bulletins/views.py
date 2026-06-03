from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Bulletin
from .forms import BulletinForm


def bulletin_list_view(request):
    bulletins = Bulletin.objects.filter(status='published').select_related('facility')
    category  = request.GET.get('category', '')
    blood_type = request.GET.get('blood_type', '')

    if category:
        bulletins = bulletins.filter(category=category)
    if blood_type:
        bulletins = bulletins.filter(blood_types_needed__icontains=blood_type)

    return render(request, 'bulletins/list.html', {
        'bulletins': bulletins,
        'selected_category': category,
        'selected_blood_type': blood_type,
        'blood_types': ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    })

def bulletin_detail_view(request, pk):
    bulletin = get_object_or_404(Bulletin, pk=pk)
    return render(request, 'bulletins/detail.html', {'bulletin': bulletin})


@login_required
def bulletin_create_view(request):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('bulletins:list')
    
    if not request.user.facility:
        messages.error(request, "Your account is not associated with a facility. Please contact an administrator.")
        return redirect('bulletins:list')
    
    if request.method == 'POST':
        form = BulletinForm(request.POST)
        if form.is_valid():
            bulletin = form.save(commit=False)
            bulletin.posted_by = request.user
            bulletin.facility  = request.user.facility
            bulletin.save()
            messages.success(request, "Bulletin created successfully.")
            return redirect('bulletins:detail', pk=bulletin.pk)
    else:
        form = BulletinForm()
    return render(request, 'bulletins/create.html', {'form': form})


@login_required
def bulletin_update_view(request, pk):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('bulletins:list')
    
    if not request.user.facility:
        messages.error(request, "Your account is not associated with a facility. Please contact an administrator.")
        return redirect('bulletins:list')
    
    bulletin = get_object_or_404(Bulletin, pk=pk)
    if request.method == 'POST':
        form = BulletinForm(request.POST, instance=bulletin)
        if form.is_valid():
            form.save()
            messages.success(request, "Bulletin updated.")
            return redirect('bulletins:detail', pk=pk)
    else:
        form = BulletinForm(instance=bulletin)
    return render(request, 'bulletins/create.html', {'form': form, 'bulletin': bulletin})


@login_required
@require_POST
def bulletin_publish_view(request, pk):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('bulletins:list')
    bulletin = get_object_or_404(Bulletin, pk=pk)
    bulletin.status = 'published'
    bulletin.save()
    messages.success(request, "Bulletin published.")
    return redirect('bulletins:detail', pk=pk)


@login_required
@require_POST
def bulletin_notify_view(request, pk):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('bulletins:list')
    bulletin = get_object_or_404(Bulletin, pk=pk)

    from apps.donors.models import DonorProfile
    donors = DonorProfile.objects.filter(status='approved')
    if bulletin.blood_type_list:
        donors = donors.filter(blood_type__in=bulletin.blood_type_list)

    phone_numbers = [d.user.phone_number for d in donors if d.user.phone_number]
    emails = [d.user.email for d in donors if d.user.email]

    try:
        from medimatch.utils.notifications import send_sms, send_templated_email
        if phone_numbers:
            msg = f"[MediMatch] {bulletin.title}. {bulletin.facility.name}. {bulletin.event_date or 'See website for details'}: medimatch.ug/bulletins/{pk}/"
            send_sms(phone_numbers, msg)
        if emails:
            send_templated_email(
                subject=f'MediMatch — {bulletin.title}',
                template_name='bulletin_notify',
                context={'bulletin': bulletin},
                recipient_list=emails,
            )
    except Exception as e:
        messages.warning(request, f"Notification attempt completed with errors: {e}")

    bulletin.sms_sent    = True
    bulletin.email_sent  = True
    bulletin.sms_sent_at = timezone.now()
    bulletin.save()

    if request.htmx:
        return render(request, 'bulletins/_notify_btn.html', {'bulletin': bulletin, 'notified': True})

    messages.success(request, f"Notifications sent to {len(phone_numbers)} donors.")
    return redirect('bulletins:detail', pk=pk)
