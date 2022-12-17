from typing import Dict
from paho.mqtt import client as mqtt_client
from server.classes.CollectUtils import Sensor, Helpers, DeltaDetect
from server.classes.DataBase import DataBase
from server.classes.TinyTools import Content, ConfigSettings, MySqlDbFactory

settings = ConfigSettings(Content.get('config.json'))
broker = settings.get('host')
port = int(settings.get('mqtt_port'))
topic = settings.get('mqtt_topic')
client_id = f'python-mqtt'
db: DataBase = MySqlDbFactory.settings(settings)
count: int = 0
sensor = Sensor(db)
delta = DeltaDetect(1.5)


def connect_mqtt():
    def on_connect(client1, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client1, userdata, msg):
        global count
        count += 1
        # Make dictionary with address as key, only changed values
        insert_dict: Dict[str, float] = delta.check(Helpers.split_message(msg.payload.decode()))
        if len(insert_dict) > 0:  # Data has changed
            sample_id = db.insert('Sample', {})  # insert Sample with Id
            for key in insert_dict:
                db.insert('Measure',
                          {'SampleId': sample_id, 'SensorId': sensor.get(key), 'Temperature': insert_dict[key]})
            if count > 0:
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
