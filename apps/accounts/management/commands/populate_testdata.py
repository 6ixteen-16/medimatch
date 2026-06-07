from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from apps.accounts.models import CustomUser, Facility
from apps.donors.models import DonorProfile, EligibilityChecklist, DonationRecord
from apps.bulletins.models import Bulletin
from apps.sos.models import SOSRequest, SOSStatusUpdate
from apps.transport.models import TransportRequest


class Command(BaseCommand):
    help = 'Populate database with realistic test data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database population...\n')

        # Create Facilities
        facilities = self._create_facilities()
        self.stdout.write(f'✓ Created {len(facilities)} facilities\n')

        # Create Staff Accounts
        staff = self._create_staff_accounts(facilities)
        self.stdout.write(f'✓ Created {len(staff)} staff accounts\n')

        # Create Donor Accounts
        donors = self._create_donor_accounts(facilities)
        self.stdout.write(f'✓ Created {len(donors)} donor accounts\n')

        # Create Bulletins
        bulletins = self._create_bulletins(facilities, staff)
        self.stdout.write(f'✓ Created {len(bulletins)} bulletins\n')

        # Create SOS Requests
        sos_requests = self._create_sos_requests(facilities, staff)
        self.stdout.write(f'✓ Created {len(sos_requests)} SOS requests\n')

        # Create Donation Records
        donation_records = self._create_donation_records(donors, facilities, staff)
        self.stdout.write(f'✓ Created {len(donation_records)} donation records\n')

        # Skip transport requests for now to avoid voucher code conflicts
        self.stdout.write('✓ Transport requests: (create manually via UI)\n')

        self.stdout.write(self.style.SUCCESS('\n✓ Database population complete!'))
        self._print_test_accounts(staff, donors)

    def _create_facilities(self):
        """Create clinics and blood banks"""
        facilities_data = [
            # Blood Banks
            {'name': 'Uganda National Blood Bank', 'type': 'blood_bank', 'district': 'Kampala', 'address': 'Plot 1-3 Hospital Lane, Kampala', 'phone': '+256312302500', 'email': 'info@unbb.ug'},
            {'name': 'Kampala Central Blood Bank', 'type': 'blood_bank', 'district': 'Kampala', 'address': 'Fort Street, Kampala', 'phone': '+256312305000', 'email': 'central@unbb.ug'},
            {'name': 'Jinja Regional Blood Bank', 'type': 'blood_bank', 'district': 'Jinja', 'address': 'Main Street, Jinja', 'phone': '+256434122456', 'email': 'jinja@unbb.ug'},

            # Clinics
            {'name': 'Mulago National Referral Hospital', 'type': 'clinic', 'district': 'Kampala', 'address': 'Mulago Hill, Kampala', 'phone': '+256312303000', 'email': 'info@mulago.go.ug'},
            {'name': 'Case Clinic – Kampala', 'type': 'clinic', 'district': 'Kampala', 'address': 'Plot 123 Tweed Street, Kampala', 'phone': '+256701123456', 'email': 'kampala@case.ug'},
            {'name': 'Nsambya Hospital', 'type': 'clinic', 'district': 'Kampala', 'address': 'Nsambya, Kampala', 'phone': '+256312201000', 'email': 'info@nsambya.org'},
            {'name': 'Jinja Regional Referral Hospital', 'type': 'clinic', 'district': 'Jinja', 'address': 'Jinja, Uganda', 'phone': '+256434121000', 'email': 'info@jinja-ref.go.ug'},
            {'name': 'Mbale Health Centre IV', 'type': 'clinic', 'district': 'Mbale', 'address': 'Mbale, Uganda', 'phone': '+256456789000', 'email': 'mbale@health.go.ug'},
        ]

        facilities = []
        for fac_data in facilities_data:
            facility, created = Facility.objects.get_or_create(
                name=fac_data['name'],
                defaults={
                    'facility_type': fac_data['type'],
                    'address': fac_data['address'],
                    'district': fac_data['district'],
                    'phone': fac_data['phone'],
                    'email': fac_data['email'],
                    'is_active': True,
                }
            )
            facilities.append(facility)
        
        return facilities

    def _create_staff_accounts(self, facilities):
        """Create staff accounts with different roles"""
        staff_data = [
            # Superadmin
            {'username': 'admin', 'email': 'admin@medimatch.ug', 'first_name': 'System', 'last_name': 'Administrator', 'password': 'TestAdmin123!', 'role': 'superadmin', 'phone': '+256700000001'},
            
            # Blood Bank Admins
            {'username': 'bankadmin1', 'email': 'admin@unbb.ug', 'first_name': 'James', 'last_name': 'Kato', 'password': 'TestBank123!', 'role': 'bank_admin', 'phone': '+256700000002', 'facility_idx': 0},
            {'username': 'bankadmin2', 'email': 'admin@jinja-bb.ug', 'first_name': 'Sarah', 'last_name': 'Okello', 'password': 'TestBank123!', 'role': 'bank_admin', 'phone': '+256700000003', 'facility_idx': 2},
            
            # Clinic Admins
            {'username': 'clinicadmin1', 'email': 'admin@mulago.go.ug', 'first_name': 'Dr. David', 'last_name': 'Mukama', 'password': 'TestClinic123!', 'role': 'clinic_admin', 'phone': '+256700000004', 'facility_idx': 3},
            {'username': 'clinicadmin2', 'email': 'admin@case.ug', 'first_name': 'Maria', 'last_name': 'Nakamatte', 'password': 'TestClinic123!', 'role': 'clinic_admin', 'phone': '+256700000005', 'facility_idx': 4},
            {'username': 'clinicadmin3', 'email': 'admin@nsambya.org', 'first_name': 'Fr. Joseph', 'last_name': 'Kasirye', 'password': 'TestClinic123!', 'role': 'clinic_admin', 'phone': '+256700000006', 'facility_idx': 5},
            {'username': 'clinicadmin4', 'email': 'admin@jinja-ref.go.ug', 'first_name': 'Dr. Robert', 'last_name': 'Kyambadde', 'password': 'TestClinic123!', 'role': 'clinic_admin', 'phone': '+256700000007', 'facility_idx': 6},
        ]

        staff = []
        for staff_data_item in staff_data:
            facility_idx = staff_data_item.pop('facility_idx', None)
            # Use email as the unique identifier / username
            user, created = CustomUser.objects.get_or_create(
                email=staff_data_item['email'],
                defaults={
                    'username': staff_data_item['email'],
                    'first_name': staff_data_item['first_name'],
                    'last_name': staff_data_item['last_name'],
                    'phone_number': staff_data_item['phone'],
                    'role': staff_data_item['role'],
                    'facility': facilities[facility_idx] if facility_idx is not None else None,
                    'is_active': True,
                    'is_verified': True,
                }
            )
            if created:
                user.set_password(staff_data_item['password'])
                user.save()
            staff.append(user)
        
        return staff

    def _create_donor_accounts(self, facilities):
        """Create donor profiles with various statuses"""
        donor_data = [
            # Approved donors
            {'first': 'Alice', 'last': 'Karungi', 'blood': 'O+', 'dob': '1985-03-15', 'gender': 'm', 'nid': '1011111111111', 'district': 'Kampala', 'status': 'approved', 'needs_transport': False},
            {'first': 'Benjamin', 'last': 'Omondi', 'blood': 'A+', 'dob': '1990-07-22', 'gender': 'm', 'nid': '1022222222222', 'district': 'Kampala', 'status': 'approved', 'needs_transport': True, 'transport_notes': 'Lives in Kibuli, needs pickup'},
            {'first': 'Grace', 'last': 'Mukisa', 'blood': 'B+', 'dob': '1992-11-08', 'gender': 'f', 'nid': '1033333333333', 'district': 'Wakiso', 'status': 'approved', 'needs_transport': False},
            {'first': 'Daniel', 'last': 'Ssempijja', 'blood': 'AB-', 'dob': '1988-05-19', 'gender': 'm', 'nid': '1044444444444', 'district': 'Kampala', 'status': 'approved', 'needs_transport': True, 'transport_notes': 'Prefers evening collections'},

            # Pending donors (awaiting approval)
            {'first': 'Catherine', 'last': 'Nakawulo', 'blood': 'O+', 'dob': '1995-02-14', 'gender': 'f', 'nid': '1055555555555', 'district': 'Jinja', 'status': 'pending', 'needs_transport': True, 'transport_notes': 'First time donor, needs transport'},
            {'first': 'Edward', 'last': 'Mulwana', 'blood': 'B-', 'dob': '1993-09-27', 'gender': 'm', 'nid': '1066666666666', 'district': 'Mbale', 'status': 'pending', 'needs_transport': False},
            {'first': 'Fiona', 'last': 'Kitaka', 'blood': 'A-', 'dob': '1997-01-05', 'gender': 'f', 'nid': '1077777777777', 'district': 'Kampala', 'status': 'pending', 'needs_transport': False},

            # Flagged donors
            {'first': 'George', 'last': 'Komakech', 'blood': 'AB+', 'dob': '1980-12-31', 'gender': 'm', 'nid': '1088888888888', 'district': 'Gulu', 'status': 'flagged', 'needs_transport': False, 'flag_reason': 'Recent tattoo within 6 months'},

            # Suspended donor
            {'first': 'Helen', 'last': 'Nabwire', 'blood': 'O-', 'dob': '1989-06-16', 'gender': 'f', 'nid': '1099999999999', 'district': 'Kampala', 'status': 'suspended', 'needs_transport': False},
        ]

        donors = []
        for donor_info in donor_data:
            flag_reason = donor_info.pop('flag_reason', None)
            
            email = f"{donor_info['first'].lower()}.{donor_info['last'].lower()}@donors.medimatch.ug"
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=donor_info['first'],
                last_name=donor_info['last'],
                role='donor',
                phone_number=f"+256{''.join([str(random.randint(0,9)) for _ in range(9)])}",
                is_verified=True,
            )
            
            profile = DonorProfile.objects.create(
                user=user,
                blood_type=donor_info['blood'],
                date_of_birth=datetime.strptime(donor_info['dob'], '%Y-%m-%d').date(),
                gender=donor_info['gender'],
                national_id=donor_info['nid'],
                address=f"{donor_info['district']}, Uganda",
                district=donor_info['district'],
                status=donor_info['status'],
                needs_transport=donor_info['needs_transport'],
                transport_notes=donor_info.get('transport_notes', ''),
            )
            
            # Create eligibility checklist
            is_flagged = donor_info['status'] == 'flagged'
            checklist = EligibilityChecklist.objects.create(
                donor=profile,
                hiv_positive=False,
                hepatitis_b=False,
                hepatitis_c=False,
                malaria_last_3months=False,
                tuberculosis_active=False,
                recent_tattoo_6months=is_flagged,  # Example flag reason
                recent_surgery_6months=False,
                on_anticoagulants=False,
                pregnancy_or_breastfeed=False,
                donated_last_3months=False,
                weight_below_50kg=False,
                feels_well_today=True,
                no_alcohol_last_24h=True,
                is_auto_flagged=is_flagged,
                flagged_reason=flag_reason or '',
            )
            
            donors.append(profile)
        
        return donors

    def _create_bulletins(self, facilities, staff):
        """Create blood drive bulletins and awareness campaigns"""
        bulletin_data = [
            {
                'title': 'Emergency Blood Drive – Mulago Hospital',
                'body': 'Urgent call for blood donors. Mulago Hospital is facing critical shortages. All blood types needed. Please come to the main donation center.',
                'category': 'urgent_appeal',
                'blood_types': 'O+,O-,A+,B+',
                'facility_idx': 3,
                'staff_idx': 3,
                'event_date': (timezone.now() + timedelta(days=1)).date(),
                'event_time': '10:00',
                'event_location': 'Mulago Hospital – Main Hall',
                'status': 'published',
            },
            {
                'title': 'World Blood Donor Day Campaign',
                'body': 'Celebrate World Blood Donor Day with us! Join thousands of donors saving lives. One donation can save three lives.',
                'category': 'awareness',
                'blood_types': '',
                'facility_idx': 0,
                'staff_idx': 0,
                'event_date': (timezone.now() + timedelta(days=7)).date(),
                'event_time': '09:00',
                'event_location': 'Multiple venues across Kampala',
                'status': 'published',
            },
            {
                'title': 'Scheduled Blood Drive at Case Clinic',
                'body': 'Regular blood collection at Case Clinic. Walk-ins welcome. Refreshments provided.',
                'category': 'blood_drive',
                'blood_types': 'A+,AB+,AB-',
                'facility_idx': 4,
                'staff_idx': 4,
                'event_date': (timezone.now() + timedelta(days=3)).date(),
                'event_time': '14:00',
                'event_location': 'Case Clinic – Donation Center',
                'status': 'published',
            },
            {
                'title': 'Save Lives – Donate Blood Today',
                'body': 'Blood is a precious resource. Regular donors are the lifeline of our health system. Register and donate today.',
                'category': 'general',
                'blood_types': '',
                'facility_idx': 1,
                'staff_idx': 1,
                'event_date': None,
                'event_time': None,
                'event_location': '',
                'status': 'published',
            },
            {
                'title': 'Critical Shortage: O- Blood Type',
                'body': 'We are experiencing a critical shortage of O- blood. If you are an O- donor, please come donate immediately. Your donation can save a life today.',
                'category': 'urgent_appeal',
                'blood_types': 'O-',
                'facility_idx': 5,
                'staff_idx': 5,
                'event_date': timezone.now().date(),
                'event_time': '08:00',
                'event_location': 'Nsambya Hospital – Blood Bank',
                'status': 'published',
            },
        ]

        bulletins = []
        for bulletin_info in bulletin_data:
            bulletin = Bulletin.objects.create(
                title=bulletin_info['title'],
                body=bulletin_info['body'],
                category=bulletin_info['category'],
                blood_types_needed=bulletin_info['blood_types'],
                facility=facilities[bulletin_info['facility_idx']],
                posted_by=staff[bulletin_info['staff_idx']],
                event_date=bulletin_info['event_date'],
                event_time=bulletin_info['event_time'],
                event_location=bulletin_info['event_location'],
                status=bulletin_info['status'],
                email_sent=True,
                sms_sent=True,
                sms_sent_at=timezone.now() - timedelta(hours=12),
            )
            bulletins.append(bulletin)
        
        return bulletins

    def _create_sos_requests(self, facilities, staff):
        """Create SOS requests with different statuses"""
        sos_data = [
            {
                'requesting': 3,  # Mulago
                'target_bank': 0,  # Uganda National BB
                'blood_type': 'O+',
                'units': 2,
                'patient': 'Trauma patient from accident',
                'urgency': 'critical',
                'status': 'resolved',
                'staff_idx': 3,
                'bank_staff_idx': 0,
            },
            {
                'requesting': 4,  # Case Clinic
                'target_bank': 0,  # Uganda National BB
                'blood_type': 'A+',
                'units': 1,
                'patient': 'Post-surgical hemorrhage',
                'urgency': 'urgent',
                'status': 'in_transit',
                'staff_idx': 4,
                'bank_staff_idx': 0,
            },
            {
                'requesting': 5,  # Nsambya
                'target_bank': 0,  # Uganda National BB
                'blood_type': 'B+',
                'units': 3,
                'patient': 'Obstetric emergency',
                'urgency': 'critical',
                'status': 'open',
                'staff_idx': 5,
                'bank_staff_idx': 0,
            },
            {
                'requesting': 6,  # Jinja Referral
                'target_bank': 2,  # Jinja Regional BB
                'blood_type': 'O-',
                'units': 2,
                'patient': 'Bullet wound case',
                'urgency': 'urgent',
                'status': 'acknowledged',
                'staff_idx': 6,
                'bank_staff_idx': 2,
            },
        ]

        sos_requests = []
        for sos_info in sos_data:
            sos = SOSRequest.objects.create(
                requesting_facility=facilities[sos_info['requesting']],
                target_bank=facilities[sos_info['target_bank']],
                blood_type_needed=sos_info['blood_type'],
                units_needed=sos_info['units'],
                patient_condition=sos_info['patient'],
                urgency=sos_info['urgency'],
                status=sos_info['status'],
                requested_by=staff[sos_info['staff_idx']],
                acknowledged_by=staff[sos_info['bank_staff_idx']] if sos_info['status'] != 'open' else None,
                deadline=timezone.now() + timedelta(hours=1 if sos_info['urgency'] == 'critical' else 2),
                created_at=timezone.now() - timedelta(hours=random.randint(1, 12)),
            )
            sos_requests.append(sos)
            
            # Add status updates
            if sos_info['status'] == 'resolved':
                SOSStatusUpdate.objects.create(
                    sos_request=sos,
                    updated_by=staff[sos_info['bank_staff_idx']],
                    old_status='open',
                    new_status='acknowledged',
                    note='Blood located and dispatch arranged',
                )
                SOSStatusUpdate.objects.create(
                    sos_request=sos,
                    updated_by=staff[sos_info['bank_staff_idx']],
                    old_status='acknowledged',
                    new_status='in_transit',
                    note='Blood dispatched',
                )
                SOSStatusUpdate.objects.create(
                    sos_request=sos,
                    updated_by=staff[sos_info['staff_idx']],
                    old_status='in_transit',
                    new_status='resolved',
                    note='Blood received and transfusion completed',
                )
                sos.resolved_at = timezone.now() - timedelta(hours=2)
                sos.save()
        
        return sos_requests

    def _create_donation_records(self, donors, facilities, staff):
        """Create donation history"""
        donation_records = []
        
        # Only create records for approved donors
        approved_donors = [d for d in donors if d.status == 'approved']
        
        for donor in approved_donors:
            # Each donor has 1-4 past donations
            num_donations = random.randint(1, 4)
            for i in range(num_donations):
                donation = DonationRecord.objects.create(
                    donor=donor,
                    facility=random.choice(facilities[3:]),  # Clinics only
                    donated_at=(timezone.now() - timedelta(days=random.randint(30, 365))).date(),
                    blood_units=Decimal(str(round(random.uniform(0.4, 0.5), 2))),
                    notes='Regular donation' if i == 0 else f'Donation #{i+1}',
                    recorded_by=random.choice([s for s in staff if s.role == 'clinic_admin']),
                )
                donation_records.append(donation)
            
            # Update donor's last donation date and total
            donor.last_donation_date = min([d.donated_at for d in DonationRecord.objects.filter(donor=donor)])
            donor.total_donations = DonationRecord.objects.filter(donor=donor).count()
            donor.save()
        
        return donation_records

    def _create_transport_requests(self, donors, facilities):
        """Create transport requests"""
        transport_requests = []
        
        # Create transport requests for donors needing transport
        transport_donors = [d for d in donors if d.needs_transport and d.status == 'approved']
        
        for donor in transport_donors:
            # Create 1-2 transport requests per transport-needing donor
            num_requests = random.randint(1, 2)
            for _ in range(num_requests):
                # Only create pending status to avoid voucher code generation issues
                status_choice = 'pending'
                transport = TransportRequest.objects.create(
                    donor=donor,
                    facility=random.choice(facilities[3:]),  # Clinics
                    pickup_address=f"{donor.address}, {donor.district}",
                    estimated_cost=Decimal(str(random.randint(5000, 50000))),
                    funding_source=random.choice(['clinic_budget', 'ngo_partner', 'health_dept']),
                    status=status_choice,
                    notes='Transport for donation drive',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                )
                transport_requests.append(transport)
        
        return transport_requests

    def _print_test_accounts(self, staff, donors):
        """Print test account credentials"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('TEST ACCOUNT CREDENTIALS')
        self.stdout.write('='*60 + '\n')

        self.stdout.write(self.style.SUCCESS('ADMIN ACCOUNTS:\n'))
        test_staff = [
            ('admin@medimatch.ug', 'TestAdmin123!', 'System Admin'),
            ('admin@unbb.ug', 'TestBank123!', 'Blood Bank Admin'),
            ('admin@mulago.go.ug', 'TestClinic123!', 'Clinic Admin'),
        ]
        for email, password, description in test_staff:
            self.stdout.write(f'  {description}:')
            self.stdout.write(f'    Username: {email}')
            self.stdout.write(f'    Password: {password}\n')

        self.stdout.write(self.style.SUCCESS('DONOR ACCOUNTS (for testing donor flow):\n'))
        approved = [d for d in donors if d.status == 'approved']
        pending = [d for d in donors if d.status == 'pending']
        
        if approved:
            self.stdout.write(f'  Approved Donor: {approved[0].user.get_full_name()}')
            self.stdout.write(f'    Username: {approved[0].user.username}')
            self.stdout.write(f'    Status: Approved\n')
        
        if pending:
            self.stdout.write(f'  Pending Donor: {pending[0].user.get_full_name()}')
            self.stdout.write(f'    Username: {pending[0].user.username}')
            self.stdout.write(f'    Status: Pending Review\n')
