import csv
from parser.parser_validator import WeatherDataValidator
from models.weather_reading import WeatherReading


class WeatherFileParser:
    
    def __init__(self):
        self.validator = WeatherDataValidator()
    
    def parse_file(self, file_path):
        readings = []

        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    validated = self.validator.validate(row)
                    if validated:
                        readings.append(WeatherReading(**validated))
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        return readings
