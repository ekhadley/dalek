import cv2, pynput, scipy, numpy as np
from tqdm import tgrange

purple = '\033[95m'
blue = '\033[94m'
cyan = '\033[96m'
lime = '\033[92m'
yellow = '\033[93m'
red = "\033[38;5;196m"
pink = "\033[38;5;206m"
orange = "\033[38;5;202m"
green = "\033[38;5;34m"
gray = "\033[38;5;8m"
colors = [purple, blue, cyan, lime, yellow, red, pink, orange, green, gray]

bold = '\033[1m'
underline = '\033[4m'
endc = '\033[0m'

def diff(arr):
    a = np.array(arr, copy=True)
    x1 = np.append(a, [0])
    x2 = np.insert(a, 0, 0)
    return x1-x2

def jumps(arr, height=1300, minDist=60):
    d = diff(arr)
    ppeakx, pstatx = scipy.signal.find_peaks(d, height=height, distance=minDist)
    npeakx, pstatx = scipy.signal.find_peaks(-d, height=height, distance=minDist)
    peakx = np.sort(np.append(ppeakx, npeakx))
    ptx = peakx
    pty = [d[zz] for zz in ptx]
    return ptx, pty

def wallBounds(ptx, pty, xmin=100, xmax=250, ymin=3000):
    for i, z in enumerate(zip(ptx[:-1], pty[:-1])):
        x1, y1 = z
        x2, y2 = ptx[i+1], pty[i+1]
        xdiff, ydiff = x2-x1, y2-y1

        if xmax > xdiff > xmin and ydiff > ymin:
            return x1, x2
    return -1, -1


def imscale(img, s):
    try:
        w, h, d = np.shape(img)
    except:
        w, h = np.shape(img)
    assert w*h > 0, "empty src image"
    return cv2.resize(img, (round(len(img[0])*s), round(len(img)*s)), interpolation=cv2.INTER_NEAREST)