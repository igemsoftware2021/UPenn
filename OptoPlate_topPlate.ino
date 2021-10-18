// OPTOPLATE 

// Driver setup
#include "Adafruit_TLC5947.h"

const uint8_t NUM_TLC5974 = 12; 
const uint8_t data  = 4;
const uint8_t clock = 5;
const uint8_t latch = 6;
const uint8_t enable  = 7;  // set to -1 to not use the enable pin (its optional)
int redint = 300;

const int chanNum = 24*NUM_TLC5974;

Adafruit_TLC5947 tlc = Adafruit_TLC5947(NUM_TLC5974, clock, data, latch); //creates LED driver object
// End of driver setup

// Define variables


int intensity[] = {0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0,
                   0,0,0,0,0,0,0,0,0,0,0,0}; //  blue LED intensity for wells 1-96

                   
int timeON[] = {0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0};  //  blue LED time ON interval for wells 1-96
                
int timeOFF[] = {0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0};  //  blue LED time OFF interval for wells 1-96



long previousMillisStim[] = {0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0,
                             0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,0,0};  //  time at last stimulation for wells 1-96

int state[] = {0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,0,0,0,0}; //  track whether blue LEDs are ON (1) or OFF (0) for wells 1-96
               
String protocol;
long currentMillis;
String all_wells;
int fpSwitch = 0;


void setup() {  
  
  //Driver setup
  pinMode(enable, OUTPUT);
  digitalWrite(enable, HIGH);
  tlc.begin();
  Serial.begin(9600);
  
  // Loop through all 96 wells (chanNum/3 = 96) and set to initial OFF (0) state
  
  for (uint16_t i = 0; i < chanNum/3; i++){
    setAll(i, 0);
  }
  tlc.write();
  tlc.write();
  
  // Set enable pin HIGH to turn on drivers if using 
  
  if (enable >= 0) {
    pinMode(enable, OUTPUT);
    digitalWrite(enable, HIGH);
  }
  
  while (Serial.available() == 0) {
    //Wait for connection
  }
    
  while (Serial.available() > 0) {
    Serial.read();
  }  
  
  while(Serial.available() == 0){
    //Wait
  }
  
  while (Serial.readStringUntil(';') != "S"){
    // wait
  }
  while (Serial.available() == 0) {
    //Wait for connection
  }
  
  // CALIBRATE RED LEDS
  
  String r = Serial.readStringUntil(';'); 
  if (r == "calibrate"){
    calibrate();
  }

  //  READ STIMULATION LED PROTOCOLS FROM PYTHON 
  
  all_wells = Serial.readStringUntil(';'); // string of 96 characters indicating which wells are in use via setting index to 1
  
  for (int i = 0; i < 96; i++) { // Take in blue LED-specific instructions 
    intensity[i] = Serial.readStringUntil(';').toInt(); // LED intensity
  }

  for (int i = 0; i < 96; i++) { // Take in blue LED-specific instructions 
    timeON[i] = Serial.readStringUntil(';').toInt(); // LED ON duration
  }

  for (int i = 0; i < 96; i++) { // Take in blue LED-specific instructions     
    timeOFF[i] = Serial.readStringUntil(';').toInt(); // LED OFF duration
  }
    

// Calibrating timer

  int startMillis = round(millis()/1000);
  for(int i = 0; i < 96; i++){
    previousMillisStim[i] == startMillis;
  }
}

void loop() {
  currentMillis = round(millis()/1000);
  
  protocol = Serial.readStringUntil(';'); // Constantly waiting to read from pi

  if (protocol == "O"){   //  OPTICAL DENSITY READING LOOP
    OpticalDensity();
  }

  if (protocol == "odoff"){   // TURN ALL RED LEDS OFF AND RESUME STIMULATION AFTER OD READING
    resumeStim_OD();
  }
  

  if (protocol == "blueoff"){   // TURN STIM LEDS OFF WHEN READING FLUORESCENCE
    Fluorescence();
  }

  if (protocol == "blueon"){   // RESUME STIMULATION AFTER FLUORESCENCE READING
    resumeStim_Fluor();
  }

  if (protocol == "new_stim"){ // BEGIN STIMULATION ON COMPUTER COMMAND
    new_stimulation();
  }
  
  if (protocol == "shutdown"){   // SHUTDOWN PLATE
    endComm();
  }

  //  *** STIMULATION LIGHT PROTOCOL ***
  
  // TURN BLUE LEDS ON
  for (int i = 0; i < 96; i++) {
    if (currentMillis - previousMillisStim[i] >= timeOFF[i]){ // checking timer
      if ((state[i] == 0) && (fpSwitch == 0)){ // checking if well is OFF and fluorescence reading is not occurring 
        setBlue(i, intensity[i]);  
        state[i] = 1; // indicates that well light is ON
        previousMillisStim[i] = currentMillis;  // resets timer
      }
    }
  }
  tlc.write();
       
  // TURN BLUE LEDS OFF
  for (int i = 0; i < 96; i++) { 
    if (currentMillis - previousMillisStim[i] >= timeON[i]){ // checking timer
      if (state[i] == 1){ // checking if well is ON
        setBlue(i, 0);  
     
        state[i] = 0; // indicates that well light is OFF
        previousMillisStim[i] = currentMillis; 
      }
    }
  }
  tlc.write();
}

// *** CALIBRATION PROTOCOL *** //

void calibrate(){ 
  for (int i = 0; i < 96; i++) {//
    setOD(i, 500);
    setBlue(i, 0);
    tlc.write();
    tlc.write();
    
    Serial.println("odon");
    String r = Serial.readStringUntil(';');
    while (r != "nextO"){
      r = Serial.readStringUntil(';');
    }
    setOD(i,0);
    tlc.write();       
  }
  
  Serial.end();  // SHUTDOWN PLATE
  while (true) { // Experiment Complete 
  }
}

// *** OPTICAL DENSITY READING *** //

void OpticalDensity(){
  int cal = Serial.readStringUntil(';').toInt(); // save calibrated red LED intentisty for first well
  for (int i = 0; i < 96; i++) {
    setBlue(i,0); // turn all blue LEDs OFF 
  }  
  tlc.write();
  
  // Reading loop
  for (int i = 0; i < 96; i++) {
    if (all_wells.charAt(i) == '1'){
      setOD(i, cal); // turn single red LED ON
      tlc.write();
      Serial.println(cal);
      Serial.println("odon");
      String r = Serial.readStringUntil(';');
      while (r != "nextO"){
        r = Serial.readStringUntil(';');
      }
      cal = Serial.readStringUntil(';').toInt(); // save calibrated red LED intensity for next well
      setOD(i,0); // turn singlered LED OFF
      tlc.write();       
    }
  }  
}

// *** RESUME STIMULATION PATTERN AFTER OD READING *** //

void resumeStim_OD(){
  // Turn red LEDs OFF
  for (int i = 0; i < 96; i++) {
        setOD(i, 0); // turn single red LED OFF
   }

  // Resume stimulation LEDs
  for (int i = 0; i < 96; i++) { 
    if (state[i] == 1){ // checking if stimulation LED is meant to be ON 
       setBlue(i,intensity[i]);
    }
  }
  tlc.write();
  tlc.write();
}

// *** FLUORESCENCE READING *** 

void Fluorescence(){
  for (int i = 0; i < 96; i++) { // turn all LEDs OFF
    setBlue(i,0);
  }
  tlc.write();
  fpSwitch = 1; // Indicate fluorescence is being read
  String r =  Serial.readStringUntil(';');
  while (r != "done"){ // wait until fluorescence is complete
    r =  Serial.readStringUntil(';');
  }
 
}

// *** RESUME STIMULATION PATTERN AFTER FLUOR READING ***

void resumeStim_Fluor(){
  if(fpSwitch == 1){
      fpSwitch = 0; // indicates fluorescence is no longer reading
      for (int i = 0; i < 96; i++) { 
        if (state[i] == 1){ // checking if stimulation LED is meant to be ON
          setBlue(i,intensity[i]); //
        }
      }
  tlc.write();
  }
}

// *** NEW STIMULATION PATTERN FEEDBACK *** //
// python needs to send "number of wells; x; intensity; timeON; timeOFF; ...x_n; intensity_n; timeON_n; timeOFF_n" 

void new_stimulation(){
  int well_count = Serial.readStringUntil(';').toInt(); // number of wells who's settings are changing
  for (int i = 0; i < well_count; i++){
      int w = Serial.readStringUntil(';').toInt(); // index of well
      intensity[w] = Serial.readStringUntil(';').toInt(); // LED intensity
      // timeON[w] = Serial.readStringUntil(';').toInt(); // LED ON duration
      // timeOFF[w] = Serial.readStringUntil(';').toInt(); // LED OFF duration
    }
}

// *** SHUTDOWN *** //

void endComm(){
  for (int i = 0; i < 96; i++){
    setBlue(i,0);
    setOD(i,0);
  }
  tlc.write();
  tlc.write();
  Serial.end();
  while (true) { // Experiment Complete
  }
}

void setBlue(uint16_t well, uint16_t bright){
  //This is how Lukasz encoded each well to a channel number
  //well is a number ranging from 0 to 95 (for 96 total wells)
  //The formula well/12+8*(well%12) gives the driver channel controlling
  //the blue LED at that well
  uint16_t bluePosition = (uint16_t)((int)(well/12) + 8*(11-well%12));
  tlc.setPWM(bluePosition, bright);   //Set Blue

}

void setRed(uint16_t well, uint16_t bright){
  //The formula (well/12) + 8*(well%12)+96) gives the driver channel 
  //controlling the red LED at that well
  //uint16_t redPosition = (uint16_t)((int)(well/12) + 8*(well%12)+96); 
  uint16_t redPosition = (uint16_t)((int)(well/12) + 8*(11-(well%12))+96);  
  tlc.setPWM(redPosition, (bright));   //Set Red
}

void setOD(uint16_t well, uint16_t bright){
  //The formula (well/12) + 8*(well%12)+96) gives the driver channel 
  //controlling the red LED at that well
    uint16_t fBluePosition = (uint16_t)((int)(well/12)*12 +(11-(well%12))+192);
    tlc.setPWM(fBluePosition, bright); 

}


// *** ALL LED CONTROL *** //

//This function turns on all 3 LEDs at that position
void setAll(uint16_t well, uint16_t bright){
  setBlue(well, bright);
  setOD(well, bright);
}
