import requests
import traceback
import json


class APIHandler:
    BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

    def __init__(self):
        print("[DEBUG] APIHandler initialized")

    def get_air_index(self, station_id):
        """indeksy"""
        url = f"https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/{station_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch air index: {e}")
            return None

    def get_stations(self):
        """stacje"""
        try:
            print("[DEBUG] Fetching all stations...")
            url = f"{self.BASE_URL}/station/findAll"
            response = requests.get(url)
            response.raise_for_status()
            stations = response.json().get("Lista stacji pomiarowych", [])
            print(f"[DEBUG] Retrieved {len(stations)} stations")
            return stations
        except Exception as e:
            print(f"[ERROR] Failed to fetch stations: {e}")
            traceback.print_exc()
            return []

    def get_sensors(self, station_id):
        """sensory"""
        url = f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            sensors = response.json()
            print(f"[DEBUG] Raw sensors: {json.dumps(sensors, indent=2)}")  # Optional debug
            return sensors
        except Exception as e:
            print(f"[ERROR] Failed to fetch sensors: {e}")
            return []

    def get_sensor_data(self, sensor_id):
        """pomiary"""
        url = f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch data for sensor {sensor_id}: {e}")
            return None

    def get_station_pollutant_value(self, station_id, pollutant):
        """ostatnie dane"""
        try:
            sensors = self.get_sensors(station_id)
            for sensor in sensors:
                if sensor.get("param", {}).get("paramCode") == pollutant:
                    sensor_id = sensor.get("id")
                    print(f"[DEBUG] Fetching data for sensor {sensor_id} ({pollutant})...")
                    url = f"{self.BASE_URL}/data/getData/{sensor_id}"
                    response = requests.get(url)
                    response.raise_for_status()
                    values = response.json().get("values", [])
                    for v in values:
                        if v.get("value") is not None:
                            print(f"[DEBUG] Found value: {v['value']}")
                            return v["value"]
            print(f"[WARN] No valid value found for pollutant {pollutant} at station {station_id}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch pollutant value: {e}")
            traceback.print_exc()
            return None

    def get_sensor_id_for_pollutant(self, station_id, pollutant_code):
        sensors = self.get_sensors(station_id)
        for sensor in sensors:
            param = sensor.get("param")
            if param and param.get("paramCode") == pollutant_code:
                return sensor.get("id")
        return None

    def get_sensor_data_for_station(self, station_id, pollutant):
        """dane historyczne"""
        try:
            sensors = self.get_sensors(station_id)
            for sensor in sensors:
                if sensor.get("param", {}).get("paramCode") == pollutant:
                    sensor_id = sensor.get("id")
                    print(f"[DEBUG] Fetching historical data for sensor {sensor_id} ({pollutant})...")
                    url = f"{self.BASE_URL}/data/getData/{sensor_id}"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json().get("values", [])
                    print(f"[DEBUG] Retrieved {len(data)} historical entries")
                    return data
            print(f"[WARN] No sensor found for pollutant {pollutant} at station {station_id}")
            return []
        except Exception as e:
            print(f"[ERROR] Failed to fetch historical data: {e}")
            traceback.print_exc()
            return []
