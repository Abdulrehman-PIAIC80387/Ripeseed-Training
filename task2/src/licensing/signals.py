from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from django.core.exceptions import ValidationError
from licensing import models

@receiver(post_save, sender=models.License)
def track_license_creation(sender, instance, created, **kwargs):

    models.LicenseHistory.objects.create(license=instance,action=models.LicenseHistory.ActionType.CREATED,performed_by='system',old_values={},new_values={
    'start_date': instance.start_date.isoformat(),
    'end_date': instance.end_date.isoformat(),
    'seat_cap': instance.seat_cap,
    'seat_price': str(instance.seat_price),
    'status': instance.status
    },
    notes=f"License created for {instance.organization.name}"
    )
