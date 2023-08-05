import cv2, time, pynput, math, numpy as np
import matplotlib.pyplot as plt
import capture
from tqdm import trange
from utils import *

# The game class defines a state of the game. It should be able to take in
# noisy data about positions of objects and clean it so that we can query
# the game class instance to get temporally-consistent information.

class wall:
    def __init__(self, xpos, top, bot, time, speed, lifespan=2.5):
        self.xpos = xpos
        self.top = top
        self.bot = bot
        self.speed = speed
        self.locked = False
        self.lifespan = lifespan

        self.maxMem = 60

        self.positions, self.times, self.tops, self.bots = [xpos], [time], [top], [bot]
    
    def isConsistent(self, xpos, top, bot, time, gapthresh=5, dispthresh=15):
        if self.locked: return False
        bot_est, top_est = np.mean(self.bots), np.mean(self.tops)
        if abs(top_est - top) > gapthresh or  abs(bot_est - bot) > gapthresh: return False
        x_est = self.positions[-1] + self.speed*(time - self.times[-1]) # where the wall should be after dt elapsed time
        return abs(xpos - x_est) < dispthresh

    def addObservation(self, xpos, top, bot, time):
        self.positions.append(xpos)
        self.times.append(time)
        self.tops.append(top)
        self.bots.append(bot)
        if len(self.positions) == self.maxMem:
            self.locked = True
            self.top = np.mean(self.tops)
            self.bot = np.mean(self.bots)

    def getPos(self):
        xpos = self.positions[-1] + self.speed*(time.time() - self.times[-1])
        return xpos, self.top, self.bot

    def isStale(self, time):
        return time - self.times[-1] >= self.lifespan

    def __repr__(self):
        xpos, top, bot = self.getPos()
        return f"{green}x:{xpos:.2f},{yellow}[{top:.2f}:{bot:.2f}]{endc}"

class boot:
    def __init__(self, height, xpos, xHome, size=24):
        self.height = height
        self.xpos = xpos
        self.xHome = xHome
        self.time = time.time()
        self.vel = 0
        self.live = False
        
        if isinstance(size, tuple): self.size = size
        if isinstance(size, int): self.size = (size, size)

    def observe(self, xpos, height, t):
        self.live = abs(xpos - self.xHome) < 10
        self.xpos = xpos
        self.vel = (height - self.height)/(t - self.time)
        self.time = t
        self.height = height
    def getHeight(self): return self.height


class game:
    def __init__(self, fps=60, window=2, wallLifespan=2.5):
        self.bootSize = (24,22)
        self.walls = []
        # all spatial units are pixels, time units is real time seconds
        self.scrollVel = -146.4 # importantly negative
        self.jumpVel = -290
        self.gravity = 0
        self.bootMaxH, self.bootMinH = 330, 100
        self.bootXpos = 230
        self.newWallMinX = 380

        self.wallLifespan = wallLifespan
        
        self.boot = boot(50, self.bootXpos, self.bootXpos, size=self.bootSize)
        self.cam = capture.reader(fps=fps, window=window, bootSize=self.bootSize)
        self.cam.start()

    def grab(self): return self.cam.grabGame()
    def getBootHeight(self): return self.boot.getHeight()
    def observeBoot(self, im):
        x, y = self.cam.bootPos(im)
        self.boot.observe(x, y, time.time())

    #[(50, 84, 202), (254, 231, 347), (449, 258, 375)] typical wall positions
    def observeWalls(self, im, gapmin=70, gapmax=250, dispmin=10):
        wpos = self.cam.findWalls(im, gapmin=gapmin, gapmax=gapmax, jumpmin=2600)
        wpos = [e for e in wpos if gapmax>e[2]-e[1]>gapmin]
        if len(wpos) == 0: return wpos
        for pos in wpos:
            attributed = False
            xpos, top, bot = pos
            t = time.time()
            for w in self.walls:
                if abs(w.positions[-1] - xpos) <= dispmin: attributed = True
                cons = w.isConsistent(xpos, top, bot, t)
                if cons and not attributed:
                    attributed = True
                    w.addObservation(xpos, top, bot, t)
            if not attributed and xpos > self.newWallMinX:
                self.walls.append(wall(xpos, top, bot, t, self.scrollVel, lifespan=self.wallLifespan))

    def getWallPos(self):
        self.walls = [e for e in self.walls if not e.isStale(time.time())]
        return sorted([e.getPos() for e in self.walls], key= lambda w: w[0])
    def drawBoot(self, im, pos=None, vel=False, vscale=7, color=(0,0,255)):
        pos = (self.bootXpos, self.boot.height) if pos is None else pos
        x, y = pos
        self.cam.drawBoot(im, pos, color=color)
        if vel: cv2.line(im, (x, y), (x, int(y + self.boot.vel//vscale)), color=color, thickness=3)
    def drawWalls(self, im, pos=None):
        pos = self.getWallPos() if pos is None else pos
        self.cam.drawWalls(im, pos)


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