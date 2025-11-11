class WeatherReading:
    
    def __init__(self, date, max_temp, mean_temp, min_temp, max_humidity, mean_humidity, min_humidity):
        self.date = date
        self.max_temp = max_temp
        self.mean_temp = mean_temp
        self.min_temp = min_temp
        self.max_humidity = max_humidity
        self.mean_humidity = mean_humidity
        self.min_humidity = min_humidity
    
    def is_valid(self):
        return (self.max_temp is not None and 
                self.min_temp is not None and 
                self.max_humidity is not None)
    
    @classmethod
    def from_dict(cls, data):
        reading = cls(
            date=data.get('date'),
            max_temp=data.get('max_temp'),
            mean_temp=data.get('mean_temp'),
            min_temp=data.get('min_temp'),
            max_humidity=data.get('max_humidity'),
            mean_humidity=data.get('mean_humidity'),
            min_humidity=data.get('min_humidity')
        )
        return reading if reading.is_valid() else None