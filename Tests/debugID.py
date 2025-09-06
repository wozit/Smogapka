import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Sources.api_handler import APIHandler

def debug_all_pollutants_for_station(station_id):
    print(f"\n[DEBUG] Starting full debug for station ID {station_id}...\n")
    api = APIHandler()


    stations = api.get_stations()
    station = next((s for s in stations if s.get("Identyfikator stacji") == station_id), None)

    if not station:
        print(f"[ERROR] Station ID {station_id} not found.")
        return

    name = station.get("Nazwa stacji")
    city = station.get("Nazwa miasta")
    print(f"[INFO] Station: {name} ({city})")


    sensors = api.get_sensors(station_id)
    if not sensors:
        print("[WARN] No sensors found for this station.")
        return

    print(f"\n[INFO] Found {len(sensors)} sensors:")
    param_codes = set()

    for sensor in sensors:
        param = sensor.get("param")
        if not param:
            print(" - [WARN] Sensor missing 'param' field.")
            continue

        param_name = param.get("paramName")
        param_code = param.get("paramCode")
        print(f" - {param_name or 'Unknown'} [{param_code or 'Unknown'}]")

        if param_code:
            param_codes.add(param_code)


    print("\n[RESULT] Latest values by pollutant:")
    for sensor in sensors:
        param = sensor.get("param")
        if not param:
            continue

        param_code = param.get("paramCode")
        sensor_id = sensor.get("id")
        data = api.get_sensor_data(sensor_id)

        latest_entry = next((v for v in data.get("values", []) if v["value"] is not None), None)
        if latest_entry:
            print(f" - {param_code}: {latest_entry['value']} at {latest_entry['date']}")
        else:
            print(f" - {param_code}: Brak danych")


    index = api.get_air_index(station_id)
    print("\n[INFO] Air Quality Index:")
    if not index:
        print(" - No index data available.")
    else:
        main_index = index.get("stIndexLevel", {}).get("indexLevelName")
        print(f" - Overall Index Level: {main_index or 'Brak danych'}")
        for key, value in index.items():
            if key.endswith("IndexLevel") and key != "stIndexLevel":
                pollutant = key.replace("IndexLevel", "")
                level = value.get("indexLevelName") if isinstance(value, dict) else None
                print(f" - {pollutant}: {level or 'Brak danych'}")

if __name__ == "__main__":
    try:
        station_id = int(input("Enter station ID to debug: "))
        debug_all_pollutants_for_station(station_id)
    except ValueError:
        print("[ERROR] Invalid station ID. Please enter a numeric value.")
