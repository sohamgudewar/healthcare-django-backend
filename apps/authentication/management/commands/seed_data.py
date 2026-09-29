from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.mappings.models import PatientDoctorMapping


class Command(BaseCommand):
    help = 'Populates the database with realistic sample users, doctors, patients, and mappings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding initial healthcare dataset...'))

        # 1. Create Demo Admin User
        admin_email = 'admin@healthcare.com'
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                name='Healthcare Administrator',
                password='AdminPass123!',
            )
            self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_user.email} (Password: AdminPass123!)'))
        else:
            admin_user = User.objects.get(email=admin_email)

        # 2. Create Demo Doctor User
        user_email = 'doctor.demo@healthcare.com'
        if not User.objects.filter(email=user_email).exists():
            demo_user = User.objects.create_user(
                email=user_email,
                name='Dr. Demo Clinician',
                password='DoctorPass123!',
            )
            self.stdout.write(self.style.SUCCESS(f'Created Clinician User: {demo_user.email} (Password: DoctorPass123!)'))
        else:
            demo_user = User.objects.get(email=user_email)

        # 3. Create Doctors
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

        # 4. Create Patients owned by demo_user
        patients_data = [
            {
                'name': 'John Smith',
                'age': 45,
                'gender': 'Male',
                'contact_number': '+1-555-0201',
                'email': 'john.smith@example.com',
                'address': '742 Evergreen Terrace, Springfield',
                'medical_history': 'Hypertension diagnosed in 2021. Occasional migraines.',
            },
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

        patients = []
        for p_info in patients_data:
            patient, created = Patient.objects.get_or_create(
                name=p_info['name'],
                created_by=demo_user,
                defaults=p_info,
            )
            patients.append(patient)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Patient: {patient.name} (Owned by: {demo_user.email})'))

        # 5. Create Sample Mappings
        sample_mappings = [
            (patients[0], doctors[0], 'Complex diagnostic review for chronic migraines.'),
            (patients[0], doctors[2], 'Neurosurgery consultation for spinal nerve assessment.'),
            (patients[1], doctors[1], 'Post-orthopedic surgery general physical assessment.'),
        ]

        for pat, doc, notes in sample_mappings:
            mapping, created = PatientDoctorMapping.objects.get_or_create(
                patient=pat,
                doctor=doc,
                defaults={'notes': notes},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Mapped: Patient [{pat.name}] -> Doctor [{doc.name}]'))

        self.stdout.write(self.style.SUCCESS('\nSample healthcare data seeding completed successfully!'))
