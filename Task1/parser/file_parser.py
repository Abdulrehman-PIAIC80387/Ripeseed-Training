import csv
from models.weather_reading import WeatherReading


class WeatherFileParser:
    
    def parse_file(self, file_path):
        readings = []
        
        try:
            lines = self._read_file_lines(file_path)
            
            for row in lines:
                reading = self._reading_holder(row)
                if reading:
                    readings.append(reading)
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        return readings
    
    def _read_file_lines(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    
    def _reading_holder(self, row):
        if not self._is_valid_row(row):
            return None
        
        weather_data = self._extract_weather_data(row)
        
        return WeatherReading(
            weather_data['date'],
            weather_data['max_temp'],
            weather_data['mean_temp'],
            weather_data['min_temp'],
            weather_data['max_humidity'],
            weather_data['mean_humidity'],
            weather_data['min_humidity']
        )
    
    def _is_valid_row(self, row):
        if not row:
            return False
        if 'PKT' not in row:
            return False
        return True
    
    def _extract_weather_data(self, row):
        data = {
            'date': self._extract_date(row),
            'max_temp': self._parse_float(row.get('Max TemperatureC', '')),
            'mean_temp': self._parse_float(row.get('Mean TemperatureC', '')),
            'min_temp': self._parse_float(row.get('Min TemperatureC', '')),
            'max_humidity': self._parse_humidity(row.get('Max Humidity', '')),
            'mean_humidity': self._parse_humidity(row.get(' Mean Humidity', '')),
            'min_humidity': self._parse_humidity(row.get(' Min Humidity', ''))
        }
        return data
    
    def _extract_date(self, row):
        try:
            return row.get('PKT', '').strip()
        except Exception:
            return None
    
    def _parse_float(self, value):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    
    def _parse_humidity(self, value):
        value = value.strip()
        if not value or value == '-1':
            return None
        try:
            return int(value)
        except ValueError:
            return None


def parse_weather_file(file_path):
    parser = WeatherFileParser()
    return parser.parse_file(file_path)