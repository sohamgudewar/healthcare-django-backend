from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Patient(models.Model):
    """Model representing a patient registered by an authenticated user."""

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    name = models.CharField(
        max_length=255,
        help_text='Full legal name of the patient.',
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth (YYYY-MM-DD).',
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text='Age of the patient in years.',
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Other',
        help_text='Gender of the patient.',
    )
    contact_number = models.CharField(
        max_length=25,
        help_text='Contact phone number.',
    )
    email = models.EmailField(
        blank=True,
        default='',
        help_text='Optional email address of the patient.',
    )
    address = models.TextField(
        blank=True,
        default='',
        help_text='Residential address.',
    )
    medical_history = models.TextField(
        blank=True,
        default='',
        help_text='Brief medical history or existing conditions.',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        help_text='The authenticated user who registered this patient record.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'healthcare_patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} (Age: {self.age}, ID: {self.id})'
