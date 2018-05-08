import paho.mqtt.client as mqtt
import jokes
import threading
import time
import json
import codecs



class JokeSkill(object):
    def __init__(self):
        self._msgThread = threading.Thread(target = self._run)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
        
        self._jokeProvider = jokes.RandomJoker()
        #self._jokeProvider.add(jokes.OfflineJoker("stupidstuff.json"))
        #self._jokeProvider.add(jokes.OfflineJoker("wocka.json"))
        #self._jokeProvider.add(jokes.ChuckJokeProvider())
        self._jokeProvider.add(jokes.LineJoker('yomomma.txt'))
        
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe('hermes/intent/async:Joke')	
    
    def start(self):
        self._mqtt_client.connect('localhost', 1883)
        self._msgThread.start()
    
    def _run(self):
        self._mqtt_client.loop_forever()
        print("Ended Skill")
        
    def stop(self):
        print("Skill should end")
        self._mqtt_client.disconnect()
        print("mqtt disconnected")

    def _onMessage(self, client, userdata, msg):
        data = json.loads(msg.payload.decode("utf-8"))
        sessionId = data['sessionId']
        joke = self._jokeProvider.getJoke()
        
        print("Joke for %s: %s" % (sessionId, joke))
        print(sessionId)
        
        returnMsg = {
            "sessionId" : sessionId, 
            "text": joke
            }
        
        client.publish("hermes/dialogueManager/endSession", json.dumps(returnMsg))




skill = JokeSkill()
skill.start()
while(True):
    time.sleep(5)
skill.stop()