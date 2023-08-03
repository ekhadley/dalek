import cv2
import pyautogui
import numpy as np
from tqdm import trange
import time
from utils import *

# The game class defines a state of the game. It should be able to take in
# noisy data about positions of objects and clean it so that we can query
# the game class instance to get temporally-consistent information.

class wall:
    def __init__(self, xpos, top, bot):
        self.x, self.top, self.bot = xpos, top, bot
    
    def 

class game:
    def __init__(self, cam):
        self.cam = cam
        self.walls = []

    def grab(self): return self.cam.grabGame()

    def getPositions(self):
        im = self.grab()
        wpos, wnum = self.cam.findWalls()