import csv
from parser.data_extractor import DataExtractor
from models.weather_reading import WeatherReading


class WeatherFileParser:
    
    def __init__(self):
        self.extractor = DataExtractor()
    
    def parse_file(self, file_path):
        readings = []

        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    reading = self._create_reading(row)
                    if reading:
                        readings.append(reading)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

        return readings
    
    def _create_reading(self, row):
        data = self.extractor.extract_from_row(row)
        return WeatherReading.from_dict(data)