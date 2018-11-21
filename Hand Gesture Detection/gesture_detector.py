import cv2
import numpy as np
import math
import imutils
import argparse

print('Hello')

cap = cv2.VideoCapture(0)


lower = np.array([0, 48, 80], dtype = "uint8")       #Define the range of colors that seems to be skin color
upper = np.array([20, 255, 255], dtype = "uint8")

def skin_detector(grabbed,frame): #define a function to blur the "non-skin" pixels
    frame = imutils.resize(frame, width = 400)
    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    skinMask = cv2.inRange(converted, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    skinMask = cv2.erode(skinMask, kernel, iterations = 2)
    skinMask = cv2.dilate(skinMask, kernel, iterations = 2)
    skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
    skin = cv2.bitwise_and(frame, frame, mask = skinMask)
    new_frame = np.hstack([frame, skin])
    return ret, new_frame

#Counts the time when someone closes his hand
picture_frames = 0

#Counts the number of pictures taken
picture_taken =  0

#Counts the frames
frames_number =0

#"Date" of the last picture
last_picture = 0

while(1):
          #therefore this try error statement
    ret, frame = cap.read()
    ret, frame = skin_detector(ret,frame)
    frame=cv2.flip(frame,1)
    kernel = np.ones((3,3),np.uint8)

    #define region of interest
    roi=frame[100:300, 100:300]

    frames_number +=1

    cv2.rectangle(frame,(100,100),(300,300),(0,255,0),0)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)



    # define range of skin color in HSV
    lower_skin = np.array([0,20,70], dtype=np.uint8)
    upper_skin = np.array([20,255,255], dtype=np.uint8)

     #extract skin colur imagw
    mask = cv2.inRange(hsv, lower_skin, upper_skin)



    #extrapolate the hand to fill dark spots within
    mask = cv2.dilate(mask,kernel,iterations = 4)

    #blur the image
    mask = cv2.GaussianBlur(mask,(5,5),100)



    #find contours
    _,contours,hierarchy= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

   #find contour of max area(hand)
    cnt = max(contours, key = lambda x: cv2.contourArea(x))

    #approx the contour a little
    epsilon = 0.0005*cv2.arcLength(cnt,True)
    approx= cv2.approxPolyDP(cnt,epsilon,True)


    #make convex hull around hand
    hull = cv2.convexHull(cnt)

     #define area of hull and area of hand
    areahull = cv2.contourArea(hull)
    areacnt = cv2.contourArea(cnt)

    #find the percentage of area not covered by hand in convex hull
    arearatio=((areahull-areacnt)/areacnt)*100

     #find the defects in convex hull with respect to hand
    hull = cv2.convexHull(approx, returnPoints=False)
    defects = cv2.convexityDefects(approx, hull)

    # l = no. of defects
    l=0

    #code for finding no. of defects due to fingers
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(approx[s][0])
        end = tuple(approx[e][0])
        far = tuple(approx[f][0])
        pt= (100,180)


        # find length of all sides of triangle
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
        s = (a+b+c)/2
        ar = math.sqrt(s*(s-a)*(s-b)*(s-c))

        #distance between point and convex hull
        d=(2*ar)/a

        # apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57


        # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
        if angle <= 90 and d>30:
            l += 1
            cv2.circle(roi, far, 3, [255,0,0], -1)   #draw lines around hand
            cv2.line(roi,start, end, [0,255,0], 2)


    l+=1

        #print corresponding gestures which are in their ranges
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,'Pictures taken : {}'.format(picture_taken),(500,250), font, 1, (255,255,0), 3, cv2.LINE_AA) #Shows the number of pictures taken
    if l==1:
            if areacnt<2000:
                cv2.putText(frame,'Put hand in the box',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)#Tells the user to put his hand in the box
            else:
                if arearatio<12: #first case of recognizing a closed fist
                    picture_frames += 1 #implement in order to see how much time the fist is closed
                    if frames_number-last_picture>100 and picture_taken >50 : #if the fist is closed long enough and the last picture is old, it takes a picture
                        cv2.putText(frame,'Picture taken',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                        picture_taken +=1
                        picture_frames = 0 #Reset
                        last_picture = frames_number #memorize the frame number of the last picture
                    else:
                        cv2.putText(frame,'Take a picture',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                elif arearatio<17.5: #second case of recognizing a closed fist
                    picture_frames += 1
                    if frames_number-last_picture>100 and picture_frames >50 :
                        cv2.putText(frame,'Picture taken',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                        picture_frames = 0
                        picture_taken += 1
                        last_picture = frames_number
                    else :
                        cv2.putText(frame,'Take a picture',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

    elif l==2: #The hand seems to be open
            cv2.putText(frame,'Say Hello',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            if picture_frames >0 :
                picture_frames -= 1 #decrease to reset continuously

    elif l==3: #The hand seems to be open
              if arearatio<27:
                    cv2.putText(frame,'Say Hello',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                    if picture_frames > 0:
                        picture_frames -=1
              #else:
                    #cv2.putText(frame,'ok',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

    #elif l==4:
     #       cv2.putText(frame,'4',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

    #elif l==5:
            #cv2.putText(frame,'5',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

    elif l==6:
            cv2.putText(frame,'reposition',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

    else :
            cv2.putText(frame,'reposition',(10,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

        #show the windows
    #cv2.imshow('mask',mask)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(5) & 0xFF
          #Ends the program if the user press "Escape"
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()