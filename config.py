# Config.py file for track-inout.py  Release 0.5

# Display Settings
# ----------------
verbose = True        # Set to False for no data display
save_log = False      # Send console log messages to a log file instead of screen
window_on = True      # Set to True displays opencv windows (GUI desktop reqd)
show_fps = False      # Show Frames per second

centerline_vert = True  # True=Vert False=horiz centerline trigger orientation
show_moves = False      # show detailed x,y tracking movement data
save_CSV = True         # save CSV data file
save_images = True      # save image when leave or enter activated
image_path = "media/images"   # Folder for storing images (rel or abs)
movelist_timeout = 0.5  # seconds with no motion then clear movelist

# Camera Settings
# ---------------
WEBCAM = True       # default = False False=PiCamera True=USB WebCamera

# Web Camera Settings
WEBCAM_SRC = 0        # default = 0   USB opencv connection number
WEBCAM_WIDTH = 320    # default = 320 USB Webcam Image width
WEBCAM_HEIGHT = 240   # default = 240 USB Webcam Image height
WEBCAM_HFLIP = False  # default = False USB Webcam flip image horizontally
WEBCAM_VFLIP = False  # default = False USB Webcam flip image vertically

# Pi Camera Settings
CAMERA_WIDTH = 320    # default = 320 PiCamera image width can be greater if quad core RPI
CAMERA_HEIGHT = 240   # default = 240 PiCamera image height
CAMERA_HFLIP = False  # True=flip camera image horizontally
CAMERA_VFLIP = False  # True=flip camera image vertically
CAMERA_ROTATION = 0   # Rotate camera image valid values 0, 90, 180, 270
CAMERA_FRAMERATE = 25 # default = 25 lower for USB Web Cam. Try different settings


# OpenCV Settings
# ---------------
MIN_AREA = 700            # excludes all contours less than or equal to this Area
diff_window_on = False    # Show OpenCV image difference window
thresh_window_on = False  # Show OpenCV image Threshold window
SHOW_CIRCLE = True        # True= show circle False= show rectancle on biggest motion
CIRCLE_SIZE = 5           # diameter of circle for SHOW_CIRCLE
LINE_THICKNESS = 2        # thickness of bounding line in pixels
font_scale = .5           # size opencv text
WINDOW_BIGGER = 2   # Resize multiplier for Movement Status Window
                    # if gui_window_on=True then makes opencv window bigger
                    # Note if the window is larger than 1 then a reduced frame rate will occur
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10
