import random
from typing import Dict
from paho.mqtt import client as mqtt_client
from DataBase import MySqlDb, DataBase


class Sensor:
    """" Get Database Id of a sensor Address
    """

    def __init__(self, data_base: DataBase):
        self.__cache: Dict[str, int] = {}
        self.__data_base = data_base

    def get(self, search: str) -> int:
        result = self.__cache.get(search)
        if result is not None:
            return result
        result = self.__data_base.select_one_field('select Id from Sensor where Address=%s', (search,))
        if result is not None:
            self.__cache[search] = result
            return result
        result = db.insert('Sensor', {'Address': search})
        self.__cache[search] = result
        return result


broker = 'broker.hivemq.com'
port = 1883
topic = "costman.temp"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = None
password = None
db: DataBase = MySqlDb('adm', '1qazJI90!', 'localhost', 'pico_data')
count: int = 0
sensor = Sensor(db)


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('')
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global count
        count += 1
        sample_list = msg.payload.decode().split('|')[1][:-1].split(';')
        if len(sample_list) > 0:
            sample_id = db.insert('Sample', {})
            for sample_raw in sample_list:
                sample = sample_raw.split(':')
                db.insert('Measure', {'SampleId': sample_id, 'SensorId': sensor.get(sample[0]), 'Temperature': sample[1]})
            db.insert('temp_sample', {'data': msg.payload.decode()})
            if count > 50:
                db.commit()
                count = 0
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()

