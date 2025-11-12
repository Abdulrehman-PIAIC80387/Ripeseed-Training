from datetime import datetime
class WeatherReading:
    
    def __init__(self, row):
        date_str = row.get('PKT', '').strip() or row.get('PSKT', '').strip()
        self.date = datetime.strptime(date_str, '%Y-%m-%d')
        self.max_temp = int(row.get('Max TemperatureC', ''))
        self.mean_temp = int(row.get('Mean TemperatureC', ''))
        self.min_temp = int(row.get('Min TemperatureC', ''))
        self.max_humidity = int(row.get('Max Humidity', ''))
        self.mean_humidity = int(row.get(' Mean Humidity', ''))
        self.min_humidity = int(row.get(' Min Humidity', ''))