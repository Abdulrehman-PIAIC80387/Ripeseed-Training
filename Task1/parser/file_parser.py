import csv
from models.weather_reading import WeatherReading


class WeatherFileParser:
    
    def parse_file(self, file_path):
        readings = []

        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        reading = WeatherReading(row)
                        readings.append(reading)
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        return readings