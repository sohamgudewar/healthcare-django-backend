from django.db import models


class PatientDoctorMapping(models.Model):
    """
    Mapping entity representing the clinical association between a Patient and a Doctor.
    Enforces a unique constraint so a doctor cannot be mapped multiple times to the same patient.
    """

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text='The patient who is assigned to the doctor.',
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text='The doctor assigned to the patient.',
    )
    assigned_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the doctor was assigned to the patient.',
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text='Consultation notes, assignment reason, or medical remarks.',
    )

    class Meta:
        db_table = 'healthcare_patient_doctor_mappings'
        verbose_name = 'Patient-Doctor Mapping'
        verbose_name_plural = 'Patient-Doctor Mappings'
        ordering = ['-assigned_date']
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'doctor'],
                name='unique_patient_doctor_mapping',
            )
        ]

    def __str__(self):
        return f'Patient [{self.patient.name}] assigned to Doctor [{self.doctor.name}]'
