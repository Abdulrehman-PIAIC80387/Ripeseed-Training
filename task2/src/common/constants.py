from django.db import models

class LicenseStatus(models.TextChoices):
    ACTIVATE = "A", "Activate"
    DEACTIVATE = "D", "Deactivate"

class ActionType(models.TextChoices):
        CREATED = 'CR', 'Created'
        RENEWED = 'RN', 'Renewed'
        SEAT_INCREASED = 'SI', 'Seat Increased'
        SEAT_DECREASED = 'SD', 'Seat Decreased'
        PRICE_UPDATED = 'PU', 'Price Updated'
        DEACTIVATED = 'DA', 'Deactivated'
        SUSPENDED = 'SP', 'Suspended'
        REACTIVATED = 'RA', 'Reactivated'