"""
Management command to auto-generate monthly M&E reports.
Run manually: python manage.py generate_monthly_report
Or schedule via Render cron job: 0 6 1 * * (1st of every month at 6am)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.models import MonthlyNewsletter, MonthlyReport
from reports.ai_utils import generate_newsletter_narrative
from reports.report_utils import generate_report_data
import json


class Command(BaseCommand):
    help = 'Auto-generate monthly M&E report and AI newsletter'

    def add_arguments(self, parser):
        parser.add_argument('--month', type=int, help='Month (1-12). Defaults to current month.')
        parser.add_argument('--year', type=int, help='Year. Defaults to current year.')
        parser.add_argument('--force', action='store_true', help='Regenerate even if report exists')

    def handle(self, *args, **options):
        now = timezone.now()
        month = options.get('month') or now.month
        year = options.get('year') or now.year

        self.stdout.write(f'Generating report for {month}/{year}...')

        # Check if already exists
        existing = MonthlyReport.objects.filter(month=month, year=year).first()
        if existing and not options.get('force'):
            self.stdout.write(self.style.WARNING(f'Report for {month}/{year} already exists. Use --force to regenerate.'))
            return

        # Generate report data snapshot
        data = generate_report_data(month, year)

        # Save report snapshot
        if existing:
            existing.data_snapshot = json.dumps(data)
            existing.save()
            report = existing
        else:
            report = MonthlyReport.objects.create(
                month=month,
                year=year,
                data_snapshot=json.dumps(data),
            )

        # Generate AI newsletter
        narrative = generate_newsletter_narrative(month, year)
        newsletter, _ = MonthlyNewsletter.objects.update_or_create(
            month=month,
            year=year,
            defaults={'content': narrative}
        )

        self.stdout.write(self.style.SUCCESS(
            f'Report generated: {month}/{year}\n'
            f'  Fistula operated: {data["fistula_operated"]}/{data["fistula_goal"]}\n'
            f'  MPDSR events: {data["total_mpdsr"]} ({data["pending_mpdsr"]} pending)\n'
            f'  Beneficiaries: {data["total_beneficiaries"]}\n'
            f'  Newsletter: saved (ID {newsletter.id})'
        ))
