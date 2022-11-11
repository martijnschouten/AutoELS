# Automagically Enhanced Lightning System (AutoELS)
Simple tool for semi-automatically optimising the contrast of 16-bit images from a fluorescent microscope.

![screenshot](https://user-images.githubusercontent.com/6079002/201364552-2d6266b8-f84b-4094-a112-1105e4072ca3.JPG)

# Compilation instructions
On windows:
1. Make sure you have a working python installation (tested using python 3.9.9)
1. Open command prompt
1. Use the `cd` to go to the folder that contains the content of this git
1. Make a virtual environment by running `python -m venv venv`
1. Activate the virtual environment by running `venv\Scripts\activate`
1. Install the dependencies by running `pip install pyqt6 pyqtgraph pyyaml numpy opencv-python`
1. Freeze the python app by running `make.bat` in the terminal
