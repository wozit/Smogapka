import matplotlib.pyplot as plt
from datetime import datetime

def historia_stacja(sensor_data, pollutant="PM10"):
    """
    sensor_data['values'] = [{"date": "YYYY-MM-DD HH:MM:SS", "value": 12}, ...]
    """
    if not sensor_data or "values" not in sensor_data:
        print("Brak danych do wyświetlenia.")
        return

    valid_values = [v for v in sensor_data["values"] if v.get("value") is not None]
    if not valid_values:
        print("Brak ważnych pomiarów do wyświetlenia.")
        return

    last5 = valid_values[-5:]

    try:
        times = [datetime.fromisoformat(v["date"]) for v in last5]
    except ValueError:
        # W razie innego formatu daty
        times = [datetime.strptime(v["date"], "%Y-%m-%d %H:%M:%S") for v in last5]

    values = [v["value"] for v in last5]

    plt.figure(figsize=(6, 4))
    plt.plot(times, values, marker="o", color="blue")
    plt.axhline(y=20, color="green", linestyle="--", label="Próg niski")
    plt.axhline(y=50, color="red", linestyle="--", label="Próg wysoki")
    plt.xlabel("Czas pomiaru")
    plt.ylabel(f"{pollutant} [µg/m³]")
    plt.title(f"Ostatnie 5 pomiarów – {pollutant}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
