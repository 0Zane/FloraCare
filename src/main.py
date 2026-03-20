import dht
import time
from machine import Pin, ADC, I2C

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
BH1750_CONT_H_RES = 0x10  # Continuous high resolution mode

#Defining objects for each sensor
capteur = dht.DHT22(Pin(DHT_PIN))
adc = ADC(Pin(SOIL_PIN)) #adc : analog to digital converter on soil sensor
i2c = I2C(0, sda=Pin(LIGHT_SDA), scl=Pin(LIGHT_SCL), freq=400000)
i2c.writeto(BH1750_ADDR, bytes([BH1750_CONT_H_RES]))

def read_light():
    data = i2c.readfrom(BH1750_ADDR, 2)
    return (data[0] << 8 | data[1]) / 1.2

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
    lux = read_light()

    print(f"Température : {temp}°C")
    print(f"Humidité    : {humi}%")
    print(f"Soil: raw={raw}  moisture={soil_pct}%")
    print(f"Lumière     : {lux:.1f} lx")
    print("---")

    time.sleep(2)
