# Mengimpor modul yang dibutuhkan
import RPi.GPIO as GPIO
import time
import requests

# Menetapkan token, label perangkat, dan label variabel ubidots
TOKEN = "BBFF-EvIMYWATzgqXOOEgWzoZ0pt4aWjLSC"
DEVICE_LABEL = "tugasakhir"
VARIABLE_LABEL = "tutup"

# Menetapkan pin GPIO yang digunakan untuk servo
servo_pin = 16

# Mengatur mode GPIO sebagai BCM
GPIO.setmode(GPIO.BCM)

# Mengatur pin servo sebagai output
GPIO.setup(servo_pin, GPIO.OUT)

# Membuat objek PWM untuk pin servo dengan frekuensi 50 Hz
pwm = GPIO.PWM(servo_pin, 50)

# Memulai PWM dengan duty cycle 0
pwm.start(0)

# Fungsi untuk mendapatkan nilai variabel ubidots
def get_var(device, variable, token):
    try:
        url = "http://industrial.api.ubidots.com/api/v1.6/devices/{0}/{1}/lv".format(device, variable)
        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
        r = requests.get(url=url, headers=headers)
        return r.json()
    except:
        return None

# Fungsi untuk mengubah nilai variabel ubidots menjadi sudut servo
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Fungsi untuk menggerakkan servo sesuai dengan nilai variabel ubidots
def update_servo(value):
    angle = map_value(value, 0, 1, 0, 180) # Mengubah nilai 0 atau 1 menjadi sudut 0 atau 180 derajat
    duty = map_value(angle, 0, 180, 2.5, 7.5) # Mengubah sudut menjadi duty cycle PWM
    pwm.ChangeDutyCycle(duty) # Mengubah duty cycle PWM
    print("Servo bergerak ke sudut {} derajat".format(angle))
    time.sleep(1) # Memberi jeda selama 1 detik

# Loop utama program
while True:
    # Mendapatkan nilai variabel ubidots
    value = get_var(DEVICE_LABEL, VARIABLE_LABEL, TOKEN)
    
    # Jika nilai variabel ubidots ada, maka menggerakkan servo sesuai dengan nilai tersebut
    if value is not None:
        update_servo(value)
    
    # Jika tidak ada nilai variabel ubidots, maka memberi pesan kesalahan dan berhenti
    else:
        print("Tidak ada nilai variabel ubidots")
        break

# Membersihkan pin GPIO dan menghentikan PWM
GPIO.cleanup()
pwm.stop()
