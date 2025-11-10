class WeatherDataValidator:

    def validate(self, row):
        try:
            data = {
                'date': self._extract_date(row),
                'max_temp': self._parse_float(row.get('Max TemperatureC', '')),
                'mean_temp': self._parse_float(row.get('Mean TemperatureC', '')),
                'min_temp': self._parse_float(row.get('Min TemperatureC', '')),
                'max_humidity': self._parse_float(row.get('Max Humidity', '')),
                'mean_humidity': self._parse_float(row.get(' Mean Humidity', '')),
                'min_humidity': self._parse_float(row.get(' Min Humidity', ''))
            }

            if not self._has_valid_data(data):
                return None

            return data

        except Exception:
            return None


    def _has_valid_data(self, weather_data):
        return (weather_data['max_temp'] is not None and 
                weather_data['min_temp'] is not None and 
                weather_data['max_humidity'] is not None)


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
