import tkinter as tk
from tkinter import ttk, messagebox
import traceback
import json
from Sources.api_handler import APIHandler
from Sources.input_handler import InputHandler
from Visuals.ranking_stacje import ranking_stacje
from Visuals.historia_stacja import historia_stacja
from Visuals.jakosc_powietrza import get_air_quality_index


class Smogapka:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smogapka")
        self.root.geometry("900x550")

        self.api = APIHandler()
        self.input = InputHandler()
        self.all_stations = []

        self._build_widgets()

    def _build_widgets(self):
        try:
            logo_img = tk.PhotoImage(file="GUI/icon.PNG")
            logo_label = ttk.Label(self.root, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(side=tk.TOP, pady=10)
        except Exception as e:
            print(f"[DEBUG] Nie udało się wczytać logo: {e}")

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(control_frame, text="Pobierz wszystkie stacje",
                   command=self.load_stations).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Miasto:").pack(side=tk.LEFT, padx=(10, 5))
        self.city_var = tk.StringVar()
        city_entry = ttk.Entry(control_frame, textvariable=self.city_var, width=20)
        city_entry.pack(side=tk.LEFT)
        city_entry.bind("<Return>", lambda e: self.filter_by_city())
        ttk.Button(control_frame, text="Filtruj", command=self.filter_by_city).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="ID stacji:").pack(side=tk.LEFT, padx=(10, 5))
        self.station_id_var = tk.StringVar()
        station_id_entry = ttk.Entry(control_frame, textvariable=self.station_id_var, width=10)
        station_id_entry.pack(side=tk.LEFT)
        station_id_entry.bind("<Return>", lambda e: self.filter_by_station_id())
        ttk.Button(control_frame, text="Filtruj", command=self.filter_by_station_id).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Pokaż jakość powietrza dla stacji",
                   command=self.show_air_quality_index).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Parametr:").pack(side=tk.LEFT, padx=(10, 5))
        self.pollutant_var = tk.StringVar(value="PM10")
        pollutant_combo = ttk.Combobox(
            control_frame, textvariable=self.pollutant_var,
            values=["PM10", "PM2.5", "O3", "NO2", "SO2", "CO"],
            width=10, state="readonly"
        )
        pollutant_combo.pack(side=tk.LEFT)
        pollutant_combo.current(0)

        ttk.Button(control_frame, text="Ranking stacji",
                   command=self.show_ranking_chart).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Trend dla stacji",
                   command=self.show_trend_chart).pack(side=tk.LEFT, padx=5)

        mid_frame = ttk.LabelFrame(self.root, text="Lista stacji", padding=5)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stations_listbox = tk.Listbox(mid_frame, selectmode=tk.MULTIPLE)
        self.stations_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.stations_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stations_listbox.config(yscrollcommand=scrollbar.set)

        self.status_var = tk.StringVar(value="Gotowy")
        ttk.Label(self.root, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def load_stations(self):
        try:
            print("[DEBUG] load_stations triggered")
            self.status_var.set("Pobieranie listy stacji...")
            self.root.update_idletasks()

            stations = self.api.get_stations() or []
            if not stations:
                messagebox.showwarning("Brak danych", "API nie zwróciło żadnych stacji.")
            self.all_stations = stations
            self.update_station_list(stations)
            self.status_var.set(f"Załadowano {len(stations)} stacji")
        except Exception as e:
            traceback.print_exc()
            self.status_var.set("Błąd przy pobieraniu stacji")
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy stacji:\n{e}")

    def update_station_list(self, stations):
        self.stations_listbox.delete(0, tk.END)
        for s in stations:
            station_id = s.get("Identyfikator stacji")
            station_name = s.get("Nazwa stacji")
            city_name = s.get("Nazwa miasta", "Brak miasta")
            self.stations_listbox.insert(tk.END, f"{station_id} - {station_name} ({city_name})")

    def filter_by_city(self):
        try:
            city = self.city_var.get().strip()
            if not city:
                messagebox.showinfo("Brak danych", "Wpisz nazwę miasta.")
                return

            filtered = self.input.filter_by_city(self.all_stations, city)
            if not filtered:
                messagebox.showinfo("Brak wyników", f"Nie znaleziono stacji dla miasta: {city}")
                return

            self.update_station_list(filtered)
            self.status_var.set(f"Znaleziono {len(filtered)} stacji w mieście '{city}'")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się przefiltrować po mieście:\n{e}")

    def filter_by_station_id(self):
        try:
            station_id_input = self.station_id_var.get().strip()
            if not station_id_input:
                messagebox.showinfo("Brak danych", "Wpisz ID stacji.")
                return

            filtered = self.input.filter_by_station_id(self.all_stations, station_id_input)
            if not filtered:
                messagebox.showinfo("Brak wyników", f"Nie znaleziono stacji o ID: {station_id_input}")
                return

            self.update_station_list(filtered)
            self.status_var.set(f"Znaleziono {len(filtered)} stację o ID '{station_id_input}'")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się przefiltrować po ID:\n{e}")

    def show_air_quality_index(self):
        try:
            selected_indices = self.stations_listbox.curselection()
            if len(selected_indices) != 1:
                messagebox.showwarning("Uwaga", "Wybierz dokładnie jedną stację.")
                return

            entry = self.stations_listbox.get(selected_indices[0])
            station_id, _ = entry.split(" - ", 1)
            station_id = int(station_id.strip())

            data = get_air_quality_index(station_id)
            if "error" in data:
                messagebox.showerror("Błąd", data["error"])
                return

            summary = f"""
🏭 Stacja ID: {data['Stacja ID']}
📅 Data obliczeń: {data['Data obliczeń']}
📊 Wartość indeksu: {data['Wartość indeksu']} ({data['Kategoria']})
✅ Dostępność: {data['Status dostępności']}
☣️ Zanieczyszczenie krytyczne: {data['Zanieczyszczenie krytyczne']}

🧪 Indeksy cząstkowe:
"""
            for param in data["Parametry"]:
                summary += f"\n🔹 {param['Parametr']}: {param['Wartość indeksu']} ({param['Kategoria']}) — {param['Data źródłowa']}"

            messagebox.showinfo("Jakość powietrza", summary)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych indeksu:\n{e}")

    def show_ranking_chart(self):
        try:
            print("[DEBUG] show_ranking_chart triggered")

            selected_indices = self.stations_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Uwaga", "Wybierz co najmniej jedną stację.")
                return

            pollutant = self.pollutant_var.get()
            stations_data = []

            for idx in selected_indices:
                entry = self.stations_listbox.get(idx)
                station_id, name = entry.split(" - ", 1)
                station_id = int(station_id.strip())
                sensor_id = self.api.get_sensor_id_for_pollutant(station_id, pollutant)

                if sensor_id is None:
                    print(f"[DEBUG] Station {station_id}: No sensor found for {pollutant}")
                    value = None
                else:
                    sensor_data = self.api.get_sensor_data(sensor_id)
                    print(
                        f"[DEBUG] Sensor data for station {station_id}, pollutant {pollutant}:\n{json.dumps(sensor_data, indent=2)}")

                    if sensor_data and "values" in sensor_data:
                        latest_entry = next((v for v in sensor_data["values"] if v.get("value") is not None), None)
                        value = latest_entry["value"] if latest_entry else None
                    else:
                        print(f"[DEBUG] Station {station_id}: No valid data found")
                        value = None

                stations_data.append({"name": name, "value": value})


            ranking_stacje(stations_data, pollutant=pollutant)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się wygenerować wykresu:\n{e}")

    def show_trend_chart(self):
        try:
            selected_indices = self.stations_listbox.curselection()
            if len(selected_indices) != 1:
                messagebox.showwarning("Uwaga", "Wybierz dokładnie jedną stację.")
                return

            pollutant = self.pollutant_var.get()
            entry = self.stations_listbox.get(selected_indices[0])
            station_id, _ = entry.split(" - ", 1)
            station_id = int(station_id.strip())

            sensor_id = self.api.get_sensor_id_for_pollutant(station_id, pollutant)
            if sensor_id is None:
                messagebox.showinfo("Brak danych", f"Brak czujnika dla parametru {pollutant} na tej stacji.")
                return

            sensor_data = self.api.get_sensor_data(sensor_id)
            print(
                f"[DEBUG] Sensor data for station {station_id}, pollutant {pollutant}:\n{json.dumps(sensor_data, indent=2)}")

            if not sensor_data or not sensor_data.get("values"):
                messagebox.showinfo("Brak danych", f"Brak danych dla parametru {pollutant} na tej stacji.")
                return

            historia_stacja(sensor_data, pollutant=pollutant)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się wygenerować wykresu:\n{e}")

    def run(self):
        self.root.mainloop()
