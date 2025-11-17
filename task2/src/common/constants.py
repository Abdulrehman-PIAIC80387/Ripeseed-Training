from django.db import models
from django.utils.translation import gettext_lazy as _


class ActionType(models.TextChoices):
    CREATED = 'CREATED', _('License Created')
    RENEWED = 'RENEWED', _('License Renewed')
    SEAT_INCREASED = 'SEAT_INCREASED', _('Seats Increased')
    SEAT_DECREASED = 'SEAT_DECREASED', _('Seats Decreased')
    PRICE_UPDATED = 'PRICE_UPDATED', _('Price Updated')
    ACTIVATED = 'ACTIVATED', _('License Activated')
    DEACTIVATED = 'DEACTIVATED', _('License Deactivated')