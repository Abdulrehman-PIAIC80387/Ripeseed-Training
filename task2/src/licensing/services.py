from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from licensing.models import License, LicenseHistory
from common.constants import ActionType
from common.utils import *

class LicenseService:

    @staticmethod
    @transaction.atomic
    def renew_license(license_instance, months=12, performed_by='Admin'):
        old_end_date = license_instance.end_date 
        new_end_date = add_months_to_date(old_end_date, months)
        license_instance.end_date = new_end_date
        license_instance.save()
        
        create_license_history(
            license=license_instance,
            action=ActionType.RENEWED,
            performed_by=performed_by,
            old_values={'end_date': str(old_end_date)},
            new_values={'end_date': str(new_end_date)},
            notes=f"License renewed for {months} months"
        )
        
        return license_instance

    @staticmethod
    @transaction.atomic
    def deactivate_license(license_instance, performed_by='Admin'):    
        refund_amount = RefundService.calculate_refund(license_instance)
        license_instance.is_active = False
        license_instance.save()
        
        create_license_history(
            license=license_instance,
            action=ActionType.DEACTIVATED,
            performed_by=performed_by,
            old_values={'is_active': True},
            new_values={'is_active': False},
            refund_amount=refund_amount,
            notes=f"License deactivated. Refund: ${refund_amount}"
        )
        
        return license_instance, refund_amount


class RefundService:

    @staticmethod
    def calculate_refund(license_instance):
        today = timezone.now().date()
        days_remaining = (license_instance.end_date - today).days
        total_days = (license_instance.end_date - license_instance.start_date).days
        total_cost = get_license_total_cost(license_instance)
        
        return calculate_prorated_refund(total_cost, days_remaining, total_days)