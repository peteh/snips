import paho.mqtt.client as mqtt
import datetime
import json


def time_now():
    return datetime.datetime.now().strftime('%H:%M:%S.%f')

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    # subscribe to all messages
    #client.subscribe('#')
    pass


# Process a message as it arrives
def on_message(client, userdata, msg):
    excludes = []
    if msg.topic in excludes:
        return
    if len(msg.payload) > 0 and len(msg.payload) < 2000 and not msg.topic in excludes:
        print('[{}] - {}: {}'.format(time_now(), msg.topic, msg.payload))
    else:
        print('[{}] - {}'.format(time_now(), msg.topic))

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect('localhost', 1883)

message = json.dumps({'recipient': '+49176914xxxx', 
                 'message': 'test'})
config = configparser.ConfigParser()
config.read('config.ini')
siteid = config.get('snips', 'siteid', fallback='signal')
signalNumber = config.get('signal', 'signalnumber')
mqtt_client.publish("signal-cli/messages/send/"+signalNumber, message)
mqtt_client.disconnect()
