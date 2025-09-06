import sys
import os
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Sources.api_handler import APIHandler

def debug_fetch_stations():
    print("\n[DEBUG] Fetching all stations...")
    api = APIHandler()
    stations = api.get_stations()
    print(f"[RESULT] Total stations fetched: {len(stations)}")

    for s in stations[:5]:
        station_id = s.get("Identyfikator stacji")
        name = s.get("Nazwa stacji")
        city = s.get("Nazwa miasta")
        print(f" - {name} ({city})")

        print(f"   [DEBUG] Sensors for station {station_id}:")
        sensors = api.get_sensors(station_id)

        if not isinstance(sensors, list):
            print(f"   [ERROR] Unexpected sensor format: {type(sensors)} - {sensors}")
            continue

        for sensor in sensors:
            if isinstance(sensor, dict):
                param = sensor.get("param", {}).get("paramName")
                code = sensor.get("param", {}).get("paramCode")
                print(f"     - {param} [{code}]")
            else:
                print(f"     [WARN] Skipping malformed sensor: {sensor}")


def debug_fetch_sensors(station_id):
    print(f"\n[DEBUG] Fetching sensors for station ID {station_id}...")
    api = APIHandler()
    sensors = api.get_sensors(station_id)

    print("[DEBUG] Raw sensors:", sensors)

    for s in sensors:
        param = s.get("param", {}).get("paramName")
        code = s.get("param", {}).get("paramCode")
        print(f" - Sensor: {param} [{code}]")

def debug_fetch_sensor_data(station_id, pollutant="PM10"):
    print(f"\n[DEBUG] Fetching {pollutant} data for station ID {station_id}...")
    api = APIHandler()
    value = api.get_station_pollutant_value(station_id, pollutant)
    print(f"[RESULT] Latest {pollutant} value: {value}")

def debug_save_to_db(station_id, pollutant="PM10"):
    print(f"\n[DEBUG] Saving {pollutant} data to DB for station ID {station_id}...")
    api = APIHandler()
    value = api.get_station_pollutant_value(station_id, pollutant)
    if value is not None:
        APIHandler.save_sensor_data(station_id, pollutant, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("[RESULT] Data saved successfully.")
    else:
        print("[RESULT] No data to save.")

def debug_air_index(station_id):
    print(f"\n[DEBUG] Fetching air index for station ID {station_id}...")
    api = APIHandler()
    index = api.get_air_index(station_id)

    if not index:
        print("[RESULT] No index data available.")
        return

    print(f"[RESULT] Air quality index for station {station_id}:\n")


    main_index = index.get("stIndexLevel", {}).get("indexLevelName")
    calc_date = index.get("stCalcDate")
    source_date = index.get("stSourceDataDate")

    print(f" - Index Level: {main_index or 'Brak danych'}")
    print(f" - Calculated at: {calc_date or 'Brak daty'}")
    print(f" - Source data timestamp: {source_date or 'Brak daty'}")


    for key, value in index.items():
        if key.endswith("IndexLevel") and key != "stIndexLevel":
            pollutant = key.replace("IndexLevel", "")
            level = value.get("indexLevelName") if isinstance(value, dict) else None
            print(f" - {pollutant}: {level or 'Brak danych'}")



if __name__ == "__main__":
    # Legnica ma dane do testów
    test_station_id = 52

    debug_fetch_stations()
    debug_fetch_sensors(test_station_id)
    debug_fetch_sensor_data(test_station_id, "PM10")
    debug_save_to_db(test_station_id, "PM10")
    debug_air_index(test_station_id)
