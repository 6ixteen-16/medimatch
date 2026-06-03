from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count


@login_required
def dashboard_view(request):
    user = request.user
    ctx  = {'user': user}

    if user.role == 'donor':
        try:
            from apps.bulletins.models import Bulletin
            profile  = user.donor_profile
            donations = profile.donations.all()[:5]
            recent_bulletins = Bulletin.objects.filter(status='published').order_by('-created_at')[:5]
            ctx.update({'profile': profile, 'donations': donations, 'recent_bulletins': recent_bulletins})
        except Exception:
            pass

    elif user.role in ('clinic_admin', 'bank_admin', 'superadmin'):
        from apps.donors.models import DonorProfile
        from apps.sos.models import SOSRequest
        from apps.bulletins.models import Bulletin
        from apps.transport.models import TransportRequest

        donors = DonorProfile.objects.all()
        ctx['total_donors']       = donors.count()
        ctx['approved_donors']    = donors.filter(status='approved').count()
        ctx['pending_donors']     = donors.filter(status='pending').count()
        ctx['active_sos']         = SOSRequest.objects.filter(status__in=['open','acknowledged','in_transit']).count()
        ctx['overdue_sos']        = SOSRequest.objects.filter(is_overdue=True).count()
        ctx['pending_transport']  = TransportRequest.objects.filter(status='pending').count()
        ctx['recent_bulletins']   = Bulletin.objects.filter(status='published').order_by('-created_at')[:5]
        ctx['active_sos_list']    = SOSRequest.objects.filter(status__in=['open','acknowledged','in_transit']).select_related('requesting_facility')[:10]

        # Blood type distribution for Chart.js
        bt_data = donors.filter(status='approved').values('blood_type').annotate(count=Count('blood_type')).order_by('blood_type')
        ctx['bt_labels'] = [d['blood_type'] for d in bt_data]
        ctx['bt_counts'] = [d['count'] for d in bt_data]

        if user.role == 'superadmin':
            from apps.accounts.models import CustomUser, Facility
            ctx['pending_staff']  = CustomUser.objects.filter(is_active=False, role__in=['clinic_admin','bank_admin']).count()
            ctx['facilities']     = Facility.objects.all()

    return render(request, 'dashboard/index.html', ctx)


@login_required
def dashboard_stats_partial(request):
    """HTMX partial for live stat refresh."""
    from apps.sos.models import SOSRequest
    active = SOSRequest.objects.filter(status__in=['open','acknowledged','in_transit']).select_related('requesting_facility')
    for s in active:
        s.check_overdue()
    return render(request, 'dashboard/_stats.html', {'active_sos_list': active})
