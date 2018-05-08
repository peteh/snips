import snowboydecoder_snips
import sys
import signal

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) != 3:
    print("Error: need to specify model name")
    print("Usage: python demo.py siteid your.model")
    sys.exit(-1)

siteId = sys.argv[1]
model = sys.argv[2]


# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder_snips.HotwordDetector(model, sensitivity=0.42)
from snipsbridge import SnipsHotwordBridge
hotwordBridge = SnipsHotwordBridge(siteId, detector)
hotwordBridge.start()
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder_snips.play_audio_file,
               interrupt_check=interrupt_callback,
               sleep_time=0.05)
hotwordBridge.stop()
detector.terminate()
