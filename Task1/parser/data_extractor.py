class DataExtractor:
    
    def extract_from_row(self, row):
        return {
            'date': self._extract_date(row),
            'max_temp': self._parse_float(row.get('Max TemperatureC', '')),
            'mean_temp': self._parse_float(row.get('Mean TemperatureC', '')),
            'min_temp': self._parse_float(row.get('Min TemperatureC', '')),
            'max_humidity': self._parse_float(row.get('Max Humidity', '')),
            'mean_humidity': self._parse_float(row.get(' Mean Humidity', '')),
            'min_humidity': self._parse_float(row.get(' Min Humidity', ''))
        }
    
    def _extract_date(self, row):
        date_str = row.get('PKT', '').strip() or row.get('PSKT', '').strip()
        return date_str or None
    
    def _parse_float(self, value):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None