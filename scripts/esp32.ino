//This is the code for the ESP32, transmitting 3-bit values to the Jetson Nano
// instantiating pins
const int in1 = 14; // Greeting Zone
const int in2 = 12;// Playing Zone
const int in3 = 13; // ADC Master Status

// instantiating timing delays
const unsigned long ENTRY_DELAY = 1000; // 3 seconds to confirm entry
const unsigned long EXIT_DELAY  = 3000; // 3 seconds to confirm departure

// timers 
unsigned long greetEntryCount = 0, greetExitCount = 0;
unsigned long playEntryCount = 0, playExitCount = 0;

// logical States (the filtered results)
bool greetState = false; // Greeting active
bool playState = false; // Playing active

void setup() {
 
  Serial.begin(115200); // baud rate is 
 
  pinMode(in1, INPUT_PULLDOWN);
  pinMode(in2, INPUT_PULLDOWN);
  pinMode(in3, INPUT_PULLDOWN);
}

void loop() {
  unsigned long now = millis();
  bool adcActive = digitalRead(in3);

  // PROCESS TIMING LOGIC (Only if ADC is ON)
  if (adcActive) {
    
    // GREETING ZONE (in1)
    if (digitalRead(in1)) {
      greetExitCount = 0; // Reset exit timer
      if (greetEntryCount == 0) 
          greetEntryCount = now; 
      if (now - greetEntryCount >= ENTRY_DELAY) 
        greetState = true;
    } else {
      greetEntryCount = 0; // Reset entry timer
      if (greetState && greetExitCount == 0) greetExitCount = now;
      if (greetExitCount > 0 && (now - greetExitCount >= EXIT_DELAY)) {
        greetState = false;
        greetExitCount = 0;
      }
    }

    // PLAYING ZONE (in2)
    if (digitalRead(in2)) {
      playExitCount = 0;
      if (playEntryCount == 0) 
        playEntryCount = now;
      if (now - playEntryCount >= ENTRY_DELAY) 
        playState = true;
    } else {
      playEntryCount = 0;
      if (playState && playExitCount == 0) 
        playExitCount = now;
      if (playExitCount > 0 && (now - playExitCount >= EXIT_DELAY)) {
        playState = false;
        playExitCount = 0;
      }
    }

  } else {
    // ADC is OFF: Reset everything immediately
    greetState = playState = false;
    greetEntryCount = playEntryCount = greetExitCount = playExitCount = 0;
  }

  // DETERMINE GAME STATE (Whiteboard Logic)
  int gameState; // Default: None (System ON, no one there)

  if (!adcActive) {
    gameState = 0; // Optional: System OFF
  } else if (playState) {
    gameState = 3; // PlayZone (Highest Priority)
  } else if (greetState) {
    gameState = 2; // Warning (Greeting)
  } else {
    gameState = 1; //System is on, No one is detected
  }

  // OUTPUT RESULTS — send only on state change + 1 Hz heartbeat.
  // Cuts USB serial traffic ~10x vs the old 10 Hz unconditional stream,
  // freeing bandwidth for the camera on the shared USB hub.
  static int lastSent = -1;
  static unsigned long lastSerialTime = 0;
  if (gameState != lastSent || (now - lastSerialTime >= 1000)) {
    Serial.println(gameState);
    lastSent = gameState;
    lastSerialTime = now;
  }

}