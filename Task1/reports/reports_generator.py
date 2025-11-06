from datetime import datetime
from utils.helpers import fetch_day_string, fetch_month_string


class Reports:
    
    def print_bar_chart(self, readings):
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


    def print_bar_chart_single_liner(self, readings):
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



    def print_monthly_averages_report(self, averages): 
        if averages.avg_highest_temp is not None:
            print(f"Highest Average: {round(averages.avg_highest_temp,2)}C ")
        if averages.avg_lowest_temp is not None:
            print(f"Lowest Average: {round(averages.avg_lowest_temp,2)}C ")
        if averages.avg_mean_humidity is not None:
            print(f"Average Mean Humidity: {round(averages.avg_mean_humidity,2)}%")



    def print_yearly_report(self, stats):
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