import dht
import time
from machine import Pin, ADC, I2C
import socket
import network
from webpage import webpage 
import ujson


#SENSOR PINS
SOIL_PIN = 18
DHT_PIN = 15
LIGHT_SCL = 2
LIGHT_SDA = 1

#SCREEN PINS
RES = 9
CS = 10
MOSI = 11
SCLK = 12
LED = 13
DC = 14

#HARDWARE ADDRESS
BH1750_ADDR = 0x23
BH1750_CONT_H_RES = 0x10

#FloraCareWIFI
SSID = "FloraCare"
WIFIPASSWORD = "pythonTNSI2026"
MAX_USER = 4
APWIFI = True   # We use this variable to check  if the wifi is on before trying to read the socket between ESP32-S3 and Webpage
MAX_PACKETSIZE = 1024

#Define plant models
orchidee = { "name": 'ORCHIDÉE', "humid": 65, "temp": 22, "moisture": 55, "light": 45 }
cactus =   { "name": 'CACTUS',   "humid": 20, "temp": 28, "moisture": 20, "light": 85 }
monstera= { "name": 'MONSTERA', "humid": 58, "temp": 24, "moisture": 60, "light": 40 }
jacinthe= { "name": 'JACINTHE', "humid": 50, "temp": 14, "moisture": 50, "light": 70 }

# Other dictionnary to link strings to each dictionnary (useful to select plant from HTTP POST reception)
PLANT_MODELS = {
    "orchidee": orchidee,
    "cactus": cactus,
    "monstera": monstera,
    "jacinthe": jacinthe
}


#Plant stats
norm_air_temp = 22
norm_air_hum = 40
norm_moisture = 30
norm_light = 1
 
#Initializing sensor objects using libraries
capteur = dht.DHT22(Pin(DHT_PIN))
adc = ADC(Pin(SOIL_PIN))
i2c = I2C(0, sda=Pin(LIGHT_SDA), scl=Pin(LIGHT_SCL), freq=400000)
try:
    i2c.writeto(BH1750_ADDR, bytes([BH1750_CONT_H_RES]))
except:
    print("Could not write address on light sensor")

#______________Functions to read sensors______________

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

#______________Function to launch the WIFI access point______________
def launch_ap():
    try:
        sta = network.WLAN(network.AP_IF)
        sta.active(True)
        sta.config(essid=SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=WIFIPASSWORD)
        print('Network config:', sta.ifconfig())
    except:
        print("Failed to launch AP")



#______________MAIN CODE AT BOOTING______________

# Launch AP and create socket ONCE, outside loop
launch_ap()


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

# Main loop
while True:
    if socketFloraCare and APWIFI:
        try:
            conn, addr = socketFloraCare.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(MAX_PACKETSIZE).decode('utf-8')
            first_line = request.split('\r\n')[0]
            print(request)

            if "POST /save" in first_line:
                try:
                    parts = request.split('\r\n\r\n')
                    if len(parts) > 1:
                        body = parts[1]
                        data = ujson.loads(body)
                        
                      
                        plant_name = data.get("plant") 
                        
                        selected_plant = PLANT_MODELS.get(plant_name)

                        if selected_plant:
                            norm_air_temp = selected_plant["temp"]
                            norm_air_hum = selected_plant["humid"]
                            norm_moisture = selected_plant["moisture"]
                            norm_light = selected_plant["light"]
                            
                            print(f"Succès : {plant_name} configurée.")
                            print(f"Objectif : Temp {norm_air_temp}°C, Hum {norm_air_hum}%")
                        else:
                            print(f"Erreur : La plante '{plant_name}' n'existe pas dans la base de données FloraCare ")

                        conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")

                except Exception as e:
                    print("Erreur POST:", e)

            elif "POST /wifi_off" in first_line:
                conn.send("HTTP/1.1 200 OK\r\n\r\nWifi en cours de desactivation...")
                conn.close()
                time.sleep(1)
                network.WLAN(network.AP_IF).active(False)
                APWIFI = False
                print("WIFI OFF")
            else:
                    response = webpage()
                    conn.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")  
                    conn.send(response)
                    conn.close()
        except :
            pass  # No connection available
    



    # Read sensors every iteration
    temp, humi = read_temp()
    raw, soil_pct = read_soil()
    lux = read_light()
    

    time.sleep(2)

