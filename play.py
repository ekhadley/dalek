# i was gonna move the game playing code here..
import time

import pynput
from tqdm import trange
import cv2

from utils import red, green, blue, bold, endc
from game import game

g = game(fps=60)
kb = pynput.keyboard.Controller()

a = []

for i in (t:=trange(1_000_000, ncols=80)): #tqdm loop shows us the fps
    im = g.grab() # grab the image of the game from 2nd monitor
    g.observeBoot(im) # find the boot in the image
    g.observeWalls(im) # find the walls

    walls = g.getWallPos()
    if g.boot.live:
        walls = [w for w in walls if w[0] >= g.boot.xpos-25] #select the closest wall not yet cleared
        
        if len(walls) >= 1:
            xpos, top, bot = walls[0]
            #disp = 1*g.boot.vel*(time.time()-g.boot.time)
            disp = max(1, min(27, g.boot.vel//11)) #clip the velocity to prevent way early jumping
            
            bot += g.cam.verticalPlayingBounds[0] - 15 # aim for slightly above the lower boundary
            h = g.boot.height + disp # account for current velocity when deciding when to jump
            
            #cv2.line(im, (int(xpos-60), int(bot)), (int(xpos+60), int(bot)), color=(255,120,0), thickness=2) #this is where the boot is aiming
            
            if h > bot:
                kb.press("e")
                time.sleep(0.014) #this is how long to hold the jump. going much shorter and the keypress is not registered
                kb.release("e")
                
                #print(f"{orange}walls:{walls}, {pink}jumping from {g.boot.height:.2f}=({h}) for wall [{top:.2f}-{bot:.2f}]{endc}")
            #print(g.walls)

    if not g.boot.live: #not drawing/displaying improves fps
        g.drawBoot(im, vel=True)
        g.drawWalls(im, pos=walls)
        cv2.imshow("drg", im)
        cv2.waitKey(1)

    desc = f"{blue}{bold}{len(walls)=}, "
    L = g.boot.live
    if L: desc += f"{green}live:{L}{endc}"
    else: desc += f"{red}live:{L}{endc}"
    t.set_description(f"{desc}{blue}")
