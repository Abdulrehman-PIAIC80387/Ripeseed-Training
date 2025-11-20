from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from licensing.models import LicenseHistory
from licensing.models import LicenseHistory
from common.constants import ActionType


def add_months_to_date(base_date, months):
    return base_date + relativedelta(months=months)


def parse_admin_user(request):
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.username
    return 'System'


def create_license_history(license, action, performed_by, old_values, new_values, notes='', refund_amount=None):
    return LicenseHistory.objects.create(
        license=license,
        action=action,
        performed_by=performed_by,
        old_values=old_values,
        new_values=new_values,
        refund_amount=refund_amount,
        notes=notes
    )
    
    
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
            'refund': float(refund)
        }