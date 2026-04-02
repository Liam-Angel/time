
from PIL import Image
import cv2 as cv
import os, sys, inspect
import numpy as np;
import serial
import datetime
import time

cam = cv.VideoCapture(0)
#prevtime = datetime.datetime.now()

while True:
  #nowtime = datetime.datetime.now()
  ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
  ser.reset_input_buffer()  
  #print(datetime.datetime.now())

  check, frame = cam.read()
  img = cv.resize(frame,(320,240))

  image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
  image = cv.GaussianBlur(image, (11, 11), sigmaX=0)

  _, image = cv.threshold(image, 125, 255, cv.THRESH_BINARY)

  image = cv.Canny(image, 60,200)

  contours, hierarchy = cv.findContours(image,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

  imageC = cv.cvtColor(image, cv.COLOR_BGR2RGB)

  filter = [c for c in contours if (cv.minAreaRect(c)[1][0] + cv.minAreaRect(c)[1][1]) >80]
  rects = [cv.minAreaRect(c) for c in filter]

  mindiff = 180
  pair = (None, None)
  
  for i in range(len(rects)):
    for j in range(i+1, len(rects)):

      ri = rects[i][2]
      rj = rects[j][2]

      wi, hi = rects[i][1]
      wj, hj = rects[j][1]

      if wi < hi:
        ri = ri + 90
      if wj < hj:
        rj = rj + 90

      linediff = abs(ri - rj)
      linediff = min(linediff, 180 - linediff)

      if linediff < mindiff:
        mindiff = linediff
        pair = (filter[i], filter[j])
        rectx = int((rects[j][0][0] + rects[i][0][0])/2)
        recty = int((rects[j][0][1] + rects[i][0][1])/2)
          
  if pair[0] is not None:
    cv.circle(imageC, (rectx, recty), 10, (255,0,0),2)

    #if (prevtime - time).total_seconds() > 3:
    ser.write(bytes(str(rectx), encoding="utf-8"))


    #print(prevtime)
    #print((prevtime - time).total_seconds())
    

    #print(rectx)
    #time.sleep(0.1)
    #if ser.in_waiting > 0:          
      #line = ser.readline().decode('utf-8').rstrip()
      #print("line", line)

    for item in pair:
      rows, cols = (imageC.shape[:2])

      [vx, vy, x, y,] = cv.fitLine(item, cv.DIST_L2,0,0.01,0,0.01)
      if vx > 0:
        lefty = int((-x*vy/vx)+y)
        righty = int(((cols-x)*vy/vx)+y)
        cv.line(imageC,(cols-1,righty),(0,lefty),(0,255,0),2)
        #print(vx, vy, x, y)

  cv.imshow('imageC', imageC)

  key = cv.waitKey(1)
  if key == 27: 
    break

cam.release()
cv.destroyAllWindows()