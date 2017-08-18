#!/bin/bash
# Convenient track-inout motion-track-install.sh script written by Claude Pageau 1-Jul-2016
ver="0.7"
APP_DIR='track-inout'  # Default folder install location

cd ~
if [ -d "$APP_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade track-inout"
else
  echo "New track-inout Install"
  STATUS="New Install"
  echo "$APP_DIR Folder Created"
fi

mkdir -p $APP_DIR/media

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $APP_DIR
INSTALL_PATH=$( pwd )

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "------------------------------------------------"
echo "  track-inout-Install.sh script ver $ver"
echo "  $STATUS track-inout Track Enter Leave Activity"
echo "------------------------------------------------"
echo ""
echo "1 - Downloading GitHub Repo files to $INSTALL_PATH"
wget -O media/webserver.txt -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.txt
wget -O inout-install.sh -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh
if [ $? -ne 0 ] ;  then
  wget -O inout-install.sh https://raw.githubusercontent.com/pageauc/track-inout/master/inout-install.sh
  wget -O inout.py https://raw.githubusercontent.com/pageauc/track-inout/master/inout.py
  wget -O inout.sh https://raw.githubusercontent.com/pageauc/track-inout/master/inout.sh
  wget -O config.py https://raw.githubusercontent.com/pageauc/track-inout/master/config.py
  wget -O config-240.py https://raw.githubusercontent.com/pageauc/track-inout/master/config-240.py
  wget -O Readme.md https://raw.githubusercontent.com/pageauc/track-inout/master/Readme.md
  wget -O webserver.py https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.py
  wget -O webserver.sh https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.sh
  wget -O media/webserver.txt https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.txt
else
  wget -O inout.py -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/inout.py
  wget -O inout.sh -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/inout.sh
  wget -O config.py -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/config.py
  wget -O config-240.py -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/config-240.py
  wget -O Readme.md -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/Readme.md
  wget -O webserver.py -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.py
  wget -O webserver.sh -q --show-progress https://raw.githubusercontent.com/pageauc/track-inout/master/webserver.sh
fi
echo "Done Download"
echo "------------------------------------------------"
echo ""
echo "2 - Make required Files Executable"
chmod +x *py
chmod -x config*
chmod +x *sh
echo "Done Permissions"
echo "------------------------------------------------"
# check if system was updated today
NOW="$( date +%d-%m-%y )"
LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
if [ "$NOW" == "$LAST" ] ; then
  echo "4 Raspbian System is Up To Date"
  echo ""
else
  echo ""
  echo "3 - Performing Raspbian System Update"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y update
  echo "Done update"
  echo "------------------------------------------------"
  echo ""
  echo "4 - Performing Raspbian System Upgrade"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y upgrade
  echo "Done upgrade"
fi
echo "------------------------------------------------"
echo ""
echo "5 - Installing track-inout Dependencies"
sudo apt-get install -y python-opencv python-picamera dos2unix
dos2unix *
echo "Done Dependencies"
cd $DIR
# Check if track-inout-install.sh was launched from track-inout folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'track-inout-install.sh' ]; then
    echo "$STATUS Cleanup track-inout-install.sh"
    rm inout-install.sh
  fi
fi
echo "-----------------------------------------------"
echo "6 - $STATUS Complete"
echo "-----------------------------------------------"
echo " "
echo "1. Reboot RPI if there are significant Raspbian system updates"
echo "2. if config.py window_on=True then a monitor/TV display is needed"
echo "   for the opencv window"
echo "   Run inout.py with the Raspbian Desktop GUI running"
echo "3. To start open file manager or a Terminal session then change to"
echo "   track-inout folder and launch per commands below"
echo ""
echo "   cd ~/track-inout"
echo "   ./inout.py"
echo ""
echo "-----------------------------------------------"
echo "See Readme.md for Further Details"
echo $APP_DIR "Good Luck Claude ..."
echo "Bye"
echo ""