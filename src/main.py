import dht
import time
from machine import Pin, ADC

SOIL_PIN = 18
DHT_PIN = 15

capteur = dht.DHT11(Pin(DHT_PIN))
adc = ADC(Pin(SOIL_PIN))

def read_soil():
    adc.atten(ADC.ATTN_11DB)
    raw = adc.read_u16()
    moisture_pct = max(0, min(100, 100 - (raw * 100 // 65535)))
    return raw, moisture_pct

def read_temp():
    capteur.measure()
    temp = capteur.temperature()
    humi = capteur.humidity()
    return temp, humi

while True:
    temp, humi = read_temp()
    raw, soil_pct = read_soil()

    print(f"Température : {temp}°C")
    print(f"Humidité    : {humi}%")
    print(f"Soil: raw={raw}  moisture={soil_pct}%")
    print("---")

    time.sleep(2)
