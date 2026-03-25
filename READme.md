# 📹 FollowCam - Projekt Kamery Pan-Tilt (Raspberry Pi Zero W)

Witamy w repozytorium projektu **FollowCam**! Budujemy system zdalnie sterowanej kamery na złączu obrotowym (slip ring), z podglądem na żywo i sterowaniem przez przeglądarkę.

---

## 🛠️ Architektura i Technologie
- **Sprzęt:** Raspberry Pi Zero W + Camera Module V1.
- **Backend:** Python + Flask (Serwer WWW i obsługa kamery).
- **Streaming:** MJPEG (nisko-opóźnieniowy strumień bezpośrednio do tagu `<img>`).
- **Narzędzia:** VS Code + SFTP (automatyczna synchronizacja kodu z Malinką).

---

## 🚀 Instrukcja dla zespołu (Jak zacząć?)

### 1. Przygotowanie Twojego komputera (Windows)
Zanim pobierzesz kod, zainstaluj niezbędne narzędzia:
* **VS Code** – nasz edytor.
* **Wtyczka SFTP** (autor: *Natizyskunk*) – kluczowa do wysyłania kodu na Malinkę.
* **FFmpeg** – do szybkich testów podglądu.
  * Otwórz PowerShell jako Admin i wpisz: `winget install ffmpeg`

### 2. Klonowanie i Konfiguracja SFTP
1. Sklonuj to repozytorium na swój dysk.
2. Ctrl Shift P - STFP: Config
3. W folderze `.vscode` stwórz plik `sftp.json` (jest on w `.gitignore`, więc każdy musi mieć swój lokalnie).
4. Wklej poniższą konfigurację (używamy wspólnego konta):

```json
{
    "name": "RaspberryPi-FollowCam",
    "host": "192.168.0.43", //trzeba sprawdzic jakie przypisała sieć
    "protocol": "sftp",
    "port": 22,
    "username": "martowicz",
    "password": "TWOJE_HASLO_KTORE_ZNASZ", //podam wam
    "remotePath": "/home/martowicz/FollowCam",
    "uploadOnSave": true
}
```
5. Potem jak mamy jakiś plik to trzeba kliknąć go prawym i dać `Upload` i w `Output` sprawdzić czy się przeslało

### 3. Jak połączyć się z terminalem Malinki (SSH)
Terminal to nasze główne centrum dowodzenia. Używamy go do uruchamiania skryptów i instalacji paczek.

1. Otwórz **PowerShell** lub **Wiersz polecenia** na Windowsie.
2. Wpisz komendę połączenia:
   ```bash
   ssh martowicz@ADRES_IP_MALINY
   ```
3. Jeśli pojawi się pytanie o "fingerprint", wpisz yes i wciśnij Enter.
4. Podaj hasło: TWOJE_HASLO (uwaga: podczas wpisywania hasła w terminalu nie widać znaków – to normalne zabezpieczenie w Linuxie).