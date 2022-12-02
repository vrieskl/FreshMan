from machine import Pin
import onewire, ds18x20
import binascii
from time import sleep

import network
import secrets

from umqtt.simple import MQTTClient

# MQTT functions
mqtt_server = 'broker.hivemq.com'
client_id = 'bigles98765'
topic_pub = b'costman.temp'


def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker' % (mqtt_server))
    return client


def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()


# initialize sensors
ds_pin = machine.Pin(2, Pin.ALT, Pin.PULL_UP)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
rom_count = len(roms)
print('Found DS devices:' + str(rom_count))

# initialize WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

for rom in roms:
    print(binascii.hexlify(rom))
print('Temperature (°C)')

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

count = 0
while True:
    ds_sensor.convert_temp()
    sleep(29.5)
    avg = 0
    values = []
    count += 1
    print(count, end=' ')
    topic_msg = "{:6} ".format(count)
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        avg += temp
        values.append(temp)
        topic_msg += "{:.4f} ".format(temp) + ' '
    #     print("{:.4f}".format(temp), end=' ')
    #  print("avg:{:.4f}".format(avg / rom_count))
    #  for value in values:
    #    print("{:.4f}".format(value - avg / rom_count), end=' ')
    client.publish(topic_pub, topic_msg)
    print()
    sleep(0.5)
