from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from licensing.models import LicenseHistory


def calculate_prorated_refund(total_cost, days_remaining, total_days):
    refund_ratio = Decimal(str(days_remaining)) / Decimal(str(total_days)) #remove convertions
    refund_amount = total_cost * refund_ratio
    return refund_amount(Decimal('0.01'), rounding=ROUND_HALF_UP) #remove convertions


def add_months_to_date(base_date, months):
    return base_date + relativedelta(months=months)


def format_currency(amount):
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"


def parse_admin_user(request):
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.username
    return 'System'


def get_license_duration_days(license_instance):
    if license_instance.start_date and license_instance.end_date:
        return (license_instance.end_date - license_instance.start_date).days
    return 0


def get_license_monthly_cost(license_instance):
    return license_instance.seat_cap * license_instance.seat_price


def get_license_total_cost(license_instance):
    months = get_license_duration_days(license_instance) / 30.0
    return get_license_monthly_cost(license_instance) * Decimal(str(months)) # remove convertions


def get_license_days_remaining(license_instance):
    today = timezone.now().date()
    if license_instance.end_date and license_instance.end_date > today:
        return (license_instance.end_date - today).days
    return 0


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