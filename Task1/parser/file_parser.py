from models.weather_reading import WeatherReading


class WeatherFileParser:
    
    def parse_file(self, file_path):
        readings = []
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
                for i in range(1, len(lines)):
                    reading = self._parse_line(lines[i])
                    if reading:
                        readings.append(reading)
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        return readings
    
    def _parse_line(self, line):
        line = line.strip()
        if not line:
            return None
        
        parts = line.split(',')
        if len(parts) < 10:
            return None
        
        try:
            date = parts[0].strip()
        except Exception:
            return None
        
        max_temp = self._parse_float(parts[1])
        mean_temp = self._parse_float(parts[2])
        min_temp = self._parse_float(parts[3])
        max_humidity = self._parse_humidity(parts[7])
        mean_humidity = self._parse_humidity(parts[8])
        min_humidity = self._parse_humidity(parts[9])
        
        return WeatherReading(
            date, max_temp, mean_temp, min_temp,
            max_humidity, mean_humidity, min_humidity
        )
    
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