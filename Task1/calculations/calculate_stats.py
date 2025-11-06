from models.yearly_stats import YearlyStats


def calculate_yearly_stats(readings):
    stats = YearlyStats()
    
    for reading in readings:
        if reading.max_temp is not None:
            if stats.highest_temp is None or reading.max_temp > stats.highest_temp:
                stats.highest_temp = reading.max_temp
                stats.highest_temp_date = reading.date
        
        if reading.min_temp is not None:
            if stats.lowest_temp is None or reading.min_temp < stats.lowest_temp:
                stats.lowest_temp = reading.min_temp
                stats.lowest_temp_date = reading.date
        
        if reading.max_humidity is not None:
            if stats.most_humid is None or reading.max_humidity > stats.most_humid:
                stats.most_humid = reading.max_humidity
                stats.most_humid_date = reading.date
    
    return stats