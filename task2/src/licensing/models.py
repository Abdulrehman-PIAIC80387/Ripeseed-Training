from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import Decimal
from common.constants import *

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class Organization(BaseModel):
    name = models.CharField(_("Name"),max_length=50)
    email = models.EmailField(_("Email"), unique=True, null=False)
    address = models.CharField(_("address"),max_length=100)
    contact_number = PhoneNumberField()


class License(BaseModel):
    organization = models.OneToOneField("Organization", verbose_name=_("licence Attached"), on_delete=models.CASCADE)
    start_date = models.DateField(_("Start Date"), auto_now=False, auto_now_add=False)
    end_date = models.DateField(_("End Date"), auto_now=False, auto_now_add=False)
    seat_cap = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Maximum number of seats/users")
    )
    seat_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Price per seat per month in USD")
    )
    is_active = models.BooleanField(_("Activate license"))
    class Meta:
        db_table = 'licenses'
        ordering = ['-created_at']
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='valid_date_range'
            ),
            models.CheckConstraint(
                check=models.Q(seats_used__lte=models.F('seat_cap')),
                name='seats_within_capacity'
            ),
        ]

    def _str_(self):
        return f"{self.organization.name} - License ({self.status})"

    def clean(self):
        super().clean()
        
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _('End date must be after start date.')
            })
        
        if self.seats_used > self.seat_cap:
            raise ValidationError({
                'seats_used': _('Seats used cannot exceed seat capacity.')
            })
        
        if self.is_active and self.end_date:
            today = timezone.now().date()
            if today > self.end_date:
                self.status = self.LicenseStatus.EXPIRED
                self.is_active = False


class LicenseHistory(BaseModel):

    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='history',
        db_index=True,
        help_text=_("Associated license")
    )
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        db_index=True,
        help_text=_("Type of action performed")
    )
    performed_by = models.CharField(
        max_length=255,
        help_text=_("User or system that performed the action")
    )
    old_values = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Previous values before change")
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("New values after change")
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Refund amount for deactivation")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes or context")
    )

    class Meta:
        db_table = 'license_history'
        ordering = ['-created_at']
        verbose_name = _('License History')
        verbose_name_plural = _('License Histories')

    def _str_(self):
        return f"{self.license.organization.name} - {self.action} at {self.created_at}"