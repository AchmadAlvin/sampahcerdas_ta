# Mengimpor modul GPIO dan time
import RPi.GPIO as GPIO
import time
import requests

UBIDOTS_TOKEN = 'BBFF-EvIMYWATzgqXOOEgWzoZ0pt4aWjLSC'
DEVICE_LABEL = 'tugasakhir'
VARIABLE_LABEL = 'ultrasonik'

# Mengatur mode GPIO sebagai BCM
GPIO.setmode(GPIO.BCM)

# Menentukan pin GPIO untuk trigger dan echo
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Menentukan pin GPIO untuk sensor PIR dan servo
PIR_PIN = 23  # Ganti dengan pin GPIO yang sesuai
SERVO_PIN = 16  # Ganti dengan pin GPIO yang sesuai

# Mengatur pin GPIO sebagai output dan input
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Mengatur objek servo
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz (frekuensi servo)

# Inisialisasi servo ke posisi awal
servo.start(0)
time.sleep(0.1)

# Fungsi untuk menghitung jarak
def hitung_jarak():
    # Mengirim sinyal trigger
    GPIO.output(GPIO_TRIGGER, True)

    # Menunggu 0.01 ms
    time.sleep(0.00001)
    # Menonaktifkan sinyal trigger
    GPIO.output(GPIO_TRIGGER, False)

    # Mencatat waktu awal dan akhir
    waktu_awal = time.time()
    waktu_akhir = time.time()

    # Menunggu sampai sinyal echo diterima
    while GPIO.input(GPIO_ECHO) == 0:
        waktu_awal = time.time()

    # Menunggu sampai sinyal echo selesai
    while GPIO.input(GPIO_ECHO) == 1:
        waktu_akhir = time.time()

    # Menghitung selisih waktu
    selisih_waktu = waktu_akhir - waktu_awal

    # Menghitung jarak dengan rumus v = s/t
    jarak = (selisih_waktu * 34300) / 2

    # Mengembalikan nilai jarak
    return jarak

# Fungsi untuk menghitung persentase
def hitung_persentase(jarak):
    # Menentukan batas bawah dan atas jarak dalam cm
    batas_bawah = 3
    batas_atas = 13

    # Jika jarak kurang dari atau sama dengan batas bawah, maka persentase adalah 100%
    if jarak <= batas_bawah:
        persentase = 100

    # Jika jarak lebih dari atau sama dengan batas atas, maka persentase adalah 0%
    elif jarak >= batas_atas:
        persentase = 0

    # Jika jarak di antara batas bawah dan atas, maka persentase adalah proporsional dengan selisih batas atas dan jarak terhadap selisih batas atas dan bawah
    else:
        persentase = (batas_atas - jarak) / (batas_atas - batas_bawah) * 100

    # Mengembalikan nilai persentase
    return persentase


# Fungsi untuk menggerakkan servo
def gerakkan_servo():
    servo.ChangeDutyCycle(2.5)  # Menggerakkan servo ke posisi 90 derajat
    time.sleep(5)  # Tunggu selama 5 detik
    servo.ChangeDutyCycle(7.5)  # Mengembalikan servo ke posisi awal
    time.sleep(3)

# Fungsi untuk mengirim data persentase ke Ubidots
def kirim_persentase_ubidots(persentase):
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_LABEL}/values"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "value": persentase
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print(f"Persentase terkirim ke Ubidots: {persentase}%")
    else:
        print(f"Error saat mengirim persentase ke Ubidots: {response.status_code}")

# Program utama
if __name__ == '__main__':
    try:
        # Mengulangi pengukuran jarak dan persentase selama program berjalan
        while True:
            # Memanggil fungsi hitung_jarak dan menyimpan hasilnya
            jarak_terukur = hitung_jarak()
            # Memanggil fungsi hitung_persentase dan menyimpan hasilnya
            persentase_terukur = hitung_persentase(jarak_terukur)
            # Mencetak hasilnya dengan format 1 angka di belakang koma untuk jarak dan tanpa koma untuk persentase
            print("Jarak terukur = %.1f cm, Persentase terukur = %d%%" % (jarak_terukur, persentase_terukur))

            # Mengirim persentase ke Ubidots
            kirim_persentase_ubidots(persentase_terukur)

            # Mendeteksi gerakan menggunakan sensor PIR
            if GPIO.input(PIR_PIN):
                print("Gerakan terdeteksi!")
                gerakkan_servo()

            # Memberi jeda 1 detik
            time.sleep(0.1)

    # Menangkap interupsi dengan CTRL + C
    except KeyboardInterrupt:
        # Membersihkan pin GPIO yang digunakan
        print("Pengukuran dihentikan oleh pengguna")
        GPIO.cleanup()
