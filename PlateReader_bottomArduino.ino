  /* PLATE READER TESTING */

/* ----------------DRIVER SETUP------------- */
#include "Adafruit_TLC5947.h"

//Sets up arduino pins for drivers
const uint8_t NUM_TLC5974 = 8; 
const uint8_t data  = 13;
const uint8_t clock = 5;
const uint8_t latch = 4;

Adafruit_TLC5947 tlc = Adafruit_TLC5947(NUM_TLC5974, clock, data, latch); //creates LED driver object

const int UVs[24] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 23, 22, 21, 20, 12, 13, 14, 15, 16, 17, 18, 19};

const int Blues[24] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 22, 23, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12};


/* ---------------MULTIPLEXER SETUP--------------- */
//Sets up arduino pins for multiplexer

int S[4] = {A1, A2, A3, A4};
int CS[6] = {7, 8, 9, 10, 11, 12};
int INPIN = A0;

/* ----------------VARIABLE SETUP ----------------- */
// Protocol inputs
String ledType1;  
String readNum1;  //Number of photodiode readings for Red LED
int od_readNum;
String stringWells1;
String all_wells;
String ledType2;      //LED type read from Python
String readNum2;      //Number of photodiode readings for UV LED
int fp_readNum;             
String protocol;


/* ----------------SETUP-------------- */
void setup() {
  //DRIVER SETUP
  tlc.begin();                //Initiate driver library
  Serial.begin(9600); //Begin serial monitor

  for (int x = 0; x < 4; x++) {
    pinMode(S[x], OUTPUT); // multiplexer outputs
  }
  
  for (int x = 0; x < 6; x++) {
    pinMode(CS[x], OUTPUT); // chip select outputs
  }
  pinMode(A0, INPUT);
  for (int i=0; i<96; i++) {
    SetBlues(i, 0); // sets blue LEDs to OFF
    SetUVs(i, 0); // sets UV LEDs to OFF 
    tlc.write();
  }

  //Establish serial connection between Python and Arduino
  while (Serial.available() == 0) {
    //Wait for connection
  }
  while (Serial.available() > 0) {
    Serial.read();
  }
  
  //Serial.println(Serial.readStringUntil(';'));
  while (Serial.readStringUntil(';') != "start"){
    //Wait
  }
  while (Serial.available() == 0) {
    //Wait for connection;
  }
  String r = Serial.readStringUntil(';');
  if (r == "calibrate"){
    calibrate();
  }
  
  
  // Read serial data from Python
  // Optical Density Reading Protocol
  ledType1 = Serial.readStringUntil(';'); //  O 
  readNum1 = Serial.readStringUntil(';'); // number of photodiode readings for Red LED
  stringWells1 = Serial.readStringUntil(';'); //  String of 96 char 0/1 numbers [same for Fluorescence reading]

  // Fluorescence Reading Protocol
  ledType2 = Serial.readStringUntil(';'); //  F
  readNum2 = Serial.readStringUntil(';'); // number of photodiode readings for UV LED
  

  //Serial.println("Received"); //Notify Python that it has been received

  // Save optical density protocol variable
  if (ledType1 == "O") { //  Saves OD protocol variables 
    od_readNum = readNum1.toInt();
    all_wells = stringWells1; 
  }
 // Save fluorescence protocol variable
  if (ledType2 == "F") {
    fp_readNum = readNum2.toInt(); 
  }
 }

void loop() {
  
  protocol = Serial.readStringUntil(';'); // Constantly waiting to read from Pi
  // protocol = Serial.readString(); // alternative 

  
  if (protocol == "F"){ // FLUORESCENCE READING 
    Fluorescence();
  }  
  
  if (protocol == "O") {  // OPTICAL DENSITY READING 
    OpticalDensity();
  }


  if (protocol == "shutdown"){  // SHUTDOWN EXPERIMENT
    endComm();
  }
} 

// *** CALIBRATION PROTOCOL **** //

void calibrate(){
  for (int i = 0; i < 96; i++) {
     String r = Serial.readStringUntil(';');
     while (r != "readO") {
          //wait
        r = Serial.readStringUntil(';');
      }

      SetWell(i); // connects multiplexer and pin
      delay(100); 
        
      //Take photodiode readings and send to Pi 
      Serial.println(".");
        
        double sum = 0;
        for (int q = 0; q < 10; q++){
           sum = sum + analogRead(INPIN);    
        }
        String readout = String(round(sum/10)) + "D";
        Serial.println(readout); // sends OD reading to Pi
      }
    Serial.println("*");    // Signals end of OD readings
    Serial.end();
    while (true) {
      // Experiment Complete
    }
}


//  *** FLUORESCENCE READING  PROTOCOL *** //

void Fluorescence(){ 
  for (int i = 0; i < all_wells.length(); i++) {
    if (all_wells.charAt(i) == '1'){  // selecting well that is part of protocol
    
      //Turn on UV LED
      SetUVs(i, 4095);
      tlc.write(); 

      SetWell(i); // connects multiplexer and pin
      delay(100); 
      
      //Take photodiode readings and send to Pi 
      Serial.println("#");
      double sum = 0;
      for(int j = 0; j < fp_readNum; j++){ // reads x number of readings
        sum = sum + analogRead(INPIN);  // sends UV reading to Pi
      }
      Serial.println(round(sum/fp_readNum)); // sends FP reading to Pi
      
      //Turn off UV LED
      SetUVs(i, 0);
      tlc.write();
    }
  }
  Serial.println("!");    // Signals end of Fluorescence readings
  Serial.flush();
}

//  *** OPTICAL DENSITY READING  PROTOCOL *** //

void OpticalDensity(){
  for (int i = 0; i < 96; i++) {
      if (all_wells.charAt(i) == '1'){

        String r = Serial.readStringUntil(';');
        while (r != "readO") {
          //wait
          r = Serial.readStringUntil(';');
        }

        SetWell(i); // connects multiplexer and pin
        delay(100);
        
        //Take photodiode readings and send to Pi 
        Serial.println("."); // signal beginning of well readings
        
        double sum = 0;
        for (int q = 0; q < od_readNum; q++){
           sum = sum + analogRead(INPIN); // takes the specified number of readings and sums them    
        }
        String readout = String(round(sum/od_readNum)) + "D"; // gets average reading for indivudal well; 
        Serial.println(readout); // sends raw OD reading to computer
      }
    }
    Serial.println("*");    // Signals end of OD readings
  
}

//  *** SHUTDOWN PROTOCOL *** //

void endComm(){
  Serial.end();
  for (int i = 0; i < 96; i++){
    SetUVs(i, 0);     //Turn off UV LED
    tlc.write();
    while (true) { // Experiment Complete
    }
  }
}

// *** SELECT MULTIPLEXER AND PIN *** //
void SetWell (int Well) {
  int VerticalWell = 8*(Well%12)+Well/12;
  int SetPin = VerticalWell;
  if ((VerticalWell/8)%2==1) {
    SetPin = VerticalWell+(8-VerticalWell)*2+7;
  }

  //CSselect function followed by pinselect in the same function
  for (int i=0; i<6; i++){
    digitalWrite(CS[i], HIGH);
  }
  delay(100);
  int CSselect = CS[VerticalWell/16];
  digitalWrite(CSselect, LOW);
  for (int x = 0; x<4; x++){
    byte state = bitRead(SetPin, x);
    digitalWrite(S[x], state);
  }
  delay(100);
}

// *** CONTROLS BLUE LEDS *** //
void SetBlues(int Well, int Int) {
  int VerticalWell = 8*(Well%12)+Well/12;
  int BluePin = Blues[VerticalWell%24]+24*(VerticalWell/24)+96;
  tlc.setPWM(BluePin, Int);
}

// *** CONTROLS UV LEDS *** //
void SetUVs(int Well, int Int) {
  int VerticalWell = 8*(Well%12)+Well/12;
  int UVPin = UVs[VerticalWell%24]+24*(VerticalWell/24);
  tlc.setPWM(UVPin, Int);
}
