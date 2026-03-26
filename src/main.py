import dht
import time
from machine import Pin, ADC, I2C
import socket
import network
from webpage import webpage
import ujson
from statehandler import plantstate
from drivers.display.robot_face import Display as FaceDisplay, Face

# --- Sensor pins ---
SOIL_PIN  = 18
DHT_PIN   = 15
LIGHT_SCL = 2
LIGHT_SDA = 1

# --- Screen pins ---
RES  = 9
CS   = 10
MOSI = 11
SCLK = 12
LED  = 13
DC   = 14

# DC pin shared between DHT22 and the display driver (both on GPIO 15)
# After every DHT read, face.lcd.restore_dc() must be called to reclaim it.
DISPLAY_DC = 15

# --- Hardware addresses ---
BH1750_ADDR       = 0x23
BH1750_CONT_H_RES = 0x10

# --- Wi-Fi access point ---
SSID          = "FloraCare"
WIFIPASSWORD  = "pythonTNSI2026"
MAX_USER      = 4
MAX_PACKETSIZE = 1024
APWIFI = True  # set to False when the AP is disabled at runtime

# --- Plant models ---
orchidee = {"name": "ORCHIDEE", "humid": 65, "temp": 22, "moisture": 55, "light": 45}
cactus   = {"name": "CACTUS",   "humid": 20, "temp": 28, "moisture": 20, "light": 85}
monstera = {"name": "MONSTERA", "humid": 58, "temp": 24, "moisture": 60, "light": 40}
jacinthe = {"name": "JACINTHE", "humid": 50, "temp": 14, "moisture": 50, "light": 70}

# Dictionary mapping POST plant names to their model
PLANT_MODELS = {
    "orchidee": orchidee,
    "cactus":   cactus,
    "monstera": monstera,
    "jacinthe": jacinthe,
}

# --- Light average state ---
period  = 0
lum_sum = 0
lightstate = 0
# --- Plant target thresholds (updated when a plant is selected via the web UI) ---
norm_air_temp = 22
norm_air_hum  = 40
norm_moisture = 50
norm_light    = 1

# --- Sensor initialisation ---
capteur = dht.DHT22(Pin(DHT_PIN))
adc     = ADC(Pin(SOIL_PIN))
i2c     = I2C(0, sda=Pin(LIGHT_SDA), scl=Pin(LIGHT_SCL), freq=400000)
try:
    i2c.writeto(BH1750_ADDR, bytes([BH1750_CONT_H_RES]))
except:
    print("Light sensor not found — skipping init")


# --- Sensor read functions ---

def read_light():
    try:
        data = i2c.readfrom(BH1750_ADDR, 2)
        return (data[0] << 8 | data[1]) / 1.2
    except:
        return -1


def read_soil():
    try:
        adc.atten(ADC.ATTN_11DB)
        raw = adc.read_u16()
        moisture_pct = max(0, min(100, 100 - (raw * 100 // 65535)))
        return raw, moisture_pct
    except:
        return -1, -1


def read_temp():
    try:
        capteur.measure()
        temp = capteur.temperature()
        humi = capteur.humidity()
        return temp, humi
    except:
        return -1, -1


# --- Wi-Fi access point ---

def launch_ap():
    try:
        sta = network.WLAN(network.AP_IF)
        sta.active(True)
        sta.config(essid=SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=WIFIPASSWORD)
        print("Network config:", sta.ifconfig())
    except:
        print("Failed to launch AP")


# --- Boot sequence ---

launch_ap()

face = Face(FaceDisplay())
face.draw()

try:
    socketFloraCare = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketFloraCare.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketFloraCare.bind(('', 80))
    socketFloraCare.listen(MAX_USER)
    socketFloraCare.setblocking(False)
    print("Server listening on port 80")
except Exception as e:
    print(f"Error creating socket: {e}")
    socketFloraCare = None

# --- Main loop ---

_sensor_at = time.ticks_ms()
_temp = _humi = _soil_pct = _lux = -1

while True:
    face.update()

    if socketFloraCare and APWIFI:
        try:
            conn, addr = socketFloraCare.accept()
            conn.settimeout(2.0)
            print("Connection from", addr)
            request    = conn.recv(MAX_PACKETSIZE).decode('utf-8')
            first_line = request.split('\r\n')[0]
            print(request)

            if "POST /save" in first_line:
                try:
                    parts = request.split('\r\n\r\n')
                    if len(parts) > 1:
                        data       = ujson.loads(parts[1])
                        plant_name = data.get("plant")
                        selected   = PLANT_MODELS.get(plant_name)

                        if selected:
                            norm_air_temp = selected["temp"]
                            norm_air_hum  = selected["humid"]
                            norm_moisture = selected["moisture"]
                            norm_light    = selected["light"]
                            print(f"Succès : {plant_name} configurée.")
                            print(f"Objectif : Temp {norm_air_temp}°C, Hum {norm_air_hum}%")
                        else:
                            print(f"Erreur : La plante '{plant_name}' n'existe pas dans la base de données FloraCare")

                        conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                except Exception as e:
                    print("POST /save error:", e)

            elif "POST /wifi_off" in first_line:
                conn.send("HTTP/1.1 200 OK\r\n\r\nDisabling Wi-Fi...")
                conn.close()
                time.sleep(1)
                network.WLAN(network.AP_IF).active(False)
                APWIFI = False
                print("Wi-Fi AP disabled")

            else:
                response = webpage()
                conn.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
                conn.send(response)
                conn.close()

        except:
            pass  # no incoming connection — non-blocking accept raises here

    # Read sensors every 2 s without blocking the animation loop
    if time.ticks_diff(time.ticks_ms(), _sensor_at) >= 0:
        _sensor_at = time.ticks_ms() + 2000

        try:
            _temp, _humi = read_temp()
            # DHT22 and display DC share GPIO 15 — restore pin direction after DHT use
            face.lcd.restore_dc()
            _raw, _soil_pct = read_soil()
            _lux            = read_light()

            tempstate, humstate, moiststate = plantstate(
                _temp, norm_air_temp, _humi, norm_air_hum, _soil_pct, norm_moisture
            )

            if period < 1000:
                period  += 1
                lum_sum += _lux
            elif period >= 1000:
                period  = 0
                avg_lum = lum_sum // 1000
                lum_sum = 0
                if avg_lum + 10 < norm_light:
                    lightstate = -1
                    print("Votre plante est en manque de lumière depuis quelques temps.")

            if tempstate == 1:
                print("Votre plante a trop chaud.")
            elif tempstate == -1:
                print("Votre plante a froid.")

            if moiststate == 1:
                print("Votre plante est trop submergée.")
            elif moiststate == -1:
                print("Votre plante est en sécheresse, veuillez arroser la plante.")

            if humstate == 1:
                print("L'air est trop humide pour votre plante.")
            elif humstate == -1:
                print("L'air est trop sec pour votre plante.")

        except Exception as e:
            print(f"Sensor error: {e}")

        face.set_sensors(_temp, _humi, _soil_pct, _lux)
