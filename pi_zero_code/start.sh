#!/bin/bash

echo "=========================================="
echo "🤖 Uruchamianie systemu FollowCam..."
echo "=========================================="

# 1. Uruchomienie demona GPIO
echo "[1/3] Budzenie demona pigpiod..."
sudo systemctl start pigpiod
sleep 1 # Dajemy mu sekunde na rozruch

# 2. Uruchomienie uStreamera w tle
echo "[2/3] Uruchamianie strumienia wideo..."
# Odpalamy Twój stary skrypt w tle (ukrywamy jego logi, żeby nie śmieciły ekranu)
./start_stream.sh > /dev/null 2>&1 &
STREAM_PID=$! # Zapisujemy "dowód osobisty" (PID) tego procesu, żeby go potem zabić
sleep 2

# 3. Uruchomienie serwera
echo "[3/3] Start głównego serwera z hardware API..."
echo "Aby wyłączyć wszystko, wciśnij po prostu [Ctrl+C]"
echo "------------------------------------------"
python3 pi_serwer.py

# --- TEN KOD WYKONA SIĘ DOPIERO PO WCIŚNIĘCIU CTRL+C ---
echo ""
echo "=========================================="
echo " Zamykanie systemu..."
echo "=========================================="
# Zabijamy proces kamery, żeby nie zjadał zasobów w tle
kill $STREAM_PID
echo "Kamera wyłączona. Wszystko bezpiecznie zamknięte."