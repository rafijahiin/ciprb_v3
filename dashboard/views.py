import os
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent
from activities.models import ActivityLog
from training.models import TrainingSession


def get_user_context(request):
    """Return role/org info for the logged-in user."""
    try:
        profile = request.user.profile
        return {
            'user_role': profile.role,
            'user_org': profile.organisation,
            'is_unfpa_admin': profile.is_unfpa_admin(),
            'is_org_admin': profile.is_org_admin(),
            'can_enter_data': profile.can_enter_data(),
        }
    except Exception:
        return {
            'user_role': 'VIEWER',
            'user_org': 'CIPRB',
            'is_unfpa_admin': False,
            'is_org_admin': False,
            'can_enter_data': False,
        }


@login_required(login_url='/accounts/login/')
def dashboard_main(request):
    uctx = get_user_context(request)
    user_org = uctx['user_org']
    is_unfpa = uctx['is_unfpa_admin']

    # --- Fistula (filter by org unless UNFPA) ---
    fistula_goal = 100
    fistula_qs = FistulaCase.objects.all()
    fistula_operated = fistula_qs.filter(referral_status='OPERATED').count()
    fistula_total = fistula_qs.count()
    fistula_progress = round((fistula_operated / fistula_goal * 100) if fistula_goal > 0 else 0, 1)

    pipeline = {}
    for status, label in FistulaCase.REFERRAL_STATUS_CHOICES:
        pipeline[label] = fistula_qs.filter(referral_status=status).count()

    # --- MPDSR ---
    mpdsr_qs = MPDSREvent.objects.all()
    total_mpdsr = mpdsr_qs.count()
    implemented_mpdsr = mpdsr_qs.filter(action_status='IMPLEMENTED').count()
    pending_mpdsr = mpdsr_qs.filter(action_status='PENDING').count()
    stalled_mpdsr = mpdsr_qs.filter(action_status='STALLED').count()
    action_gap_percent = round((implemented_mpdsr / total_mpdsr * 100) if total_mpdsr > 0 else 0, 1)

    mpdsr_by_district = mpdsr_qs.values('district').annotate(count=Count('event_id')).order_by('-count')
    heatmap_labels = json.dumps([x['district'] for x in mpdsr_by_district])
    heatmap_data = json.dumps([x['count'] for x in mpdsr_by_district])
    mpdsr_events = mpdsr_qs.order_by('-event_id')[:20]

    # --- Partner breakdown (UNFPA sees all, others see own org) ---
    partners = ['CIPRB', 'PHD', 'Bondhu'] if is_unfpa else [user_org]
    partner_data = {}
    for p in ['CIPRB', 'PHD', 'Bondhu']:
        partner_data[p] = {
            'activities': ActivityLog.objects.filter(partner=p).count(),
            'beneficiaries': ActivityLog.objects.filter(partner=p).aggregate(t=Sum('beneficiary_count'))['t'] or 0,
            'trainings': TrainingSession.objects.filter(partner=p).count(),
            'participants': TrainingSession.objects.filter(partner=p).aggregate(t=Sum('participants_count'))['t'] or 0,
        }

    partner_labels = json.dumps(partners)
    partner_activities = json.dumps([partner_data[p]['activities'] for p in partners])
    partner_beneficiaries = json.dumps([partner_data[p]['beneficiaries'] for p in partners])

    # --- Alerts (org-filtered) ---
    activity_targets = {'CIPRB': 50, 'PHD': 30, 'Bondhu': 20}
    alerts = []
    for p in partners:
        actual = partner_data[p]['activities']
        target = activity_targets.get(p, 30)
        pct = round((actual / target * 100) if target > 0 else 0, 1)
        if pct < 50:
            alerts.append({'partner': p, 'actual': actual, 'target': target, 'pct': pct, 'level': 'critical'})
        elif pct < 80:
            alerts.append({'partner': p, 'actual': actual, 'target': target, 'pct': pct, 'level': 'warning'})

    # --- Activities (org-filtered) ---
    act_qs = ActivityLog.objects.all() if is_unfpa else ActivityLog.objects.filter(partner=user_org)
    recent_activities = act_qs.order_by('-activity_date', '-created_at')[:10]
    total_beneficiaries = act_qs.aggregate(t=Sum('beneficiary_count'))['t'] or 0

    # --- Training ---
    tr_qs = TrainingSession.objects.all() if is_unfpa else TrainingSession.objects.filter(partner=user_org)
    total_participants = tr_qs.aggregate(t=Sum('participants_count'))['t'] or 0
    total_training_sessions = tr_qs.count()

    context = {
        **uctx,
        'fistula_operated': fistula_operated,
        'fistula_total': fistula_total,
        'fistula_goal': fistula_goal,
        'fistula_progress': fistula_progress,
        'pipeline': pipeline,
        'total_mpdsr': total_mpdsr,
        'implemented_mpdsr': implemented_mpdsr,
        'pending_mpdsr': pending_mpdsr,
        'stalled_mpdsr': stalled_mpdsr,
        'action_gap_percent': action_gap_percent,
        'heatmap_labels': heatmap_labels,
        'heatmap_data': heatmap_data,
        'mpdsr_events': mpdsr_events,
        'partner_data': partner_data,
        'partner_labels': partner_labels,
        'partner_activities': partner_activities,
        'partner_beneficiaries': partner_beneficiaries,
        'visible_partners': partners,
        'alerts': alerts,
        'recent_activities': recent_activities,
        'total_beneficiaries': total_beneficiaries,
        'total_participants': total_participants,
        'total_training_sessions': total_training_sessions,
        'fistula_cases': FistulaCase.objects.all().order_by('-id'),
        'training_sessions': tr_qs.order_by('-session_date'),
        'kobo_fistula_url': os.environ.get('KOBO_FISTULA_URL', ''),
        'kobo_mpdsr_url': os.environ.get('KOBO_MPDSR_URL', ''),
        'kobo_baseline_url': os.environ.get('KOBO_BASELINE_URL', ''),
    }
    return render(request, 'dashboard/main.html', context)
