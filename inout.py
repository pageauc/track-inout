#!/usr/bin/env python
progname = "inout.py"
ver = "version 0.6"

"""
track-inout  written by Claude Pageau pageauc@gmail.com
Windows, Unix, Raspberry (Pi) - python opencv2 motion tracking
using web camera or raspberry pi camera module.

This is a python opencv2 motion tracking demonstration program.
It will detect motion in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.  Object is tracked
until it crosses a vert or horiz centerline, Enter and Leave data
is update and optionaly recorded including optional image.
Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is a my YouTube video demonstrating this demo program using a
Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

This will run on a Windows, Unix OS using a Web Cam or a Raspberry Pi
using a Web Cam or RPI camera module installed and configured

To do a quick install On Raspbian or Debbian Copy and paste command below
into a terminal sesssion to download and install motion_track demo.
Program will be installed to ~/motion-track-demo folder

curl -L https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh | bash

How to Run

cd ~/track-inout
./inout.py

"""
print("%s %s Track Enter and Leave Activity using python and OpenCV" % (progname, ver))
print("Loading Please Wait ....")

import os
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

# Check for variable file to import and error out if not found.
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    print("ERROR - Missing config.py file - Could not find Configuration file %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/motion-track/master/config.py"
    print("Attempting to Download new config.py file")
    print("from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR - Download of config.py Failed")
        print("   Try Rerunning the motion-track-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % ( progName ))
        quit(1)
    f = open('config.py','wb')
    f.write(wgetfile.read())
    f.close()

# Read Configuration variables from config.py file
from config import *

# import the necessary packages
import logging
import time
import datetime
import cv2
from threading import Thread

try:  # Bypass loading picamera library if not available eg. UNIX or WINDOWS
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except:
    WEBCAM = True
    pass

if WEBCAM:   # Get centerline for movement counting
    x_center = WEBCAM_WIDTH/2
    y_center = WEBCAM_HEIGHT/2
    x_max = WEBCAM_WIDTH
    y_max = WEBCAM_HEIGHT
    x_buf = WEBCAM_WIDTH/10
    y_buf = WEBCAM_HEIGHT/10
else:
    x_center = CAMERA_WIDTH/2
    y_center = CAMERA_HEIGHT/2
    x_max = CAMERA_HEIGHT
    y_max = CAMERA_WIDTH
    x_buf = CAMERA_WIDTH/10
    y_buf = CAMERA_HEIGHT/10

logFilePath = baseDir + baseFileName + ".log"
if verbose:
    print("Logging to Console per Variable verbose=True")
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
elif save_log:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=logFilePath,
                    filemode='w')
else:
    print("Logging Disabled per Variable verbose=False")
    logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if not os.path.isdir(image_path):
    logging.info("Creating Image Storage Folder %s", image_path )
    os.makedirs(image_path)


# Color data for OpenCV lines and text
cvWhite = (255,255,255)
cvBlack = (0,0,0)
cvBlue = (255,0,0)
cvGreen = (0,255,0)
cvRed = (0,0,255)

color_mo = cvRed  # color of motion circle or rectangle
color_txt = cvBlue   # color of openCV text and centerline

font = cv2.FONT_HERSHEY_SIMPLEX
FRAME_COUNTER = 1000  # used when show_fps=True  Sets frequency of display
quote = '"'  # Used for creating quote delimited log file of speed data

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
class WebcamVideoStream:
    def __init__(self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH, CAM_HEIGHT=WEBCAM_HEIGHT):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3,CAM_WIDTH)
        self.stream.set(4,CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
def show_FPS(start_time,frame_count):
    if debug:
        if frame_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            FPS = float(frame_count / duration)
            logging.info("Processing at %.2f fps last %i frames", FPS, frame_count)
            frame_count = 0
            start_time = time.time()
        else:
            frame_count += 1
    return start_time, frame_count

#-----------------------------------------------------------------------------------------------
def get_image_name(path, prefix):
    # build image file names by number sequence or date/time
    rightNow = datetime.datetime.now()
    filename = ("%s/%s-%04d%02d%02d-%02d%02d%02d.jpg" %
          ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second ))
    return filename

#-----------------------------------------------------------------------------------------------
def log_to_csv_file(data_to_append):
    log_file_path = baseDir + baseFileName + ".csv"
    if not os.path.exists(log_file_path):
        open( log_file_path, 'w' ).close()
        f = open( log_file_path, 'ab' )
        f.close()
        logging.info("Create New Data Log File %s", log_file_path )
    filecontents = data_to_append + "\n"
    f = open( log_file_path, 'a+' )
    f.write( filecontents )
    f.close()
    return

#-----------------------------------------------------------------------------------------------
def crossed_x_centerline(enter, leave, movelist):
    xbuf = 20  # buffer space on either side of x_center to avoid extra counts
    # Check if over center line then count
    if len(movelist) > 1:  # Are there two entries
        if ( movelist[0] <= x_center
                   and  movelist[-1] > x_center + x_buf):
            leave += 1
            movelist = []
        elif ( movelist[0] > x_center
                   and  movelist[-1] < x_center - x_buf):
            enter += 1
            movelist = []
    return enter, leave, movelist

#-----------------------------------------------------------------------------------------------
def crossed_y_centerline(enter, leave, movelist):
    # Check if over center line then count
    if len(movelist) > 1:  # Are there two entries
        if ( movelist[0] <= y_center
                   and  movelist[-1] > y_center + y_buf ):
            leave += 1
            movelist = []
        elif ( movelist[0] > y_center
                   and  movelist[-1] < y_center - y_buf ):
            enter += 1
            movelist = []
    return enter, leave, movelist

#-----------------------------------------------------------------------------------------------
def track():
    image1 = vs.read()   # initialize image1 (done once)
    try:
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    except:
        vs.stop()
        print("Problem Connecting To Camera Stream.")
        print("Restarting Camera.  One Moment Please .....")
        time.sleep(4)
        return

    if window_on:
        print("Press q in window Quits")
    else:
        print("Press ctrl-c to Quit")
    print("Start Tracking Enter Leave Activity ....")

    if not verbose:
        print("Note: Console Messages Suppressed per verbose=%s" % verbose)

    big_w = int(CAMERA_WIDTH * WINDOW_BIGGER)
    big_h = int(CAMERA_HEIGHT * WINDOW_BIGGER)
    cx, cy, cw, ch = 0, 0, 0, 0   # initialize contour center variables
    frame_count = 0  #initialize for show_fps
    start_time = time.time() #initialize for show_fps

    still_scanning = True
    movelist = []
    move_time = time.time()
    enter = 0
    leave = 0
    while still_scanning:
        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA
        image2 = vs.read()  # initialize image2

        if WEBCAM:
            if ( WEBCAM_HFLIP and WEBCAM_VFLIP ):
                image2 = cv2.flip( image2, -1 )
            elif WEBCAM_HFLIP:
                image2 = cv2.flip( image2, 1 )
            elif WEBCAM_VFLIP:
                image2 = cv2.flip( image2, 0 )

        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        grayimage1 = grayimage2  # save grayimage2 to grayimage1 ready for next image2
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold( differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY )
        try:
            thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        except:
            contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        if contours:
            total_contours = len(contours)  # Get total number of contours
            #cx, cy, cw, ch = 0, 0, 0, 0
            for c in contours:              # find contour with biggest area
                found_area = cv2.contourArea(c)  # get area of next contour
                # find the middle of largest bounding rectangle
                if found_area > biggest_area:
                    motion_found = True
                    biggest_area = found_area
                    (x, y, w, h) = cv2.boundingRect(c)
                    cx = int(x + w/2)   # put circle in middle of width
                    cy = int(y + h/2)   # put circle in middle of height
                    cw, ch = w, h

            if motion_found:
                move_timer = time.time() - move_time
                if (move_timer >= movelist_timeout):
                    movelist = []
                    #logging.info("Exceeded %.2f Seconds - Clear movelist" % movelist_timeout)
                move_time = time.time()

                old_enter = enter
                old_leave = leave
                if centerline_vert:
                    movelist.append(cx)
                    enter, leave, movelist = crossed_x_centerline(enter, leave, movelist)
                else:
                    movelist.append(cy)
                    enter, leave, movelist = crossed_y_centerline(enter, leave, movelist)

                if not movelist:
                    if enter > old_enter:
                        prefix = "enter"
                    elif leave > old_leave:
                        prefix = "leave"
                    else:
                        prefix = "error"

                    logging.info("enter=%i leave=%i Diff=%i" % ( enter, leave, abs(enter-leave)))

                    # Save image
                    if save_images:
                        filename = get_image_name( image_path, prefix)
                        save_image = vs.read()
                        logging.info("Save: %s", filename)
                        cv2.imwrite(filename, save_image)

                    # Save data to csv file
                    if save_CSV:
                        log_time = datetime.datetime.now()
                        log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s,%s%02d%s" %
                                       ( quote, log_time.year, log_time.month,
                                         log_time.day, quote,
                                         quote, log_time.hour, quote,
                                         quote, log_time.minute, quote,
                                         quote, log_time.second, quote ))

                        log_csv_text = ("%s,%s%s%s,%s%s%s,%i,%i,%i,%i,%i" %
                                    ( log_csv_time,
                                      quote, prefix, quote,
                                      quote, filename, quote,
                                      cx, cy, cw, ch, cw * ch ))
                        log_to_csv_file( log_csv_text )

                if window_on:
                    # show small circle at motion location
                    if SHOW_CIRCLE:
                        cv2.circle(image2,(cx,cy),CIRCLE_SIZE,(color_mo), LINE_THICKNESS)
                    else:
                        cv2.rectangle(image2,(cx,cy),(x+cw,y+ch),(color_mo), LINE_THICKNESS)
                if show_moves:
                    logging.info("cx,cy(%i,%i) C:%2i A:%ix%i=%i SqPx" %
                                      (cx ,cy, total_contours, cw, ch, biggest_area))
        if show_fps:
            start_time, frame_count = show_FPS(start_time, frame_count)

        if window_on:
            if centerline_vert:
                cv2.line( image2,( x_center, 0 ),( x_center, y_max ),color_txt, 2 )
            else:
                cv2.line( image2,( 0, y_center ),( x_max, y_center ),color_txt, 2 )
            img_text = ("ENTER %i          LEAVE %i" % (enter, leave))
            cv2.putText( image2, img_text, (35,15), font, font_scale,(color_txt),1)

            if diff_window_on:
                cv2.imshow('Difference Image',differenceimage)
            if thresh_window_on:
                cv2.imshow('OpenCV Threshold', thresholdimage)
            if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
                image3 = cv2.resize( image2,( big_w, big_h ))
            cv2.imshow('Press q in Window Quits)', image3)

            # Close Window if q pressed while mouse over opencv gui window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                vs.stop()
                print("End Motion Tracking")
                quit(0)

#-----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    while True:
        try:
            # Save images to an in-program stream
            # Setup video stream on a processor Thread for faster speed
            if WEBCAM:   #  Start Web Cam stream (Note USB webcam must be plugged in)
                print("Initializing USB Web Camera ....")
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                time.sleep(4.0)  # Allow WebCam to initialize
            else:
                print("Initializing Pi Camera ....")
                vs = PiVideoStream().start()
                vs.camera.rotation = CAMERA_ROTATION
                vs.camera.hflip = CAMERA_HFLIP
                vs.camera.vflip = CAMERA_VFLIP
                time.sleep(2.0)  # Allow PiCamera to initialize
            track()
        except KeyboardInterrupt:
            vs.stop()
            print("")
            print("+++++++++++++++++++++++++++++++++++")
            print("User Pressed Keyboard ctrl-c")
            print("%s %s - Exiting" % (progname, ver))
            print("+++++++++++++++++++++++++++++++++++")
            print("")
            quit(0)



