# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 11:36:21 2021

@author: Gloria Lee
"""
# Updated 06/11

# Import Packages
from serial import Serial
import time
import sys
import csv
import math

# Protocol Class takes in input from the GUI and sends to optoplate and platereader
class Protocol(object):

  # GUI Inputs
  wells = []
  intensity = []
  redCalFactors = []
  timeOn = []
  timeOff = []
  fp = []
  od = []
  duration = []
  totalWells = []
  totalStrWells = ""
  strPatternWells = ""
  redCalFactors = []

      
  # Initialize protocol object
  def __init__(self,wells,intensity, timeOn,timeOff,fp,od,duration,totalWells): 

    # Set inputs
    self.wells = wells # [[wells_1], [wells_2],...[wells_n]] for n patterns
    self.intensity = intensity # [intensity_1, intensity_2,...intensity_n] for n patterns
    self.timeOn = timeOn # [timeOn_1, timeOn_2,...timeOn_n] for n patterns
    self.timeOff = timeOff # [timeOff_1, timeOff_2,...timeOff_n] for n patterns
    self.fp = fp # [fp interval, fp num readings]
    self.od = od # [od interval, od num readings]
    self.duration = duration # Total experiment duration (seconds)
    self.totalWells = totalWells # List of wells in use
   
    
    # Create String lists of wells
    Protocol.wellsList(self,totalWells)
    self.redCalFactors = Protocol.getCalibrationFactors()
    
    # Set up Serial Communications
  
    # Optoplate Serial Communication
    optoplate_ser = Serial('COM12', 9600) # What port to use?; usually L
    optoplate_ser.flush()
    optoplate_ser.write('Connected;'.encode())
    
    # Initialize Optoplate
    Protocol.initializeOptoplate(self,optoplate_ser)
   
 
    # Platereader Serial Commuication
    platereader_ser = Serial('COM11', 9600) # What port to use?; usually R
    platereader_ser.flush()
    platereader_ser.write('Connected;'.encode())

    # Initialize PlateReader
    Protocol.initializePlatereader(self,platereader_ser)

    # Lists to store readings data
    fp_expData = []

    # Run while time is less than experiment duration    
    startTime = time.perf_counter()
    previousTimeO = startTime
    previousTimeF = startTime
    takeReadings = False
    
    # CSV File Header
    header = ["Time (minutes)"] + [f"Well_{entry}" for entry in totalWells]

    with open('Fluorescence_100621.csv','w',newline='') as csvfile_f:
        f_writer = csv.writer(csvfile_f,delimiter= ',')
        f_writer.writerow(header)
        with open('OD_1000621.csv','a',newline='') as csvfile_o:
            o_writer = csv.writer(csvfile_o,delimiter= ',')
            o_writer.writerow(header)
            
            OD_switch = 1
    
            while (time.perf_counter() - startTime) < duration:
                currentTime = time.perf_counter() # (seconds)
              
                # FP Protocol
                if ((round(currentTime - previousTimeF) >= round(fp[0])) or (previousTimeF == startTime)): # remove round
                    print("FP READ LOOP")
                    fp_list = [currentTime-startTime]
                   
                    optoplate_ser.write(bytes('blueoff;','utf-8')) # Should tell optoplate to turn off blue
                    platereader_ser.write(bytes('F;','utf-8')) # Should tell platereader to turn on UV lights/read
                   
                    r = platereader_ser.readline().decode('utf-8').strip()                 
                    # Wait until done reading (until platereader sends '*')
                    while not ('!' in r):
                      if (takeReadings and r != "#" and r != "!"):
                          fp_list.append(r)
                          print("fluor reading: ", r)
                      if ('#' in r):
                          takeReadings = True
                      r = platereader_ser.readline().decode('utf-8').strip()
                    
                    takeReadings = False
                    fp_expData.append(fp_list)  
                    f_writer.writerow(fp_list)
                    
                    optoplate_ser.write(bytes('done;','utf-8'))  
                    optoplate_ser.write(bytes('blueon;','utf-8')) # Tell optoplate to turn on blue if needed
                    
           
                    previousTimeF = currentTime
        
                # OD Protocol
                
                if ((round(currentTime - previousTimeO) >= round(od[0])) or (previousTimeO == startTime)):
                     print("OD READ LOOP")
                     calValue = round(500 * (self.redCalFactors[0])) # SPECTIFY INTENSITY HERE AND BELOW
                     print("read OD: ", 1, " cal value: ", calValue )
                            
                     optoplate_ser.write(bytes('O;','utf-8')) # Should tell optoplate to turn on OD and turn off blues 
                     optoplate_ser.write(bytes(str(calValue) + ';','utf-8')) #sends calibrated value for first well here
                     platereader_ser.write(bytes('O;','utf-8')) # Should tell platereader to read OD
                                          
                     od_list = [currentTime - startTime] #CHANGE HERE

                             
                     for j in range(len(totalWells)):
                         newRead = ""
                         r = optoplate_ser.readline().decode('utf-8').strip()
                         print("cal from arduino: ", r)
                         # Wait until optoplate signals OD on
                         while not ('odon' in r):
                             r = optoplate_ser.readline().decode('utf-8').strip()
                         # Signal to platereader to read OD
                         platereader_ser.write(bytes('readO;','utf-8'))
                         newRead = newRead + platereader_ser.readline().decode('utf-8').strip()
                         while not ('D' in newRead):
                             newRead = newRead + platereader_ser.readline().decode('utf-8').strip()
                         index1 = newRead.index(".")
                         index2 = newRead.index("D")
                         od_list.append(newRead[index1+1:index2])
                         optoplate_ser.write(bytes('nextO;','utf-8'))
                         
                         
                         if j < (len(totalWells)-1):
                             # NEW CALIBRATION
                             calValue = round(500 * (self.redCalFactors[totalWells[j+1]-1])) # SPECIFY INTENSITY HERE AND ABOVE
                             
                            
                             optoplate_ser.write(bytes(str(calValue) +';','utf-8')) # sends CALVALUE here
                             print("read OD: ", j+2, "cal values: ", calValue)
                            
                             
                         else: 
                             optoplate_ser.write(bytes('0;','utf-8'))
                            
                    
                     print("Raw OD Readings: ", od_list)
                     
                     # o_writer.writerow(od_list) # prints raw readings into file, not OD
                       
                     # Converting Raw Readings into Absorbance (Optical Density) readings
                     
                     od_list = [int(q) for q in od_list]
                     
                     if OD_switch == 1:
                         max_transmission = 550 # can change this value to "maximum transmission through LB"
                         OD_switch = 2
                     od_absorbance = []
                     for i in range(len(od_list)):
                         if od_list[i] == 0:
                             od_list[i] = 1
                             print("changed 0")
                    
                     print("od_list: ", od_list)
                     for rawRead in od_list[1:]:
                         
                         OD = math.log((max_transmission/rawRead), 10) 
                         od_absorbance.append(str(OD))
       
                     
                     o_writer.writerow(od_absorbance) # prints calculated OD int file, not raw readings
                     
                     print("Time: ",time.perf_counter())
                     print("OD Readings: ", od_absorbance)              
                     optoplate_ser.write(bytes('odoff;','utf-8')); # sends end of OD reading at time point to Arduino
                     
                     previousTimeO = currentTime
                       
                       
                    # ------------FEEDBACK FUNCTION HERE -------------
                     
                     #Protocol.Feedback1(self, optoplate_ser, self.wells[4], od_absorbance, 0.3, 0)  # applying feedback1 to specific pattern
                     # pattern_wells, absorbance_values, OD_threshold, new_intensity) 
                

    # Exit Python
    optoplate_ser.write(bytes('shutdown;','utf-8')) # Tell optoplate to turn off
    platereader_ser.write(bytes('shutdown;','utf-8')) # Tell optoplate to turn off
    sys.exit()
    
        
  # Converts list of number wells to string of 0s and 1s
  def wellsList(self,wells_list):
    intWells = []
    for i in range(96):
        if i+1 in wells_list:
            intWells.append('1')
        else:
            intWells.append('0')
    strWells = "".join(intWells)
    self.totalStrWells = strWells
    

  # Converts list of pattern wells to 96-length string of pattern numbers (0-96)
  # def patternList(self,wells_list):
      
    # intWells = ["00"]*96
    # for i in range (len(wells_list)):    
      # for entry in wells_list[i]:
        # intWells[entry-1] = "%.2d" % (i+1) 
    
    
    # strWells = "".join(intWells)
    # self.strPatternWells = strWells
      
  # Initializes optoplate with inputs from GUI
  def initializeOptoplate(self,optoplate_ser):

    # Create output Strings to send wells, intensity, time ON, and time OFF parameters 
    output = 'S;' + 'ready;' + self.totalStrWells + ';'
    
    
    all_intensities = [0]*96
    all_timeONs = [0]*96
    all_timeOFFs = [0]*96
    
    for i in range(len(wells)):
        for well in wells[i]:
            all_intensities[well-1] = self.intensity[i]
            all_timeONs[well-1] = self.timeOn[i]
            all_timeOFFs[well-1] = self.timeOff[i]
    
    intensity_output = ""
    timeON_output = ""
    timeOFF_output = ""
    
    for intensity in all_intensities:
        intensity_output = intensity_output + str(intensity) + ";"
        
    for timeOn in all_timeONs:
        timeON_output = timeON_output + str(timeOn) + ";"
    
    for timeOff in all_timeOFFs: 
        timeOFF_output = timeOFF_output + str(timeOff) + ";"
       
    
    # Send outputs to OptoPlate
    optoplate_ser.write(bytes(output,'utf-8')) # sending ready signal and wells in use string
    # print("output: ", output)
    optoplate_ser.write(bytes(intensity_output,'utf-8')) # sending 96 intensity settings (default is 0)
    # print("intensity: ", intensity_output)
    optoplate_ser.write(bytes(timeON_output,'utf-8')) # sending 96 time ON settings (default is 0)
    # print("timeON: ", timeON_output)
    optoplate_ser.write(bytes(timeOFF_output,'utf-8'))
    # print("timeOFF: ", timeOFF_output)
    

  # Initializes PlateReader with inputs from GUI 
  def initializePlatereader(self,platereader_ser):

    # Prepare Arduino to receive inputs
    x = 'start;'.encode()
    platereader_ser.write(x)

    # Create output String  
    output = 'ready;' + 'O;' + str(self.od[1]) + ";" + self.totalStrWells + ";" + "F;" + str(self.fp[1]) +";"
  
    # Send output to optoplate
    platereader_ser.write(bytes(output,'utf-8'))
    
  def calibrate():
    # Optoplate Serial Communication
    optoplate_ser = Serial('COM12', 9600) # left port
    optoplate_ser.write('hello;'.encode())
    optoplate_ser.write('S;'.encode())
    
    # Platereader Serial Commuication
    platereader_ser = Serial('COM11', 9600) # Right port
    platereader_ser.write('Connected;'.encode())
    platereader_ser.write('start;'.encode())
        
    with open('Calibration_Factors_newPlateReader.csv','w',newline='') as csvfile_c: #CHANGE FILE
        c_writer = csv.writer(csvfile_c,delimiter= ',')
        optoplate_ser.write(bytes('calibrate;','utf-8')) # Should tell optoplate to turn on OD and turn off blues                
        platereader_ser.write(bytes('calibrate;','utf-8')) # Should tell platereader to read OD
        cal_list = []
       
        for j in range(len(totalWells)): 
            print(j)
            newRead = ""
            r = optoplate_ser.readline().decode('utf-8').strip()

          # Wait until optoplate signals OD on
            while not ('odon' in r):
                print("stuck" + r)
                r = optoplate_ser.readline().decode('utf-8').strip()
            print(r)
          # Signal to platereader to read OD
            platereader_ser.write(bytes('readO;','utf-8'))
            newRead = newRead + platereader_ser.readline().decode('utf-8').strip()
            print("um" + newRead)
            while not ('D' in newRead):
                newRead = newRead + platereader_ser.readline().decode('utf-8').strip()
                print(newRead)
            index1 = newRead.index(".")
            index2 = newRead.index("D")
            cal_list.append(int(newRead[index1+1:index2]))
            optoplate_ser.write(bytes('nextO;','utf-8'))
        
        # NEW CALIBRATION
        
        avg_cals = (sum(cal_list))/96 # takes average of plate
        print("Average: ", avg_cals)
        Rcal_factors = []
        for raw_value in cal_list:
            cal_factor = avg_cals/raw_value  # raw_value * cal_factor = avg_cals    
            Rcal_factors.append(cal_factor) 
            
        
        # Red LEDs that do not work
        # Rcal_factors[7] = 0

       
        
        c_writer.writerow(Rcal_factors)
        c_writer.writerow(cal_list)
        print("Calibration Factor: ", Rcal_factors)
        print("Uncalibrated Readings: ", cal_list)
                
        optoplate_ser.write(bytes('odoff;','utf-8'))
        sys.exit()
    
  def getCalibrationFactors():
      with open('Calibration_Factors_newPlateReader.csv','r',newline='') as csvfile: #CHANGE FILE
          c_reader = csv.reader(csvfile, delimiter=',')
          redCalFactors = []
          line_count = 0
          for row in c_reader:
              if line_count == 0:
                  for entry in row:
                      redCalFactors.append(float(entry))
              line_count = line_count + 1
          return redCalFactors
    
  ## FEEDBACK FUNCTION ## 

  def Feedback1(self, optoplate_ser, pattern_wells, absorbance_values, OD_threshold, new_intensity): 
    # ** changes intensity of blue LED once well reaches a certain OD threshold) ** #     
    
    absorbance_values = [float(q) for q in absorbance_values]
    
    pattern_absorbance = [absorbance_values[well-1] for well in pattern_wells] # list of absorbance values for wells in pattern 
    
    print("pattern_wells: ", pattern_wells)
    print("pattern_abosrbance: ", pattern_absorbance)
    
    well_change = []
    if any(OD > OD_threshold for OD in pattern_absorbance):
        optoplate_ser.write(bytes('new_stim;','utf-8')) # signals arduino that new stimulation values are entering
        well_change = [well for well in pattern_wells if absorbance_values[well-1] > OD_threshold] # list of wells that will be changed
        print("well_change: ", well_change)
        
    well_count = len(well_change) #number of wells ready for intensity change
    print("well_count: ", well_count)
    
    output = str(well_count) + ";"
    for well in well_change:
        output = output + str(well-1) + ";" + str(new_intensity) + ";"
        # "number of wells; well index_1; new intensity; well index_2; new intensity; ... well index_n; new intensity
    
    print("any output: ", output)   
    if output != "0;":
        print("output to send: ", output)
        optoplate_ser.write(bytes(output,'utf-8'))

              
        
# # Manually Input Protocols

# wells = [[1, 2, 3, 4, 5], [i for i in range(5, 11)]] # [[pattern 1 wells], [pattern 2 wells], ...]
# intensity = [255, 255]# Intensity (0-4096) for each patterrn 
# intensity = [0,0] # Intensity (0-4096) for each pattern to be changed from initial settings
# timeOn = [3, 3] # Time on (seconds) for each pattern
# timeOff = [10, 10]# Time off (seconds) for each pattern
# fp = [60*20,10] # [interval (seconds), number of readings]
# od = [60*20,10] # [interval (seconds), number of readings]
# duration = 60*60*12 # Experiment duration (sec)
# totalWells = [i for i in range(1, 11)]; # Total wells in use


#Protocol(wells,intensity,timeOn,timeOff,fp,od,duration,totalWells) # To manually run experiment

#Protocol.calibrate() # To calibrate OptoPlate 

