import paho.mqtt.client as mqtt
import threading
import time
import json
import wave
import io
import picotts


class SnipsTTS(object):
    def __init__(self):
        self._msgThread = threading.Thread(target = self._run)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
        
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe('hermes/tts/say')	
    
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
        waveId = data['id']
        siteId = data['siteId']
        text = data['text']
        tts = picotts.PicoTTS()
        ttswav = tts.synth_wav(text)
        
        hermesPath = "hermes/audioServer/%s/playBytes/%s" % (siteId, waveId)
        self._mqtt_client.publish(hermesPath, ttswav)
            
            
        # send when we finished sending wave
        returnMsg = {
            "id" : waveId, 
            "sessionId": None
            }
        client.publish("hermes/tts/sayFinished", json.dumps(returnMsg))
        
    def excluded(self):
        # TODO: maybe necessary for very long messages to split it
        while(True):
            newWaveFp = io.BytesIO()
            newWav = wave.open(newWaveFp, "wb")
            newWav.setparams((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), 0, 'NONE', 'not compressed'))
            newFrames = wav.readframes(2048)
            if(len(newFrames) == 0):
                break;
            packages = packages + 1
            newWav.writeframes(newFrames)
            newWaveFp.seek(0)
            wavBinary = newWaveFp.read()
            newWav.close()
            newWaveFp.close()
            print("Decoding "+str(packages))
            hermesPath = "hermes/audioServer/default/playBytes/%s" % (waveId)
            self._mqtt_client.publish(hermesPath, wavBinary)
            
            
        # send when we finished sending wave
        returnMsg = {
            "id" : waveId, 
            "sessionId": None
            }
        client.publish("hermes/tts/sayFinished", json.dumps(returnMsg))




skill = SnipsTTS()
skill.start()
while(True):
    try:
       time.sleep(5)
    except KeyboardInterrupt:
        break;
skill.stop()