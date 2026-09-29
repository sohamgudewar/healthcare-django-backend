from django.db import models


class Doctor(models.Model):
    """Model representing a medical practitioner / doctor in the healthcare system."""

    name = models.CharField(
        max_length=255,
        help_text='Full name and title of the doctor (e.g., Dr. Jane Smith).',
    )
    specialization = models.CharField(
        max_length=150,
        help_text='Medical specialty (e.g., Cardiology, Dermatology, Pediatrics).',
    )
    license_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique medical license registration number.',
    )
    contact_number = models.CharField(
        max_length=25,
        help_text='Direct contact phone number.',
    )
    email = models.EmailField(
        unique=True,
        help_text='Official contact email address.',
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text='Total years of clinical medical experience.',
    )
    hospital_affiliation = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Hospital, clinic, or medical center affiliation.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_doctors'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.specialization} (License: {self.license_number})'
