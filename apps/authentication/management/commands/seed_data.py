from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.mappings.models import PatientDoctorMapping


class Command(BaseCommand):
    help = 'Populates the database with realistic credentials for every role, plus doctors, patients, and mappings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding initial healthcare dataset...'))

        # =========================================================================
        # 1. Role Credentials (One for Every Role)
        # =========================================================================

        # Role 1: Admin / Superuser
        admin_email = 'admin@healthcare.com'
        admin_user, _ = User.objects.get_or_create(
            email=admin_email,
            defaults={'name': 'Healthcare Administrator', 'role': User.ROLE_ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        admin_user.role = User.ROLE_ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('AdminPass123!')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'[Role: Admin] {admin_user.email} (Password: AdminPass123!)'))

        # Role 2: Doctor / Clinician
        doctor_email = 'doctor@healthcare.com'
        doctor_user, _ = User.objects.get_or_create(
            email=doctor_email,
            defaults={'name': 'Dr. Sarah Mitchell', 'role': User.ROLE_DOCTOR},
        )
        doctor_user.role = User.ROLE_DOCTOR
        doctor_user.set_password('DoctorPass123!')
        doctor_user.save()
        self.stdout.write(self.style.SUCCESS(f'[Role: Doctor] {doctor_user.email} (Password: DoctorPass123!)'))

        # Postman demo compatibility
        demo_email = 'doctor.demo@healthcare.com'
        demo_user, _ = User.objects.get_or_create(
            email=demo_email,
            defaults={'name': 'Dr. Demo Clinician', 'role': User.ROLE_DOCTOR},
        )
        demo_user.role = User.ROLE_DOCTOR
        demo_user.set_password('DoctorPass123!')
        demo_user.save()

        # Role 3: Patient User
        patient_email = 'patient@healthcare.com'
        patient_user, _ = User.objects.get_or_create(
            email=patient_email,
            defaults={'name': 'John Smith (Patient)', 'role': User.ROLE_PATIENT},
        )
        patient_user.role = User.ROLE_PATIENT
        patient_user.set_password('PatientPass123!')
        patient_user.save()
        self.stdout.write(self.style.SUCCESS(f'[Role: Patient] {patient_user.email} (Password: PatientPass123!)'))

        # Role 4: Hospital Staff / Receptionist
        staff_email = 'staff@healthcare.com'
        staff_user, _ = User.objects.get_or_create(
            email=staff_email,
            defaults={'name': 'Emma Watson (Front Desk Staff)', 'role': User.ROLE_STAFF, 'is_staff': True},
        )
        staff_user.role = User.ROLE_STAFF
        staff_user.is_staff = True
        staff_user.set_password('StaffPass123!')
        staff_user.save()
        self.stdout.write(self.style.SUCCESS(f'[Role: Staff] {staff_user.email} (Password: StaffPass123!)'))

        # =========================================================================
        # 2. Doctors Directory
        # =========================================================================
        doctors_data = [
            {
                'name': 'Dr. Gregory House',
                'specialization': 'Diagnostic Medicine',
                'license_number': 'MD-HOUSE-001',
                'contact_number': '+1-555-0101',
                'email': 'gregory.house@princetonplainsboro.test',
                'years_of_experience': 20,
                'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital',
            },
            {
                'name': 'Dr. Meredith Grey',
                'specialization': 'General Surgery',
                'license_number': 'MD-GREY-002',
                'contact_number': '+1-555-0102',
                'email': 'meredith.grey@greysloan.test',
                'years_of_experience': 14,
                'hospital_affiliation': 'Grey Sloan Memorial Hospital',
            },
            {
                'name': 'Dr. Stephen Strange',
                'specialization': 'Neurosurgery',
                'license_number': 'MD-STRANGE-003',
                'contact_number': '+1-555-0103',
                'email': 'stephen.strange@metrohealth.test',
                'years_of_experience': 16,
                'hospital_affiliation': 'Metropolitan General Hospital',
            },
            {
                'name': 'Dr. Shaun Murphy',
                'specialization': 'Pediatric Surgery',
                'license_number': 'MD-MURPHY-004',
                'contact_number': '+1-555-0104',
                'email': 'shaun.murphy@stbonaventure.test',
                'years_of_experience': 7,
                'hospital_affiliation': 'St. Bonaventure Hospital',
            },
        ]

        doctors = []
        for doc_info in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                license_number=doc_info['license_number'],
                defaults=doc_info,
            )
            doctors.append(doctor)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Doctor: {doctor.name} - {doctor.specialization}'))

        # =========================================================================
        # 3. Patient Records by Roles
        # =========================================================================

        # Records owned by Clinicians
        clinician_patients_data = [
            {
                'name': 'Sarah Connor',
                'age': 34,
                'gender': 'Female',
                'contact_number': '+1-555-0202',
                'email': 'sarah.c@example.com',
                'address': '10880 Wilshire Blvd, Los Angeles',
                'medical_history': 'Previous right shoulder fracture (healed). No medication allergies.',
            },
            {
                'name': 'Bruce Wayne',
                'age': 38,
                'gender': 'Male',
                'contact_number': '+1-555-0203',
                'email': 'bruce@wayneenterprises.test',
                'address': '1007 Mountain Drive, Gotham',
                'medical_history': 'Multiple contusions and physical trauma history. High physical endurance.',
            },
        ]

        clinician_patients = []
        for user_acc in [demo_user, doctor_user]:
            for p_info in clinician_patients_data:
                patient, created = Patient.objects.get_or_create(
                    name=p_info['name'],
                    created_by=user_acc,
                    defaults=p_info,
                )
                if user_acc == doctor_user:
                    clinician_patients.append(patient)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created Patient: {patient.name} (Owned by: {user_acc.email})'))

        # Record owned by Patient Account (Self Record)
        patient_self_record, p_created = Patient.objects.get_or_create(
            email='patient@healthcare.com',
            created_by=patient_user,
            defaults={
                'name': 'John Smith',
                'age': 45,
                'gender': 'Male',
                'contact_number': '+1-555-0201',
                'address': '742 Evergreen Terrace, Springfield',
                'medical_history': 'Hypertension diagnosed in 2021. Occasional migraines.',
            },
        )
        if p_created:
            self.stdout.write(self.style.SUCCESS(f'Created Patient: {patient_self_record.name} (Owned by: {patient_user.email})'))

        # Record owned by Hospital Staff Account
        staff_patient_record, s_created = Patient.objects.get_or_create(
            email='clara.oswald@example.com',
            created_by=staff_user,
            defaults={
                'name': 'Clara Oswald',
                'age': 28,
                'gender': 'Female',
                'contact_number': '+1-555-0204',
                'address': '221B Baker Street, London',
                'medical_history': 'Routine annual preventive health assessment.',
            },
        )
        if s_created:
            self.stdout.write(self.style.SUCCESS(f'Created Patient: {staff_patient_record.name} (Owned by: {staff_user.email})'))

        # =========================================================================
        # 4. Patient-Doctor Mappings
        # =========================================================================
        mappings_data = [
            (patient_self_record, doctors[0], 'Complex diagnostic review for chronic migraines.'),
            (patient_self_record, doctors[2], 'Neurosurgery consultation for spinal nerve assessment.'),
            (clinician_patients[0] if clinician_patients else patient_self_record, doctors[1], 'Post-orthopedic surgery general physical assessment.'),
            (staff_patient_record, doctors[3], 'Pediatric and family health consultation.'),
        ]

        for pat, doc, notes in mappings_data:
            mapping, created = PatientDoctorMapping.objects.get_or_create(
                patient=pat,
                doctor=doc,
                defaults={'notes': notes},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Mapped: Patient [{pat.name}] -> Doctor [{doc.name}]'))

        self.stdout.write(self.style.SUCCESS('\nSample healthcare data seeding completed successfully with all role credentials!'))
