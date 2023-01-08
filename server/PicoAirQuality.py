from paho.mqtt import client as mqtt_client
from server.classes.TinyTools import Content, ConfigSettings, MySqlDbFactory
from server.classes.VOC_Algorithm import DFRobot_VOC_ALGORITHM
content = Content.get('/Users/maxml/PycharmProjects/FreshMan/server/config2.json')
settings = ConfigSettings(content)
broker = settings.get('host')
port = int(settings.get('mqtt_port'))
topic = settings.get('mqtt_topic')
client_id = f'python-mqtt'
count: int = 0
voc_algorithm = DFRobot_VOC_ALGORITHM()
voc_algorithm.VOC_ALGORITHM_init()

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
        raw = int(msg.payload.decode())
        vocIndex = voc_algorithm.VOC_ALGORITHM_process(raw)
        print('Raw data:', raw, 'VOC Index', vocIndex)
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
