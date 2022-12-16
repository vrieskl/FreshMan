from machine import Pin
import onewire
import binascii
import time,ds18x20
ds_pin = machine.Pin(2, Pin.ALT, Pin.PULL_UP)
ow = onewire.OneWire(ds_pin)
print(ow.scan())
ds = ds18x20.DS18X20(ow)

while True:
    roms = ds.scan()
    time.sleep_ms(100)
    print('-----------------------------------')
    ds.convert_temp()
    time.sleep(1)
    for rom in roms:
        try:
            print(str(binascii.hexlify(rom)).replace('b\'', '').replace('\'', ''), ds.read_temp(rom))
        except:
            print('Error')