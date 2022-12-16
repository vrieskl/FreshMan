from machine import Pin, PWM
import time
fan = PWM(Pin(0))
fan.freq(1000)
count = 0
while True:
    fan.duty_u16(count * 1000)
    time.sleep_ms(200)
    if count > 63:
        count = 0
    count += 1
