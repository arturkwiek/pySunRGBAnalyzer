import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timedelta

# Funkcja do konwersji wartości R, G, B
def remove_label_convert_int(value):
    return int(value.split(': ')[1])

# Ścieżka do pliku CSV z danymi
file_path = "2024_06_10.csv"

# Wczytanie danych, stosując funkcję konwersji do odpowiednich kolumn
data = pd.read_csv(
    file_path,
    converters={
        ' R': remove_label_convert_int,
        ' G': remove_label_convert_int,
        ' B': remove_label_convert_int
    }
)

# Zmiana nazw kolumn, usunięcie początkowych spacji
data.columns = ['Timestamp', 'R', 'G', 'B']

# Konwersja kolumny 'Timestamp' na typ datetime i ustawienie jej jako indeks DataFrame
data['Timestamp'] = pd.to_datetime(data['Timestamp'])
data.set_index('Timestamp', inplace=True)

# Pobranie daty z pierwszego wpisu w danych
log_date = data.index[0].date()

# Ustawienie lokalizacji (Tarnów)
city = LocationInfo(name="Tarnów", region="Poland", timezone="Europe/Warsaw", latitude=50.0123, longitude=20.9856)

# Funkcja do pobierania godzin wschodu i zachodu słońca dla danego dnia i lokalizacji
def get_sun_times(date, city, delta_minutes=5):
    s = sun(city.observer, date=date, tzinfo=city.timezone)
    sunrise = s['sunrise'] - timedelta(minutes=delta_minutes)
    sunset = s['sunset'] + timedelta(minutes=delta_minutes)
    return sunrise, sunset

# Funkcja do obliczania średniej wartości składowej B w przedziale +-5 minut w chwilach wschodu i zachodu słońca
def calculate_avg_b_values(data, sunrise, sunset):
    bw = data.between_time((sunrise - timedelta(minutes=5)).time(), (sunrise + timedelta(minutes=5)).time())['B'].mean()
    bavg = data.between_time(sunrise.time(), sunset.time())['B'].mean()
    bz = data.between_time((sunset - timedelta(minutes=5)).time(), (sunset + timedelta(minutes=5)).time())['B'].mean()
    return bw, bavg, bz

# Pobranie godzin wschodu i zachodu słońca
sunrise, sunset = get_sun_times(log_date, city)

# Obliczenie wartości średnich dla wschodu, zachodu słońca oraz całego okresu między nimi
bw, bavg, bz = calculate_avg_b_values(data, sunrise, sunset)

# Rysowanie wykresów dla składowych R, G, B
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['R'], label='R', color='red')
plt.plot(data.index, data['G'], label='G', color='green')
plt.plot(data.index, data['B'], label='B', color='blue')

# Dodanie pionowych linii dla wschodu i zachodu słońca
plt.axvline(sunrise, color='orange', linestyle='--', label='Wschód słońca')
plt.axvline(sunset, color='purple', linestyle='--', label='Zachód słońca')

# Dodanie poziomej linii dla średniej wartości B w całym okresie
plt.axhline(bavg, color='blue', linestyle='-', linewidth=0.7, label='Średnia B (cały okres)')

# Dodanie punktów dla wartości B w wschodzie i zachodzie słońca
plt.scatter(sunrise, bw, color='cyan', zorder=5, label='Średnia B (wschód słońca)')
plt.scatter(sunset, bz, color='magenta', zorder=5, label='Średnia B (zachód słońca)')

# Dodanie adnotacji dla wartości B w wschodzie i zachodzie słońca
plt.annotate(f'{bw:.2f}', (sunrise, bw), textcoords="offset points", xytext=(-10,10), ha='center', color='black')
plt.annotate(f'{bz:.2f}', (sunset, bz), textcoords="offset points", xytext=(-10,10), ha='center', color='black')

# Formatowanie osi X do wyświetlania daty i godziny
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

# Dodanie legendy, tytułu i etykiet osi
plt.legend()
plt.title(f'Zmiany wartości RGB w czasie ({file_path})')
plt.xlabel('Czas')
plt.ylabel('Wartość składowych RGB')

# Obrócenie etykiet na osi X dla lepszej czytelności
plt.xticks(rotation=45)

# Wyświetlenie wykresu
plt.tight_layout()

# Zapisanie wykresu do pliku graficznego
output_file_path = file_path.replace('.csv', '.png') # Tworzenie nazwy pliku wyjściowego
plt.savefig(output_file_path) # Zapisanie wykresu do pliku

plt.show()

# Wypisanie godzin wschodu i zachodu słońca
print(f"Wschód słońca: {sunrise.strftime('%H:%M')}")
print(f"Zachód słońca: {sunset.strftime('%H:%M')}")
print(f"Średnia B (wschód słońca): {bw}")
print(f"Średnia B (cały okres): {bavg}")
print(f"Średnia B (zachód słońca): {bz}")
