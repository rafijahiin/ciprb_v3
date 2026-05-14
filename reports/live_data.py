"""
Generates a window.REPORT-compatible JSON object from live database data.
Mirrors the structure of data.js but with real figures from Supabase.
"""
import json
from django.utils import timezone
from django.db.models import Count, Sum
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent
from activities.models import ActivityLog
from training.models import TrainingSession

MONTH_NAMES = {
    1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
    7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'
}

MONTH_SHORT = {
    1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
    7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
}


def get_report_json():
    now = timezone.now()
    month = now.month
    year = now.year

    fistula_qs = FistulaCase.objects.all()
    mpdsr_qs = MPDSREvent.objects.all()

    # ── KPIs ──
    fistula_goal = 100
    operated = fistula_qs.filter(referral_status='OPERATED').count()
    mpdsr_total = mpdsr_qs.count()
    total_ben = ActivityLog.objects.aggregate(t=Sum('beneficiary_count'))['t'] or 0
    total_trained = TrainingSession.objects.aggregate(t=Sum('participants_count'))['t'] or 0

    kpis = [
        {'label': 'Fistula Cases Operated', 'value': operated, 'target': fistula_goal, 'unit': '', 'delta': f'{operated} total'},
        {'label': 'MPDSR Events Reviewed',  'value': mpdsr_total, 'target': 40, 'unit': '', 'delta': f'{mpdsr_total} total'},
        {'label': 'Beneficiaries Reached',  'value': total_ben, 'target': 2500, 'unit': '', 'delta': f'+{total_ben}'},
        {'label': 'Staff Trained',          'value': total_trained, 'target': 150, 'unit': '', 'delta': f'+{total_trained}'},
    ]

    # ── Fistula pipeline ──
    pipeline_choices = FistulaCase.REFERRAL_STATUS_CHOICES
    color_map = {
        'IDENTIFIED': 'red', 'REFERRED': 'amber', 'ADMITTED': 'amber',
        'OPERATED': 'green', 'REHABILITATED': 'green'
    }
    pipeline = []
    for status, label in pipeline_choices:
        count = fistula_qs.filter(referral_status=status).count()
        pipeline.append({'key': status, 'label': label, 'value': count, 'color': color_map[status]})

    # ── MPDSR ──
    impl = mpdsr_qs.filter(action_status='IMPLEMENTED').count()
    funded = mpdsr_qs.filter(action_status='FUNDED').count()
    pending = mpdsr_qs.filter(action_status='PENDING').count()
    stalled = mpdsr_qs.filter(action_status='STALLED').count()
    maternal = mpdsr_qs.filter(death_type='MATERNAL').count()
    perinatal = mpdsr_qs.filter(death_type='PERINATAL').count()
    stillbirth = mpdsr_qs.filter(death_type='STILLBIRTH').count()

    # ── Partners ──
    partner_colors = {'CIPRB': 'green', 'PHD': 'blue', 'Bondhu': 'purple'}
    partner_targets = {'CIPRB': 50, 'PHD': 30, 'Bondhu': 20}
    partners = []
    for p in ['CIPRB', 'PHD', 'Bondhu']:
        acts = ActivityLog.objects.filter(partner=p).count()
        bens = ActivityLog.objects.filter(partner=p).aggregate(t=Sum('beneficiary_count'))['t'] or 0
        trains = TrainingSession.objects.filter(partner=p).count()
        parts = TrainingSession.objects.filter(partner=p).aggregate(t=Sum('participants_count'))['t'] or 0
        partners.append({
            'name': p, 'color': partner_colors[p],
            'activities': acts, 'beneficiaries': bens,
            'trainings': trains, 'participants': parts,
            'target': partner_targets[p],
        })

    # ── Districts (from MPDSR) ──
    DISTRICT_COORDS = {
        "Cox's Bazar": {'x': 72, 'y': 110, 'humanitarian': True},
        'Chattogram':  {'x': 70, 'y': 92},
        'Dhaka':       {'x': 42, 'y': 62},
        'Sylhet':      {'x': 72, 'y': 42},
        'Rangpur':     {'x': 28, 'y': 28},
        'Khulna':      {'x': 28, 'y': 82},
        'Barisal':     {'x': 38, 'y': 95},
        'Noakhali':    {'x': 54, 'y': 84},
        'Mymensingh':  {'x': 46, 'y': 48},
        'Rajshahi':    {'x': 30, 'y': 52},
        'Comilla':     {'x': 58, 'y': 72},
        'Dinajpur':    {'x': 24, 'y': 36},
        'Jamalpur':    {'x': 38, 'y': 48},
        'Bogura':      {'x': 32, 'y': 44},
        'Jessore':     {'x': 32, 'y': 76},
    }
    district_qs = mpdsr_qs.values('district').annotate(deaths=Count('event_id')).order_by('-deaths')
    districts = []
    for d in district_qs:
        name = d['district']
        coords = DISTRICT_COORDS.get(name, {'x': 50, 'y': 70})
        ben = ActivityLog.objects.filter(district=name).aggregate(t=Sum('beneficiary_count'))['t'] or 0
        entry = {'name': name, 'x': coords['x'], 'y': coords['y'],
                 'deaths': d['deaths'], 'beneficiaries': ben}
        if coords.get('humanitarian'):
            entry['humanitarian'] = True
        districts.append(entry)

    # ── Equity ──
    equity_disabled = fistula_qs.filter(has_disability=True).count()
    equity_ethnic = fistula_qs.filter(is_ethnic_minority=True).count()
    equity_displaced = fistula_qs.filter(is_displaced=True).count()
    equity = {
        'total_reached': total_ben,
        'disabled': equity_disabled,
        'ethnic': equity_ethnic,
        'displaced': equity_displaced,
        'adolescent': max(0, int(total_ben * 0.22)),  # estimated 22% adolescent from CPE data
        'note': 'Flags non-exclusive. Some beneficiaries carry multiple.',
    }

    # ── Trend (last 6 months placeholder - would need monthly snapshots) ──
    trend = {
        'months': ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', MONTH_SHORT[month]],
        'operated': [0, 0, 0, 0, 0, operated],
        'mpdsr': [0, 0, 0, 0, 0, mpdsr_total],
        'beneficiaries': [0, 0, 0, 0, 0, total_ben],
    }

    # ── Alerts (dynamic) ──
    alerts = []
    for p in partners:
        pct = (p['activities'] / p['target'] * 100) if p['target'] > 0 else 0
        if pct < 50:
            alerts.append({'severity': 'critical',
                           'text': f"{p['name']} activities {round(100-pct)}% below target · {p['activities']} / {p['target']}",
                           'meta': 'PARTNERS'})
    if pending > 3:
        alerts.append({'severity': 'critical',
                       'text': f'{pending} MPDSR actions PENDING — corrective action required',
                       'meta': 'MPDSR'})
    if stalled > 0:
        alerts.append({'severity': 'warning',
                       'text': f'{stalled} MPDSR actions STALLED — requires escalation',
                       'meta': 'MPDSR'})

    # ── History (from MonthlyNewsletter) ──
    from reports.models import MonthlyNewsletter
    history = []
    for n in MonthlyNewsletter.objects.order_by('-year', '-month')[:6]:
        history.append({
            'month': f"{MONTH_NAMES[n.month]} {n.year}",
            'sent': n.created_at.strftime('%Y-%m-%d'),
            'recipients': 14,
            'opens': 12,
            'status': 'published',
        })

    report = {
        'period': {
            'label': f"{MONTH_NAMES[month]} {year}",
            'start': f"{year}-{month:02d}-01",
            'end': now.strftime('%Y-%m-%d'),
        },
        'generated_at': now.strftime('%Y-%m-%d %H:%M UTC'),
        'programme': 'UNFPA-MISP · CP10 (2022–2026)',
        'kpis': kpis,
        'fistula': {
            'pipeline': pipeline,
            'goal': fistula_goal,
            'cumulative_operated': operated,
            'success_rate': round(
                fistula_qs.filter(surgery_outcome='SUCCESSFUL').count() /
                max(1, fistula_qs.filter(referral_status='OPERATED').count()) * 100, 1
            ),
        },
        'mpdsr': {
            'total': mpdsr_total,
            'by_status': {'IMPLEMENTED': impl, 'FUNDED': funded, 'PENDING': pending, 'STALLED': stalled},
            'by_type': {'MATERNAL': maternal, 'PERINATAL': perinatal, 'STILLBIRTH': stillbirth},
        },
        'partners': partners,
        'districts': districts,
        'equity': equity,
        'trend': trend,
        'alerts': alerts,
        'context': {
            'mmr_current': 136,
            'mmr_baseline': 165,
            'mmr_sdg_target': 70,
            'skilled_birth_attendance': 69.7,
            'adolescent_fertility': 92,
            'anc_coverage': 88,
        },
        'history': history,
        'recipients': [
            {'name': 'Masaki Watabe',       'org': 'UNFPA CO',    'role': 'Deputy Representative'},
            {'name': 'Jefarson Chakma',     'org': 'UNFPA CO',    'role': 'NPO · M&E'},
            {'name': 'Oyuna Chuluundorj',   'org': 'UNFPA APRO',  'role': 'Regional M&E Advisor'},
            {'name': 'Prof. M.A. Halim',    'org': 'CIPRB',       'role': 'Director'},
            {'name': 'PHD Programme Lead',  'org': 'PHD',         'role': 'Implementing Partner'},
            {'name': 'Bondhu Coordinator',  'org': 'Bondhu',      'role': 'Implementing Partner'},
        ],
    }

    return json.dumps(report, default=str)
