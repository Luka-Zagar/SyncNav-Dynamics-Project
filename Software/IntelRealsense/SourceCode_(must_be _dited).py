####   tole je je snip code k se je uporablala v enm mojm prejsnm projectu in je nek dober base za naprej delat karkol povezanga s rpi4 in intel realsense kamero 
if True: #Setup
    import pyrealsense2.pyrealsense2 as rs
    import numpy as np
    import cv2
    import time
    import RPi.GPIO as IO
    IO.setwarnings(False)
    IO.setmode(IO.BOARD)
    pipeline = rs.pipeline()
    config = rs.config()

    def IndicateBoot (runner):
        while runner <= 5:
            IO.setup(PinChoice(runner), IO.OUT)
            runner+=1
        runner = 1
        while runner <= 4:
            IO.output(PinChoice(runner), 1)
            time.sleep(0.2)
            IO.output(PinChoice(runner), 0)
            runner += 1
        while runner >= 1:
            IO.output(PinChoice(runner), 1)
            time.sleep(0.2)
            IO.output(PinChoice(runner), 0)
            runner -= 1
        runner = 1

    def PinChoice (a):  ####izbereš kter motor LL=1 LE=2 NA=3 DE=4 DD=5
        a = a + a -1
        return 28+a

    def Colour(b):
        if b == 2:
            CLR = [0,0,255]
        elif b == 1:
            CLR = [255,0,0]
        else:
            CLR = [0,0,0]
        return CLR

    def FindZoneOfX (x):
        Zones = [1, 170, 340, 508, 678, 848]
        XFinder = 1
        while XFinder <=5:
            if x <=Zones[XFinder]:
                XisINzone = XFinder
                XFinder = 69
            XFinder +=1
        return XisINzone
        

    IndicateBoot (1)

    red = 2

    blue = 1

    black = 0

    o = 1

    PotrebnePikice = 7


    BlinkingCnt = 0
    engages= [False,False,False,False,False,False]
    Colours = [0,0,0,0,0,0]

    PodTemRdeče = 1.1
    PodTemModru = 2.2

    Zones = [0, 170, 340, 508, 678, 848]

    config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
    pipeline.start(config)

    IndicateBoot (69)

while True: #Workhorse program
    CntRed = [0, 0, 0, 0, 0, 0]
    CntBlue = [0, 0, 0, 0, 0, 0]
    PikcaBarva = [0,0,0]
    x = 847
    y = 479

    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    depth_image = np.asanyarray(depth_frame.get_data())
    depth_colormap1 = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03),cv2.COLORMAP_INFERNO)  # DOBRE IZBIRE SO E:HSV, INFERNO, BONE, TURBO
  
    while y > 12 and x > 16:  #####UVRSTI X V CONO IN PREVERI NJEGOVO ODDALJENOST->VEČAJ COUNTERJE
        Zone = FindZoneOfX(x)
        Distance = depth_frame.get_distance(x, y)
        if Distance == 0:
            Distance = 69
        PikcaBarva = [0,0,0]
        if Distance <= PodTemRdeče:
            CntRed[Zone] += 1
            PikcaBarva = [0,0,255]
        elif Distance <= PodTemModru:
            CntBlue[Zone] += 1
            PikcaBarva = [255 - BlinkingCnt, 0, 0]

        
        pixelsize = 8
        cv2.rectangle(depth_colormap1, (x - pixelsize, y - pixelsize), (x + pixelsize, y + pixelsize), PikcaBarva, -1)
        
        x -= 16    #######################################################################SPREMENI NAZAJ NA 16!!!!!!
        if x <= 33:
            x = 847
            y -= 12  ##############################12!!!!!!!!!!!!!!!!!!!!!

    while o <= 5: ##### ALI JE DOVOLJ PIKIC DA NAŠTIMAMO STATE????
        engages[o] = True

        if CntRed[o] > PotrebnePikice:
            Colours[o] = red
            
        elif CntBlue[o] > PotrebnePikice:
            Colours[o] = blue

        else:
            Colours[o] = black
            engages[o] = False
        cv2.rectangle(depth_colormap1, ((Zones[o - 1]), 220), (Zones[o], 260), Colour(Colours[o]), 5)         
        o += 1
        
    o=1


    while o<= 5: ######## DEJANSKO PRIŽIGANJE MOTORJEV
        
        if Colours[o] == blue:
            BlinkingCnt+=1
            if BlinkingCnt <15:
                IO.output(PinChoice(o),0)
            elif BlinkingCnt > 15:
                IO.output(PinChoice(o), 1)
            if BlinkingCnt > 25:
                BlinkingCnt=0
        else:
            IO.output(PinChoice(o),engages[o])
        o+=1
    o=1
    cv2.imshow('RealSense1', depth_colormap1)
    cv2.waitKey(1)
