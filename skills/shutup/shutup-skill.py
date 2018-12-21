import paho.mqtt.client as mqtt
import threading
import time
import json
import wave
import io
import time
from threading import Thread
class HotwordBeep(object):
    def __init__(self):
        self._msgThread = threading.Thread(target = self._run)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
        
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe("hermes/intent/async:Shutup")
        client.subscribe("hermes/intent/async:StartListening")	
    
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
        if msg.topic == "hermes/intent/async:Shutup":
            msgPayload = json.loads(msg.payload.decode("utf-8"))
            thread = Thread(target = self._handleShutup, args = (msgPayload, ))
            thread.start()
        if msg.topic == "hermes/intent/async:StartListening":
            self._handleStartListening(json.loads(msg.payload.decode("utf-8")))
            
    def _handleShutup(self, msg):
        print("Shutup")
        sessionId = msg["sessionId"];
        siteId = msg["siteId"];
        duration = self._getDurationInSeconds(msg)
        print(duration)
        text = "I will shut up for %d seconds" % duration
        returnMsg = {
            "sessionId" : sessionId, 
            "text": text
            }
        
        self._mqtt_client.publish("hermes/dialogueManager/endSession", json.dumps(returnMsg))
        print("Dialog ended")
        # stop listening:
        # TODO: handle site id
        stopMsg = {
            "sessionId" : "null", 
            "siteId": siteId
            }
        
        print("Waiting 5 sec")
        time.sleep(5)
        print("%s: Stop listening" % siteId)
        self._mqtt_client.publish("hermes/hotword/toggleOff", json.dumps(stopMsg))
        
        stepsSeconds = 10
        while duration > 0:
            sleepTime = duration if duration < stepsSeconds else stepsSeconds
            
            print("%s: Activating again in %d seconds" % (siteId, duration))
            duration -= sleepTime
            time.sleep(sleepTime)
            
        print("%s: Start listening" % siteId)
        self._mqtt_client.publish("hermes/hotword/toggleOn", json.dumps(stopMsg))
   
    def _getDurationInSeconds(self, msg):
        defaultDuration = 15*60;
        if not 'slots' in msg:
            return defaultDuration
        slots = msg["slots"]
        for slot in slots:
            if slot["slotName"] == "duration":
                value = slot["value"]
                duration = 0
                duration += value["seconds"]
                duration += 60 * value["minutes"]
                duration += 60 * 60 * value["hours"]
                return duration
            
        return defaultDuration
    
    
    def _handleStartListening(self, msg):
        print("Start listening")
        print(msg)
    

        
            

skill = HotwordBeep()
skill.start()
while(True):
    try:
       time.sleep(5)
    except KeyboardInterrupt:
        break;
skill.stop()
