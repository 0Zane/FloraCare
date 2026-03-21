import dht
import time
from machine import Pin, ADC, I2C
import socket
import network
from webpage import webpage 

#SENSOR PINS
SOIL_PIN = 18
DHT_PIN = 16
LIGHT_SCL = 2
LIGHT_SDA = 1

#SCREEN PINS
RES = 9
CS = 10
MOSI = 11
SCLK = 12
LED = 13
DC = 15

BH1750_ADDR = 0x23
BH1750_CONT_H_RES = 0x10

#FloraCareWIFI
SSID = "FloraCare"
WIFIPASSWORD = "pythonTNSI2026"
MAX_USER = 4
APWIFI = True  


capteur = dht.DHT22(Pin(DHT_PIN))
adc = ADC(Pin(SOIL_PIN))
i2c = I2C(0, sda=Pin(LIGHT_SDA), scl=Pin(LIGHT_SCL), freq=400000)
try:
    i2c.writeto(BH1750_ADDR, bytes([BH1750_CONT_H_RES]))
except:
    print("Could not write address on light sensor")

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

def launch_ap():
    try:
        sta = network.WLAN(network.AP_IF)
        sta.active(True)
        sta.config(essid=SSID, authmode=network.AUTH_WPA_WPA2_PSK, password=WIFIPASSWORD)
        print('Network config:', sta.ifconfig())
    except:
        print("Failed to launch AP")

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
    # Handle web requests (non-blocking)
    if socketFloraCare and APWIFI:
        try:
            conn, addr = socketFloraCare.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            print('Content = %s' % str(request))
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

    print(f"Température : {temp}°C")
    print(f"Humidité    : {humi}%")
    print(f"Soil: raw={raw}  moisture={soil_pct}%")
    print(f"Lumière     : {lux:.1f} lx")
    print("---")

    time.sleep(2)