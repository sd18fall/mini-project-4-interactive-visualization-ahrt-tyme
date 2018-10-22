""" Experiment with face detection and image filtering using OpenCV """

import cv2
import numpy as np
import math
import copy

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('~/Toolboxes/CompVis/Spin.avi')

class Color():
    """A container for blue, green, red values to return to OpenCV"""
    def __init__(self, B, G=0, R=0):
        if type(B) != int:
            R = int(B[2])
            G = int(B[1])
            B = int(B[0])
        self.B = B
        self.G = G
        self.R = R

    def __str__(self):
        return "({}, {}, {})".format(self.B, self.G, self.R)

    def tuple(self):
        return (self.B, self.G, self.R)

    def list(self):
        return [self.B, self.G, self.R]

black = Color(0,0,0)
white = Color(255,255,255)
red = Color(0,0,255)
orange = Color(0,140,255)
yellow = Color(0,215,255)
green = Color(0,255,0)
cyan = Color(255,255,0)
blue = Color(255,0,0)
purple = Color(211,0,148)
magenta = Color(255,0,255)


class Pixel():
    """A container for x, y, and color values to be packed into changes lists and groups"""
    def __init__(self, x, y, c=black):
        self.x = x
        self.y = y
        if type(c) != Color:
            c = Color(c)
        self.color = c

    # def __repr__(self):
    #     return "("+str(self.x)+' , '+str(self.y)+")"

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.color)

    def getXY(self):
        return (self.x, self.y)

class Group():
    """Batches of pixels"""
    def __init__(self, pixelList):
        self.pixels = pixelList

    # def __repr__(self):
    #     return self.pixels

    def addPixels(self, pixelList):
        if type(pixelList) != list:
            pixelList = [pixelList]
        self.pixels += pixelList

    def size(self):
        return len(self.pixels)

    def __str__(self):
        ret = ''
        for pixel in self.pixels:
            ret += str(pixel)
        return ret

def isDif(pixelColor1,pixelColor2):
    currBlue = pixelColor1.B
    lastBlue = pixelColor2.B
    currGreen = pixelColor1.G
    lastGreen = pixelColor2.G
    currRed = pixelColor1.R
    lastRed = pixelColor2.R

    changeThresh = 20
    blueChanged = abs(currBlue-lastBlue) > changeThresh
    greenChanged = abs(currGreen-lastGreen) > changeThresh
    redChanged = abs(currRed-lastRed) > changeThresh
    ret = blueChanged and redChanged and greenChanged
    return ret

def findMove(frame, lastFrame, lastLastFrame):
    """Detects changing pixel colors and reports their x,y coordinates"""
    changes = Group([]) #list of x,y tuples of pixels that changed
    for y in range(0, height-1, cS):
        for x in range(0, width-1, cS):
            if isDif(Color(frame[y][x]),Color(lastFrame[y][x])) and isDif(Color(lastFrame[y][x]),Color(lastLastFrame[y][x])):
                changes.addPixels(Pixel(x,y,frame[y][x]))
    return changes

def isDiagonalTo(pixel1, changes):
    """checks if a pixel in changes has another pixel diagonally adjacent to it"""
    for pixel2 in changes.pixels:
        # print('xDiff:', pixel1.x-pixel2.x, 'yDiff:', pixel1.y-pixel2.y, 'testing against cS of:', cS)
        if abs(pixel1.x-pixel2.x) == cS and abs(pixel1.y-pixel2.y) == cS:
            return True
    return False

def isLine(pixel1, changes):
    """checks if a pixel in changes has another horizontally or vertically pixel adjacent to it"""
    for pixel2 in changes.pixels:
        if abs(pixel1.x-pixel2.x) == cS and pixel1.y == pixel2.y:
            return True
        elif abs(pixel1.y-pixel2.y) == cS and pixel1.x == pixel2.x:
            return True
    return False

def isTouching(pixel1,pixel2):
    """checks if a pixel 2 pixels are touching diagonally, vertically or horizontally"""
    return isDiagonalTo(pixel1,pixel2) or isLine(pixel1,pixel2)

def findDiagonals(changes):
    """Detects a diagonal pair of changing pixel colors and reports their x,y coordinates"""
    diagonalChanges = Group([])
    for pixel in changes.pixels:
        if isDiagonalTo(pixel,changes):
            diagonalChanges.addPixels(pixel)
    return diagonalChanges

def findLines(changes):
    """Detects a square of changing pixel colors and reports their x,y coordinates"""
    lineChanges = Group([])
    for pixel in changes.pixels:
        if isLine(pixel,changes):
            lineChanges.addPixels(pixel)
    return lineChanges


def showMove(frame, changes, color):
    """Changes the color of everything that changed in frame"""
    for pixel in changes.pixels:
        (x,y) = pixel.x, pixel.y
        cv2.rectangle(frame, (x,y), (x+cS, y+cS), color.tuple(), -1)
        # frame[y:(y+cS)][x:(x+cS)] = [0,0,255]
    return frame

def findThisGroup(foundPixel, changes):
    adjPixels = []
    for pixel in changes:
        if isTouching(foundPixel, pixel):
            adjPixels.append(pixel)
    if len(adjPixels) == 0:
        return [foundPixel]
    changes.remove(foundPixel)
    res = [foundPixel]
    for pixel in adjPixel:
        res += findThisGroup (pixel,changes)
    return res

def findAllGroups(changes):
    """Finds the groups of changed pixels in frame"""
    groupToSplit = copy.deepcopy(changes)
    contigGroups = []
    for pixel in groupToSplit.pixels:
        contigGroups = contigGroups + findThisGroup(pixel, groupToSplit)
        # groupToSplit.remove(those pixels)

def findLargestGroup(groups):
    """Finds the largest group of changed pixels in frame"""
    groupList = findAllGropus(changes)
    #groupName.size each group
    #find the max amond the sizes, return that group

#Cheating! Doing things once so we don't redefine constants constantly
ret, lastFrame = cap.read()
lastLastFrame = lastFrame
lastMajorChanges = Group([])
height, width = lastFrame.shape[:2]
cS = 7

while(True):
    ret, frame = cap.read()

    changes = findMove(frame, lastFrame, lastLastFrame)
    majorChanges = findDiagonals(changes)
    #changes is a Group object
    frame = showMove(frame, majorChanges, magenta)
    frame = showMove(frame, lastMajorChanges, cyan)

    # Create window displaying frame, with Colors drawn on top
    cv2.imshow('Frame', frame)

    lastLastFrame = lastFrame
    lastFrame = frame
    lastMajorChanges = majorChanges

    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break



# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()


#Debugging and testing dumping ground:
#to use, change != to == and the while(True) to while(False)
if __name__ != "__main__":
    newGroup = Group([])
    print(newGroup)
    p1 = Pixel(3, 8)
    p2 = Pixel(5,2)
    p3 = Pixel(2, 1, [0,255,0])
    p4 = Pixel(3,1, blue)
    c1 = Color(1,1,1)
    c2 = Color([2,2,2])
    c3 = Color ([3,2,2])

    # newGroup.addPixels([p1,p2,p3,p4])
    # print(type(newGroup.pixels))
    # print(newGroup.pixels)
    # newGroup.addPixels([p1,p1,p2])
    # print(newGroup.pixels)
    # print(p1.color, p2.color, p3.color, p4.color)

    print(type(c1))
    print(type(c2.tuple()))
    bs = c2.tuple()
    print(bs)
    print(type(bs))
    bull = c3.list()
    print(bull)
    print(type(bull))
    print(str(c3))
