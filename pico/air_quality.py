from machine import Pin, I2C
from time import sleep
from sgp40 import SGP40

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=40000)  # all sensor connected through I2C

while True:
    air_quality = SGP40(i2c, 0x59)
    Air_quality = air_quality.measure_raw()
    print("Air quality = ", Air_quality)

    sleep(5)
