#JoyMouse

# Arduino Joystick Mouse Interface (Recycled Hardware Project)

# Project Objective

The primary goal of this project was to design and build a fully functional computer mouse using an **Arduino Uno** and a recycled **PS3 Joystick module**.

While the Arduino Leonardo has native mouse capabilities, the standard Arduino Uno does not. This project bridges that gap by creating a custom Serial-to-HID (Human Interface Device) protocol, allowing the Uno to control the computer's cursor, clicks, and drag-and-drop operations with precision equal to a commercial mouse.

-----

## The Engineering Journey

Making a standard mouse is easy. Making a reliable mouse from recycled console parts and an Arduino Uno presented three distinct engineering challenges that I had to solve.

### Challenge 1: The "Non-HID" Limitation

**The Problem:** The Arduino Uno acts as a Serial device, not a generic USB Mouse.
**The Solution:** I developed a "Bridge Architecture."

1.  **Firmware (C++):** The Arduino acts as a high-speed sensor hub, reading analog data and streaming it via UART at 50Hz.
2.  **Driver (Python):** A custom host script listens to the stream, performs signal processing, and injects cursor events into the operating system using the `pyautogui` library.

### Challenge 2: Signal Integrity (The Voltage Divider vs. Analog Input)

**The Problem:** The recycled PS3 joystick module had non-standard internal wiring. When I tried to read the button press digitally, the voltage didn't drop to a clean logic LOW (0V).
**Attempted Solution (Voltage Divider):** I initially built a voltage divider circuit to force the logic level down. While this fixed the button read, it caused **"Ground Bounce"** (Rail Sag). The current draw from the divider shifted the Ground reference for the X and Y potentiometers, causing the cursor to jump wildly every time I clicked.
**Final Solution (Analog Thresholding):** To solve the drift, I removed the digital logic and routed the switch to an **Analog Input (ADC)**. By reading the raw voltage and setting a software threshold (\> 4.0V = Pressed), I could detect clicks reliably without putting load on the circuit or disturbing the sensitive X/Y motion sensors.

### Challenge 3: Single-Button User Experience

**The Problem:** The hardware only has one physical button (the Z-axis switch), but a PC requires Left-Click, Right-Click, and Dragging.
**The Solution:** I implemented a **Heuristic State Machine** in Python to infer user intent based on time and movement:

  * **Click:** Press & Release quickly.
  * **Drag:** Press & Move joystick immediately.
  * **Right Click:** Press & Hold stationary for 0.8 seconds.

-----

## Technical Implementation

### Hardware Logic

  * **X/Y Axis:** Standard potentiometer reading mapped to screen coordinates.
  * **Z Axis (Button):** Analog voltage sampling to bypass "floating ground" issues found in recycled hardware.

### Signal Processing Algorithms

  * **Anti-Drift Calibration:** On startup, the system calculates the specific resting voltage of the recycled joystick (e.g., Center \~318) to prevent cursor drift.
  * **Dynamic Deadzone:** To prevent the cursor from shaking when the button is pressed (mechanical vibration), the software automatically expands the sensor deadzone during click events, ensuring the mouse stays steady while clicking.

-----

## Setup Instructions

### 1\. Wiring

  * **Joystick VRx** $\rightarrow$ Arduino **A0**
  * **Joystick VRy** $\rightarrow$ Arduino **A1**
  * **Joystick SW** $\rightarrow$ Arduino **A2** (Analog Input)
  * **VCC/GND** $\rightarrow$ 5V Rail

### 2\. Installation

1.  Upload the `firmware.ino` to your Arduino Uno.
2.  Install Python dependencies:
    ```bash
    pip install pyserial pyautogui
    ```
3.  Run the driver script:
    ```bash
    python mouse_driver.py
    ```

-----

## Future Improvements

  * Add PID control loops to smooth out the acceleration curve of the cursor.
  * Implement a dedicated "Scroll Mode" toggle.
