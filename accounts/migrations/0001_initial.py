from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('UNFPA_ADMIN','UNFPA Admin'),('CIPRB_ADMIN','CIPRB Admin'),('PHD_USER','PHD User'),('BONDHU_USER','Bondhu User'),('VIEWER','Viewer (Read Only)')], default='VIEWER', max_length=20)),
                ('organisation', models.CharField(choices=[('UNFPA','UNFPA'),('CIPRB','CIPRB'),('PHD','PHD'),('Bondhu','Bondhu')], default='CIPRB', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
