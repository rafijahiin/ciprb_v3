from django.db.models import Count, Sum
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent
from activities.models import ActivityLog
from training.models import TrainingSession


def generate_report_data(month, year):
    """Generate a full data snapshot for a given month/year."""
    fistula_qs = FistulaCase.objects.all()
    mpdsr_qs = MPDSREvent.objects.all()

    fistula_goal = 100
    fistula_operated = fistula_qs.filter(referral_status='OPERATED').count()
    fistula_total = fistula_qs.count()

    pipeline = {}
    for status, label in FistulaCase.REFERRAL_STATUS_CHOICES:
        pipeline[label] = fistula_qs.filter(referral_status=status).count()

    total_mpdsr = mpdsr_qs.count()
    implemented = mpdsr_qs.filter(action_status='IMPLEMENTED').count()
    pending = mpdsr_qs.filter(action_status='PENDING').count()
    stalled = mpdsr_qs.filter(action_status='STALLED').count()
    action_gap = round((implemented / total_mpdsr * 100) if total_mpdsr > 0 else 0, 1)

    by_district = list(
        mpdsr_qs.values('district').annotate(count=Count('event_id')).order_by('-count')[:10]
    )
    by_death_type = list(
        mpdsr_qs.values('death_type').annotate(count=Count('event_id'))
    )

    partners = ['CIPRB', 'PHD', 'Bondhu']
    partner_data = {}
    for p in partners:
        partner_data[p] = {
            'activities': ActivityLog.objects.filter(partner=p).count(),
            'beneficiaries': ActivityLog.objects.filter(partner=p).aggregate(t=Sum('beneficiary_count'))['t'] or 0,
            'trainings': TrainingSession.objects.filter(partner=p).count(),
            'participants': TrainingSession.objects.filter(partner=p).aggregate(t=Sum('participants_count'))['t'] or 0,
        }

    total_beneficiaries = ActivityLog.objects.aggregate(t=Sum('beneficiary_count'))['t'] or 0
    total_training = TrainingSession.objects.count()
    total_participants = TrainingSession.objects.aggregate(t=Sum('participants_count'))['t'] or 0

    equity_data = {
        'disability': fistula_qs.filter(has_disability=True).count(),
        'ethnic_minority': fistula_qs.filter(is_ethnic_minority=True).count(),
        'displaced': fistula_qs.filter(is_displaced=True).count(),
    }

    return {
        'month': month,
        'year': year,
        'fistula_operated': fistula_operated,
        'fistula_total': fistula_total,
        'fistula_goal': fistula_goal,
        'fistula_progress': round((fistula_operated / fistula_goal * 100) if fistula_goal > 0 else 0, 1),
        'pipeline': pipeline,
        'total_mpdsr': total_mpdsr,
        'implemented_mpdsr': implemented,
        'pending_mpdsr': pending,
        'stalled_mpdsr': stalled,
        'action_gap_percent': action_gap,
        'by_district': by_district,
        'by_death_type': by_death_type,
        'partner_data': partner_data,
        'total_beneficiaries': total_beneficiaries,
        'total_training_sessions': total_training,
        'total_participants': total_participants,
        'equity_data': equity_data,
    }
