"""
python manage.py seed_data

Seeds a FULLY POPULATED demo database:
  - 5 Facilities  (3 clinics + 2 blood banks across Uganda)
  - 1 Superadmin
  - 3 Clinic Admins  (one per clinic)
  - 2 Blood Bank Admins
  - 20 Donors       (all blood types, various statuses, districts)
  - 8 Bulletins     (drives, urgent appeals, awareness)
  - 6 SOS Requests  (open / acknowledged / in_transit / resolved / cancelled)
  - 10 Donation Records
  - 5 Transport Requests
  - Full SOS status update timelines
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta


# helpers

def make_user(CustomUser, email, password, first, last, role, facility=None,
              phone='', active=True):
    if CustomUser.objects.filter(email=email).exists():
        return CustomUser.objects.get(email=email)
    kwargs = dict(username=email, email=email, password=password,
                  first_name=first, last_name=last, role=role,
                  is_active=active, phone_number=phone)
    if facility:
        kwargs['facility'] = facility
    if role == 'superadmin':
        u = CustomUser.objects.create_superuser(**kwargs)
    else:
        u = CustomUser.objects.create_user(**kwargs)
    return u


def make_donor(DonorProfile, EligibilityChecklist, user, blood_type, dob,
               gender, nid, address, district, status='approved',
               last_don=None, total=0, transport=False, transport_notes='',
               flagged_fields=None):
    if hasattr(user, 'donor_profile'):
        return user.donor_profile
    p = DonorProfile.objects.create(
        user=user, blood_type=blood_type, date_of_birth=dob, gender=gender,
        national_id=nid, address=address, district=district,
        status=status, last_donation_date=last_don, total_donations=total,
        needs_transport=transport, transport_notes=transport_notes,
    )
    flags = flagged_fields or {}
    EligibilityChecklist.objects.create(
        donor=p,
        hiv_positive            = flags.get('hiv_positive', False),
        hepatitis_b             = flags.get('hepatitis_b', False),
        hepatitis_c             = flags.get('hepatitis_c', False),
        malaria_last_3months    = flags.get('malaria_last_3months', False),
        tuberculosis_active     = flags.get('tuberculosis_active', False),
        recent_tattoo_6months   = flags.get('recent_tattoo_6months', False),
        recent_surgery_6months  = flags.get('recent_surgery_6months', False),
        on_anticoagulants       = flags.get('on_anticoagulants', False),
        pregnancy_or_breastfeed = flags.get('pregnancy_or_breastfeed', False),
        donated_last_3months    = flags.get('donated_last_3months', False),
        weight_below_50kg       = flags.get('weight_below_50kg', False),
        feels_well_today        = flags.get('feels_well_today', True),
        no_alcohol_last_24h     = flags.get('no_alcohol_last_24h', True),
    )
    return p


class Command(BaseCommand):
    help = 'Seed rich demo data for MediMatch'

    def handle(self, *args, **options):
        from apps.accounts.models import CustomUser, Facility
        from apps.donors.models  import DonorProfile, EligibilityChecklist, DonationRecord
        from apps.bulletins.models import Bulletin
        from apps.sos.models     import SOSRequest, SOSStatusUpdate
        from apps.transport.models import TransportRequest

        W = self.style.WARNING
        S = self.style.SUCCESS
        self.stdout.write(S('\n══════════════════════════════════════'))
        self.stdout.write(S('  MediMatch — Seeding Demo Database'))
        self.stdout.write(S('══════════════════════════════════════\n'))

        #FACILITIES

        self.stdout.write(' Creating facilities...')

        mulago, _ = Facility.objects.get_or_create(
            name='Mulago Community Health Centre',
            defaults=dict(facility_type='clinic', address='Mulago Hill, Kampala',
                          district='Kampala', phone='+256414530020',
                          email='mulago@clinic.ug', latitude=0.3394, longitude=32.5765))

        kisenyi, _ = Facility.objects.get_or_create(
            name='Kisenyi Health Centre IV',
            defaults=dict(facility_type='clinic', address='Kisenyi, Kampala',
                          district='Kampala', phone='+256414272150',
                          email='kisenyi@clinic.ug', latitude=0.3136, longitude=32.5599))

        jinja, _ = Facility.objects.get_or_create(
            name='Jinja Regional Referral Hospital',
            defaults=dict(facility_type='clinic', address='Lubas Road, Jinja',
                          district='Jinja', phone='+256434120400',
                          email='jinja.referral@moh.go.ug', latitude=0.4244, longitude=33.2041))

        nakasero, _ = Facility.objects.get_or_create(
            name='Uganda Blood Transfusion Service – Nakasero',
            defaults=dict(facility_type='blood_bank', address='Nakasero Hospital Road, Kampala',
                          district='Kampala', phone='+256414340506',
                          email='info@ubts.go.ug', latitude=0.3167, longitude=32.5833))

        mbarara_bank, _ = Facility.objects.get_or_create(
            name='UBTS Regional Centre – Mbarara',
            defaults=dict(facility_type='blood_bank', address='Mbarara University Road',
                          district='Mbarara', phone='+256485420400',
                          email='mbarara@ubts.go.ug', latitude=-0.6070, longitude=30.6545))

        self.stdout.write(S('   ✓ 5 facilities ready\n'))

        # STAFF USERS
        self.stdout.write('  Creating staff accounts...')

        superadmin = make_user(CustomUser, 'admin@medimatch.ug', 'Admin1234!',
                               'Super', 'Admin', 'superadmin', phone='+256700000001')

        clinic1 = make_user(CustomUser, 'grace.nakato@medimatch.ug', 'Clinic1234!',
                            'Grace', 'Nakato', 'clinic_admin', facility=mulago,
                            phone='+256701111001')
        clinic2 = make_user(CustomUser, 'robert.onen@medimatch.ug', 'Clinic1234!',
                            'Robert', 'Onen', 'clinic_admin', facility=kisenyi,
                            phone='+256701111002')
        clinic3 = make_user(CustomUser, 'sarah.akello@medimatch.ug', 'Clinic1234!',
                            'Sarah', 'Akello', 'clinic_admin', facility=jinja,
                            phone='+256701111003')

        bank1 = make_user(CustomUser, 'david.ssali@medimatch.ug', 'Bank1234!',
                          'David', 'Ssali', 'bank_admin', facility=nakasero,
                          phone='+256702222001')
        bank2 = make_user(CustomUser, 'patricia.tumusiime@medimatch.ug', 'Bank1234!',
                          'Patricia', 'Tumusiime', 'bank_admin', facility=mbarara_bank,
                          phone='+256702222002')

        self.stdout.write(S('   ✓ 1 superadmin + 3 clinic admins + 2 bank admins\n'))

        # DONORS (20)

        self.stdout.write('  Creating 20 donor accounts...')

        donor_specs = [
            # (email, password, first, last, phone,
            #  blood_type, dob, gender, nid, address, district,
            #  status, last_donation, total_donations,
            #  needs_transport, transport_notes, flagged_fields)
            ('amina.nalumansi@donors.medimatch.ug', 'Donor1234!',
             'Amina', 'Nalumansi', '+256771000001',
             'O+', date(1995, 6, 15), 'female', 'CM9500001234ABCD',
             'Kiira Road, Kampala', 'Kampala',
             'approved', date(2024, 9, 1), 3, False, '', {}),

            ('brian.okello@donors.medimatch.ug', 'Donor1234!',
             'Brian', 'Okello', '+256771000002',
             'A+', date(1990, 3, 22), 'male', 'CM9000002345EFGH',
             'Ntinda, Kampala', 'Kampala',
             'approved', date(2024, 11, 10), 7, False, '', {}),

            ('catherine.achola@donors.medimatch.ug', 'Donor1234!',
             'Catherine', 'Achola', '+256771000003',
             'B+', date(1998, 8, 5), 'female', 'CM9800003456IJKL',
             'Gulu Road, Gulu', 'Gulu',
             'approved', date(2024, 7, 20), 2, True,
             'Lives 12km from Mulago; boda-boda pickup needed from Gulu Stage',
             {}),

            ('daniel.mugisha@donors.medimatch.ug', 'Donor1234!',
             'Daniel', 'Mugisha', '+256771000004',
             'O-', date(1985, 12, 30), 'male', 'CM8500004567MNOP',
             'Mbarara Town', 'Mbarara',
             'approved', date(2024, 6, 5), 12, False, '', {}),

            ('esther.namukasa@donors.medimatch.ug', 'Donor1234!',
             'Esther', 'Namukasa', '+256771000005',
             'AB+', date(2000, 1, 19), 'female', 'CM0000005678QRST',
             'Entebbe Road, Wakiso', 'Wakiso',
             'approved', None, 0, False, '', {}),

            ('fred.wamala@donors.medimatch.ug', 'Donor1234!',
             'Fred', 'Wamala', '+256771000006',
             'A-', date(1992, 5, 14), 'male', 'CM9200006789UVWX',
             'Mbale Town Centre', 'Mbale',
             'approved', date(2024, 10, 3), 5, True,
             'No personal vehicle; lives 8km from Jinja referral on Tororo Road',
             {}),

            ('grace.apio@donors.medimatch.ug', 'Donor1234!',
             'Grace', 'Apio', '+256771000007',
             'B-', date(1997, 9, 28), 'female', 'CM9700007890YZAB',
             'Lira Municipality', 'Lira',
             'approved', date(2024, 4, 18), 4, False, '', {}),

            ('henry.byaruhanga@donors.medimatch.ug', 'Donor1234!',
             'Henry', 'Byaruhanga', '+256771000008',
             'O+', date(1988, 7, 11), 'male', 'CM8800008901CDEF',
             'Fort Portal Town', 'Kabarole',
             'approved', date(2025, 1, 7), 9, False, '', {}),

            ('irene.atim@donors.medimatch.ug', 'Donor1234!',
             'Irene', 'Atim', '+256771000009',
             'AB-', date(2002, 4, 3), 'female', 'CM0200009012GHIJ',
             'Arua Hill, Arua', 'Arua',
             'pending', None, 0, False, '', {}),

            ('james.ssebulime@donors.medimatch.ug', 'Donor1234!',
             'James', 'Ssebulime', '+256771000010',
             'A+', date(1993, 11, 25), 'male', 'CM9300010123KLMN',
             'Bugolobi, Kampala', 'Kampala',
             'approved', date(2024, 8, 14), 6, False, '', {}),

            ('kevin.opio@donors.medimatch.ug', 'Donor1234!',
             'Kevin', 'Opio', '+256771000011',
             'O+', date(1986, 2, 8), 'male', 'CM8600011234OPQR',
             'Soroti Municipality', 'Soroti',
             'approved', date(2024, 3, 30), 8, True,
             'Elderly mother dependent on him; needs afternoon pickup after 14:00',
             {}),

            ('lydia.nansubuga@donors.medimatch.ug', 'Donor1234!',
             'Lydia', 'Nansubuga', '+256771000012',
             'B+', date(1999, 6, 17), 'female', 'CM9900012345STUV',
             'Masaka Road, Masaka', 'Masaka',
             'pending', None, 0, True,
             'New donor; no motorbike; needs taxi fare reimbursement',
             {}),

            ('moses.kato@donors.medimatch.ug', 'Donor1234!',
             'Moses', 'Kato', '+256771000013',
             'O-', date(1980, 10, 22), 'male', 'CM8000013456WXYZ',
             'Kawempe Division, Kampala', 'Kampala',
             'approved', date(2025, 2, 1), 15, False, '', {}),

            ('norah.tumwine@donors.medimatch.ug', 'Donor1234!',
             'Norah', 'Tumwine', '+256771000014',
             'A+', date(1994, 3, 5), 'female', 'CM9400014567ABCD',
             'Kabale Town', 'Kabale',
             'approved', date(2024, 12, 20), 3, False, '', {}),

            ('paul.lubega@donors.medimatch.ug', 'Donor1234!',
             'Paul', 'Lubega', '+256771000015',
             'AB+', date(1991, 8, 31), 'male', 'CM9100015678EFGH',
             'Nakawa Division, Kampala', 'Kampala',
             'approved', None, 1, False, '', {}),

            # Flagged donors — auto-flagged by checklist
            ('rita.nabirye@donors.medimatch.ug', 'Donor1234!',
             'Rita', 'Nabirye', '+256771000016',
             'A-', date(1996, 5, 20), 'female', 'CM9600016789IJKL',
             'Jinja Road, Mukono', 'Mukono',
             'flagged', None, 0, False, '',
             {'malaria_last_3months': True}),

            ('sam.tugume@donors.medimatch.ug', 'Donor1234!',
             'Sam', 'Tugume', '+256771000017',
             'B+', date(1983, 1, 15), 'male', 'CM8300017890MNOP',
             'Kololo, Kampala', 'Kampala',
             'flagged', None, 0, False, '',
             {'recent_surgery_6months': True, 'on_anticoagulants': True}),

            # Suspended donor
            ('tina.akello@donors.medimatch.ug', 'Donor1234!',
             'Tina', 'Akello', '+256771000018',
             'O+', date(2003, 7, 9), 'female', 'CM0300018901QRST',
             'Nakivubo, Kampala', 'Kampala',
             'suspended', date(2024, 1, 10), 1, False, '',
             {'hiv_positive': True}),

            # Young new donors — pending
            ('umar.ssekandi@donors.medimatch.ug', 'Donor1234!',
             'Umar', 'Ssekandi', '+256771000019',
             'O-', date(2001, 9, 4), 'male', 'CM0100019012UVWX',
             'Wandegeya, Kampala', 'Kampala',
             'pending', None, 0, False, '', {}),

            ('violet.nanteza@donors.medimatch.ug', 'Donor1234!',
             'Violet', 'Nanteza', '+256771000020',
             'AB-', date(2004, 2, 28), 'female', 'CM0400020123YZAB',
             'Entebbe Municipality', 'Wakiso',
             'pending', None, 0, True,
             'Wheelchair user; needs accessible transport and advance notice',
             {}),
        ]

        donors = {}
        for spec in donor_specs:
            (email, pwd, first, last, phone,
             bt, dob, gender, nid, addr, dist,
             status, last_don, total, transport, tnotes, flags) = spec
            u = make_user(CustomUser, email, pwd, first, last, 'donor', phone=phone)
            p = make_donor(DonorProfile, EligibilityChecklist,
                           u, bt, dob, gender, nid, addr, dist,
                           status=status, last_don=last_don, total=total,
                           transport=transport, transport_notes=tnotes,
                           flagged_fields=flags)
            donors[email] = p

        self.stdout.write(S('   ✓ 20 donors created (approved / pending / flagged / suspended)\n'))

        # DONATION RECORDS 

        self.stdout.write('  Creating donation records...')

        donation_data = [
            ('amina.nalumansi@donors.medimatch.ug', mulago,  date(2024, 9, 1),  0.45, clinic1),
            ('amina.nalumansi@donors.medimatch.ug', mulago,  date(2024, 3, 15), 0.45, clinic1),
            ('amina.nalumansi@donors.medimatch.ug', mulago,  date(2023, 9, 10), 0.45, clinic1),
            ('brian.okello@donors.medimatch.ug',    kisenyi, date(2024, 11, 10), 0.45, clinic2),
            ('brian.okello@donors.medimatch.ug',    kisenyi, date(2024, 7, 22),  0.45, clinic2),
            ('daniel.mugisha@donors.medimatch.ug',  jinja,   date(2024, 6, 5),   0.45, clinic3),
            ('henry.byaruhanga@donors.medimatch.ug',mulago,  date(2025, 1, 7),   0.45, clinic1),
            ('james.ssebulime@donors.medimatch.ug', kisenyi, date(2024, 8, 14),  0.45, clinic2),
            ('moses.kato@donors.medimatch.ug',      mulago,  date(2025, 2, 1),   0.45, clinic1),
            ('norah.tumwine@donors.medimatch.ug',   jinja,   date(2024, 12, 20), 0.45, clinic3),
        ]

        for email, facility, don_date, units, recorder in donation_data:
            profile = donors.get(email)
            if profile and not DonationRecord.objects.filter(donor=profile, donated_at=don_date).exists():
                DonationRecord.objects.create(
                    donor=profile, facility=facility,
                    donated_at=don_date, blood_units=units,
                    recorded_by=recorder,
                )

        self.stdout.write(S('   ✓ 10 donation records created\n'))

        # BULLETINS (8)

        self.stdout.write(' Creating bulletins...')

        bulletin_specs = [
            dict(
                title='Monthly Blood Drive — Mulago Community Health Centre',
                body='Join us for our monthly blood drive at Mulago CHC. All blood types are welcome. Refreshments and certificates provided. '
                     'Donors who give 5+ times receive a MediMatch Champion badge. Bring your National ID.',
                category='blood_drive', blood_types='O+, O-, A+, A-, B+',
                facility=mulago, posted_by=clinic1,
                event_date=date.today() + timedelta(days=7),
                event_time_h=9, event_location='Mulago CHC, Ground Floor Hall',
                status='published', sms_sent=True,
            ),
            dict(
                title='URGENT: O- Blood Needed — Kisenyi HC IV',
                body='We are facing a critical shortage of O-negative blood. Post-surgical patients are at risk. '
                     'If you are O- and have not donated in the last 90 days, please come immediately to Kisenyi HC IV. '
                     'No appointment needed. We are open until 20:00 tonight.',
                category='urgent_appeal', blood_types='O-',
                facility=kisenyi, posted_by=clinic2,
                event_date=date.today(),
                event_time_h=8, event_location='Kisenyi HC IV, Blood Collection Room',
                status='published', sms_sent=True,
            ),
            dict(
                title='World Blood Donor Day — Jinja Regional Hospital',
                body='Celebrate World Blood Donor Day with us! Free health screening, blood pressure check, HIV testing, '
                     'and blood donation all in one visit. Community musicians will perform. All donors receive a free T-shirt.',
                category='awareness', blood_types='A+, A-, B+, B-, O+, O-, AB+, AB-',
                facility=jinja, posted_by=clinic3,
                event_date=date.today() + timedelta(days=14),
                event_time_h=8, event_location='Jinja Hospital Community Grounds',
                status='published', sms_sent=False,
            ),
            dict(
                title='Emergency AB- Appeal — Mulago CHC',
                body='AB-negative blood is urgently needed for a paediatric patient undergoing emergency surgery. '
                     'If you are AB- or O-, please report to Mulago CHC immediately. '
                     'Transport reimbursement available for donors coming from outside Kampala.',
                category='urgent_appeal', blood_types='AB-, O-',
                facility=mulago, posted_by=clinic1,
                event_date=date.today(),
                event_time_h=6, event_location='Mulago CHC, Theatre Building',
                status='published', sms_sent=True,
            ),
            dict(
                title='Quarterly Drive — Kisenyi Health Centre',
                body='Our quarterly blood drive is here. We need to replenish stocks before the rainy season '
                     'when road accidents and maternal complications increase. '
                     'Donors will receive free malaria testing and nutritional counselling.',
                category='blood_drive', blood_types='O+, B+, A+',
                facility=kisenyi, posted_by=clinic2,
                event_date=date.today() + timedelta(days=21),
                event_time_h=8, event_location='Kisenyi HC IV, Outpatient Area',
                status='published', sms_sent=False,
            ),
            dict(
                title='Safe Blood Saves Lives — Awareness Campaign',
                body='Did you know one blood donation can save up to 3 lives? '
                     'Join our awareness walk starting at Mulago Hill. '
                     'We will visit schools and community centres to educate Uganda\'s next generation of donors.',
                category='awareness', blood_types='',
                facility=mulago, posted_by=clinic1,
                event_date=date.today() + timedelta(days=30),
                event_time_h=7, event_location='Starting point: Mulago Hill Gate',
                status='published', sms_sent=False,
            ),
            dict(
                title='Staff Blood Drive — Jinja Referral Hospital',
                body='All Jinja Regional Referral Hospital staff are encouraged to donate. '
                     'This is a closed staff drive. Walk-in donors from the community are also welcome from 12:00.',
                category='blood_drive', blood_types='A+, A-, O+, O-',
                facility=jinja, posted_by=clinic3,
                event_date=date.today() + timedelta(days=3),
                event_time_h=9, event_location='Jinja RRH Staff Conference Room',
                status='published', sms_sent=False,
            ),
            dict(
                title='New Donor Registration Open — Mulago CHC',
                body='Mulago Community Health Centre is now accepting new donor registrations online at medimatch.ug. '
                     'Register from the comfort of your home and get matched to blood drives near you. '
                     'Transport support available for donors in Wakiso and Mukono districts.',
                category='general', blood_types='',
                facility=mulago, posted_by=clinic1,
                event_date=None,
                event_time_h=None, event_location='',
                status='published', sms_sent=False,
            ),
        ]

        bulletins_created = []
        for bs in bulletin_specs:
            if Bulletin.objects.filter(title=bs['title']).exists():
                bulletins_created.append(Bulletin.objects.get(title=bs['title']))
                continue
            from datetime import time as dtime
            b = Bulletin.objects.create(
                title=bs['title'], body=bs['body'],
                category=bs['category'],
                blood_types_needed=bs['blood_types'],
                facility=bs['facility'], posted_by=bs['posted_by'],
                event_date=bs['event_date'],
                event_time=dtime(bs['event_time_h'], 0) if bs['event_time_h'] else None,
                event_location=bs['event_location'],
                status=bs['status'],
                sms_sent=bs['sms_sent'],
                email_sent=bs['sms_sent'],
            )
            bulletins_created.append(b)

        self.stdout.write(S('   ✓ 8 bulletins created (drives, appeals, awareness)\n'))

        # SOS REQUESTS (6)

        self.stdout.write(' Creating SOS requests...')

        sos_specs = [
            dict(
                requesting_facility=mulago, target_bank=nakasero,
                blood_type='O-', units=3, urgency='critical', status='open',
                requested_by=clinic1,
                condition='Post-partum haemorrhage following emergency C-section. '
                           'Rh-negative patient, surgical team standing by. BP dropping.',
                resolution_notes='', resolved_at=None,
            ),
            dict(
                requesting_facility=kisenyi, target_bank=nakasero,
                blood_type='A+', units=2, urgency='urgent', status='acknowledged',
                requested_by=clinic2,
                condition='Trauma patient — RTA (road traffic accident) on Entebbe Road. '
                           'Blunt abdominal trauma, internal bleeding suspected.',
                resolution_notes='', resolved_at=None,
            ),
            dict(
                requesting_facility=jinja, target_bank=mbarara_bank,
                blood_type='B+', units=4, urgency='urgent', status='in_transit',
                requested_by=clinic3,
                condition='Three units needed for elective sickle cell transfusion; '
                           'one additional unit for surgical backup.',
                resolution_notes='', resolved_at=None,
            ),
            dict(
                requesting_facility=mulago, target_bank=nakasero,
                blood_type='AB+', units=1, urgency='standard', status='resolved',
                requested_by=clinic1,
                condition='Paediatric anaemia — elective pre-surgical top-up.',
                resolution_notes='1 unit of AB+ delivered from Nakasero at 14:32. Patient stable and surgery proceeded.',
                resolved_at=timezone.now() - timedelta(hours=6),
            ),
            dict(
                requesting_facility=kisenyi, target_bank=None,
                blood_type='O+', units=5, urgency='critical', status='resolved',
                requested_by=clinic2,
                condition='Mass casualty — bus accident on Masaka Road. '
                           'Multiple patients with blood loss. O+ broadcast to all banks.',
                resolution_notes='5 units sourced: 3 from Nakasero, 2 from emergency donor walk-ins. All patients stabilised.',
                resolved_at=timezone.now() - timedelta(days=2),
            ),
            dict(
                requesting_facility=jinja, target_bank=nakasero,
                blood_type='O-', units=2, urgency='urgent', status='cancelled',
                requested_by=clinic3,
                condition='Pre-operative preparation for kidney surgery. Patient rescheduled.',
                resolution_notes='Surgery postponed by 3 weeks on consultant advice. SOS cancelled.',
                resolved_at=None,
            ),
        ]

        sos_list = []
        for i, ss in enumerate(sos_specs):
            existing = SOSRequest.objects.filter(
                requesting_facility=ss['requesting_facility'],
                blood_type_needed=ss['blood_type'],
                urgency=ss['urgency'],
                status=ss['status'],
            ).first()
            if existing:
                sos_list.append(existing)
                continue

            sos = SOSRequest(
                requesting_facility=ss['requesting_facility'],
                target_bank=ss['target_bank'],
                blood_type_needed=ss['blood_type'],
                units_needed=ss['units'],
                urgency=ss['urgency'],
                status=ss['status'],
                requested_by=ss['requested_by'],
                patient_condition=ss['condition'],
                resolution_notes=ss['resolution_notes'],
            )
            if ss['resolved_at']:
                sos.resolved_at = ss['resolved_at']
            if ss['status'] in ('acknowledged', 'in_transit', 'resolved'):
                sos.acknowledged_by = bank1
            sos.save()

            # Status update timeline
            SOSStatusUpdate.objects.get_or_create(
                sos_request=sos, old_status='', new_status='open',
                defaults=dict(updated_by=ss['requested_by'], note='SOS created'))

            if ss['status'] in ('acknowledged', 'in_transit', 'resolved'):
                SOSStatusUpdate.objects.get_or_create(
                    sos_request=sos, old_status='open', new_status='acknowledged',
                    defaults=dict(updated_by=bank1, note='Acknowledged — checking stock availability'))

            if ss['status'] in ('in_transit', 'resolved'):
                SOSStatusUpdate.objects.get_or_create(
                    sos_request=sos, old_status='acknowledged', new_status='in_transit',
                    defaults=dict(updated_by=bank1, note='Blood dispatched via UBTS courier vehicle'))

            if ss['status'] == 'resolved':
                SOSStatusUpdate.objects.get_or_create(
                    sos_request=sos, old_status='in_transit', new_status='resolved',
                    defaults=dict(updated_by=ss['requested_by'], note=ss['resolution_notes']))

            if ss['status'] == 'cancelled':
                SOSStatusUpdate.objects.get_or_create(
                    sos_request=sos, old_status='open', new_status='cancelled',
                    defaults=dict(updated_by=ss['requested_by'], note=ss['resolution_notes']))

            sos_list.append(sos)

        self.stdout.write(S('   ✓ 6 SOS requests with full status timelines\n'))

        # TRANSPORT REQUESTS (5)

        self.stdout.write('  Creating transport requests...')

        transport_specs = [
            dict(
                donor_email='catherine.achola@donors.medimatch.ug',
                facility=mulago, bulletin=bulletins_created[0],
                pickup='Gulu Stage, Kitgum Road, near Total station',
                cost=25000, funding='health_dept', status='approved',
                approved_by=clinic1, notes='Boda-boda arranged for 08:00 pickup',
            ),
            dict(
                donor_email='fred.wamala@donors.medimatch.ug',
                facility=jinja, bulletin=bulletins_created[2],
                pickup='Tororo Road, Mbale — opposite Stanbic Bank',
                cost=30000, funding='ngo_partner', status='approved',
                approved_by=clinic3, notes='Shared taxi arranged with another donor from Mbale',
            ),
            dict(
                donor_email='kevin.opio@donors.medimatch.ug',
                facility=kisenyi, bulletin=bulletins_created[4],
                pickup='Soroti Market Bus Stage',
                cost=45000, funding='clinic_budget', status='completed',
                approved_by=clinic2, notes='Donor confirmed arrival at 09:15. Donation completed.',
            ),
            dict(
                donor_email='lydia.nansubuga@donors.medimatch.ug',
                facility=mulago, bulletin=bulletins_created[0],
                pickup='Masaka Road, Lukaya Town — near Shell station',
                cost=20000, funding='pending_review', status='pending',
                approved_by=None, notes='',
            ),
            dict(
                donor_email='violet.nanteza@donors.medimatch.ug',
                facility=kisenyi, bulletin=None,
                pickup='Entebbe Municipality, near Airport Road junction',
                cost=15000, funding='health_dept', status='pending',
                approved_by=None,
                notes='Wheelchair user — needs accessible vehicle. Confirm before dispatch.',
            ),
        ]

        for ts in transport_specs:
            donor_profile = donors.get(ts['donor_email'])
            if not donor_profile:
                continue
            if TransportRequest.objects.filter(donor=donor_profile, facility=ts['facility']).exists():
                continue
            tr = TransportRequest(
                donor=donor_profile,
                facility=ts['facility'],
                bulletin=ts['bulletin'],
                pickup_address=ts['pickup'],
                estimated_cost=ts['cost'],
                funding_source=ts['funding'],
                status=ts['status'],
                approved_by=ts['approved_by'],
                notes=ts['notes'],
            )
            if ts["status"] in ("approved", "completed"):
                import uuid as _uuid
                tr.voucher_code = 'MM-' + _uuid.uuid4().hex[:8].upper()
            tr.save()

        self.stdout.write(S('   ✓ 5 transport requests (pending / approved / completed)\n'))

        # SUMMARY 
        self.stdout.write(S('\n══════════════════════════════════════'))
        self.stdout.write(S('  ✓ Seed complete — database ready!'))
        self.stdout.write(S('══════════════════════════════════════\n'))

        self.stdout.write('  STAFF ACCOUNTS')
        self.stdout.write('  ─────────────────────────────────────────────────────────────')
        self.stdout.write(W('  SUPERADMIN'))
        self.stdout.write('  admin@medimatch.ug                   Admin1234!')
        self.stdout.write('')
        self.stdout.write(W('  CLINIC ADMINS  (password: Clinic1234!)'))
        self.stdout.write('  grace.nakato@medimatch.ug            Mulago Community Health Centre')
        self.stdout.write('  robert.onen@medimatch.ug             Kisenyi Health Centre IV')
        self.stdout.write('  sarah.akello@medimatch.ug            Jinja Regional Referral Hospital')
        self.stdout.write('')
        self.stdout.write(W('  BLOOD BANK ADMINS  (password: Bank1234!)'))
        self.stdout.write('  david.ssali@medimatch.ug             UBTS Nakasero (Kampala)')
        self.stdout.write('  patricia.tumusiime@medimatch.ug      UBTS Regional Centre (Mbarara)')
        self.stdout.write('')
        self.stdout.write('  DONOR ACCOUNTS  (all passwords: Donor1234!)')
        self.stdout.write('  ─────────────────────────────────────────────────────────────')
        rows = [
            ('amina.nalumansi',    'O+',  'Approved',  'Kampala',  '3 donations'),
            ('brian.okello',       'A+',  'Approved',  'Kampala',  '7 donations'),
            ('catherine.achola',   'B+',  'Approved',  'Gulu',     'Needs transport'),
            ('daniel.mugisha',     'O-',  'Approved',  'Mbarara',  '12 donations'),
            ('esther.namukasa',    'AB+', 'Approved',  'Wakiso',   'New donor'),
            ('fred.wamala',        'A-',  'Approved',  'Mbale',    'Needs transport'),
            ('grace.apio',         'B-',  'Approved',  'Lira',     '4 donations'),
            ('henry.byaruhanga',   'O+',  'Approved',  'Kabarole', '9 donations'),
            ('irene.atim',         'AB-', 'Pending',   'Arua',     'New donor'),
            ('james.ssebulime',    'A+',  'Approved',  'Kampala',  '6 donations'),
            ('kevin.opio',         'O+',  'Approved',  'Soroti',   'Needs transport'),
            ('lydia.nansubuga',    'B+',  'Pending',   'Masaka',   'Needs transport'),
            ('moses.kato',         'O-',  'Approved',  'Kampala',  '15 donations'),
            ('norah.tumwine',      'A+',  'Approved',  'Kabale',   '3 donations'),
            ('paul.lubega',        'AB+', 'Approved',  'Kampala',  '1 donation'),
            ('rita.nabirye',       'A-',  'Flagged',   'Mukono',   'Malaria in last 3mo'),
            ('sam.tugume',         'B+',  'Flagged',   'Kampala',  'Surgery + anticoags'),
            ('tina.akello',        'O+',  'Suspended', 'Kampala',  'HIV positive'),
            ('umar.ssekandi',      'O-',  'Pending',   'Kampala',  'New donor'),
            ('violet.nanteza',     'AB-', 'Pending',   'Wakiso',   'Wheelchair; transport'),
        ]
        for r in rows:
            email_part = f'{r[0]}@donors.medimatch.ug'
            self.stdout.write(f'  {email_part:<45}  {r[1]:<4}  {r[2]:<10}  {r[3]:<10}  {r[4]}')

        self.stdout.write('')
        self.stdout.write(S('  Run:  python manage.py runserver'))
        self.stdout.write(S('  URL:  http://127.0.0.1:8000\n'))
