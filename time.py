
from PIL import Image
import cv2 as cv
import numpy as np;
import serial

cam = cv.VideoCapture(0, cv.CAP_V4L2)
cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
cam.set(cv.CAP_PROP_FPS, 30)

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer() 

while True:
  
  
  check, frame = cam.read()
  

  image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  image = cv.GaussianBlur(image, (11, 11), sigmaX=0)

  _, image = cv.threshold(image, 125, 255, cv.THRESH_BINARY)

  image = cv.Canny(image, 60,200)

  contours, hierarchy = cv.findContours(image,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)


  filter = [c for c in contours if (cv.minAreaRect(c)[1][0] + cv.minAreaRect(c)[1][1]) >80]
  rects = [cv.minAreaRect(c) for c in filter]

  mindiff = 180
  pair = (None, None)
  angle = 0

  if len(rects) == 1:
    r = rects[0][2]

    w, h = rects[0][1]

    if w < h:
        r = r + 90

    mapp = np.interp(int(r), [0, 180], [0, 640])
    ser.write(bytes(str(mapp) + '\n', encoding="utf-8"))



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
      dist = (rects[j][0][0] - rects[i][0][0])

      if linediff < mindiff and dist > 8:
        mindiff = linediff
        pair = (filter[i], filter[j])
        rectx = int((rects[j][0][0] + rects[i][0][0])/2)
        recty = int((rects[j][0][1] + rects[i][0][1])/2)
        angle = rj
          
  if pair[0] is not None:
    cv.circle(frame, (rectx, recty), 10, (255,0,0),2)

    mapp = np.interp(int(angle), [0, 180], [0, 640])
    
    if rectx in range(290, 350):
      ser.write(bytes(str(int(mapp)) + '\n', encoding="utf-8"))
    else:
     ser.write(bytes(str(rectx) + '\n', encoding="utf-8"))
     #print(rectx)

    if ser.in_waiting > 0:          
      line = ser.readline().decode('utf-8').rstrip()
      print("line", line)

    for item in pair:
      rows, cols = (frame.shape[:2])

      [vx, vy, x, y,] = cv.fitLine(item, cv.DIST_L2,0,0.01,0,0.01)
      if vx > 0:
        lefty = int((-x*vy/vx)+y)
        righty = int(((cols-x)*vy/vx)+y)
        cv.line(frame,(cols-1,righty),(0,lefty),(0,255,0),2)

  cv.imshow('imageC', frame)

  key = cv.waitKey(1)
  if key == 27: 
    break

cam.release()
cv.destroyAllWindows()