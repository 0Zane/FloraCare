from machine import Pin
import time


led = Pin(21, Pin.OUT)
while True:
    led.value(0)
    time.sleep(1)
    led.value(1)
    time.sleep(1)

