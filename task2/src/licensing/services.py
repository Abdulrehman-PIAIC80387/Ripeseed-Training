from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from licensing.models import License, LicenseHistory
from common.constants import *
from common.utils import *


class LicenseService:

    @staticmethod
    @transaction.atomic
    def renew_license(license_instance, performed_by):
        today = timezone.now().date()
        
        old_start_date = license_instance.start_date
        old_end_date = license_instance.end_date
        
        new_start_date = today
        new_end_date = add_months_to_date(new_start_date, reniew_months)
        
        license_instance.start_date = new_start_date
        license_instance.end_date = new_end_date
        license_instance.save()
        
        create_license_history(
            license=license_instance,
            action=ActionType.RENEWED,
            performed_by=performed_by,
            old_values={
                'start_date': str(old_start_date),
                'end_date': str(old_end_date)
            },
            new_values={
                'start_date': str(new_start_date),
                'end_date': str(new_end_date)
            },
            notes=f"License renewed for {reniew_months} months from today"
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
        days_remaining = get_license_days_remaining(license_instance)
        total_days = get_license_duration_days(license_instance)
        total_cost = get_license_total_cost(license_instance)
        refund_ratio = Decimal(str(days_remaining)) / Decimal(str(total_days)) 
        refund_amount = total_cost * refund_ratio
        return refund_amount,total_days,days_remaining