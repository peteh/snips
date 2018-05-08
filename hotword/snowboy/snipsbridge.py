import paho.mqtt.client as mqtt
import datetime
import wave
import mmap
import time
import threading
import logging
import json

logging.basicConfig()
logger = logging.getLogger("snips-snowboy")
logger.setLevel(logging.DEBUG)
def time_now():
    return datetime.datetime.now().strftime('%H:%M:%S.%f')

class SnipsHotwordBridge(object):
    def __init__(self, siteId, detector):
        self._detector = detector
        self._hotword = "default"
        self._siteId = siteId
        self._msgThread = threading.Thread(target = self._stream)
        self._detector.addHotwordDetectedListener(self)
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._onConnect
        self._mqtt_client.on_message = self._onMessage
    
    def onHotwordDetected(self):
        print("Hotword was detected")
        topic = "hermes/hotword/%s/detected" % (self._hotword)
        payload = '''{"siteId":"''' + self._siteId + '''","modelId":"default"}'''

        self._mqtt_client.publish(topic, payload)
    
    def _hermesAudioPath(self):
        return "hermes/audioServer/%s/audioFrame" % (self._siteId)
    
    def _onConnect(self, client, userdata, flags, rc):
        # subscribe to all messages
        client.subscribe(self._hermesAudioPath())
        
        client.subscribe("hermes/hotword/toggleOn")
        client.subscribe("hermes/hotword/toggleOff")

    def start(self):
        self._mqtt_client.connect('localhost', 1883)
        self._msgThread.start()
    
    def _stream(self):
        self._mqtt_client.loop_forever()
        print("Ended wav streaming")
        
    def stop(self):
        print("WAV Streaming should end")
        self._mqtt_client.disconnect()
        print("mqtt disconnected")
        


    # Process a message as it arrives
    def _onMessage(self, client, userdata, msg):
        #print('[{}] - {}'.format(time_now(), msg.topic))
        if(msg.topic == self._hermesAudioPath()):
            self._processAudioMessage(msg.payload)
            return
        
        if(msg.topic == "hermes/hotword/toggleOn"):
            payloadJson = json.loads(msg.payload)
            if payloadJson['siteId'] == self._siteId:
                self._detector.enableDetection()
            return
        
        if(msg.topic == "hermes/hotword/toggleOff"):
            payloadJson = json.loads(msg.payload)
            if payloadJson['siteId'] == self._siteId:
                self._detector.disableDetection()
            return
        
        logger.warn("Unexpected message: %s" % (msg.topic))
        
    def _processAudioMessage(self, payload):
        size = len(payload)
        
        if size == 0:
            print("WARN: Received size = 0 message from audio")
            return
        
        # -1 is anonoymous memory
        mm = mmap.mmap(-1, size)
        mm.write(payload)
        mm.seek(0)
        wf = wave.open(mm)
        
        channels = wf.getnchannels()
        framerate = wf.getframerate()
        numframes = wf.getnframes()
        samplewidth = wf.getsampwidth()
        
        #print("Channels %d" % (wf.getnchannels()))
        #print("Framerate %d" % (wf.getframerate()))
        #print("n frames %d" % (wf.getnframes()))
        #print("sample width %d" % (wf.getsampwidth()))
        
        # write all to output
        frames = wf.readframes(wf.getnframes())
        wf.close()
        mm.close()
        
        self._detector.onNewFrames(channels, framerate, samplewidth, numframes, frames)


