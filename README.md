# SmartMice 2
A user-oriented, modularized logic control system for behavioral neuroscience research.\
This toolkit enables you to use Serial and UDP to control your device. It also implements data collection from cameras, serial devices, UDP services, self-defined runtime variables, etc. Besides, it enables you to create extensions in the form of variables and nodes, so you can control your customized devices and synchronize every one of them easily.\
Specially, this toolkit is built to support 1D and 2D VR devices. You can find example VR software in ```\vr```, which is created using Unity3D.\
This toolkit works under Windows 10 and 11.

## Installation
Make sure conda is installed in your computer and has been added to your environment variables.\
Download all project files, ```cd``` into project directory and run:
```commandline
conda create -n SmartMice2 python==3.9
conda activate SmartMice2
pip install -r requirements.txt
```

## Usage
To run SmartMice2, ```cd``` into project directory and use command line:
```commandline
conda activate SmartMice2
python main.py
```
After a while, there will be a splash, and then the main menu pops out. \
For further user reference, see [wiki](github.com/TallOpen/SmartMice/wiki).
