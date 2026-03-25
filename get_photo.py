import subprocess
import time

print("--- Start programu ---")
print("Uruchamiam kamerę. Przygotuj się...")

# Dajemy kamerze 2 sekundy na dostosowanie jasności kolorów
time.sleep(2)

# Definiujemy komendę tak samo, jak robiliśmy to w terminalu
komenda = [
    "rpicam-still", 
    "-t", "2000",                  # Czas działania w milisekundach przed zrobieniem zdjęcia
    "--width", "1280",             # Szerokość zdjęcia
    "--height", "960",             # Wysokość zdjęcia
    "-o", "moje_zdjecie.jpg"       # Nazwa pliku wyjściowego
]

try:
    print("Pstryk! Robię zdjęcie...")
    # Wykonanie komendy w systemie
    subprocess.run(komenda, check=True)
    print("Sukces! Zdjęcie zostało zapisane jako 'moje_zdjecie.jpg'")
except Exception as e:
    print(f"Ups, wystąpił błąd: {e}")

print("--- Koniec programu ---")