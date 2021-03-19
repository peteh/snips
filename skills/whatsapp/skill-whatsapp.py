from yowsup.stacks import YowStackBuilder
from layer import MqttLayer
from layer import EchoLayer
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.common import YowConstants
from yowsup.profile.profile import YowProfile
from yowsup.config.manager import ConfigManager
from yowsup.config.v1.config import Config

stackBuilder = YowStackBuilder()

stack = stackBuilder\
        .pushDefaultLayers()\
        .push(MqttLayer())\
        .build()
config_manager = ConfigManager()
config = config_manager.load("36309040975")
profile = YowProfile(config.login,config)
stack.setProfile(profile)

stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal

stack.loop() #this is the program mainloop`
