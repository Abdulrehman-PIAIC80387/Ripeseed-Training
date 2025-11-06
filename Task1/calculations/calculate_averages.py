from models.montly_averages import MonthlyAverages


def calculate_monthly_averages(readings):
    averages = MonthlyAverages()
    
    max_temps = []
    min_temps = []
    mean_humidities = []
    
    for reading in readings:
        if reading.max_temp is not None:
            max_temps.append(reading.max_temp)
        if reading.min_temp is not None:
            min_temps.append(reading.min_temp)
        if reading.mean_humidity is not None:
            mean_humidities.append(reading.mean_humidity)
    
    if len(max_temps) > 0:
        total = sum(max_temps)
        averages.avg_highest_temp = total / len(max_temps)
    
    if len(min_temps) > 0:
        total = sum(min_temps)
        averages.avg_lowest_temp = total / len(min_temps)
    
    if len(mean_humidities) > 0:
        total = sum(mean_humidities)
        averages.avg_mean_humidity = total / len(mean_humidities)
    
    return averages