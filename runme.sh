#!/bin/bash

#cd hotword/beep
#lxterminal -e python3 beep.py
#cd ../../

. env/bin/activate
 
cd skills

cd shutup
lxterminal -e python3 shutup-skill.py
cd ..

cd joke
lxterminal -e python3 joke-skill.py
cd ..

cd SuperSonic
lxterminal -e sudo build/DeviceSwitch
cd ../

# weather service is too unreliable
#cd ../../snips-skill-owm
#ls
#lxterminal -e ./run.sh
