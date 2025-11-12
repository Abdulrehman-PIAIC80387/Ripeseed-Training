from datetime import datetime
from utils.helpers import fetch_day_string, fetch_month_string


class Reports:
    
    def __init__(self):
        self.red = '\033[91m'
        self.blue = '\033[94m'
        self.reset = '\033[0m'
    
    def print_bar_chart(self, readings):
        for reading in readings:  
            day = reading.date.day
            temp = reading.max_temp
            bar = self.red + '+' * temp + self.reset
            print(f"{day:02d} {bar} {temp}C")
            temp = reading.min_temp
            bar = self.blue + '+' * temp + self.reset
            print(f"{day:02d} {bar} {temp}C")


    def print_bar_chart_single_liner(self, readings):
        for reading in readings:  
            day = reading.date.day
            temp_max = reading.max_temp
            temp_low = reading.min_temp
            bar = self.blue + '+' * temp_low + self.reset + self.red + '+' * temp_max + self.reset
            print(f"{day:02d} {bar} {temp_low}C - {temp_max}C")


    def print_monthly_averages_report(self, averages): 
        print(f"Highest Average: {averages.avg_highest_temp}C ")
        print(f"Lowest Average: {averages.avg_lowest_temp}C ")
        print(f"Average Mean Humidity: {averages.avg_mean_humidity}%")


    def print_yearly_report(self, stats):
        month = stats.highest_temp_date.strftime("%B")
        day = stats.highest_temp_date.day
        print(f"Highest: {stats.highest_temp}C on {month} {day}")
        
        month = stats.lowest_temp_date.strftime("%B")
        day = stats.lowest_temp_date.day
        print(f"Lowest: {stats.lowest_temp:02d}C on {month} {day}")
        
        month = stats.most_humid_date.strftime("%B")
        day = stats.most_humid_date.day
        print(f"Humidity: {stats.most_humid}% on {month} {day}")