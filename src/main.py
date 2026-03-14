import dht
import time
from machine import Pin

capteur = dht.DHT11(Pin(15))


while True:
    capteur.measure()
    
    temp = capteur.temperature()
    humi = capteur.humidity()
    
    print(f"Température : {temp}°C")
    print(f"Humidité    : {humi}%")
    print("---")
    
    time.sleep(2)
