# FollowCam

FollowCam to system zdalnego sterowania kamerą z funkcją automatycznego śledzenia twarzy. Kamera sterowana jest bezpośrednio z interfejsu webowego (web-console).

## Struktura projektu

* `pi_zero_code/` - główny kod uruchamiany na Raspberry Pi Zero. Przyjmuje komendy za pomocą socket.io i porusza serwami za pomocą biblioteki pigpio. Zawiera również skrypty do strumieniowania obrazu z kamery.
* `pi_zero_code/web-console/` - główny interfejs webowy do sterowania kamerą i podglądu wideo (obsługuje zintegrowane śledzenie twarzy).

---

## Raspberry Pi Zero - Uruchamianie

Kod znajduje się bezpośrednio na Raspberry Pi podłączonym do kamery i serw.

### Uruchamianie całości
Najwygodniej uruchomić cały system zintegrowanym skryptem startowym, który uruchamia kamerę, serwer HTTP dla konsoli oraz serwer sprzętowy pigpio:

1. Upewnij się, że zależności zostały zainstalowane (`pip install -r pi_zero_code/requirements_pi.txt`).
2. Odpal skrypt startowy:
   ```bash
   cd pi_zero_code
   bash start.sh
   ```
   *(Skrypt automatycznie powoła pigpiod, strumień kamery port 8080, serwer http port 8000 i socket.io port 5000)*
3. Wejdź na adres `http://<IP_MALINKI>:8000` w przeglądarce komputera lub telefonu.

### Ręczne uruchamianie poszczególnych komponentów (dla debugowania)
- **Strumień wideo:** `bash pi_zero_code/start_stream.sh`
- **Serwer API (socket.io):** `sudo systemctl start pigpiod` a następnie `python3 pi_zero_code/pi_serwer.py`
- **Interfejs webowy:** `cd pi_zero_code/web-console && python3 -m http.server 8000`

---

## Opis głównych procedur sterowania
- Konfiguracja i łączenie z Pi następuje automatycznie w momencie załadowania strony.
- Sterowanie TILT (Oś Y / góra-dół) następuje poprzez ustawienie kąta ułożenia (0-180 stopni).
- Sterowanie PAN (Oś X / lewo-prawo) polega na kontroli prędkości z powodu obrotu serwa dookoła własnej osi. Prędkość nadąża proporcjonalnie do potrzeb interfejsu lub detekcji twarzy w przeglądarce.
