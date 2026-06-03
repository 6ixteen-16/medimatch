from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import SOSRequest, SOSStatusUpdate
from .forms import SOSRequestForm, SOSResolveForm


def staff_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, "Access denied.")
                return redirect('dashboard:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def sos_list_view(request):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')

    active   = SOSRequest.objects.filter(status__in=['open','acknowledged','in_transit']).select_related('requesting_facility', 'target_bank', 'requested_by')
    resolved = SOSRequest.objects.filter(status__in=['resolved','cancelled']).select_related('requesting_facility')[:20]

    # Check overdue
    for sos in active:
        sos.check_overdue()

    return render(request, 'sos/list.html', {'active': active, 'resolved': resolved})


@login_required
def sos_active_partial(request):
    """HTMX partial for auto-refreshing active SOS list."""
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        return render(request, 'sos/_empty.html')
    active = SOSRequest.objects.filter(status__in=['open','acknowledged','in_transit']).select_related('requesting_facility', 'target_bank')
    for sos in active:
        sos.check_overdue()
    return render(request, 'sos/_active_list.html', {'active': active})


@login_required
def sos_create_view(request):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    if not request.user.facility:
        messages.error(request, "You must be linked to a facility to create SOS requests.")
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = SOSRequestForm(request.POST)
        if form.is_valid():
            sos = form.save(commit=False)
            sos.requesting_facility = request.user.facility
            sos.requested_by        = request.user
            sos.save()

            SOSStatusUpdate.objects.create(
                sos_request=sos, updated_by=request.user,
                old_status='', new_status='open', note='SOS created'
            )

            # SMS notification
            try:
                from medimatch.utils.notifications import send_sms, send_templated_email
                from apps.accounts.models import CustomUser
                site_url = request.build_absolute_uri('/')[:-1]
                msg = (f"[MEDIMATCH SOS] {sos.requesting_facility.name} urgently needs "
                       f"{sos.units_needed} units of {sos.blood_type_needed}. "
                       f"Urgency: {sos.get_urgency_display()}. "
                       f"Log in to respond: {site_url}/sos/{sos.pk}/")

                # Notify target bank admins
                bank_admins = CustomUser.objects.filter(role='bank_admin', is_active=True)
                if sos.target_bank:
                    bank_admins = bank_admins.filter(facility=sos.target_bank)
                phones = [u.phone_number for u in bank_admins if u.phone_number]
                emails = [u.email for u in bank_admins if u.email]
                if phones:
                    send_sms(phones, msg)
                if emails:
                    send_templated_email('MediMatch SOS Alert', 'sos_created', {'sos': sos, 'site_url': site_url}, emails)
            except Exception:
                pass

            messages.success(request, f"SOS #{sos.pk} created. Blood banks have been notified.")
            return redirect('sos:detail', pk=sos.pk)
    else:
        form = SOSRequestForm()

    return render(request, 'sos/create.html', {'form': form})


@login_required
def sos_detail_view(request, pk):
    if request.user.role not in ('clinic_admin', 'bank_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    sos = get_object_or_404(SOSRequest.objects.select_related('requesting_facility', 'target_bank', 'requested_by', 'acknowledged_by'), pk=pk)
    sos.check_overdue()
    updates = sos.updates.all().order_by('updated_at')
    resolve_form = SOSResolveForm()
    return render(request, 'sos/detail.html', {'sos': sos, 'updates': updates, 'resolve_form': resolve_form})


def _update_sos_status(request, pk, new_status, allowed_roles, note=''):
    if request.user.role not in allowed_roles:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    sos = get_object_or_404(SOSRequest, pk=pk)
    old = sos.status
    sos.status = new_status
    if new_status == 'acknowledged':
        sos.acknowledged_by = request.user
    if new_status == 'resolved':
        sos.resolved_at = timezone.now()
        sos.is_overdue  = False
        resolution_notes = request.POST.get('resolution_notes', '')
        sos.resolution_notes = resolution_notes
    sos.save()
    SOSStatusUpdate.objects.create(sos_request=sos, updated_by=request.user, old_status=old, new_status=new_status, note=note)
    return None


@login_required
@require_POST
def sos_acknowledge_view(request, pk):
    result = _update_sos_status(request, pk, 'acknowledged', ['bank_admin', 'superadmin'], 'Acknowledged by blood bank')
    if result:
        return result
    messages.success(request, "SOS acknowledged.")
    return redirect('sos:detail', pk=pk)


@login_required
@require_POST
def sos_transit_view(request, pk):
    result = _update_sos_status(request, pk, 'in_transit', ['bank_admin', 'superadmin'], 'Blood dispatched')
    if result:
        return result
    messages.success(request, "Marked as in transit.")
    return redirect('sos:detail', pk=pk)


@login_required
@require_POST
def sos_resolve_view(request, pk):
    result = _update_sos_status(request, pk, 'resolved', ['clinic_admin', 'bank_admin', 'superadmin'], request.POST.get('resolution_notes', ''))
    if result:
        return result

    sos = get_object_or_404(SOSRequest, pk=pk)
    try:
        from medimatch.utils.notifications import send_templated_email
        site_url = request.build_absolute_uri('/')[:-1]
        if sos.requested_by and sos.requested_by.email:
            send_templated_email('MediMatch SOS Resolved', 'sos_resolved', {'sos': sos, 'site_url': site_url}, [sos.requested_by.email])
    except Exception:
        pass

    messages.success(request, f"SOS #{pk} marked resolved.")
    return redirect('sos:detail', pk=pk)


@login_required
@require_POST
def sos_cancel_view(request, pk):
    result = _update_sos_status(request, pk, 'cancelled', ['clinic_admin', 'superadmin'], 'Cancelled by clinic')
    if result:
        return result
    messages.info(request, f"SOS #{pk} cancelled.")
    return redirect('sos:list')
