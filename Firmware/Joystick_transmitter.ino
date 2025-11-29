// Arduino Mouse with Analog Button Logic

const int VRx = A0; 
const int VRy = A1; 
const int SW_PIN = A2; // Now using Analog Input

// CONFIGURATION

// If your "Pressed" state is > 4V, we look for values HIGHER than this.
const int BUTTON_THRESHOLD = 10; 

void setup() {
  Serial.begin(9600);
  // No INPUT_PULLUP needed because we are reading raw voltage
  pinMode(VRx, INPUT);
  pinMode(VRy, INPUT);
  pinMode(SW_PIN, INPUT); 
}

void loop() {
  int x = analogRead(VRx);
  int y = analogRead(VRy);
  
  // Read the Button Voltage (0 to 1023)
  int sw_voltage = analogRead(SW_PIN);
  int btnState = 1; // Default to 1 (Released)

  // 
  // So if voltage is high, we send 0 (Active).
  if (sw_voltage > BUTTON_THRESHOLD) {
    btnState = 0; // Pressed
  } else {
    btnState = 1; // Released
  }

  // Debugging: Uncomment this line if you need to see the actual voltage number
  // Serial.println(sw_voltage); 

  // Send formatted data to Python: "X,Y,Button"
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.println(btnState);

  delay(50); // Stability delay
}
