
"""
Management command to seed realistic demo data based on UNFPA Bangladesh CPE 2022-2026.
Run: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from tracker.models import FistulaCase
from mpdsr.models import MPDSREvent
from activities.models import ActivityLog
from training.models import TrainingSession
import uuid
import random
from datetime import date, timedelta


# CPE report: 10 priority districts + 12 donor districts
PRIORITY_DISTRICTS = [
    'Dhaka', 'Sylhet', 'Mymensingh', 'Rajshahi', 'Rangpur',
    'Khulna', 'Barisal', 'Comilla', 'Dinajpur', 'Jamalpur'
]

DONOR_DISTRICTS = [
    'Bogura', 'Jessore', 'Noakhali', 'Faridpur', 'Tangail',
    'Narail', 'Satkhira', 'Sunamganj', 'Habiganj', 'Sirajganj'
]

ALL_DISTRICTS = PRIORITY_DISTRICTS + DONOR_DISTRICTS

UPAZILAS = {
    'Dhaka': ['Savar', 'Dhamrai', 'Keraniganj', 'Dohar'],
    'Sylhet': ['Beanibazar', 'Golapganj', 'Zakiganj', 'Companiganj'],
    'Mymensingh': ['Trishal', 'Gaffargaon', 'Nandail', 'Phulpur'],
    'Rajshahi': ['Paba', 'Godagari', 'Tanore', 'Mohanpur'],
    'Rangpur': ['Pirganj', 'Kaunia', 'Taraganj', 'Mithapukur'],
    'Khulna': ['Dumuria', 'Batiaghata', 'Dakop', 'Koyra'],
    'Barisal': ['Muladi', 'Mehendiganj', 'Agailjhara', 'Bakerganj'],
    'Comilla': ['Debidwar', 'Muradnagar', 'Brahmanpara', 'Burichong'],
    'Dinajpur': ['Birampur', 'Chirirbandar', 'Parbatipur', 'Nawabganj'],
    'Jamalpur': ['Melandaha', 'Islampur', 'Dewanganj', 'Bokshiganj'],
    'Bogura': ['Sherpur', 'Shibganj', 'Nandigram', 'Kahaloo'],
    'Jessore': ['Chaugachha', 'Jhikargachha', 'Manirampur', 'Keshabpur'],
}

FACILITIES = {
    'Dhaka': ['Savar Upazila Health Complex', 'Dhamrai UHC', 'National Institute of Cancer Research'],
    'Sylhet': ['Sylhet MAG Osmani Medical College Hospital', 'Beanibazar UHC', 'Golapganj UHC'],
    'Mymensingh': ['Mymensingh Medical College Hospital', 'Trishal UHC', 'Nandail UHC'],
    'Rajshahi': ['Rajshahi Medical College Hospital', 'Paba UHC', 'Godagari UHC'],
    'Rangpur': ['Rangpur Medical College Hospital', 'Pirganj UHC', 'Kaunia UHC'],
    'Khulna': ['Khulna Medical College Hospital', 'Dumuria UHC', 'Batiaghata UHC'],
    'Barisal': ['Sher-E-Bangla Medical College', 'Muladi UHC', 'Mehendiganj UHC'],
    'Comilla': ['Comilla Medical College Hospital', 'Debidwar UHC', 'Muradnagar UHC'],
    'Dinajpur': ['M. Abdur Rahim Medical College', 'Birampur UHC', 'Parbatipur UHC'],
    'Jamalpur': ['Jamalpur District Hospital', 'Melandaha UHC', 'Islampur UHC'],
}


class Command(BaseCommand):
    help = 'Seeds realistic demo data based on UNFPA Bangladesh CPE 2022-2026 districts'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            FistulaCase.objects.all().delete()
            MPDSREvent.objects.all().delete()
            ActivityLog.objects.all().delete()
            TrainingSession.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data.'))

        self._seed_fistula_cases()
        self._seed_mpdsr_events()
        self._seed_activities()
        self._seed_training()
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))

    def _seed_fistula_cases(self):
        """
        Based on CPE: fistula campaign across priority districts.
        CIPRB is the implementing partner for fistula.
        """
        cases = [
            # District, Upazila, Age, Referral, Surgery, Disability, Ethnic, Displaced
            ('Sylhet', 'Beanibazar', 28, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Sylhet', 'Golapganj', 34, 'OPERATED', 'SUCCESSFUL', True, False, False),
            ('Mymensingh', 'Trishal', 22, 'OPERATED', 'COMPLICATIONS', False, False, False),
            ('Mymensingh', 'Nandail', 19, 'REFERRED', 'PENDING', False, False, False),
            ('Rajshahi', 'Paba', 31, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Rajshahi', 'Godagari', 25, 'ADMITTED', 'PENDING', False, True, False),
            ('Rangpur', 'Pirganj', 27, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Rangpur', 'Kaunia', 38, 'IDENTIFIED', 'PENDING', True, False, True),
            ('Khulna', 'Dumuria', 24, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Khulna', 'Batiaghata', 33, 'REFERRED', 'PENDING', False, False, False),
            ('Barisal', 'Muladi', 29, 'OPERATED', 'SUCCESSFUL', False, False, True),
            ('Barisal', 'Mehendiganj', 21, 'IDENTIFIED', 'PENDING', False, False, False),
            ('Comilla', 'Debidwar', 26, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Comilla', 'Muradnagar', 35, 'ADMITTED', 'PENDING', True, False, False),
            ('Dinajpur', 'Birampur', 30, 'REHABILITATED', 'SUCCESSFUL', False, True, False),
            ('Dinajpur', 'Parbatipur', 23, 'OPERATED', 'SUCCESSFUL', False, False, False),
            ('Jamalpur', 'Melandaha', 32, 'OPERATED', 'SUCCESSFUL', False, False, True),
            ('Jamalpur', 'Islampur', 20, 'REFERRED', 'PENDING', False, False, False),
            ('Bogura', 'Sherpur', 28, 'IDENTIFIED', 'PENDING', False, False, False),
            ('Jessore', 'Chaugachha', 36, 'OPERATED', 'SUCCESSFUL', False, False, False),
        ]

        created = 0
        for district, upazila, age, referral, surgery, disability, ethnic, displaced in cases:
            kid = f"fistula_demo_{district}_{upazila}_{age}".replace(' ', '_').lower()
            if not FistulaCase.objects.filter(kobo_submission_id=kid).exists():
                FistulaCase.objects.create(
                    age=age,
                    district=district,
                    upazila=upazila,
                    referral_status=referral,
                    surgery_outcome=surgery,
                    has_disability=disability,
                    is_ethnic_minority=ethnic,
                    is_displaced=displaced,
                    kobo_submission_id=kid,
                )
                created += 1

        self.stdout.write(f'  Fistula cases: {created} created')

    def _seed_mpdsr_events(self):
        """
        Based on CPE: MMR 136/100,000, data-to-action gap is a documented challenge.
        Districts with highest burden: Sylhet, Mymensingh, Rangpur, Rajshahi.
        """
        events = [
            ('MATERNAL', 'Sylhet', 'Sylhet MAG Osmani Medical College Hospital', 24,
             'Postpartum haemorrhage', 'Delay in reaching facility; no transport at night',
             'Strengthen community transport mechanism; 24hr hotline', 'PENDING'),
            ('MATERNAL', 'Mymensingh', 'Mymensingh Medical College Hospital', 28,
             'Eclampsia / pre-eclampsia', 'No ANC in last trimester; first visit at delivery',
             'Community-level ANC outreach; SBCC on danger signs', 'FUNDED'),
            ('MATERNAL', 'Rangpur', 'Pirganj Upazila Health Complex', 19,
             'Sepsis post-delivery', 'Home delivery by untrained TBA; delayed referral',
             'Skilled birth attendant deployment in rural unions', 'PENDING'),
            ('MATERNAL', 'Rajshahi', 'Paba UHC', 32,
             'Obstructed labour', 'No EmOC capacity at facility level; C-section unavailable',
             'Emergency Obstetric Care equipment and training for UHC', 'IMPLEMENTED'),
            ('PERINATAL', 'Khulna', 'Dumuria UHC', 0,
             'Birth asphyxia', 'No newborn resuscitation equipment; untrained staff',
             'Newborn care corner establishment; SBA training', 'PENDING'),
            ('MATERNAL', 'Barisal', 'Sher-E-Bangla Medical College', 26,
             'Postpartum haemorrhage', 'Blood bank shortage; delayed transfusion',
             'Strengthen blood bank; train on active management of 3rd stage', 'STALLED'),
            ('STILLBIRTH', 'Comilla', 'Comilla Medical College Hospital', 0,
             'Intrauterine foetal death', 'No foetal monitoring at UHC level; late referral',
             'Foetal monitoring equipment; referral protocol training', 'PENDING'),
            ('MATERNAL', 'Dinajpur', 'M. Abdur Rahim Medical College', 22,
             'Ruptured uterus', 'Previous C-section; no scar surveillance; delayed transfer',
             'VBAC protocol; community follow-up for high-risk pregnancies', 'FUNDED'),
            ('PERINATAL', 'Jamalpur', 'Melandaha UHC', 0,
             'Preterm birth complications', 'No KMC unit; no CPAP; prematurity management gap',
             'Establish Kangaroo Mother Care unit; train nurses in preterm management', 'PENDING'),
            ('MATERNAL', 'Bogura', 'Sherpur UHC', 30,
             'Anaemia / haemorrhage', 'Severe anaemia undetected antenatally; no iron supplementation',
             'Routine haemoglobin screening at first ANC; iron-folic acid distribution', 'IMPLEMENTED'),
        ]

        created = 0
        for death_type, district, facility, age, cause, findings, action, status in events:
            kid = f"mpdsr_demo_{district}_{death_type}_{cause[:10]}".replace(' ', '_').lower()
            if not MPDSREvent.objects.filter(kobo_submission_id=kid).exists():
                MPDSREvent.objects.create(
                    death_type=death_type,
                    district=district,
                    facility_name=facility,
                    age_of_deceased=age,
                    cause_of_death=cause,
                    social_autopsy_findings=findings,
                    recommended_action=action,
                    action_status=status,
                    kobo_submission_id=kid,
                )
                created += 1

        self.stdout.write(f'  MPDSR events: {created} created')

    def _seed_activities(self):
        """Activity logs for CIPRB, PHD, Bondhu across districts."""
        activities = [
            ('CIPRB', 'Sylhet', 'Beanibazar', 'Fistula Awareness Campaign', date(2026, 4, 5), 'Dr. Rahima Khatun', 145),
            ('CIPRB', 'Mymensingh', 'Trishal', 'Community Outreach — MPDSR Awareness', date(2026, 4, 8), 'Md. Kamal Hossain', 89),
            ('CIPRB', 'Rajshahi', 'Godagari', 'Safe Motherhood Group Meeting', date(2026, 4, 12), 'Nasrin Akter', 67),
            ('CIPRB', 'Rangpur', 'Pirganj', 'Fistula Screening Camp', date(2026, 4, 15), 'Dr. Aminul Islam', 203),
            ('CIPRB', 'Khulna', 'Dumuria', 'MPDSR Review Meeting', date(2026, 4, 20), 'Sabrina Begum', 34),
            ('PHD', 'Barisal', 'Muladi', 'ANC Group Education Session', date(2026, 4, 6), 'Fatema Begum', 78),
            ('PHD', 'Comilla', 'Debidwar', 'Skilled Birth Attendant Training', date(2026, 4, 10), 'Dr. Sumaiya', 22),
            ('PHD', 'Dinajpur', 'Birampur', 'Community Health Worker Refresher', date(2026, 4, 18), 'Md. Rafiqul', 41),
            ('PHD', 'Jamalpur', 'Melandaha', 'Fistula Patient Follow-up Visit', date(2026, 4, 22), 'Roksana Parvin', 15),
            ('Bondhu', 'Bogura', 'Sherpur', 'SBCC Session — Danger Signs in Pregnancy', date(2026, 4, 7), 'Mst. Hasina', 112),
            ('Bondhu', 'Jessore', 'Chaugachha', 'Male Engagement Workshop', date(2026, 4, 14), 'Md. Jahangir', 56),
            ('Bondhu', 'Dhaka', 'Savar', 'Fistula Campaign — Industrial Workers', date(2026, 4, 25), 'Shapna Akter', 189),
        ]

        created = 0
        for partner, district, upazila, atype, adate, staff, beneficiaries in activities:
            kid = f"activity_{partner}_{district}_{atype[:8]}".replace(' ', '_').lower()
            if not ActivityLog.objects.filter(
                partner=partner, district=district, activity_type=atype, activity_date=adate
            ).exists():
                ActivityLog.objects.create(
                    partner=partner,
                    district=district,
                    upazila=upazila,
                    activity_type=atype,
                    activity_date=adate,
                    staff_name=staff,
                    beneficiary_count=beneficiaries,
                )
                created += 1

        self.stdout.write(f'  Activities: {created} created')

    def _seed_training(self):
        """Training sessions for M&E capacity building."""
        sessions = [
            ('CIPRB', 'Dhaka', date(2026, 4, 3), 'KoboToolbox Data Collection Training', 'Rafi Jahin', 18, 'PROFICIENT'),
            ('CIPRB', 'Sylhet', date(2026, 4, 10), 'MPDSR Review Process Orientation', 'Dr. S.M. Mashreky', 24, 'DEVELOPING'),
            ('PHD', 'Mymensingh', date(2026, 4, 8), 'Digital M&E Dashboard Orientation', 'Rafi Jahin', 15, 'BEGINNER'),
            ('PHD', 'Rajshahi', date(2026, 4, 17), 'Fistula Case Data Entry Protocol', 'Nasrin Akter', 12, 'DEVELOPING'),
            ('Bondhu', 'Khulna', date(2026, 4, 5), 'KoboToolbox Form Submission Training', 'Sabrina Begum', 20, 'PROFICIENT'),
            ('Bondhu', 'Barisal', date(2026, 4, 22), 'Data Quality Assurance Workshop', 'Rafi Jahin', 16, 'DEVELOPING'),
        ]

        created = 0
        for partner, district, sdate, topic, trainer, participants, level in sessions:
            if not TrainingSession.objects.filter(partner=partner, topic=topic, session_date=sdate).exists():
                TrainingSession.objects.create(
                    partner=partner,
                    district=district,
                    session_date=sdate,
                    topic=topic,
                    trainer_name=trainer,
                    participants_count=participants,
                    competency_level=level,
                )
                created += 1

        self.stdout.write(f'  Training sessions: {created} created')
