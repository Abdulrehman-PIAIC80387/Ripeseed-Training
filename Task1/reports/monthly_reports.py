def print_monthly_averages_report(averages): 
    if averages.avg_highest_temp is not None:
        print(f"Highest Average: {round(averages.avg_highest_temp,2)}C ")
    if averages.avg_lowest_temp is not None:
        print(f"Lowest Average: {round(averages.avg_lowest_temp,2)}C ")
    if averages.avg_mean_humidity is not None:
        print(f"Average Mean Humidity: {round(averages.avg_mean_humidity,2)}%")
