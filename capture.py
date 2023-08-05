import pynput, dxcam, time, cv2, numpy as np
from tqdm import trange
from utils import *
import matplotlib.pyplot as plt
import scipy

class reader:
    def __init__(self, window=2, fps=60, bootSize=(24, 24), wallWidth=30):
        #drg = pyautogui.getWindowsWithTitle("Deep Rock Galactic")[0]
        #box = (0, 0, drg.width-100, drg.height)
        self.cam = dxcam.create(output_idx=window, output_color="BGRA")
        self.fps = fps
        self.started = self.cam.is_capturing

        self.width, self.height = self.cam.width, self.cam.height
        self.winshape, self.wincenter = (self.width, self.height), (self.width//2, self.height//2)
        
        self.gameCorners = np.int32([[760, 190],[1160, 190], [700, 890], [1220, 890]])
        pad = -10
        self.gameRegion = np.int32([[700-pad, 137-pad],[1220+pad, 137-pad], [700-pad, 942+pad], [1220+pad, 942+pad]])
        self.gameSize = (self.gameRegion[1][0]-self.gameRegion[0][0], self.gameRegion[2][1]-self.gameRegion[0][1])

        self.wallWidth = wallWidth
        if isinstance(bootSize, int): self.bootSize = (bootSize, bootSize)
        else: self.bootSize = bootSize

        self.g1, self.g2 = np.int32([0, 205, 0, 0]), np.int32([210, 255, 195, 255])
        self.verticalPlayingBounds = (186, -186)

    def start(self):
        self.cam.start(target_fps=self.fps)
        self.started = True
    def stop(self):
        self.cam.stop()
        self.started = False

    def grab(self, corners=False, region=False, correct=False):
        if self.started: im = self.cam.get_latest_frame()
        else: im = self.cam.grab()
        if corners: im = self.drawGameCorners(im)
        if region: im = self.drawGameRegion(im)
        if correct: im = self.correctPerspective(im)
        return im
    def cropGameRegion(self, im):
        return im[self.gameRegion[0][1]:self.gameRegion[2][1], self.gameRegion[0][0]:self.gameRegion[1][0]]
    def correctPerspective(self, im):
        M = cv2.getPerspectiveTransform(np.float32(self.gameCorners), np.float32(self.gameRegion))
        im = cv2.warpPerspective(im, M, self.winshape)
        return im
    def grabGame(self):
        im = self.grab(correct=True)
        im = self.cropGameRegion(im)
        return im

    def drawGameCorners(self, im):
        for corner in self.gameCorners:
            cv2.circle(im, tuple(corner), 10, (0, 0, 255), 2)
        return im
    def drawGameRegion(self, im):
        for corner in self.gameRegion:
            cv2.circle(im, tuple(corner), 10, (0, 255, 0), 2)
        return im
    def drawBoot(self, im, pos, color=(30, 120, 255)):
        x, y = pos
        x, y = int(x), int(y)
        w, h = self.bootSize
        im = cv2.rectangle(im, (x-w//2, y-h//2), (x+w//2, y+h//2), color=color, thickness=2)
    def drawWall(self, im, pos, wallWidth=None):
        ww = self.wallWidth if wallWidth is None else wallWidth
        x, gtop, gbot = pos
        vtop, vbot = self.verticalPlayingBounds
        pt1 = (int(x-ww/2), int(gtop+vtop))
        pt2 = (int(x+ww/2), int(gbot+vtop))
        im = cv2.rectangle(im, pt1, pt2, color=(200, 20, 255), thickness=1)
    def drawWalls(self, im, poss):
        for pos in poss:
            self.drawWall(im, pos)
    
    def bootPos(self, im):
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)[1]
        M = cv2.moments(thresh)
        try:
            x = int(M["m10"] / M["m00"])
            y = int(M["m01"] / M["m00"])
        except:
            return (-1, -1)
        return (x, y)
    def findWalls(self, im, g1=None, g2=None, returnIm=False, wallWidth=None, gapmin=60, gapmax=250, jumpmin=2800):
        if g1 is None: g1, g2 = self.g1, self.g2
        ww = self.wallWidth if wallWidth is None else wallWidth
        grn = cv2.inRange(im, g1, g2)
        vtop, vbot = self.verticalPlayingBounds
        cols = np.sum(grn[vtop:vbot,:], axis=0)
        avgs = scipy.ndimage.uniform_filter1d(cols, size=35)
        wallx = np.sort(scipy.signal.find_peaks(avgs, prominence=3000)[0])
        
        wallpos = []
        for wx in wallx:
            slc = grn[vtop:vbot,wx-ww//2:wx+ww//2]
            rows = np.sum(slc, axis=1)
            gtop, gbot = wallBounds(*jumps(rows), xmin=gapmin, xmax=gapmax, ymin=jumpmin)
            wallpos.append((wx, gtop, gbot))
        if returnIm: return wallpos
        return wallpos
        