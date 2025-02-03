# Hydrogen evolution in hydrogel electrochemical cell
This is a repository for paper "Hydrogen Evolution and Dynamics in Hydrogel Electrochemical Cells for Ischemia-Reperfusion therapy".

This repo contains 
1. A flexible PCB designed for delivering constant current to the hydrogen producing device.
2. A user interface software code for wirelessly controlling the flexible PCB.
3. A code to plot hydrogen diffusion modelling data.
4. A code to analyze the hydrogen evolution video.

# System requirements
1. The flexible PCB design requires the installation of software KiCad 8.0 (https://www.kicad.org/download/). We use windows 64 bit system. The computer system requirements can be seen in https://www.kicad.org/help/system-requirements/.
2. The running of all the python scripts requires the installment of a few Python packages: pygame, asyncio, platform, bleak, struct, pandas, numpy, matplotlib, and cv2. Install time of all the packages would take 10-20 min.
3. All the python scripts have been tested in Windows 11.

# Instruction
1. The implement of video analysis code and heat map code is performed on Jupyter notebook. The installment of Jupyter notebook can be found here: https://jupyter.org/install.
2. The original videos and simulation data is included in corresponding folders for reproduction of the result.
3. The implement of Bluetooth user interface is performed on Spyder (https://www.spyder-ide.org/) with python 3.13. The running of the user interface codes requires the flexible PCB to be turned on.
4. The expected run tiume for demo with provided data on a "normal" desktop computer would be below 1 min.
5. The expected output for video and simulation data analysis is also included in corresponding folders for reference. 
