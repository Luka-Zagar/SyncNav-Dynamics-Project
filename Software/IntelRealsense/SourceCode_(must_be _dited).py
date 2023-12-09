import pyrealsense2 as rs
import numpy as np
import cv2
import time

print ("\n\nVISUS software rev2 2021...........See with me V3\n\nSoftware in development by Nik Stanojevic and Val Vidmar\nPress 'x' to exit program")

pipeline = rs.pipeline()
config = rs.config()
States =  [0,0,0,0,0,0]

LL=1#navezuje se na counter "o", 
LE=2
NA=3
DE=4
DD=5

thr1=1
thr2=1.6

#..................................
preset=1        #1,2,3
targetFPS=90     #6,15,30,60,90 
#..................................

if preset==1:
    width=848
    height=480

elif preset==2:
    width=640
    height=360

else:
    width=480
    height=270


OneWidth=int(width/5)

config.enable_stream(rs.stream.depth, width, height, rs.format.z16, targetFPS)
pipeline.start(config)
Zones=[1,OneWidth,(OneWidth*2),(OneWidth*3),(OneWidth*4),width]

startTime=0
newTime=0
timec=0
totalFPS=0
frameNum=0


while True:

    startTime=time.time()

    shortDistance=[0,0,0,0,0]
    mediumDistance=[0,0,0,0,0]
    longDistance=[0,0,0,0,0]

    MinDist = [100,100,100,100,100,100]
    CntARR1 = [0,0,0,0,0,0]
    CntARR2 = [0,0,0,0,0,0]
    States =  [0,0,0,0,0,0]
    minLenght=100
    x=31 #number of pixels skiped in x axis
    y=23 #number of pixels skiped in y axis
    o=1
    try:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_colormap1 = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_INFERNO)#DOBRE IZBIRE SO Å E:HSV, INFERNO, BONE, TURBO

        while y < height and x < width:
            if y>300:
                thr2=1.1
            else:
                thr2=1.6
        
            while True:
                if x < (OneWidth * o):
                    Zones[0] = o
                    if CntARR1[o] > 10:
                        if Zones[0] != 5:
                            x += OneWidth
                            Zones[0] += 1
                    break
                o += 1
            o = 1
            dist_to_center = depth_frame.get_distance(x,y)
            if dist_to_center == 0:
                dist_to_center=69

            if dist_to_center < minLenght:
                minLenght=dist_to_center
            if x<=(Zones[0]*OneWidth):
                if MinDist[Zones[0]]>dist_to_center:
                    MinDist[Zones[0]]=dist_to_center
                if dist_to_center <= thr1:
                    CntARR1[Zones[0]] += 1
                if dist_to_center > thr1 and dist_to_center <= thr2:
                    CntARR2[Zones[0]] += 1
            Zones[0] = 1
            if dist_to_center <= thr1:
                cv2.rectangle(depth_colormap1, (x - 2, y - 2), (x + 2, y + 2), (0, 0, 255), 2)
            elif dist_to_center > thr1 and dist_to_center <= thr2:
                cv2.rectangle(depth_colormap1, (x - 2, y - 2), (x + 2, y + 2), (255, 0, 0), 2)
            else:
                cv2.rectangle(depth_colormap1, (x - 2, y - 2), (x + 2, y + 2), (0, 0, 0), 2)

            x += 32
            if x >= width:
                x = 31
                y += 24
        Zones = [1, int(OneWidth), int(OneWidth * 2), int(OneWidth * 3), int(OneWidth * 4), int(width)]

        while o <= 5:
            if CntARR1[o]>10:
                States[o] = 1
                shortDistance[o-1]=1
                cv2.rectangle(depth_colormap1, ((Zones[o-1]), 220), (Zones[o], 260), (0, 0, 255), 5)
            elif CntARR2[o]>10:
                States[o] = 1.1
                mediumDistance[o-1]=1
                cv2.rectangle(depth_colormap1, ((Zones[o-1]), 220), (Zones[o], 260), (255, 0, 0), 5)
            else:
                longDistance[o-1]=1
                cv2.rectangle(depth_colormap1, ((Zones[o-1]), 220), (Zones[o], 260), (0, 0, 0), 5)
                States[o] = 0
            o+=1
        
        #imageBig = cv2.resize(depth_colormap1, (0, 0), fx=1.7, fy=1.7)
        #cv2.imshow('RealSense1', imageBig)
        if cv2.waitKey(25) & 0xFF == ord('x'):
            print("FPS: ", round(totalFPS/frameNum,2),"\nSequence closed successfully!" )
            break
        cv2.imshow('RealSense1', depth_colormap1)
        cv2.waitKey(1)
        newTime=time.time()
        timec=newTime-startTime
        fps=1/timec
        frameNum+=1
        totalFPS+=fps
        if targetFPS>(fps+1):
            print("Low FPS warning!!!")
        '''print("------------------------")
        print("Long:   ",longDistance)
        print("Medium: ",mediumDistance)
        print("Short:  ",shortDistance)'''
        print("FPS: ",round(fps,2))

    except:
        print("Camera not connected!!!")
        try:
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.depth, width, height, rs.format.z16, targetFPS)
            pipeline.start(config)
        except:
            print("Detecting for camera...")
