from datetime import datetime
from utils.helpers import fetch_day_string, fetch_month_string


def print_bar_chart(readings):
    if len(readings) == 0:
        return
    
    first_date = datetime.strptime(readings[0].date, '%Y-%m-%d')
    month_name = first_date.strftime("%B")
    year = first_date.year
    sorted_readings = sorted(readings, key=lambda r: datetime.strptime(r.date, '%Y-%m-%d').date())
    red = '\033[91m'
    blue = '\033[94m'
    reset = '\033[0m'
    
    for reading in sorted_readings:
        date = reading.date
        day = fetch_day_string(date)
        
        if reading.max_temp is not None:
            temp = int(reading.max_temp)
            bar = red + '+' * temp + reset
            print(f"{day:02d} {bar} {temp}C")
        
        if reading.min_temp is not None:
            temp = int(reading.min_temp)
            bar = blue + '+' * temp + reset
            print(f"{day:02d} {bar} {temp}C")


def print_bar_chart_single_liner(readings):
    if len(readings) == 0:
        return

    first_date = datetime.strptime(readings[0].date, '%Y-%m-%d')
    month_name = first_date.strftime("%B")
    year = first_date.year
    sorted_readings = sorted(readings, key=lambda r: datetime.strptime(r.date, '%Y-%m-%d').date())

    red = '\033[91m'
    blue = '\033[94m'
    reset = '\033[0m'
    
    for reading in sorted_readings:
        date = reading.date
        day = fetch_day_string(date)
        
        if reading.max_temp is not None and reading.min_temp is not None:
            temp_max = int(reading.max_temp)
            temp_low = int(reading.min_temp)
            bar = blue + '+' * temp_low + reset + red + '+' * (temp_max - temp_low) + reset
            print(f"{day:02d} {bar} {temp_low}C - {temp_max}C")