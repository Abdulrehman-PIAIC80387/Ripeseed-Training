from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_date_range(start_date, end_date):
    if end_date and start_date and end_date <= start_date:
        raise ValidationError({
            'end_date': _('End date must be after start date.')
        })