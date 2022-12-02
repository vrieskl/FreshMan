import machine
import utime
print("start")
led = machine.Pin("LED", machine.Pin.OUT)
for i in range(20):
    led.on()
    sleep = 1 / (i+1)
    utime.sleep(sleep)
    led.off()
    utime.sleep(sleep)
print("done")