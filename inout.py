#!/usr/bin/env python
"""
track-inout  written by Claude Pageau pageauc@gmail.com
Windows, Unix, Raspberry (Pi) - python opencv2 motion tracking
using web camera or raspberry pi camera module.

This is a python opencv2 motion tracking demonstration program.
It will detect motion in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.  Object is tracked
until it crosses a verticle or horizontal center line, Enter and Leave data
is updated and optionally recorded and optionally saving video frame image.
Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is my YouTube video demonstrating this demo program using a
Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

This will run on a Windows, Unix OS using a Web Cam or a Raspberry Pi
using a Web Cam or RPI camera module installed and configured

To do a quick install On Raspbian or Debian Copy and paste command below
into a terminal or SSH session to download and install track-inout.
Program will be installed to ~/track-inout folder

curl -L https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh | bash

How to Run

    cd ~/track-inout
    ./inout.py

"""
print("Loading ...")
# import python libraries
import logging
import os
import time
import datetime
from threading import Thread
import cv2

PROG_VER = "ver 1.10"
# Find the full path of this python script
PROG_PATH = os.path.abspath(__file__)
# get the path location only (excluding script name)
BASE_DIR = PROG_PATH[0:PROG_PATH.rfind("/")+1]
PROG_FILENAME = PROG_PATH[PROG_PATH.rfind("/")+1:PROG_PATH.rfind(".")]
PROG_NAME = os.path.basename(__file__)

print("%s %s Track Enter and Leave Activity using python and OpenCV"
      % (PROG_NAME, PROG_VER))
# Check for variable file to import and error out if not found.
CONFIG_FILE_PATH = BASE_DIR + "config.py"
if not os.path.exists(CONFIG_FILE_PATH):
    print("ERROR - Missing config.py file - Could not find Configuration file %s"
          % (CONFIG_FILE_PATH))
    import urllib2
    CONFIG_URL = "https://raw.github.com/pageauc/motion-track/master/config.py"
    print("Attempting to Download new config.py file")
    print("from %s" % CONFIG_URL)
    try:
        WGET_FILE = urllib2.urlopen(CONFIG_URL)
    except:
        print("ERROR - Download of config.py Failed")
        print("   Try Rerunning the motion-track-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % PROG_NAME)
        quit(1)
    f = open('config.py', 'wb')
    f.write(WGET_FILE.read())
    f.close()

# Read Configuration variables from config.py file
try:
    from config import *
except ImportError:
    print("ERROR - Problem importing %s" % CONFIG_FILE_PATH)
    quit(1)

# Bypass loading picamera library if not available eg. UNIX or WINDOWS
try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    WEBCAM = True

LOG_FILE_PATH = BASE_DIR + PROG_FILENAME + ".log"
if VERBOSE:
    print("Logging to Console per Variable VERBOSE=True")
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
elif SAVE_LOG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=LOG_FILE_PATH,
                        filemode='w')
else:
    print("Logging Disabled per Variable VERBOSE=False")
    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
if not os.path.isdir(IMAGE_PATH):
    logging.info("Creating Image Storage Folder %s", IMAGE_PATH)
    os.makedirs(IMAGE_PATH)
    
# Get center line for movement counting
if WEBCAM:
    X_CENTER = WEBCAM_WIDTH/2
    Y_CENTER = WEBCAM_HEIGHT/2
    X_MAX = WEBCAM_WIDTH
    Y_MAX = WEBCAM_HEIGHT
    X_BUF = WEBCAM_WIDTH/10
    Y_BUF = WEBCAM_HEIGHT/10
else:
    X_CENTER = CAMERA_WIDTH/2
    Y_CENTER = CAMERA_HEIGHT/2
    X_MAX = CAMERA_HEIGHT
    Y_MAX = CAMERA_WIDTH
    X_BUF = CAMERA_WIDTH/10
    Y_BUF = CAMERA_HEIGHT/10
    
# Color data for OpenCV lines and text
CV_WHITE = (255, 255, 255)
CV_BLACK = (0, 0, 0)
CV_BLUE = (255, 0, 0)
CV_GREEN = (0, 255, 0)
CV_RED = (0, 0, 255)
COLOR_MO = CV_RED  # color of motion circle or rectangle
COLOR_TEXT = CV_BLUE   # color of openCV text and centerline
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
FRAME_COUNTER = 1000  # used when SHOW_FPS=True  Sets frequency of display
QUOTE = '"'  # Used for creating quote delimited log file of speed data

# Setup GPIO for a Servo. Customize pin and Freq per variables
if  DEVICE_CONTROL_ON:
    # IMPORTANT - You need to setup a servo and LED's on appropriate
    # GPIO pins.  This is sample code only.
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        print("ERROR - Problem importing RPi.GPIO library")
        quit(1)
    # LED control variables
    LIGHT_TIMER = 60
    LED_GREEN_PIN = 11
    LED_RED_PIN = 13
    # SERVO control variables
    SERVO_PIN = 12  # Set gpio pin to control servo
    SERVO_FREQ = 50  # Set Frequency for servo control
    SERVO_0 = 2.5  # Set Duty Cycle for Servo at 0 degrees
    SERVO_90 = 7.5  #  Set Duty Cycle for 90 Degrees
    SERVO_180 = 12.5  # Set Duty Cycle for 180 Degrees
    # Initialize servo pwm and led status
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    p = GPIO.PWM(SERVO_PIN, SERVO_FREQ)
    GPIO.setup(LED_RED_PIN, GPIO.OUT)
    GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
    # Setup LED Status
    GPIO.output(LED_GREEN_PIN, GPIO.HIGH) # Green LED on
    GPIO.output(LED_RED_PIN, GPIO.LOW)    # Red LED Off
    logging.info("Light is GREEN")
    # Setup Servo Status
    p.start(SERVO_90)    # Set servo in Neutral 90 Position
    logging.info("Servo is Open at 90")
    
#------------------------------------------------------------------------------
def led_green(green_on):
    """ Set green and red leds based on servo position """
    if green_on:
        GPIO.output(LED_GREEN_PIN, GPIO.HIGH) # Green LED on
        GPIO.output(LED_RED_PIN, GPIO.LOW)    # Red LED off
        logging.info("Light is GREEN")
    else:
        # code to turn green LED ON and red LED OFF
        GPIO.output(LED_GREEN_PIN, GPIO.LOW) # Green LED off
        GPIO.output(LED_RED_PIN, GPIO.HIGH)  # Red LED on
        logging.info("Light is RED")

#------------------------------------------------------------------------------
def control_servo(is_open):
    """
    Sample Code to toggle servo open or closed based on boolean
    is_open variable
    """
    if is_open:
        p.ChangeDutyCycle(SERVO_180) # Move Servo to 180 Degrees
        time.sleep(1)
        led_green(False) # green led off and red on
        logging.info("Servo is Closed")
        is_open = False  # Set position for next toggle
    else:
        p.ChangeDutyCycle(SERVO_90) # Move Servo to 90 Degrees
        time.sleep(1)
        led_green(True)  # green led on and red off
        logging.info("Servo is Open")
        is_open = True  # set position for next toggle
    return is_open

#------------------------------------------------------------------------------
def timer_on(change_time, duration):
    right_now = datetime.datetime.now()
    time_diff = (right_now - change_time).total_seconds()
    if time_diff > duration:
        start = True
    else:
        start = False
    return start

#------------------------------------------------------------------------------
class PiVideoStream:
    """  Get a single stream image from pi-camera module thread """
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
                 framerate=CAMERA_FRAMERATE, rotation=0,
                 hflip=False, vflip=False):
        """ initialize the camera and stream """
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped """
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
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

#------------------------------------------------------------------------------
class WebcamVideoStream:
    """ Get a single stream image from web camera thread """
    def __init__(self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH,
                 CAM_HEIGHT=WEBCAM_HEIGHT):
        """
        initialize the video camera stream and read the first frame
        from the stream
        """
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3, CAM_WIDTH)
        self.stream.set(4, CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped """
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

#------------------------------------------------------------------------------
def show_loop_fps(start_time, frame_count):
    """ Display image processing speed if required """
    if SHOW_FPS:
        if frame_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            fps_value = float(frame_count / duration)
            logging.info("Processing at %.2f fps last %i frames",
                         fps_value, frame_count)
            frame_count = 0
            start_time = time.time()
        else:
            frame_count += 1
    return start_time, frame_count

#------------------------------------------------------------------------------
def get_image_name(path, prefix):
    """ build image file names by number sequence or date/time """
    right_now = datetime.datetime.now()
    file_name = ("%s/%s-%04d%02d%02d-%02d%02d%02d.jpg" %
                 (path, prefix,
                  right_now.year, right_now.month, right_now.day,
                  right_now.hour, right_now.minute, right_now.second))
    return file_name

#------------------------------------------------------------------------------
def log_to_csv_file(data_to_append):
    """ create log file if required and save data to csv file """
    log_file_path = BASE_DIR + PROG_FILENAME + ".csv"
    if not os.path.exists(log_file_path):
        open(log_file_path, 'w').close()
        f = open(log_file_path, 'ab')
        f.close()
        logging.info("Create New Data Log File %s", log_file_path)
    filecontents = data_to_append + "\n"
    f = open(log_file_path, 'a+')
    f.write(filecontents)
    f.close()
    return

#------------------------------------------------------------------------------
def crossed_x_centerline(enter, leave, movelist):
    """ Did the movement cross the x center line"""
    if len(movelist) > 1:  # Are there two entries
        if (movelist[0] <= X_CENTER and movelist[-1] > X_CENTER + X_BUF):
            leave += 1
            movelist = []
        elif (movelist[0] > X_CENTER and  movelist[-1] < X_CENTER - X_BUF):
            enter += 1
            movelist = []
    return enter, leave, movelist

#------------------------------------------------------------------------------
def crossed_y_centerline(enter, leave, movelist):
    """ Did the movement cross the y center line """
    if len(movelist) > 1:  # Are there two entries
        if (movelist[0] <= Y_CENTER and movelist[-1] > Y_CENTER + Y_BUF):
            leave += 1
            movelist = []
        elif (movelist[0] > Y_CENTER and  movelist[-1] < Y_CENTER - Y_BUF):
            enter += 1
            movelist = []
    return enter, leave, movelist

#------------------------------------------------------------------------------
def track():
    """ Track Movement and count enter, leave """
    image1 = vs.read()   # initialize image1 (done once)
    try:
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    except:
        vs.stop()
        print("Problem Connecting To Camera Stream.")
        print("Restarting Camera.  One Moment Please .....")
        time.sleep(4)
        return
    if WINDOW_ON:
        print("Press q in window Quits")
    else:
        print("Press ctrl-c to Quit")
    print("Start Tracking Enter Leave Activity ....")
    if not VERBOSE:
        print("Note: Console Messages Suppressed per VERBOSE=%s" % VERBOSE)
    big_w = int(CAMERA_WIDTH * WINDOW_BIGGER)
    big_h = int(CAMERA_HEIGHT * WINDOW_BIGGER)
    cx, cy, cw, ch = 0, 0, 0, 0   # initialize contour center variables
    frame_count = 0  #initialize for show_loop_fps
    start_time = time.time() #initialize for show_loop_fps
    still_scanning = True
    movelist = []
    move_time = time.time()
    enter = 0
    leave = 0
    # Data for Controlling LED
    light_timer = LIGHT_TIMER
    green_time = datetime.datetime.now() + light_timer
    logging.info("light_timer = %i", light_timer)
    servo_open = True
    led_green(True)
    while still_scanning:
        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA
        image2 = vs.read()  # initialize image2
        if WEBCAM:
            if (WEBCAM_HFLIP and WEBCAM_VFLIP):
                image2 = cv2.flip(image2, -1)
            elif WEBCAM_HFLIP:
                image2 = cv2.flip(image2, 1)
            elif WEBCAM_VFLIP:
                image2 = cv2.flip(image2, 0)
        if WINDOW_ON:
            if CENTER_LINE_VERT:
                cv2.line(image2, (X_CENTER, 0), (X_CENTER, Y_MAX), COLOR_TEXT, 2)
            else:
                cv2.line(image2, (0, Y_CENTER), (X_MAX, Y_CENTER), COLOR_TEXT, 2)
        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed images
        difference_image = cv2.absdiff(grayimage1, grayimage2)
        # save grayimage2 to grayimage1 ready for next image2
        grayimage1 = grayimage2
        difference_image = cv2.blur(difference_image, (BLUR_SIZE, BLUR_SIZE))
        # Get threshold of difference image based on
        # THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(difference_image,
                                               THRESHOLD_SENSITIVITY, 255,
                                               cv2.THRESH_BINARY)
        # Try python2 opencv syntax and fail over to
        # python3 opencv syntax if required
        try:
            contours, hierarchy = cv2.findContours(thresholdimage,
                                                   cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            thresholdimage, contours, hierarchy = cv2.findContours(thresholdimage,
                                                                   cv2.RETR_EXTERNAL,
                                                                   cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            total_contours = len(contours)  # Get total number of contours
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
                if move_timer >= MOVE_LIST_TIMEOUT:
                    movelist = []
                    #logging.info("Exceeded %.2f Seconds - Clear movelist" % MOVE_LIST_TIMEOUT)
                move_time = time.time()
                old_enter = enter
                old_leave = leave
                if CENTER_LINE_VERT:
                    movelist.append(cx)
                    enter, leave, movelist = crossed_x_centerline(enter, leave, movelist)
                else:
                    movelist.append(cy)
                    enter, leave, movelist = crossed_y_centerline(enter, leave, movelist)
                if not movelist:
                    if enter > old_enter:
                        if INOUT_REVERSE:   # reverse enter leave if required
                            prefix = "leave"
                        else:
                            prefix = "enter"
                    elif leave > old_leave:
                        if INOUT_REVERSE:
                            prefix = enter
                        else:
                            prefix = "leave"
                    else:
                        prefix = "error"
                    # Control device or devices base on counters
                    # for in and out. You can reset counter from
                    # the control_device function and reset the
                    # counters based on your control_device logic
                    if DEVICE_CONTROL_ON:
                        if timer_on(green_time, light_timer):
                            enter = 0  # Reset enter counter
                            leave = 0  # Reset leave counter
                            # Toggle Servo position
                            servo_open = control_servo(servo_open)
                            if enter > 3 or leave > 3:
                                light_timer = light_timer - 1
                                if light_timer < 10:
                                    logging.info("light_timer is at min value")
                                    light_timer = 10
                                logging.info("Changed light_timer to %i sec",
                                             light_timer)
                            green_time = datetime.datetime.now() + light_timer
                    if INOUT_REVERSE:
                        logging.info("leave=%i enter=%i Diff=%i",
                                     leave, enter, abs(enter-leave))
                    else:
                        logging.info("enter=%i leave=%i Diff=%i",
                                     enter, leave, abs(enter-leave))
                    # Save image
                    if SAVE_IMAGES:
                        filename = get_image_name(IMAGE_PATH, prefix)
                        save_image = vs.read()
                        logging.info("Save: %s", filename)
                        cv2.imwrite(filename, save_image)
                    # Save data to csv file
                    if SAVE_CSV_FILE:
                        log_time = datetime.datetime.now()
                        log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s,%s%02d%s" %
                                        (QUOTE, log_time.year, log_time.month,
                                         log_time.day, QUOTE,
                                         QUOTE, log_time.hour, QUOTE,
                                         QUOTE, log_time.minute, QUOTE,
                                         QUOTE, log_time.second, QUOTE))
                        log_csv_text = ("%s,%s%s%s,%s%s%s,%i,%i,%i,%i,%i" %
                                        (log_csv_time,
                                         QUOTE, prefix, QUOTE,
                                         QUOTE, filename, QUOTE,
                                         cx, cy, cw, ch, cw * ch))
                        log_to_csv_file(log_csv_text)
                if WINDOW_ON:
                    # show small circle at motion location
                    if SHOW_CIRCLE and motion_found:
                        cv2.circle(image2, (cx, cy), CIRCLE_SIZE,
                                   COLOR_MO, LINE_THICKNESS)
                    else:
                        cv2.rectangle(image2, (cx, cy), (x+cw, y+ch),
                                      COLOR_MO, LINE_THICKNESS)
                if SHOW_MOVES:
                    logging.info("cx,cy(%i,%i) C:%2i A:%ix%i=%i SqPx" %
                                 (cx, cy, total_contours,
                                  cw, ch, biggest_area))
        start_time, frame_count = show_loop_fps(start_time, frame_count)
        if WINDOW_ON:
            if INOUT_REVERSE:
                img_text = ("LEAVE %i          ENTER %i" % (leave, enter))
            else:
                img_text = ("ENTER %i          LEAVE %i" % (enter, leave))
            cv2.putText(image2, img_text, (35, 15),
                        TEXT_FONT, FONT_SCALE, (COLOR_TEXT), 1)
            if DIFF_WINDOW_ON:
                cv2.imshow('Difference Image', difference_image)
            if THRESH_WINDOW_ON:
                cv2.imshow('OpenCV Threshold', thresholdimage)
            # Note setting a bigger window will slow the FPS
            if WINDOW_BIGGER > 1:
                image3 = cv2.resize(image2, (big_w, big_h))
            cv2.imshow('Press q in Window Quits)', image3)
            # Close Window if q pressed while mouse in opencv gui window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                vs.stop()
                print("End Motion Tracking")
                quit(0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        while True:
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
        pass
    vs.stop()
    if DEVICE_CONTROL_ON:
        p.stop()
        GPIO.cleanup()
    print("")
    print("User Pressed Keyboard ctrl-c")
    print("%s %s - Exiting" % (PROG_NAME, PROG_VER))
    quit(0)
