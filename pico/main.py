import machine
from machine import Pin
import onewire
import binascii
from time import sleep
import time
import network
import secrets
import ds18x20
from lib.umqtt.simple import MQTTClient
print('Start')
# MQTT functions
mqtt_server = 'pi0-2w.fritz.box'
client_id = 'bigles98765'
topic_pub = b'costman.temp'

led = machine.Pin("LED", machine.Pin.OUT)
led.on()


def mqtt_connect():
    global client
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.connect()
    #    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client


def reconnect():
    #    print('Failed to connect to the MQTT Broker. Reconnecting...')
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
sleep(1.5)

client = None
try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

count = 0
pause_seconds = 1.8
while True:
    ds_sensor.convert_temp()
    led.on()
    sleep(pause_seconds)
    led.off()
    sleep(pause_seconds)
    count += 1
    topic_msg = "{:6}|".format(count).replace(' ', '')
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        topic_msg += str(binascii.hexlify(rom)).replace('b\'', '').replace('\'', '') + ":{:.4f}".format(temp) + ';'
    client.publish(topic_pub, topic_msg)
