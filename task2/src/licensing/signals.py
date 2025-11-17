from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from licensing.models import License, LicenseHistory
from common.constants import ActionType


@receiver(pre_save, sender=License)
def store_old_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = License.objects.get(pk=instance.pk)
            instance._old_seat_cap = old_instance.seat_cap
            instance._old_seat_price = old_instance.seat_price
            instance._performed_by = getattr(instance, '_performed_by', 'Admin')
        except License.DoesNotExist:
            pass


@receiver(post_save, sender=License)
def track_license_changes(sender, instance, created, **kwargs):
    if created:
        LicenseHistory.objects.create(
            license=instance,
            action=ActionType.CREATED,
            performed_by='System',
            new_values={
                'organization': instance.organization.name,
                'start_date': str(instance.start_date),
                'end_date': str(instance.end_date),
                'seat_cap': instance.seat_cap,
                'seat_price': float(instance.seat_price),
            },
            notes=f"New license created for {instance.organization.name}"
        )
    
    old_seat_cap = getattr(instance, '_old_seat_cap', None)
    old_seat_price = getattr(instance, '_old_seat_price', None)
    performed_by = getattr(instance, '_performed_by', 'Admin')
    
    if old_seat_cap is not None and old_seat_cap != instance.seat_cap:
        action = ActionType.SEAT_INCREASED if instance.seat_cap > old_seat_cap else ActionType.SEAT_DECREASED
        
        LicenseHistory.objects.create(
            license=instance,
            action=action,
            performed_by=performed_by,
            old_values={'seat_cap': old_seat_cap},
            new_values={'seat_cap': instance.seat_cap},
            notes=f"Seat capacity changed from {old_seat_cap} to {instance.seat_cap}"
        )
    
    if old_seat_price is not None and old_seat_price != instance.seat_price:
        LicenseHistory.objects.create(
            license=instance,
            action=ActionType.PRICE_UPDATED,
            performed_by=performed_by,
            old_values={'seat_price': float(old_seat_price)},
            new_values={'seat_price': float(instance.seat_price)},
            notes=f"Seat price changed from ${old_seat_price} to ${instance.seat_price}"
        )