
from PIL import Image
#import pytesseract
import cv2 as cv
import os, sys, inspect #For dynamic filepaths
import numpy as np;

#Find the execution path and join it with the direct reference
cam = cv.VideoCapture(0)

while True: 
  check, frame = cam.read()
  img = cv.resize(frame,(320,240))

  image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
  image = cv.GaussianBlur(image, (11, 11), sigmaX=0)

  # Threshold         120 is threshold, 255 is what we assign if it is below this
  _, image = cv.threshold(image, 150, 255, cv.THRESH_BINARY)

  # Canny
  image = cv.Canny(image, 30,200)

  contours, hierarchy = cv.findContours(image,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
  poly = None
  for cnt in contours:
    M = cv.moments(cnt)
    perimeter = cv.arcLength(cnt, True)
    epsilon = 10 * perimeter
    poly = cv.approxPolyDP(cnt, epsilon, True)

  imageC = cv.cvtColor(image, cv.COLOR_BGR2RGB)
  rects = [cv.minAreaRect(c) for c in poly if cv.contourArea(c) > 50]


 
    

  mindiff = 180
  pair = (None, None)
  
  for i in range(len(rects)):
    for j in range(i+1, len(rects)):
      linediff = abs(rects[i][2] - rects[j][2])
      linediff = min(linediff, 180 - linediff)

      if linediff < mindiff:
        mindiff = linediff
        pair = (contours[i], contours[j])

  if pair[0] is not None:
    cv.drawContours(image, pair[0], -1, (255,255,255),2) 
    cv.drawContours(image, pair[1], -1, (255,255,255),2) 

  
    for item in pair:
      rows, cols = (imageC.shape[:2])
      [vx, vy, x, y,] = cv.fitLine(item, cv.DIST_L2,0,0.01,0,0.01)
      if vx > 0:
        lefty = int((-x*vy/vx)+y)
        righty = int(((cols-x)*vy/vx)+y)
        cv.line(imageC,(cols-1,righty),(0,lefty),(0,255,0),2)

  cv.imshow('imageC', imageC)

  key = cv.waitKey(1)
  if key == 27: # exit on ESC
    break


cam.release()
cv.destroyAllWindows()