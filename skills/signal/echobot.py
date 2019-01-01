import paho.mqtt.client as mqtt
import datetime
import json


def time_now():
    return datetime.datetime.now().strftime('%H:%M:%S.%f')

signalNumber = "2343453"
# MQTT client to connect to the bus
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    # subscribe to all messages
    client.subscribe("signal-cli/messages/incoming/"+signalNumber+"/data")

def sendGroupMessage(groupId, message): 
    print("Sending group message to %s" % groupId)
    payload = json.dumps({'groupId': groupId, 
                 'message': message})
    mqtt_client.publish("signal-cli/messages/send/"+signalNumber, payload)

def sendDirectMessage(recipient, message): 
    print("Sending direct message to %s" % recipient)
    payload = json.dumps({'recipient': recipient, 
                 'message': message})
    mqtt_client.publish("signal-cli/messages/send/"+signalNumber, payload)
    
# Process a message as it arrives
def on_message(client, userdata, msg):
    print("Received: %s" % msg.payload)
    data = json.loads(msg.payload)
    source = data['envelope']['source']
    origMessage = data['envelope']['dataMessage']['message']
    
    # group message? 
    if "groupInfo" in data['envelope']['dataMessage'] and data['envelope']['dataMessage']['groupInfo'] is not None:
        groupId = data['envelope']['dataMessage']['groupInfo']['groupId'];
        sendGroupMessage(groupId, origMessage)
    else: 
        recipient = data['envelope']['source']
        sendDirectMessage(recipient, origMessage)
    
    

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect('localhost', 1883)
mqtt_client.loop_forever()
mqtt_client.disconnect()
