import paho.mqtt.client as mqtt
import datetime
import json
import uuid
import time
import sys
import configparser



def time_now():
    return datetime.datetime.now().strftime('%H:%M:%S.%f')


class MqttClient(): 
    def __init__(self, siteId, signalNumber): 
        self._requests = []
        # MQTT client to connect to the bus
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self.onConnect
        self._mqttClient.on_message = self.onMessage
        self._siteId = siteId
        self._signalNumber = signalNumber
        
    
    def connect(self):
        print("connecting")
        self._mqttClient.connect('192.168.36.133', 1883)


    def publish(self, topic, payload): 
        self._mqttClient.publish(topic, payload)
        
    def disconnect(self):
        self._mqttClient.loop_stop()
        self._mqttClient.disconnect()
    
    def getSiteId(self):
        return self._siteId
    
    def onConnect(self, client, userdata, flags, rc):
        print("onconnect")
        # subscribe to all messages
        client.subscribe('hermes/asr/startListening')
        client.subscribe('hermes/tts/say')
        client.subscribe('hermes/dialogueManager/sessionEnded')
        client.subscribe("hermes/audioServer/" + self._siteId + "/playBytes/#")
        client.subscribe("signal-cli/messages/incoming/" + self._signalNumber + "/data")

    def addRequest(self, request):
        self._requests.append(request)
    
    def onMessage(self, client, userdata, msg):
        if len(msg.payload) > 0 and len(msg.payload) < 2000:
            print('[{}] - {}: {}'.format(time_now(), msg.topic, msg.payload))
        else:
            print('[{}] - {}'.format(time_now(), msg.topic))
        
        if msg.topic ==  "signal-cli/messages/incoming/" + self._signalNumber + "/data":
            data = json.loads(msg.payload)
            source = data['envelope']['source']
            origMessage = data['envelope']['dataMessage']['message']
            
            print("Adding request to list")
            req = Request(mqttClient, source, origMessage)
            self._requests.append(req)
            req.start()

        audioTopic = "hermes/audioServer/" + self.getSiteId() + "/playBytes/"
        if msg.topic.startswith(audioTopic):
            print("Sending audio finished for")
            splitted = msg.topic.split("/")
            playId = splitted[4]
            playFinished = {"id": playId, "siteId": self.getSiteId()}
            
            client.publish("hermes/audioServer/" + self.getSiteId() + "/playFinished", json.dumps(playFinished))
        
        for request in self._requests:
            if not request.isFinished():
                request.onMessage(self, userdata, msg)
                
                
    def sendGroupMessage(self, groupId, message): 
        print("Sending group message to %s" % groupId)
        payload = json.dumps({'groupId': groupId, 
                    'message': message})
        self.publish("signal-cli/messages/send/" + self._signalNumber, payload)

    def sendDirectMessage(self, recipient, message): 
        print("Sending direct message to %s" % recipient)
        payload = json.dumps({'recipient': recipient, 
                    'message': message})
        self.publish("signal-cli/messages/send/" + self._signalNumber, payload)

class Request: 
    def __init__(self, mqttClient, signalSource, requestText):
        self._mqttClient = mqttClient
        self._sessionId = None
        self._signalSource = signalSource
        self._requestText = requestText
        self._requestFinished = False
    
    def start(self):
        print("Sending hotword out")
        signalDetected = {"siteId": self._mqttClient.getSiteId(),"modelId":"signal","modelVersion":"hey_snips_3.1_2018-04-13T15:27:35_model_0019","modelType":"universal","currentSensitivity":0.5,"detectionSignalMs":1546362796842,"endSignalMs":1546362796842}
        self._mqttClient.publish("hermes/hotword/default/detected", json.dumps(signalDetected))

    def isFinished(self):
        return self._requestFinished
    
    def _sendNLURequest(self):
        print("Sending text nlu request")
        if self._sessionId is None:
            print("ERROR: sessionid has not been received")
            return
        textCaptured = {"text": self._requestText,
                        "likelihood":0.8690107,
                        #"tokens":[{"value":"turn","confidence":1.0,"range_start":0,"range_end":4,"time":{"start":0.0,"end":1.8299999}},
                        #          {"value":"the","confidence":0.6610203,"range_start":5,"range_end":8,"time":{"start":1.8299999,"end":1.8987917}},
                        #          {"value":"light","confidence":0.8627513,"range_start":9,"range_end": 14,"time":{"start":1.8987917,"end":2.226477}},
                        #          {"value":"on","confidence":1.0,"range_start":15,"range_end":17,"time":{"start":2.226477,"end":3.1499999}}],
                        "seconds":3.0,
                        "siteId": self._mqttClient.getSiteId(),
                        "sessionId": self._sessionId}
                        
        self._mqttClient.publish("hermes/asr/textCaptured", json.dumps(textCaptured))
        
    # Process a message as it arrives
    def onMessage(self, client, userdata, msg):
        print(msg.topic)
        if msg.topic == "hermes/asr/startListening":
            msgJson = json.loads(msg.payload)
            print(msgJson)
            sessionId = msgJson["sessionId"]
            self._sessionId = sessionId
            print("new sessionId: %s" % self._sessionId)
            self._sendNLURequest()
            
        if msg.topic == "hermes/dialogueManager/sessionEnded": 
            self._requestFinished = True
            msgJson = json.loads(msg.payload)
            
            text = msgJson["text"]
            print("Session finished with response: %s" % text)
        
        if msg.topic == "hermes/tts/say": 
            msgJson = json.loads(msg.payload)
            sayId = msgJson['id']
            text = msgJson['text']
            sayFinished = {"id":sayId,"sessionId": self._sessionId}
            client.sendDirectMessage(self._signalSource, text)
            client.publish("hermes/tts/sayFinished", json.dumps(sayFinished))

config = configparser.ConfigParser()
config.read('config.ini')
siteid = config.get('snips', 'siteid', fallback='signal')
signalNumber = config.get('signal', 'signalnumber')

mqttClient = MqttClient(siteid, signalNumber)
mqttClient.connect()
time.sleep(1)
mqttClient._mqttClient.loop_forever()
mqttClient.disconnect()
