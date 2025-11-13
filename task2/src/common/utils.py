from time import timezone

def is_expired(end_date):
    return timezone.now().date() > end_date


def days_remaining(date):
    delta = send_date - timezone.now().date()
    return max(0, delta.days)


def total_duration_days(start_date):
        return (end_date - start_date).days