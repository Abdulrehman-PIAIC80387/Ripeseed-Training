from django.db.models.signals import post_save
from django.dispatch import receiver

from licensing.models import License
from common.constants import ActionType
from common.utils import create_license_history


@receiver(post_save, sender=License)
def track_license_creation(sender, instance, created, **kwargs):
    if created:
        create_license_history(
            license=instance,
            action=ActionType.CREATED,
            performed_by='System',
            old_values={},
            new_values={
                'organization': instance.organization.name,
                'start_date': str(instance.start_date),
                'end_date': str(instance.end_date),
                'seat_cap': instance.seat_cap,
                'seat_price': float(instance.seat_price),
            },
            notes=f"New license created for {instance.organization.name}"
        )