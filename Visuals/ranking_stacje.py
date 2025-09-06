import matplotlib.pyplot as plt

def ranking_stacje(stations_data, pollutant="PM10"):
    """
    stations_data: list of dicts [{"name": "Station name", "value": 12}, ...]
    pollutant: e.g. "PM10" or "PM2.5"
    """
    if not stations_data:
        print("Brak danych do wyświetlenia rankingu.")
        return

    clean_data = [s for s in stations_data if s.get("value") is not None]
    if not clean_data:
        print("Brak wartości pomiarowych do wyświetlenia.")
        return

    sorted_data = sorted(clean_data, key=lambda x: x["value"])

    names = [s["name"] for s in sorted_data]
    values = [s["value"] for s in sorted_data]
    colors = ["green" if v < 20 else "orange" if v < 50 else "red" for v in values]

    plt.figure(figsize=(8, max(3, len(names) * 0.4)))
    plt.barh(names, values, color=colors)
    plt.xlabel(f"{pollutant} [µg/m³]")
    plt.title(f"Ranking stacji ({pollutant})")
    plt.tight_layout()
    plt.show()
