# PetCar3.2
All of the code for PetCar3.2

## Installation Instructions
When cloning the repo, I advise cloning the folder to the desktop. Wherever you install it, make sure you update
the location of transfer.py in the /etc/init.d/transferStartup file. When it comes to the UV4L_Carcam folder,
make sure you move the contents of this folder into the UV4L carcam Directory. On a fresh install of UV4L, this directory
will not exist. In that case, make the directory at /usr/share/uv4l/demos/carcam, then place the files into it.

### Set up transfer.py on startup
First, you need to copy the transferStartup file from this repo to /etc/init.d. Once it's copied in, you need to
sudo nano into the file and update the file directory to wherever your transfer.py is saved. (For the easiest setup just
point to the repo's transfer.py location.)

### Install UV4L and WebRTC
I'll make a comprehensive guide for installing this eventually, but for now I recommend following the included
Reef Nerd Tutorial pdf for getting it all set up, up until the point where you uncomment enable-www-server. At
this point, change the www-root-path to be /usr/share/uv4l/demos/carcam. From here, open a command line at
/usr/share/uv4l/demos and do "sudo mkdir carcam" to make the carcam folder. Once this is done, you need to copy
all of the files in the repo's UV4L_Carcam folder into this new folder. (This may require using sudo in a command line,
if so you might want to look at changing the folder's permissions to allow user read/write access.)

That should be all! Restart the PetCar and you should be able to connect to the robot's IP at port 8888 in a web browser.
Give it a little bit of time for everything to start up.