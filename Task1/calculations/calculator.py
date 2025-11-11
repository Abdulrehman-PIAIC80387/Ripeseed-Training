from models.montly_averages import MonthlyAverages
from models.yearly_stats import YearlyStats


class Calculations:
    
    def calculate_monthly_averages(self, readings):
        averages = MonthlyAverages()
        
        max_temps = [r.max_temp for r in readings ]
        min_temps = [r.min_temp for r in readings ]
        mean_humidities = [r.mean_humidity for r in readings ]
        
        averages.avg_highest_temp = self._calculate_average(max_temps)
        averages.avg_lowest_temp = self._calculate_average(min_temps)
        averages.avg_mean_humidity = self._calculate_average(mean_humidities)
        
        return averages
    
    def _calculate_average(self, values):
        if len(values) > 0:
            return sum(values) / len(values)
        return None


    def calculate_yearly_stats(self, readings):
        stats = YearlyStats()
        
        for reading in readings:
            self._update_highest_temp(stats, reading)
            self._update_lowest_temp(stats, reading)
            self._update_most_humid(stats, reading)
        
        return stats
    
    def _update_highest_temp(self, stats, reading):
            if stats.highest_temp is None or reading.max_temp > stats.highest_temp:
                stats.highest_temp = reading.max_temp
                stats.highest_temp_date = reading.date
    
    def _update_lowest_temp(self, stats, reading):
            if stats.lowest_temp is None or reading.min_temp < stats.lowest_temp:
                stats.lowest_temp = reading.min_temp
                stats.lowest_temp_date = reading.date
    
    def _update_most_humid(self, stats, reading):
            if stats.most_humid is None or reading.max_humidity > stats.most_humid:
                stats.most_humid = reading.max_humidity
                stats.most_humid_date = reading.date