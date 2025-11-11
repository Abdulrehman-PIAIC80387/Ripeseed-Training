from utils.helpers import fetch_day_string, fetch_month_string, parse_date, sort_readings_by_date, colorize

class Reports:
    def __init__(self):
        self.red = '\033[91m'
        self.blue = '\033[94m'
        self.reset = '\033[0m'

    def print_bar_chart(self, readings):
        for reading in sort_readings_by_date(readings):
            day = fetch_day_string(reading.date)
            self._print_max_bar(day, reading)
            self._print_min_bar(day, reading)

    def _print_max_bar(self, day, reading):
        temp = int(reading.max_temp)
        bar = colorize('+' * temp, self.red, self.reset)
        print(f"{day:02d} {bar} {temp}C")

    def _print_min_bar(self, day, reading):
        temp = int(reading.min_temp)
        bar = colorize('+' * temp, self.blue, self.reset)
        print(f"{day:02d} {bar} {temp}C")

    def print_bar_chart_single_liner(self, readings):
        for reading in sort_readings_by_date(readings):
            self._print_single_line_bar(reading)

    def _print_single_line_bar(self, reading):
        day = fetch_day_string(reading.date)
        low = int(reading.min_temp)
        high = int(reading.max_temp)
        bar = (colorize('+' * low, self.blue, self.reset)+ colorize('+' * (high - low), self.red, self.reset))
        print(f"{day:02d} {bar} {low}C - {high}C")

    def print_monthly_averages_report(self, averages):
        print(f"Highest Average: {round(averages.avg_highest_temp, 2)}C")
        print(f"Lowest Average: {round(averages.avg_lowest_temp, 2)}C")
        print(f"Average Mean Humidity: {round(averages.avg_mean_humidity, 2)}%")

    def print_yearly_report(self, stats):
        self._print_stat_line("Highest", stats.highest_temp, stats.highest_temp_date)
        self._print_stat_line("Lowest", stats.lowest_temp, stats.lowest_temp_date)
        self._print_stat_line("Humidity", f"{stats.most_humid}%", stats.most_humid_date)

    def _print_stat_line(self, label, value, date_str):
        date = parse_date(date_str)
        month = date.strftime("%B")
        day = date.day
        print(f"{label}: {value} on {month} {day}")