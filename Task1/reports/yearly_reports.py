from datetime import datetime


def print_yearly_report(stats):
    if stats.highest_temp is not None:
        date = datetime.strptime(stats.highest_temp_date, '%Y-%m-%d')
        month = date.strftime("%B")
        day = date.day
        print(f"Highest: {int(stats.highest_temp)}C on {month} {day}")
    
    if stats.lowest_temp is not None:
        date = datetime.strptime(stats.lowest_temp_date, '%Y-%m-%d')
        month = date.strftime("%B")
        day = date.day
        print(f"Lowest: {int(stats.lowest_temp):02d}C on {month} {day}")
    
    if stats.most_humid is not None:
        date = datetime.strptime(stats.most_humid_date, '%Y-%m-%d')
        month = date.strftime("%B")
        day = date.day
        print(f"Humidity: {stats.most_humid}% on {month} {day}")