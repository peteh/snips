#!/bin/bash

#cd hotword/beep
#lxterminal -e python3 beep.py
#cd ../../
 
cd skills

cd shutup
lxterminal -e python3 shutup-skill.py
cd ..

cd joke
lxterminal -e python3 joke-skill.py
cd ..

cd SuperSonic
lxterminal -e sudo Debug/SuperSonic
cd ../

cd ../../snips-skill-owm
ls
lxterminal -e ./run.sh
