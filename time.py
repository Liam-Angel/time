
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
  image = cv.Canny(image, 60,200)

  contours, hierarchy = cv.findContours(image,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

  imageC = cv.cvtColor(image, cv.COLOR_BGR2RGB)
  rects = [cv.minAreaRect(c) for c in contours if (cv.minAreaRect(c)[1][0] + cv.minAreaRect(c)[1][1]) >80]

  for cnt in contours:
    M = cv.moments(cnt)
    perimeter = cv.arcLength(cnt, True)
    epsilon = 10 * perimeter
    approx_contour = cv.approxPolyDP(cnt, epsilon, True)

    #x, y, w, h = cv.boundingRect(cnt)
    #cv.rectangle(imageC, (x,y),(x+w,y+h),(255,0,0),2)
  
  for item in rects:
    point = item[0]

    rot1 = int(item[0][0])
    rot2 = int(item[0][1])

    word = str(rot1) + ", " + str(rot2)

    box = cv.boxPoints(item)
    box = np.intp(box)
    cv.drawContours(imageC,[box],0,(255,255,0),2)

    cv.putText(imageC, word,(int(point[0]), int(point[1])),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    #cv.putText(imageC, word,(int(point[0]), int(point[1])),cv.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)

    

  mindiff = 180
  pair = (None, None)
  
  for i in range(len(rects)):

    for j in range(i+1, len(rects)):
      linediff = abs(rects[i][2] - rects[j][2])
      linediff = min(linediff, 180 - linediff)
      if (cv.minAreaRect(contours[i])[1][0] + cv.minAreaRect(contours[i])[1][1]) >50 and (cv.minAreaRect(contours[j])[1][0] + cv.minAreaRect(contours[j])[1][1]) >50:

        if linediff < mindiff:
          mindiff = linediff

          pair = (contours[i], contours[j])
          rectx = int(rects[i][0][0] - rects[j][0][0])
          recty = int(rects[i][0][1] - rects[j][0][1])
          
  if pair[0] is not None:
    print(rectx, recty)
    cv.circle(imageC, (rectx, recty), 20, (255,0,0),2)


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