from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from licensing.models import LicenseHistory
from licensing.models import LicenseHistory
from common.constants import ActionType
from licensing.models import LicenseHistory
from decimal import Decimal
from common.constants import ActionType


def add_months_to_date(base_date, months):
    return base_date + relativedelta(months=months)


def parse_admin_user(request):
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.username
    return 'System'


def create_license_history(license, action, performed_by, old_values, new_values, notes='', refund_amount=None, action_date=None):
    if action_date is None:
        action_date = timezone.now().date()
    
    return LicenseHistory.objects.create(
        license=license,
        action=action,
        action_date=action_date,  
        performed_by=performed_by,
        old_values=old_values,
        new_values=new_values,
        refund_amount=refund_amount,
        notes=notes
    )


def get_total_cost(license_instance):
    total_days = (license_instance.end_date - license_instance.start_date).days
    monthly_cost = license_instance.seat_cap * license_instance.seat_price
    total_cost = (monthly_cost * total_days) / 30  
    return round(total_cost,2)
    
def calculate_period(period_start, period_end, seat_cap, seat_price, today, action_label):
        days_total = (period_end - period_start).days
        monthly_cost = seat_cap * seat_price
        period_cost = (monthly_cost * days_total) / 30
        days_used = (today - period_start).days
        days_remaining = (period_end - today).days
    
        if days_total == 0:
            refund = 0
        else:
            refund = (period_cost * days_remaining) / days_total
            refund = float(round(refund,2))
            period_cost = float(round(period_cost,2))
        
        return {
            'action': action_label,
            'period_start': period_start,
            'period_end': period_end,
            'seat_cap': seat_cap,
            'seat_price': seat_price,
            'days_total': days_total,
            'days_used': days_used,
            'days_remaining': days_remaining,
            'monthly_cost': monthly_cost,
            'period_cost': period_cost,
            'refund': refund
        }
        
def calculate_days(start_date, end_date, action_date):
    total_days = (end_date - start_date).days
    days_used = (action_date - start_date).days if action_date > start_date else 0
    days_remaining = (end_date - action_date).days if action_date < end_date else 0
    return total_days, days_used, days_remaining


def calculate_cost(seat_cap, seat_price, days):
    monthly_cost = Decimal(str(seat_cap)) * Decimal(str(seat_price))
    return (monthly_cost * days) / 30


def get_total_cost(license_instance):
    total_days = (license_instance.end_date - license_instance.start_date).days
    return calculate_cost(license_instance.seat_cap, license_instance.seat_price, total_days)


def create_period(action, period_start, period_end, seat_cap, seat_price,days_total, days_used, days_remaining, period_cost, refund=0, owed=0):
    return {
        'action': action,
        'period_start': period_start,
        'period_end': period_end,
        'seat_cap': seat_cap,
        'seat_price': float(seat_price),
        'days_total': days_total,
        'days_used': days_used,
        'days_remaining': days_remaining,
        'period_cost': round(float(period_cost), 2),
        'refund': round(float(refund), 2),
        'owed': round(float(owed), 2)
    }

def get_action_label(record):
    if record.action == ActionType.SEAT_INCREASED:
        old_seats = record.old_values.get('seat_cap')
        new_seats = record.new_values.get('seat_cap')
        return f"Seats Increased ({old_seats} -> {new_seats})"
    elif record.action == ActionType.SEAT_DECREASED:
        old_seats = record.old_values.get('seat_cap')
        new_seats = record.new_values.get('seat_cap')
        return f"Seats Decreased ({old_seats} -> {new_seats})"
    return record.get_action_display()