from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from licensing.models import License, LicenseHistory
from common.constants import *
from common.utils import *
from copy import copy
 
class LicenseService:

    @staticmethod
    @transaction.atomic
    def renew_license(license_instance, performed_by, action_date=None):
        if license_instance.is_active and license_instance.end_date > timezone.now().date():
            raise ValidationError("Cannot renew an active license that hasn't expired yet.")
            
        if action_date is None:
            action_date = timezone.now().date()
            
        old_start_date = license_instance.start_date
        old_end_date = license_instance.end_date
        new_start_date = action_date
        new_end_date = add_months_to_date(new_start_date, 12)
        
        license_instance.start_date = new_start_date
        license_instance.end_date = new_end_date
        license_instance.is_active = True
        license_instance.save()
        
        create_license_history(
            license=license_instance,
            action=ActionType.RENEWED,
            performed_by=performed_by,
            action_date=action_date,
            old_values={
                'start_date': str(old_start_date),
                'end_date': str(old_end_date)
            },
            new_values={
                'start_date': str(new_start_date),
                'end_date': str(new_end_date)
            },
            notes=f"License renewed for 12 months from {action_date}"
        )
        
        return license_instance


    @staticmethod
    @transaction.atomic
    def deactivate_license(license_instance, performed_by, action_date=None):
        if action_date is None:
            action_date = timezone.now().date()
            
        refund_data = RefundService.calculate_refund(license_instance, action_date)
        license_instance.is_active = False
        license_instance.save()
        
        create_license_history(
            license=license_instance,
            action=ActionType.DEACTIVATED,
            performed_by=performed_by,
            action_date=action_date,
            old_values={'is_active': True},
            new_values={'is_active': False},
            refund_amount=refund_data['net_amount'],
            notes=f"License deactivated on {action_date}. Net: ${refund_data['net_amount']}"
        )
        
        return license_instance, refund_data


class RefundService:
    @staticmethod
    def calculate_refund(license_instance, action_date):
        history = LicenseHistory.objects.filter(license=license_instance).order_by('action_date')
        renewal = history.filter(action=ActionType.RENEWED).order_by('-action_date').first()
        changes = history.filter(action__in=[ActionType.PRICE_UPDATED, ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED, ActionType.PRICE_AND_SEAT_UPDATED])
        
        if renewal and renewal.action_date >= license_instance.start_date:
            return RefundService._calculate_after_renewal(license_instance, history, renewal, action_date)
        if changes.exists():
            return RefundService._calculate_with_changes(license_instance, history, action_date)
        return RefundService._calculate_simple(license_instance, action_date)
    
    
    @staticmethod
    def _calculate_simple(license_instance, action_date):
        total_days, days_used, days_remaining = calculate_days(license_instance.start_date, license_instance.end_date, action_date)
        total_cost = get_total_cost(license_instance)
        refund = (total_cost * days_remaining) / total_days if days_remaining > 0 else 0
        
        period = create_period('LICENSE PERIOD', license_instance.start_date, license_instance.end_date,
                             license_instance.seat_cap, license_instance.seat_price, 
                             total_days, days_used, days_remaining, total_cost, refund)
        
        return {
            'total_cost': round(total_cost, 2), 'total_refund': round(refund, 2), 'total_owed': 0.00,
            'net_amount': round(refund, 2), 'scenario': 'Simple - No Changes', 'action_date': action_date,
            'periods': [period]
        }
    
    
    @staticmethod
    def _calculate_with_changes(license_instance, history, action_date):
        periods, total_refund, total_owed = [], Decimal('0'), Decimal('0')
        creation_record = history.filter(action=ActionType.CREATED).first()
        original_seat_cap = creation_record.new_values.get('seat_cap') if creation_record else license_instance.seat_cap
        original_seat_price = Decimal(str(creation_record.new_values.get('seat_price'))) if creation_record else license_instance.seat_price
    
        if (license_instance.seat_cap == original_seat_cap and license_instance.seat_price == original_seat_price):
            total_days, days_used, days_remaining = calculate_days(license_instance.start_date, license_instance.end_date, action_date)
            total_cost = get_total_cost(license_instance)
            refund = (total_cost * days_remaining) / total_days if days_remaining > 0 else 0
            
            period = create_period('Reverted to Original - No Net Change', license_instance.start_date, license_instance.end_date,
                                 license_instance.seat_cap, license_instance.seat_price, 
                                 total_days, days_used, days_remaining, total_cost, refund)
            
            return {
                'total_cost': round(total_cost, 2), 'total_refund': round(refund, 2), 'total_owed': 0.00,
                'net_amount': round(refund, 2), 'scenario': 'Reverted to Original', 'action_date': action_date,
                'periods': [period]
            }
        
        current_seat_cap, current_seat_price = license_instance.seat_cap, license_instance.seat_price
        
        for record in history.order_by('action_date'):
            if record.action == ActionType.CREATED:
                current_seat_cap, current_seat_price = record.new_values.get('seat_cap'), Decimal(str(record.new_values.get('seat_price')))
                continue
            
            if record.action not in [ActionType.PRICE_UPDATED, ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED, ActionType.PRICE_AND_SEAT_UPDATED]:
                continue
                
            period_data = RefundService._process_record(record.action_date, license_instance.end_date, current_seat_cap, current_seat_price, action_date, record)
            periods.append(period_data)
            total_refund += Decimal(str(period_data['refund']))
            total_owed += Decimal(str(period_data['owed']))
            
            if record.action == ActionType.PRICE_UPDATED:
                current_seat_price = Decimal(str(record.new_values.get('seat_price')))
            elif record.action in [ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED]:
                current_seat_cap = record.new_values.get('seat_cap')
            elif record.action == ActionType.PRICE_AND_SEAT_UPDATED:
                current_seat_price = Decimal(str(record.new_values.get('seat_price')))
                current_seat_cap = record.new_values.get('seat_cap')
        
        return {
            'total_cost': round(get_total_cost(license_instance), 2), 'total_refund': round(total_refund, 2),
            'total_owed': round(total_owed, 2), 'net_amount': round(total_refund - total_owed, 2),
            'scenario': 'With Price/Capacity Changes', 'action_date': action_date, 'periods': periods
        }
    
    
    @staticmethod
    def _process_record(period_start, period_end, seat_cap, seat_price, action_date, record, label=None):
        total_days, days_used, days_remaining = calculate_days(period_start, period_end, action_date)
        refund = owed = 0
        display_seat_cap = seat_cap
        display_seat_price = seat_price
        
        if record and record.action == ActionType.PRICE_UPDATED:
            old_price, new_price = Decimal(str(record.old_values.get('seat_price'))), Decimal(str(record.new_values.get('seat_price')))
            display_seat_price = new_price
            if new_price > old_price:
                price_diff = new_price - old_price
                owed = calculate_cost(seat_cap, price_diff, days_remaining) if days_remaining > 0 else 0
                action_label = f"Price Increased (${old_price} -> ${new_price}) - Client Owes"
            else:
                price_diff = old_price - new_price
                refund = calculate_cost(seat_cap, price_diff, days_remaining) if days_remaining > 0 else 0
                action_label = f"Price Decreased (${old_price} -> ${new_price}) - Refund"
        elif record and record.action == ActionType.PRICE_AND_SEAT_UPDATED:
            old_price, new_price = Decimal(str(record.old_values.get('seat_price'))), Decimal(str(record.new_values.get('seat_price')))
            old_seats, new_seats = record.old_values.get('seat_cap'), record.new_values.get('seat_cap')
            display_seat_cap = new_seats
            display_seat_price = new_price
            
            if new_price > old_price:
                price_diff = new_price - old_price
                price_owed = calculate_cost(new_seats, price_diff, days_remaining) if days_remaining > 0 else 0
            else:
                price_diff = old_price - new_price
                price_refund = calculate_cost(new_seats, price_diff, days_remaining) if days_remaining > 0 else 0
            
            if new_seats > old_seats:
                seat_diff = new_seats - old_seats
                seat_owed = calculate_cost(seat_diff, new_price, days_remaining) if days_remaining > 0 else 0
            else:
                seat_diff = old_seats - new_seats
                seat_refund = calculate_cost(seat_diff, new_price, days_remaining) if days_remaining > 0 else 0
            
            owed = (price_owed if 'price_owed' in locals() else 0) + (seat_owed if 'seat_owed' in locals() else 0)
            refund = (price_refund if 'price_refund' in locals() else 0) + (seat_refund if 'seat_refund' in locals() else 0)
            action_label = f"Price (${old_price} -> ${new_price}) and Seats ({old_seats} -> {new_seats}) Updated"
        elif record and record.action in [ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED]:
            old_seats, new_seats = record.old_values.get('seat_cap'), record.new_values.get('seat_cap')
            display_seat_cap = new_seats
            if new_seats > old_seats:
                seat_diff = new_seats - old_seats
                owed = calculate_cost(seat_diff, seat_price, days_remaining) if days_remaining > 0 else 0
                action_label = f"Seats Increased ({old_seats} -> {new_seats})"
            else:
                seat_diff = old_seats - new_seats
                refund = calculate_cost(seat_diff, seat_price, days_remaining) if days_remaining > 0 else 0
                action_label = f"Seats Decreased ({old_seats} -> {new_seats})"
        else:
            period_cost = calculate_cost(seat_cap, seat_price, total_days)
            refund = (period_cost * days_remaining) / total_days if days_remaining > 0 else 0
            action_label = label or (get_action_label(record) if record else "Period")
        
        period_cost = calculate_cost(display_seat_cap, display_seat_price, total_days)
        return create_period(action_label, period_start, period_end, display_seat_cap, display_seat_price, total_days, days_used, days_remaining, period_cost, refund, owed)
    
    
    @staticmethod
    def _calculate_after_renewal(license_instance, history, renewal, action_date):
        post_renewal_changes = history.filter(action_date__gt=renewal.action_date, action__in=[ActionType.PRICE_UPDATED, ActionType.SEAT_INCREASED, ActionType.SEAT_DECREASED, ActionType.PRICE_AND_SEAT_UPDATED])
        
        if not post_renewal_changes.exists():
            modified_license = copy(license_instance)
            modified_license.start_date = renewal.action_date
            return RefundService._calculate_simple(modified_license, action_date)
        
        modified_license = copy(license_instance)
        modified_license.start_date = renewal.action_date
        post_renewal_history = history.filter(action_date__gte=renewal.action_date)
        return RefundService._calculate_with_changes(modified_license, post_renewal_history, action_date)