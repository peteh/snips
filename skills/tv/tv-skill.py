import paho.mqtt.client as mqtt
import threading
import time
import json
import wave
import io
import time
import os
from threading import Thread
class HotwordBeep(object):
    def __init__(self):
        self._msgThread = threading.Thread(target = self._run)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
        
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe("hermes/intent/ChangeTVState")
    
    def start(self):
        self._mqtt_client.connect('rhasspy.local', 1883)
        self._msgThread.start()
    
    def _run(self):
        self._mqtt_client.loop_forever()
        print("Ended Skill")
        
    def stop(self):
        print("Skill should end")
        self._mqtt_client.disconnect()
        print("mqtt disconnected")
        
    def _onMessage(self, client, userdata, msg):
        if msg.topic == "hermes/intent/ChangeTVState":
            msgPayload = json.loads(msg.payload.decode("utf-8"))
            self._handleShutup(msgPayload)

            
    def _handleShutup(self, msg):
        print("Shutup")
        sessionId = msg["sessionId"];
        siteId = msg["siteId"];
        newState = self._getNewState(msg)
        
        stateText = "on" if newState else "off"
        text = "I will turn the TV %s" % (stateText)
        returnMsg = {
            "sessionId" : sessionId, 
            "text": text
            }
        
        self._mqtt_client.publish("hermes/dialogueManager/endSession", json.dumps(returnMsg))
        if newState:
            os.system('echo "on 0" | cec-client -s -d 1')
        else:
            os.system('echo "standby 0" | cec-client -s -d 1')

    def _getNewState(self, msg):
        defaultValue = True;
        if not 'slots' in msg:
            return defaultValue
        slots = msg["slots"]
        for slot in slots:
            print(slot)
            if slot["slotName"] == "state":
                value = str(slot["value"]["value"])
                return (value == "on")
            
        return defaultValue

skill = HotwordBeep()
skill.start()
while(True):
    try:
       time.sleep(5)
    except KeyboardInterrupt:
        break;
skill.stop()
