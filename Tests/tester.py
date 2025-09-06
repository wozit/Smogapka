from Sources.api_handler import APIHandler

def test_city_search(city_name):
    print(f"\n=== TEST: Szukam stacji dla miasta: {city_name} ===")
    stations = [
        s for s in APIHandler.get_stations()
        if city_name.lower() in (s.get("city", {}).get("name", "").lower())
    ]
    if stations:
        print(f"Znaleziono {len(stations)} stacji:")
        for s in stations:
            print(f"  ID: {s['id']}, Nazwa: {s['stationName']}")
    else:
        print("Nie znaleziono stacji online.")

if __name__ == "__main__":
    # Inicjalizacja bazy (jeśli testujesz też DB)
    APIHandler.initialize_database()

    # TEST – wyszukiwanie online
    test_city_search("Wrocław")
    test_city_search("Poznań")
