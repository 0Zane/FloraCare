import dht
import time
from machine import Pin, ADC

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

#Defining objects for each sensor
capteur = dht.DHT11(Pin(DHT_PIN))
adc = ADC(Pin(SOIL_PIN)) #adc : analog to digital converter on soil sensor


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
