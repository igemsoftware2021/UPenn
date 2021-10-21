# UPenn

OptoReader repository for software package to run the OptoReader, hardware files, and modeling scripts.

## Running the OptoReader

The OptoReader can be run using a computer and two Arduino Micros with the following provided code files: 

*OptoPlate_topArduino.ino* - Arduino code to control the stimulation plate. Takes in experiment stimulation settings, controls the 96 stimulation and optical density LEDs, and communicates with the reading plate for optical density measurements.

*PlateReader_bottomArduino.ino* - Arduino code to control the reading plate. Takes in experiment reading settings, controls the 96 excitation LEDs and photosensors, and communicates with the stimulation plate for optical density measurements. 

*OptoReader_Protocol.py* - Python code to take in inputs from the graphical user interface, keep track of experiment timing, and communicate with Arduinos to initiate readings and calibrate the optical density LEDs.

*GUI.py* - Python code creating a graphical user interface to take in user experiment inputs including stimulation settings, reading settings, feedback control, and experiment timing.

To run the OptoReader, first upload OptoPlate_topArduino.ino to the stimulation (top) plate Arduino and upload *PlateReader_bottomArduino.ino* to the reading (bottom) Arduino. Note the port name for each Arduino. If necessary, rename the port name from the preset COM11 and COM12 in *OptoReader_Protocol.py*. Finally, run GUI.py to open the graphical user interface and enter your experiment settings. Ensure that the image files *blue_logo.png* and *optologo_small.png* and the Python file *OptoReader_Protocol.py* are saved in the same folder as *GUI.py*.

## Hardware

### 3D Printed Parts
Includes files for our 3D-printed parts *Bottom_Adaptor.stl* and *Top_Adaptor.stl*. These files include the 3D model of the top adaptor and bottom adaptor, that fit each pcb board to a microwell plate.

### PCBs
Includes schematic files for our printed circuit boards (PCBs) *PlateReader.kicad_pcb* and *optoPlate96.kicad_pcb*. These can be sent directly to a company that provides printed circuit boards. The board components are soldered directly onto the boards. 

## Fluorescence Calibration Modeling

Files for our fluorescence calibration modeling include *FirstFit.m* and *Fluorescence_Calibration_Curve.m*. These files use our device’s fluorescence readings at different known concentrations to fit each well to a fluorescent calibration curve.

