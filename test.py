import os
import socket

print("--- TEST POŁĄCZENIA ---")
print(f"Witaj z Raspberry Pi!")
print(f"Nazwa urządzenia: {socket.gethostname()}")
print(f"Aktualny folder: {os.getcwd()}")
print("-----------------------")