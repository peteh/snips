from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
import paho.mqtt.client as mqtt

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)

        self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))


    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        # just print info
        print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.media_type == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.media_type == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.media_type == "contact":
            print("Echoing contact (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))


class MqttLayer(YowInterfaceLayer):

    def __init__(self):
        YowInterfaceLayer.__init__(self)
        self._mqttClient = MqttClient("creampi3.local", "whatsapp-cli", "36309040975")
        self._mqttClient.connect()
        self._mqttClient.publish("whatsappcli/messages/incoming", "test")
        
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)

        self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))


    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        # just print info
        print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))
        self._mqttClient.publish("whatsappcli/messages/incoming", "test")
        print("Published")

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.media_type == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.media_type == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.media_type == "contact":
            print("Echoing contact (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))


class MqttClient(): 
    def __init__(self, mqttBroker, siteId, signalNumber): 
        self._requests = []
        # MQTT client to connect to the bus
        self._mqttBroker = mqttBroker
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self.onConnect
        self._mqttClient.on_message = self.onMessage
        self._siteId = siteId
        self._signalNumber = signalNumber
        
    
    def connect(self):
        print("connecting to %s" % (self._mqttBroker))
        self._mqttClient.connect(self._mqttBroker, 1883)
        self._mqttClient.loop_start()


    def publish(self, topic, payload): 
        self._mqttClient.publish(topic, payload)
        
    def disconnect(self):
        self._mqttClient.loop_stop()
        self._mqttClient.disconnect()
    
    def getSiteId(self):
        return self._siteIdhermes/hotword/toggleOn
    
    def onConnect(self, client, userdata, flags, rc):
        print("Connected to MQTT")
        #print("Start listening for messages to %s as site %s" % (self._signalNumber, self._siteId))
        # subscribe to all messages
        client.subscribe('hermes/asr/startListening')
        print("Subscribed")

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
