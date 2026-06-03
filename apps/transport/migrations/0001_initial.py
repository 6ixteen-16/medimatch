from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('accounts', '0001_initial'),
        ('bulletins', '0001_initial'),
        ('donors', '0001_initial'),
        ('sos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='TransportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_address', models.TextField()),
                ('estimated_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('funding_source', models.CharField(
                    choices=[('clinic_budget','Clinic Emergency Fund'),('ngo_partner','NGO Partnership'),
                             ('health_dept','Health Department'),('pending_review','Pending Funding Review')],
                    default='pending_review', max_length=30)),
                ('voucher_code', models.CharField(blank=True, max_length=20, null=True, default=None, unique=True)),
                ('status', models.CharField(
                    choices=[('pending','Pending Approval'),('approved','Approved — Voucher Issued'),
                             ('completed','Completed'),('cancelled','Cancelled')],
                    default='pending', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transport_approvals', to=settings.AUTH_USER_MODEL)),
                ('bulletin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transport_requests', to='bulletins.bulletin')),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='transport_requests', to='donors.donorprofile')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    to='accounts.facility')),
                ('sos_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='transport_requests', to='sos.sosrequest')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
