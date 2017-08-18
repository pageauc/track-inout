## Track Enter and Leave Activity that cross a vert or horiz center line
### Runs on Windows or Unix using Web Cam or Raspberry Pi using Web Cam or pi camera module
### Uses Python2/3, OpenCV2/3 to track motion


### Introduction
This project came about when I decided to update my motion tracking demo and 
thought it would be a good idea to include something useful.  I decided to track
entering a leaving Activity when they cross a vertical or horizontal centerline
At first it was a simple counter but now it also allows for options to 
take an image and update a csv file.  You can add more features if you are
familiar with python programming.  See my speed camera project for some ideas
https://github.com/pageauc/speed-camera

### Prerequisites
Requires Windows, Unix computer with a Web Camera or a Raspberry Pi computer with
a Web Camera or RPI Camera Module and an up-to-date Raspbian distro.
If you wish to use a web camera that is plugged into a usb port. Set WEBCAM = True in config.py
otherwise, WEBCAM = False will use a connected raspberry pi camera module video stream.
If running under Windows or a Non RPI unix distro then Web camera will automatically be
selected WEBCAM = True

The dependencies and code files can be installed per the track-inout-install.sh script
if you are using Debbian or Raspbian, Otherwise select the Github download zip or clone
option from the github repo here https://github.com/pageauc/track-inout
See Quick or Manual install instructions below for details

### Quick Install
Easy Install of track-inout onto Debian or Raspberry Pi Computer.

    curl -L https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.
Then select ssh(Putty) window, mouse right click, paste.  The command should
download and execute the github setup.sh script and install the track-inout files.
This install can also be done directly on an Internet connected computer via a console or desktop terminal session and web browser.
Note - a raspbian/debian apt-get update and upgrade will be performed as part of install
so it may take some time if these are not up-to-date

### Manual Install
From logged in RPI SSH session or console terminal perform the following.

    wget https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh
    chmod +x inout-install.sh
    ./inout-install.sh

### How to Run
Default is console only display. Use Nano or text editor to Edit config.py
variable window_on = True
to display the opencv tracking window on GUI desktop. See other variables
and descriptions for additional variable customization settings.
From SSH session, console or GUI desktop terminal session execute the following commands

    cd ~/track-inout
    ./inout.py

On Windows make sure you have the latest python installed from https://www.python.org/downloads/
To install clone or download zip from project github web page https://github.com/pageauc/track-inout
use 7zip to unzip file if required.   
Run inout.py from IDLE or if file association exists it can also be
run from cmd prompt by double clicking on inout.py.  Use a text editor
To modify settings use a text editor to edit the config.py file 
To view opencv window(s) on GUI desktop, edit config.py variable window_on=True.


### Trouble Shooting

Edit the config.py file and set variable window_on = True so the opencv status windows can display camera
motion images and a circle marking x,y coordinates and optionally the
opencv threshold window.  The circle diameter can be change using CIRCLE_SIZE
variable.
You can set window_on=False if you need to run from SSH session.  If
verbose=True (default), then logging information will be displayed without a GUI desktop session.

### Credits
Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py


## Some of my Other motion Tracking Projects

### motion-track.py - Motion Track Demo - Basic concept of tracking moving objects
This Demo program detects motion in the field of view and uses opencv to calculate the
largest contour above a minimum size and return its x,y coordinate.
* Motion Track Demo YouTube Video http://youtu.be/09JS7twPBsQ
* GitHub Repo https://github.com/pageauc/motion-track
* RPI forum post https://www.raspberrypi.org/forums/viewtopic.php?p=790082#p790082

### speed-camera.py - Object (vehicle) speed camera based on motion tracking
Tracks vehicle speeds or other moving objects in real time and records image
and logs data. Now improved using threading for video stream and clipping of
area of interest for greater performance.
* GitHub Repo https://github.com/pageauc/speed-camera
* YouTube Speed Camera Video https://youtu.be/eRi50BbJUro
* RPI forum post https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150

### cam-track.py - Tracks camera x y movements
Uses a clipped search image rectangle to search subsequent video stream images and returns
the location. Can be used for tracking camera x y movements for stabilization,
robotics, Etc.
* GitHub Repo https://github.com/pageauc/rpi-cam-track
* YouTube Cam-Track Video https://www.youtube.com/edit?video_id=yjA3UtwbD80
* Code Walkthrough YouTube Video https://youtu.be/lkh3YbbNdYg
* RPI Forum Post https://www.raspberrypi.org/forums/viewtopic.php?p=1027463#p1027463

### hotspot-game.py - A simple motion tracking game
The game play involves using streaming video of body motion to get as many hits
as possible inside shrinking boxes that randomly move around the screen.
Position the camera so you can see body motions either close or standing.
Pretty simple but I think kids would have fun with it and they just might
take a look at the code to see how it works, change variables or game logic.
* GitHub hotspot-game Repo https://github.com/pageauc/hotspot-game
* YouTube Hotspot Gam Video https://youtu.be/xFl3lmbEO9Y
* RPI Forum Post https://www.raspberrypi.org/forums/viewtopic.php?p=1026124#p1026124

## ----------------------------------------------------------------------------


Have Fun
Claude Pageau
YouTube Channel https://www.youtube.com/user/pageaucp
GitHub Repo https://github.com/pageauc

