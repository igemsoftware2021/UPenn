## GUI

# Import Packages
from tkinter import * 
from tkinter.ttk import *
from PIL import Image, ImageTk
import math
from string import ascii_uppercase
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import tkinter as tk
from tkinter import ttk
import time
from Protocol import Protocol
import matplotlib.colors as mcolors

class GUI(object):

    # HOMESCREEN
    def homeScreen():

        # Master Tk Object
        master = Tk()
        master.configure(bg='white')
        master.title("Homescreen")

        # Set Logo Icon
        img = (Image.open("blue_logo.png"))
        resized_image= img.resize((50,50),Image.ANTIALIAS)
        new_image = ImageTk.PhotoImage(resized_image)
        master.iconphoto(False, new_image)

        # Homeframe
        homeFrame = tk.Frame(master)
        homeFrame.configure(bg='white')

        # Screen Dimensions
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # OptoReader Logo 
        canvas = Canvas(homeFrame,width=int(screen_width*0.5),height=int(screen_height*0.5))
        img = (Image.open("optologo_small.png"))
        resized_image= img.resize((650,250),Image.ANTIALIAS)
        new_image = ImageTk.PhotoImage(resized_image)
        canvas.create_image(screen_width*0.25,screen_height*0.25,anchor=CENTER,image=new_image)
                           
        # Start Button Command
        def startCommand(): 
            homeFrame.destroy()
            GUI.protocolData(master)
        
        # Start Button
        start_btn = tk.Button(homeFrame,text="Start Experiment",fg='black',command=startCommand,width=20,height=3)

        # Spacing Label
        space_lbl = tk.Label(homeFrame,text="")
        
        # Add to screen
        canvas.pack(expand=True)
        homeFrame.pack(expand=True)
        space_lbl.pack(side=BOTTOM,pady=10)
        start_btn.pack(side=BOTTOM,pady=5)
        
        # Run Mainloop
        mainloop()

    # PROTOCOL DATA
    def protocolData(master):

        # Screen Setting
        master.title("Stimulation Settings")
        master.configure(bg='white')
        
        # List of 96 Colors
        full_color_list = ['dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan',
                           'dark slate gray','steel blue','light sea green','RoyalBlue1','medium blue','SteelBlue1','sky blue','cyan']
        
        # Wells selection frame
        wellsFrame = tk.Frame(master)
        wellsFrame.configure(bg='white')
        
        # Wells Selection Label
        title = tk.Label(wellsFrame,text="Select Wells",font=('TkDefaultFont', 14, 'bold'),bg='white')

        # Translate an rgb tuple to a tkinter color code
        color_vals = full_color_list[0]
        bgColor = 'white'
        
        # Set to store the user selected wells
        selected_wells = set([])
        
        # List to store selected wells by pattern
        selected_pattern_wells  = []
        
        # List to store total selected wells
        total_selected_wells = set([])
        
        # Set number of rows and columns
        row_count = 8
        column_count = 12
        
        # List to store pattern colors
        color_list = [color_vals]
        
        # List of wells, wells[i]=1 if selected and 0 if not selected
        wells = [0]*row_count*column_count

        # Row label list
        alphabet_string = ascii_uppercase
        rows = list(alphabet_string)[0:row_count]

        # Set up grid geometry
        square_size = 50 # Grid Square size
        w = square_size*(column_count+1) # Grid Width
        h = square_size*(row_count+1) # Grid Height
        
        # Create Canvas 
        c = Canvas(wellsFrame,height=h+square_size,width=w+square_size,bg=bgColor,highlightthickness=0)
            
        ## WELLS SELECTION
        def wellsSelection(wellsFrame,square_color):

            # Function to draw the grid of wells
            def create_grid(event=None):

                for x in range(0,w,square_size):
                    for y in range(0,h,square_size):

                        # Display Row Letter Labels in the first column
                        if (x==0 and y>0):
                            row_num = int(y/square_size)-1
                            row_label = rows[row_num]
                            c.create_text(square_size*.5+x,square_size*.5+y,text=str(row_label),font=('TkDefaultFont', 14, 'bold'))

                        # Display Column Number Labels in the first row
                        elif (y==0 and x>0):
                            column_label = int(x/square_size)
                            c.create_text(square_size*.5+x,square_size*.5+y,text=str(column_label),font=('TkDefaultFont', 14, 'bold'))

                        # Display Wells
                        elif (x>0 and y>0):

                            # Draw circular well
                            c.create_oval(x,y,x+square_size,y+square_size,width=4,activewidth=6,activeoutline = "gray",fill="white")
                            
                            
                            # Fill previous selected pattern wells
                            for i in range(len(selected_pattern_wells)):
                                if well_num in set(selected_pattern_wells[i]):
                                    c.create_oval(x,y,x+square_size,y+square_size,width=4,fill=color_list[i])
                                    text_state = NORMAL # Change to NORMAL to see well numbers or HIDDEN to not see
                                    c.create_text(square_size*.5+x,square_size*.5+y,text=str(i),state=text_state,font=('TkDefaultFont', 18, 'bold'))       
                            
            # When the mouse click is released               
            def callback(event):

                # Convert to x and y grid coordinates
                x = math.floor(event.x/square_size)
                y = math.floor(event.y/square_size)

                # If the mouse has been dragged
                if firstClick[0] != 0 and firstClick[1] != 0:

                    # Reset drag values
                    first_x = math.floor(firstClick[0]/square_size)
                    first_y = math.floor(firstClick[1]/square_size)
                    firstClick[0]=0
                    firstClick[1]=0
                    c.delete(selectionBox[0])
                    selectionBox[0] = 0
                    # Delete previous well preview
                    if len(ovals)>0:
                        for entry in ovals:
                            c.delete(entry)
                        del ovals[:]

                    # Get the first and last position of the drag
                    # Ensure position is on the canvas
                    lastPosition = [min(max(x,1),column_count),min(max(y,1),row_count)]
                    firstPosition = [min(max(first_x,1),column_count),min(max(first_y,1),row_count)]

                    # Select the wells within the dragged rectangle
                    for x in range(min(firstPosition[0],lastPosition[0]),max(firstPosition[0],lastPosition[0])+1):
                        for y in range(min(firstPosition[1],lastPosition[1]),max(firstPosition[1],lastPosition[1])+1):

                            # Well number (0-96)
                            well_num = int(x+(y-1)*column_count)

                            # Select the wells that were deselected
                            if wells[well_num-1] == 0:

                                # Set the well to selected
                                wells[well_num-1] = 1

                                # Call selectWell function to set
                                selectWell(x,y,well_num)

                # If the mouse was clicked within the grid
                elif(x>0 and x<=column_count and y>0 and y<=row_count):

                    # Well number (0-96)
                    well_num = int(x+(y-1)*column_count)

                    # Flip wells entry for the well num. 0->1 and 1->0
                    wells[well_num-1] = 1-wells[well_num-1] 

                    # Call selectWell function
                    selectWell(x,y,well_num)


            # Function to highlight and select/deselect a well
            def selectWell(x,y,well_num):

                # Select the well
                if wells[well_num-1]==1:

                    # Fill selected oval
                    shape = c.create_oval(x*square_size,y*square_size,x*square_size+square_size,y*square_size+square_size,fill=square_color,width=4)
                    text_state = NORMAL # Change to NORMAL to see well numbers or HIDDEN to not see
                    c.create_text(square_size*.5+x*square_size,square_size*.5+y*square_size,text=str(len(selected_pattern_wells)+1),state=text_state)
                    
                    # Add well number to selected wells set
                    selected_wells.add(well_num)

                # Deselect the well
                elif wells[well_num-1]==0:

                    # Unfill selected oval
                    c.create_oval(x*square_size,y*square_size,x*square_size+square_size,y*square_size+square_size,width=4,activewidth = 4,activeoutline = "gray",activefill=square_color,fill="white")

                    # Delete well number from selected wells set
                    if well_num in selected_wells:
                        selected_wells.remove(well_num)

            # Index of first click in drag motion: [x,y]            
            firstClick = [0,0]

            # Store a transparent selection rectangle
            selectionBox = [0]

            # Store previewed wells
            ovals = []

            # Preview of dragged wells
            def preview(firstClick_x,firstClick_y,x,y):

                # Delete previous well preview
                if len(ovals)>0:
                    for entry in ovals:
                        c.delete(entry)
                    del ovals[:]

                # Convert to x and y grid coordinates
                first_x = math.floor(firstClick_x/square_size)
                first_y = math.floor(firstClick_y/square_size)
                x = math.floor(x/square_size)
                y = math.floor(y/square_size)

                # Get the first and last position of the drag
                # Ensure position is on the canvas
                lastPosition = [min(max(x,1),column_count),min(max(y,1),row_count)]
                firstPosition = [min(max(first_x,1),column_count),min(max(first_y,1),row_count)]


                # Select the wells within the dragged rectangle
                for x in range(min(firstPosition[0],lastPosition[0]),max(firstPosition[0],lastPosition[0])+1):
                    for y in range(min(firstPosition[1],lastPosition[1]),max(firstPosition[1],lastPosition[1])+1):

                        # Well number (0-96)
                        well_num = int(x+(y-1)*column_count)

                        # Fill selected oval
                        oval = c.create_oval(x*square_size,y*square_size,x*square_size+square_size,y*square_size+square_size,fill=square_color,width=4,outline="gray")
                        ovals.append(oval)


            # When the mouse is dragged
            def drag(event):

                # Get the mouse cursor position
                x = event.x
                y = event.y

                # Drag start
                if firstClick[0]==0 and firstClick[1]==0:

                    # Set the position to be in the canvas
                    x = min(max(x,square_size),w)
                    y = min(max(y,square_size),h)

                    # Store x and y coordinates of first click
                    firstClick[0] = x
                    firstClick[1] = y

                else:
                    # Show wells preview
                    preview(firstClick[0],firstClick[1],x,y)

            # Bind mouse click, drag, and grid configuration to canvas
            c.bind("<ButtonRelease-1>",callback)
            c.bind("<Configure>",create_grid)
            c.bind("<B1-Motion>",drag)

            # Select all wells Button callback
            def selectAllCallback():

                # For each [x,y] well coordinate
                for x in range(1,column_count+1):
                    for y in range(1,row_count+1):

                        # Well number (0-96)
                        well_num = int(x+(y-1)*column_count)

                        # If the well hasn't been selected yet
                        if wells[well_num-1]==0:
                            
                            # Set the well to selected
                            wells[well_num-1] = 1

                            # Call selectWell function to set well
                            selectWell(x,y,well_num)               

            # Clear all wells Button callback
            def clearAllCallback():

                # For each [x,y] well coordinate
                for x in range(1,column_count+1):
                    for y in range(1,row_count+1):

                        # Well number (0-96)
                        well_num = int(x+(y-1)*column_count)

                        # If the well was selected in the current pattern
                        if well_num in selected_wells:
                            
                            # Set the well to deselected
                            wells[well_num-1] = 0

                            # Call selectWell function to set well
                            selectWell(x,y,well_num)

            # Select all wells button
            select_all_button = tk.Button(wellsFrame,text="Select All Wells",command=selectAllCallback,bg='grey',fg='black')

            # Clear all wells button
            clear_all_button = tk.Button(wellsFrame,text="Clear All Wells",command=clearAllCallback,bg='grey',fg='black')

            # Place widgets on the screen
            title.grid(row=0,column=0,columnspan=2)
            c.grid(row=2,column=0,padx=square_size,columnspan=2)
            select_all_button.grid(row=3,column=0,pady=10)
            clear_all_button.grid(row=3,column=1,pady=10)
            
        wellsSelection(wellsFrame,color_vals)

        ## PROTOCOL SETTINGS 

        # Protocol data frame
        stimFrame = tk.Frame(master)
        stimFrame.configure(bg='white')
        blueSettings = tk.Frame(master)
        blueSettings.configure(bg='white')
        
        # Intensity Scale 
        intLabel = tk.Label(blueSettings, text="Intensity",bg='white')    
        intLabel.grid(row=2, column=0)
        intMax = tk.Label(blueSettings, text="100%",bg='white')      
        intMax.grid(row=2, column=3)
        intensity = tk.Scale(blueSettings, from_=0, to=100, orient=HORIZONTAL, length=200,bg='white')
        intensity.grid(row=2, column=2)

        # Time On Entry 
        onLabel = tk.Label(blueSettings, text="Time ON (s)",bg='white')
        onLabel.grid(row=3, column=0)
        onScale = tk.Entry(blueSettings,bg='white')
        onScale.grid(row=3, column=2)

        # Time Off Entry
        offLabel = tk.Label(blueSettings, text="Time OFF (s)",bg='white')
        offLabel.grid(row=4, column=0)
        offScale = tk.Entry(blueSettings,bg='white')
        offScale.grid(row=4, column=2)
        
        global pattern_data
        pattern_data = []  
        
        def gen_graph():            
            on_dur = int(onScale.get())
            off_dur = int(offScale.get())
            on_int = intensity.get()       
            pattern_data.append([round(on_dur),round(off_dur),round(on_int)])
            selected_pattern_wells.append(list(selected_wells))
            total_selected_wells.update(selected_wells)
            selected_wells.clear()
            pattern_number = len(pattern_data)+1
            new_color = full_color_list[pattern_number-1]
            color_list.append(new_color)
            pattern_design.create_oval(10,10,square_size,square_size,fill=new_color,width=4)
            pattern_design.delete(pattern_text[0])
            del pattern_text[0]
            pattern_text.append(pattern_design.create_text(square_size*.5+5,square_size*.5+5,text=str(pattern_number),font=('TkDefaultFont', 18, 'bold')))
            wellsSelection(wellsFrame,new_color)
            onScale.delete(0)
            offScale.delete(0)
            intensity.set(0) 
                  
        space1 = Label(blueSettings, text = '')
        space1.grid(row=5)
        
        graph = tk.Button(blueSettings, text='Set  Protocol', command=gen_graph,bg="white")
        graph.grid(row=6, column=3)


        # Variables to store user input
        
        global fp_data
        fp_data = [1]

        global od_data
        od_data = [1]
        
        global ed_data
        ed_data = [1]



        #creating labels so user knows what data to input into the textboxes below
        pattern_number_label = tk.Label(blueSettings,anchor = 'e',text='Protocol Number:',font=('TkDefaultFont', 14, 'bold'),bg='white').grid(row=1,column=0,columnspan=2)
        

        #input boxes 
        pattern_text = []

        pattern_design = Canvas(blueSettings,height=square_size+10,width=square_size+10,bg=bgColor,highlightthickness=0)
        pattern_design.create_oval(10,10,square_size,square_size,fill=color_vals,width=4)
        pattern_text.append(pattern_design.create_text(square_size*.5+5,square_size*.5+5,text=str(1),font=('TkDefaultFont', 14, 'bold')))
        pattern_design.grid(row=1,column=3) 


        #function to store usar inputted interval and duration information
        def set_FP_data():
            #get values from interval_entry and duration_entry 
            interval = intervalFP_entry.get()
            duration = durationFP_entry.get()

            global fp_data
            fp_data = [interval,duration]

            #resetting form
            intervalFP_entry.delete(0,END)
            durationFP_entry.delete(0,END)

            
            intervalFP_entry.grid(row=6,column=2)

          
            durationFP_entry.grid(row=7,column=2)

        #save current inputted pattern
        total_wells = []

        readingFrame = tk.Frame(master)
        readingFrame.configure(bg='white')
        master.title("Sensor Settings")
    
        space1_label = tk.Label(readingFrame, text = '',bg="white").grid(row=0,column=1)

        space3_label = tk.Label(readingFrame, text = '',bg="white").grid(row=1,column=1)

        fp_interval_label = tk.Label(readingFrame,text='Reading Interval (s)',bg="white").grid(row=4,column=1)
        fp_duration_label = tk.Label(readingFrame, text = 'Number of Readings',bg="white").grid(row=5,column=1)

        space3_label = tk.Label(readingFrame, text = '',bg="white").grid(row=6,column=1)

        od_interval_label = tk.Label(readingFrame,text='Reading Interval (s)',bg="white").grid(row=8,column=1)
        od_intensity_label = tk.Label(readingFrame, text = 'Number of Readings',bg="white").grid(row=9,column=1)

        space4_label = tk.Label(readingFrame, text = '',bg="white").grid(row=10,column=1)

        

        #for feedback
        title_label = tk.Label(readingFrame,text='Feedback',font=('TkDefaultFont', 14, 'bold'),bg="white").grid(row=11,column = 1,columnspan=2)
        feedback_label = tk.Label(readingFrame, text = 'OD Threshold',bg="white").grid(row=12,column=1)
        feedback_intensity_label = tk.Label(readingFrame, text = 'Intensity Above Threshold',bg="white").grid(row=13,column=1)
        feedback_intensity = tk.Scale(readingFrame, from_=0, to=100, orient=HORIZONTAL, length=200,bg='white').grid(row=13,column=2)
        space4_label = tk.Label(readingFrame, text = '',bg="white").grid(row=15,column=1)
        feedback_entry = tk.Entry(readingFrame,bg="white")
        feedback_entry.grid(row=12,column=2)

        #for experiment duration
        title_label = tk.Label(readingFrame,text='Experiment Duration',font=('TkDefaultFont', 14, 'bold'),bg="white").grid(row=16,column = 1,columnspan=2)
        day_label = tk.Label(readingFrame, text = 'Days',bg="white").grid(row=17,column=1)
        minute_label = tk.Label(readingFrame, text = 'Minutes',bg="white").grid(row=18,column=1)
        seconds_label = tk.Label(readingFrame,text='Seconds',bg="white").grid(row=19,column=1)

        space5_label = tk.Label(readingFrame, text = '',bg="white").grid(row=20,column=1)

        f_protein = tk.Label(readingFrame, text='Fluorescence Reading',font=('TkDefaultFont', 14, 'bold'),bg="white")
        f_protein.grid(row = 3,column = 1,columnspan=2)

        o_density = tk.Label(readingFrame,text='Optical Density Reading',font=('TkDefaultFont', 14, 'bold'),bg="white")
        o_density.grid(row = 7,column = 1,columnspan=2)



        #for FP
        intervalFP_entry = tk.Entry(readingFrame,bg="white")
        
        intervalFP_entry.grid(row=4,column=2)

        durationFP_entry = tk.Entry(readingFrame,bg="white")
    
        durationFP_entry.grid(row=5,column=2)

        #for OD
        intervalOD_entry = tk.Entry(readingFrame,bg="white")
       
        intervalOD_entry.grid(row=8,column=2)

        durationOD_entry = tk.Entry(readingFrame,bg="white")
        
        durationOD_entry.grid(row=9,column=2)



        #for expirament duration
        day_entry = tk.Entry(readingFrame,bg="white")
        day_entry.grid(row=17,column=2)

        minute_entry = tk.Entry(readingFrame,bg="white")
        minute_entry.grid(row=18,column=2)

        second_entry = tk.Entry(readingFrame,bg="white")
        second_entry.grid(row=19,column=2)
        

        def reviewPage():    
            # fp_data
            fp_data.append(intervalFP_entry.get())
            fp_data.append(durationFP_entry.get())
            
            # od_data
            od_data.append(intervalOD_entry.get())
            od_data.append(durationOD_entry.get())
            
            # ed_data
            ed_data.append(day_entry.get())
            ed_data.append(minute_entry.get())
            ed_data.append(second_entry.get())
            
            selected_pattern_wells.append(list(selected_wells))
            total_selected_wells.update(selected_wells)
            selected_wells.clear() 
            
            readingFrame.destroy()
            GUI.protocolReview(master,c,fp_data,od_data,ed_data,color_list,total_selected_wells,selected_pattern_wells,pattern_data)
              
            
        #function to navigate forward after finished imputting settings
        def readingPage():
            plt.close(1)
        
            review_button = tk.Button(master, text="Review",command = reviewPage,bg="white").grid(row=2,column=1,sticky=E)
            readingFrame.grid(row=0, column=1,columnspan=1,rowspan=2)
            
            
            blueSettings.destroy()
            wellsFrame.destroy()
            
            
        def backCommand():
            return


        next_button = tk.Button(blueSettings, text='Next Page', command = readingPage,bg="white").grid(row=8,column=3,sticky=E)
        
        # Set well selection frame and protocol frame on the window
        wellsFrame.grid(row=0,column=0,rowspan=2)
        blueSettings.grid(row=1,column=1)


        mainloop()
        
        
    def readingWin(master,wellsFrame):
        
        
        wellsFrame.grid(master,row=0,column=0)

    ## REVIEW AND EDIT

    def protocolReview(master,c,fp_data,od_data,ed_data,color_list,total_selected_wells,selected_pattern_wells,pattern_data):
        
        total_wells_data = [[0,0,0]]*96
        
        if (len(pattern_data)>0):
            for i in range(len(selected_pattern_wells)):
                for wellnum in selected_pattern_wells[i]:
                    total_wells_data[wellnum-1] = pattern_data[i]
        
        master.title("Review")
        master.configure(bg='white')
        
        # Wells selection frame
        wellsFrame = tk.Frame(master)
        wellsFrame.configure(bg='white')
        
        # Wells Selection Label
        title = tk.Label(wellsFrame,text="Stimulation Review",font=('TkDefaultFont', 20, 'bold'),bg="white")
        
        # Set number of rows and columns
        row_count = 8
        column_count = 12
        
        # List of wells, wells[i]=1 if selected and 0 if not selected
        wells = [0]*row_count*column_count
        
        # Translate an rgb tuple to a tkinter color code
        color_vals = (3,168,158)
        def color(rgb):
            return "#%02x%02x%02x" % rgb
        bgColor = color((240,240,237))
        bgColor = 'white'
        

        # Row label list
        alphabet_string = ascii_uppercase
        rows = list(alphabet_string)[0:row_count]

        # Set up grid geometry
        square_size = 60 # Grid Square size
        w = square_size*(column_count+1) # Grid Width
        h = square_size*(row_count+1) # Grid Height
        
        # Create Canvas 
        c = Canvas(wellsFrame,height=h+square_size,width=w+square_size,bg=bgColor,highlightthickness=0)
        
        ## WELLS SELECTION
        def wellsSelection(wellsFrame,square_color):

            # Function to draw the grid of wells
            def create_grid(event=None):

                for x in range(0,w,square_size):
                    for y in range(0,h,square_size):

                        # Display Row Letter Labels in the first column
                        if (x==0 and y>0):
                            row_num = int(y/square_size)-1
                            row_label = rows[row_num]
                            c.create_text(square_size*.5+x,square_size*.5+y,text=str(row_label),font=('TkDefaultFont', 14, 'bold'))

                        # Display Column Number Labels in the first row
                        elif (y==0 and x>0):
                            column_label = int(x/square_size)
                            c.create_text(square_size*.5+x,square_size*.5+y,text=str(column_label),font=('TkDefaultFont', 14, 'bold'))

                        # Display Wells
                        elif (x>0 and y>0):
                            # Display well numbers (optional) 
                            text_state = NORMAL # Change to NORMAL to see well numbers or HIDDEN to not see
                            well_num = int((x/square_size)+(y/square_size-1)*column_count)
                            c.create_text(square_size*.5+x,square_size*.5+y,text=str(well_num),state=text_state)

                            # Draw circular well
                            c.create_oval(x,y,x+square_size,y+square_size,activewidth = 4,width=4,fill="white")
                            
                            # Fill previous selected pattern wells
                            for i in range(len(selected_pattern_wells)):
                                if well_num in set(selected_pattern_wells[i]):
                                    c.create_oval(x,y,x+square_size,y+square_size,width=4,fill=color_list[i])
       
            c.bind("<Configure>",create_grid)
        
        rectangles = []
        
        def motion(event):
            
            # Delete previous well preview
            if len(rectangles)>0:
                for entry in rectangles:
                    c.delete(entry)
                del rectangles[:]
            
            
            # Get the mouse cursor position
            x = event.x
            y = event.y
            
            new_x = x-(x%square_size)
            new_y = y-(y%square_size)
            
            # Well number
            well_num = int(new_x/square_size+(new_y/square_size-1)*column_count)
            
            # If the mouse is within the wells selection
            if new_x >= square_size and new_y >= square_size and new_x<=square_size*(column_count) and new_y<=square_size*(row_count):
                rectangles.append(c.create_rectangle(new_x,new_y,new_x+square_size,new_y+square_size,
                                fill="light gray",width="5"))
                on = total_wells_data[well_num-1][0]
                off = total_wells_data[well_num-1][1]
                intensity = total_wells_data[well_num-1][2]
                rectangles.append(c.create_text(new_x+square_size/2,new_y+square_size/2,
                                               text = str(on)+"s ON\n"+str(off)+"s OFF\n"+str(intensity)+"% INT",
                                               font=('TkDefaultFont', 10, 'bold')))
                # pattern_data = [on_dur,off_dur,on_int] for each pattern
                
            
            
            
        
        
        c.bind("<Motion>",motion)  
        title.grid(row=0,column=0,columnspan=2)
        c.grid(row=1,column=0,padx=square_size,columnspan=2)
        wellsSelection(wellsFrame,"bgColor")
        wellsFrame.grid(row=0,column=0)
        
        
        
        
        # Sensor Review
        sensorFrame = tk.Frame(master)
        sensorFrame.configure(bg='white')
        
       
        sensor_title = tk.Label(sensorFrame,text="Sensor Review",font=('TkDefaultFont', 20, 'bold'),bg="white")
        sensor_title.grid(row=0,column=0,columnspan=2)
        tk.Label(sensorFrame,text=" ",bg="white").grid(row=1,column=0)
        
        f_title = tk.Label(sensorFrame,text="Fluorescence Reading",font=('TkDefaultFont', 12, 'bold'))
        f_title.grid(row=2,column=0,columnspan=2)
        
        interval_label = tk.Label(sensorFrame,text="Reading Interval",bg="white").grid(row=3,column=0)
        duration_label = tk.Label(sensorFrame,text="Number of Readings",bg="white").grid(row=4,column=0)
        f_interval = tk.Label(sensorFrame,text=fp_data[1]+" s",bg="white").grid(row=3,column=1)
        f_duration = tk.Label(sensorFrame,text=fp_data[2],bg="white").grid(row=4,column=1)
        
        tk.Label(sensorFrame,text=" ").grid(row=5,column=0)
        od_title = tk.Label(sensorFrame,text="Optical Density Reading",font=('TkDefaultFont', 12, 'bold'),bg="white").grid(row=6,column=0,columnspan=2)
        interval_label = tk.Label(sensorFrame,text="Reading Interval",bg="white").grid(row=7,column=0)
        duration_label = tk.Label(sensorFrame,text="Number of Readings",bg="white").grid(row=8,column=0)
        od_interval = tk.Label(sensorFrame,text=od_data[1] + " s",bg="white").grid(row=7,column=1)
        od_duration = tk.Label(sensorFrame,text=od_data[2],bg="white").grid(row=8,column=1)
        
        tk.Label(sensorFrame,text=" ",bg="white").grid(row=9,column=0)
        exdur_title = tk.Label(sensorFrame,text="Experiment Duration",font=('TkDefaultFont', 12, 'bold'),bg="white").grid(row=10,column=0,columnspan=2)
        days = tk.Label(sensorFrame,text="Days ",bg="white").grid(row=11,column=0)
        minutes = tk.Label(sensorFrame,text="Minutes ",bg="white").grid(row=12,column=0)
        seconds = tk.Label(sensorFrame,text="Seconds ",bg="white").grid(row=13,column=0)
        
        e_days = tk.Label(sensorFrame,text=ed_data[1],bg="white").grid(row=11,column=1)
        e_minutes = tk.Label(sensorFrame,text=ed_data[2],bg="white").grid(row=12,column=1)
        e_seconds = tk.Label(sensorFrame,text=ed_data[3],bg="white").grid(row=13,column=1)
        
        
        sensorFrame.grid(row=0,column=1,padx=30)
        
        def run_command():
            wells = []
            
            for entry in selected_pattern_wells:
                if len(entry)>0:
                    wells.append(sorted(entry))
            
            
            timeOn = []
            timeOff = []
            intensity = []
            for entry in pattern_data:
                timeOn.append(entry[0])
                timeOff.append(entry[1])
                intensity.append(round((entry[2]/100)*255,5))
              
            fp = [int(fp_data[1])*1000,int(fp_data[2])]
            od = [int(od_data[1])*1000,int(od_data[2])]
            
            duration = int(ed_data[1])*24*60*60 + int(ed_data[2])*60 + int(ed_data[3])
            
            totalWells = list(total_selected_wells)
        
            print("wells: ", wells)
            print("intensity: ", intensity)
            print("timeOn: ", timeOn)
            print("timeOff: ", timeOff)
            print("fp: ", fp)
            print("od: ", od)
            print("duration: ", duration)
            print("totalWells: ", totalWells)
              
            #Protocol(wells,intensity,timeOn,timeOff,fp,od,duration,totalWells)
       
        run_button = tk.Button(master,text="Run Plate",command = run_command,bg="white").grid(row=1,column=0,columnspan=2,pady=10)
        

# Run the GUI
GUI.homeScreen()







