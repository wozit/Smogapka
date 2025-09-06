import requests

def get_air_quality_index(station_id: int) -> dict:
    """
    indeksy z GIOŚ API.

    Args:
        station_id (int): ID of the measurement station.

    Returns:
        dict: Parsed air quality index data.
    """
    url = f"https://api.gios.gov.pl/pjp-api/v1/rest/aqindex/getIndex/{station_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # struktura wyniku
        result = {
            "Stacja ID": data.get("Identyfikator stacji pomiarowej"),
            "Data obliczeń": data.get("Data wykonania obliczeń indeksu"),
            "Wartość indeksu": data.get("Wartość indeksu"),
            "Kategoria": data.get("Nazwa kategorii indeksu"),
            "Status dostępności": data.get("Status indeksu ogólnego dla stacji pomiarowej"),
            "Zanieczyszczenie krytyczne": data.get("Kod zanieczyszczenia krytycznego"),
            "Parametry": []
        }

        # dodaje indeksy
        for param in ["SO2", "NO2", "PM10", "PM2.5", "O3"]:
            result["Parametry"].append({
                "Parametr": param,
                "Wartość indeksu": data.get(f"Wartość indeksu dla wskaźnika {param}"),
                "Kategoria": data.get(f"Nazwa kategorii indeksu dla wskażnika {param}"),
                "Data źródłowa": data.get(f"Data danych źródłowych, z których policzono wartość indeksu dla wskaźnika {param}")
            })

        return result

    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
        return {"error": str(e)}
