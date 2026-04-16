import pigpio
import sys

PAN_PIN = 18
TILT_PIN = 12

PAN_STOP = 1500

TILT_MIN = 120
TILT_MAX = 250
TILT_CENTER = (TILT_MIN + TILT_MAX)//2

PWM_MIN = 1000 
PWM_MAX = 2000

pi = pigpio.pi()

if not pi.connected:
    print("BŁĄD: Nie można połączyć się z demonem pigpiod!")
    print("Upewnij się, że wpisałeś: sudo systemctl start pigpiod")
    sys.exit()

def set_pan_speed(speed):
    if speed == 0:
        pi.set_servo_pulsewidth(PAN_PIN, PAN_STOP)
    else:
        speed = max(-100, min(100, speed))
        pulsewidth = PAN_STOP + (speed*5)
        pi.set_servo_pulsewidth(PAN_PIN, pulsewidth)

def set_tilt_angle(angle):

    clamped_angle = max(TILT_MIN, min(TILT_MAX, angle))
    pulsewidth = (clamped_angle - TILT_MIN) * (PWM_MAX - PWM_MIN) / (TILT_MAX - TILT_MIN) + PWM_MIN
    pw_final = int(pulsewidth)
    
    try:
        pi.set_servo_pulsewidth(TILT_PIN, pw_final)
        print(f"[TILT] Angle: {angle:4} (Clamped: {clamped_angle:3}) | PWM: {pw_final}")
    except Exception as e:
        print(f"Błąd sprzętowy TILT: {e}")



def cleanup():
    pi.set_servo_pulsewidth(PAN_PIN, 0)
    pi.set_servo_pulsewidth(TILT_PIN, 0)
    pi.stop()

def center_camera():
    print("\n[INIT] Procedura bezpiecznego startu...")
    
    pi.set_mode(PAN_PIN, pigpio.OUTPUT)
    pi.set_mode(TILT_PIN, pigpio.OUTPUT)
    
    
    set_pan_speed(0)
    set_tilt_angle(TILT_CENTER)
    print("[INIT] Kamera ustabilizowana.\n")


if __name__ == "hardware":
    center_camera()




