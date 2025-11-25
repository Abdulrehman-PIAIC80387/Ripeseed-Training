from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from common.constants import ActionType
from licensing.validators import validate_date_range
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    class Meta:
        abstract = True


class Organization(BaseModel):
    name = models.CharField(
        _("Organization Name"),
        max_length=255,
        help_text=_("Official name of the organization")
    )
    email = models.EmailField(
        _("Email Address"),
        unique=True,
        help_text=_("Primary contact email")
    )
    address = models.TextField(
        _("Address"),
        max_length=500,
        help_text=_("Physical address of the organization")
    )
    contact_number = PhoneNumberField(
        _("Contact Number"),
        help_text=_("Primary contact phone number")
    )

    class Meta:
        db_table = 'organizations'
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.name


class License(BaseModel):
    organization = models.OneToOneField(
        Organization,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name='license',
        help_text=_("Organization this license belongs to")
    )
    start_date = models.DateField(
        _("Start Date"),
        help_text=_("License activation date")
    )
    end_date = models.DateField(
        _("End Date"),
        help_text=_("License expiration date")
    )
    seat_cap = models.PositiveIntegerField(
        _("Seat Capacity"),
        validators=[MinValueValidator(1)],
        help_text=_("Maximum number of seats/users allowed")
    )
    seat_price = models.DecimalField(
        _("Seat Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Price per seat per month (USD)")
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether this license is currently active")
    )

    class Meta:
        db_table = 'licenses'
        ordering = ['-created_at']
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.organization.name}"

    def clean(self):
        super().clean()
        validate_date_range(self.start_date, self.end_date)


class LicenseHistory(BaseModel):
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("License"),
        db_index=True,
        help_text=_("Associated license")
    )
    action = models.CharField(
        _("Action Type"),
        max_length=50,
        choices=ActionType.choices,
        db_index=True,
        help_text=_("Type of action performed")
    )
    action_date = models.DateField(  
        _("Action Date"),
        default=timezone.now,
        help_text=_("Date when action was performed (for testing purposes)")
    )
    performed_by = models.CharField(
        _("Performed By"),
        max_length=255,
        help_text=_("User or system that performed the action")
    )
    old_values = models.JSONField(
        _("Old Values"),
        default=dict,
        blank=True,
        help_text=_("Previous values before change")
    )
    new_values = models.JSONField(
        _("New Values"),
        default=dict,
        blank=True,
        help_text=_("New values after change")
    )
    refund_amount = models.DecimalField(
        _("Refund Amount"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Refund amount for deactivation (USD)")
    )
    notes = models.TextField(
        _("Notes"),
        blank=True,
        help_text=_("Additional notes or context")
    )

    class Meta:
        db_table = 'license_history'
        ordering = ['action_date', 'created_at']  
        verbose_name = _('License History')
        verbose_name_plural = _('License Histories')
        indexes = [
            models.Index(fields=['license', 'action_date']), 
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.license.organization.name} - {self.get_action_display()} on {self.action_date}"
    
    
    
    
