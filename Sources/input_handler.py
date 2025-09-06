import unicodedata


class InputHandler:
    @staticmethod
    def normalize(text):
        """
        Normalize Polish characters and lowercase the string.
        Useful for consistent filtering and comparisons.
        """
        return ''.join(
            c for c in unicodedata.normalize('NFKD', text or "")
            if not unicodedata.combining(c)
        ).lower()

    def filter_by_city(self, stations, city):
        """
        filtruje po miastach
        """
        city_norm = self.normalize(city)
        return [
            s for s in stations
            if city_norm in self.normalize(s.get("Nazwa miasta", ""))
        ]

    def filter_by_station_id(self, stations, station_id):
        """
       filtruje po ID
        """
        return [
            s for s in stations
            if str(s.get("Identyfikator stacji")) == str(station_id)
        ]
