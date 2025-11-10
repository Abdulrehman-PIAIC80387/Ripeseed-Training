from models.montly_averages import MonthlyAverages
from models.yearly_stats import YearlyStats


class Calculations:
    
    def __init__(self):
        self.max_temps = []
        self.min_temps = []
        self.mean_humidities = []
    
    
    def calculate_monthly_averages(self, readings):
        averages = MonthlyAverages()
        
        self.max_temps = []
        self.min_temps = []
        self.mean_humidities = []
        
        for reading in readings:
            if reading.max_temp is not None:
                self.max_temps.append(reading.max_temp)
            if reading.min_temp is not None:
                self.min_temps.append(reading.min_temp)
            if reading.mean_humidity is not None:
                self.mean_humidities.append(reading.mean_humidity)
        
        if len(self.max_temps) > 0:
            total = sum(self.max_temps)
            averages.avg_highest_temp = total / len(self.max_temps)
        
        if len(self.min_temps) > 0:
            total = sum(self.min_temps)
            averages.avg_lowest_temp = total / len(self.min_temps)
        
        if len(self.mean_humidities) > 0:
            total = sum(self.mean_humidities)
            averages.avg_mean_humidity = total / len(self.mean_humidities)
        
        return averages


    def calculate_yearly_stats(self, readings):
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