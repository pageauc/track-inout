# Config.py file for inout.py  Release 0.94

# Display Settings
# ----------------
DEVICE_CONTROL_ON = False  # True=On False=Off enable/disable device_control function code
VERBOSE = True          # Set to False to suppress console logging messages
SAVE_LOG = False        # Send console log messages to a log file instead of screen
SAVE_CSV_FILE = False   # save CSV data file
SAVE_IMAGES = True      # save image when leave or enter activated
WINDOW_ON = False       # Set to True displays opencv windows (GUI desktop reqd)
SHOW_MOVES = False      # show detailed x,y tracking movement data
SHOW_FPS = False        # Show Frames per second
CENTER_LINE_VERT = True # True=Vert False=horiz centerline trigger orientation
INOUT_REVERSE = False   # reverse Enter and Leave orientation
IMAGE_PATH = "media/images"  # Folder for storing images (rel or abs)
MOVE_LIST_TIMEOUT = 0.5  # wait seconds with no motion then clear movelist

# Camera Settings
# ---------------
WEBCAM = False        # default = False False=PiCamera True=USB WebCamera

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
DIFF_WINDOW_ON = False    # Show OpenCV image difference window
THRESH_WINDOW_ON = False  # Show OpenCV image Threshold window
SHOW_CIRCLE = True        # True= show circle False= show rectancle on biggest motion
CIRCLE_SIZE = 5           # diameter of circle for SHOW_CIRCLE
LINE_THICKNESS = 2        # thickness of bounding line in pixels
FONT_SCALE = .5           # size opencv text
WINDOW_BIGGER = 2   # Resize multiplier for Movement Status Window
                    # if gui_window_on=True then makes opencv window bigger
                    # Note if the window is larger than 1 then a reduced frame rate will occur
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "media"     # default= "media" webserver root path to webserver image/video sub-folders
web_page_title = "Track Enter Leave Activity"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = False   # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # default= "180" seconds to wait for web page refresh  seconds (three minutes)
web_page_blank = True         # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
web_image_height = "768"       # default= "768" px height of images to display in iframe
web_iframe_width_usage = "70%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
web_max_list_entries = 0         # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height  # Right List - side menu height in px (link selection)
web_list_by_datetime = True      # True=datetime False=filename
web_list_sort_descending = True  # reverse sort order (filename or datetime per web_list_by_datetime setting

# ---------------------------------------------- End of User Variables -----------------------------------------------------
