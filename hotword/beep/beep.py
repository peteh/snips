import paho.mqtt.client as mqtt
import threading
import time
import json
import wave
import io


class HotwordBeep(object):
    def __init__(self):
        self._msgThread = threading.Thread(target = self._run)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
        
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe('hermes/hotword/default/detected')
        client.subscribe('hermes/hotword/toggleOn')	
    
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
        import uuid
        waveId = uuid.uuid4()
        #waveId = data['id']
        siteId = data['siteId']
        if msg.topic == 'hermes/hotword/default/detected':
            fname = "beepon.wav"
        else:
            fname = "beepoff.wav"
        fp = open(fname, "rb")

        wav = fp.read()
        fp.close()
        hermesPath = "hermes/audioServer/%s/playBytes/%s" % (siteId, waveId)
        self._mqtt_client.publish(hermesPath, wav)
            

skill = HotwordBeep()
skill.start()
while(True):
    try:
       time.sleep(5)
    except KeyboardInterrupt:
        break;
skill.stop()
