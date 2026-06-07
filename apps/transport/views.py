from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)

from .models import TransportRequest
from .forms import TransportRequestForm
from apps.donors.models import DonorProfile


@login_required
def transport_list_view(request):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    transport_requests = TransportRequest.objects.select_related('donor__user', 'facility', 'approved_by').all()
    return render(request, 'transport/list.html', {'transport_requests': transport_requests})


@login_required
def transport_create_view(request, donor_id):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    donor = get_object_or_404(DonorProfile, pk=donor_id)
    if request.method == 'POST':
        form = TransportRequestForm(request.POST)
        if form.is_valid():
            transport = form.save(commit=False)
            transport.donor = donor
            transport.save()
            messages.success(request, "Transport request created.")
            return redirect('transport:list')
    else:
        form = TransportRequestForm()
    return render(request, 'transport/create.html', {'form': form, 'donor': donor})


@login_required
@require_POST
def transport_approve_view(request, pk):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    transport = get_object_or_404(TransportRequest, pk=pk)
    transport.status      = 'approved'
    transport.approved_by = request.user
    transport.save()
    try:
        from medimatch.utils.notifications import send_sms, send_templated_email
        donor = transport.donor
        if donor.user.phone_number:
            send_sms([donor.user.phone_number],
                     f"[MediMatch] Transport approved! Voucher: {transport.voucher_code}. Show to driver.")
        send_templated_email('MediMatch — Transport Approved', 'transport_approved',
                             {'transport': transport}, [donor.user.email])
    except Exception as e:
        logger.error(f"Failed to send transport notification: {e}")
    messages.success(request, f"Transport approved. Voucher: {transport.voucher_code}")
    return redirect('transport:list')


@login_required
@require_POST
def transport_complete_view(request, pk):
    if request.user.role not in ('clinic_admin', 'superadmin'):
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    transport = get_object_or_404(TransportRequest, pk=pk)
    transport.status = 'completed'
    transport.save()
    messages.success(request, "Transport marked as completed.")
    return redirect('transport:list')
