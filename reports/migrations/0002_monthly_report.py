import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reports', '0001_initial'),
    ]
    operations = [
        migrations.AddConstraint(
            model_name='monthlynewsletter',
            constraint=models.UniqueConstraint(fields=['month', 'year'], name='unique_newsletter_month_year'),
        ),
        migrations.CreateModel(
            name='MonthlyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('data_snapshot', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-year', '-month']},
        ),
        migrations.AlterUniqueTogether(
            name='monthlyreport',
            unique_together={('month', 'year')},
        ),
    ]
