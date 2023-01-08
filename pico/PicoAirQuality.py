from machine import Pin, I2C
from time import sleep
import network
import secrets
from sgp40 import SGP40
from lib.umqtt.simple import MQTTClient

print('Start')
# MQTT functions
mqtt_server = 'pi0-2w.fritz.box'
client_id = 'bigles98765'
topic_pub = b'costman.air.quality.raw'


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

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=40000)  # all sensor connected through I2C

while True:
    air_quality = SGP40(i2c, 0x59)
    topic_msg = air_quality.measure_raw()
    print("Air quality = ", topic_msg)
    client.publish(topic_pub, str(topic_msg))
    sleep(10)
