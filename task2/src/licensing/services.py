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
    def deactivate_license(license_instance, performed_by):    
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
    
    @staticmethod
    @transaction.atomic
    def increase_seat_capacity(license_instance, seats_to_add=10, performed_by='Admin'):
        new_seat_cap = license_instance.seat_cap + seats_to_add
        license_instance.seat_cap = new_seat_cap
        license_instance.save()
        return license_instance


    @staticmethod
    @transaction.atomic
    def decrease_seat_capacity(license_instance, seats_to_remove=10, performed_by='Admin'):
        new_seat_cap = max(1, license_instance.seat_cap - seats_to_remove)
        license_instance.seat_cap = new_seat_cap
        license_instance.save()
        return license_instance


    @staticmethod
    @transaction.atomic
    def update_seat_price(license_instance, new_price, performed_by='Admin'):
        license_instance.seat_price = new_price
        license_instance.save()
        return license_instance


class RefundService:

    @staticmethod
    def calculate_refund(license_instance):
        history = LicenseHistory.objects.filter(license=license_instance).order_by('created_at')
        renewal = history.filter(action=ActionType.RENEWED).order_by('-created_at').first()
        changes = history.filter(action__in=[ActionType.PRICE_UPDATED, ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED])
       
        if renewal:
            return RefundService._calculate_refund(license_instance)
        
        elif changes.exists():
            return RefundService._calculate_refund_with_changes(license_instance, history)
        
        return RefundService._calculate_refund(license_instance)
    
    
    @staticmethod
    def _calculate_refund(license_instance):
        today = timezone.now().date()
        total_days = (license_instance.end_date - license_instance.start_date).days
        days_used = (today - license_instance.start_date).days
        days_remaining = (license_instance.end_date - today).days
        monthly_cost = license_instance.seat_cap * license_instance.seat_price
        total_cost = (monthly_cost * total_days) / 30
        refund = (total_cost * days_remaining) / total_days
        
        return {
            'total_refund': round(refund,2),
            'scenario': 'Simple Refund No Changes',
            'periods': [{
                'action': 'LICENSE PERIOD',
                'period_start': license_instance.start_date,
                'period_end': license_instance.end_date,
                'seat_cap': license_instance.seat_cap,
                'seat_price': license_instance.seat_price,
                'days_total': total_days,
                'days_used': days_used,
                'days_remaining': days_remaining,
                'monthly_cost': monthly_cost,
                'period_cost': round(total_cost,2),
            }]
        }
    
    @staticmethod
    def _calculate_refund_with_changes(license_instance, history, today):
        periods = []
        total_refund = 0
        period_start = license_instance.start_date
        current_seat_cap = None
        current_seat_price = None
        today = timezone.now().date()
        
        for record in history:
            if record.action == ActionType.CREATED:
                current_seat_cap = record.new_values.get('seat_cap', license_instance.seat_cap)
                current_seat_price = record.new_values.get('seat_price', license_instance.seat_price)
                continue
            
            period_end = record.created_at.date()
            period_data = calculate_period(
                period_start, period_end, current_seat_cap, current_seat_price, 
                today, record.get_action_display()
            )
            periods.append(period_data)
            total_refund += period_data['refund']
            
            if record.action == ActionType.PRICE_UPDATED:
                current_seat_price = record.new_values.get('seat_price')
            elif record.action in [ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED]:
                current_seat_cap = record.new_values.get('seat_cap')
            
            period_start = period_end
        
        if period_start < license_instance.end_date:
            period_data = calculate_period(
                period_start, license_instance.end_date, 
                license_instance.seat_cap, license_instance.seat_price,
                today, 'CURRENT PERIOD'
            )
            periods.append(period_data)
            total_refund += period_data['refund']
        
        return {
            'total_refund': total_refund,
            'scenario': 'Seat Price or Capacity Changed',
            'periods': periods
        }