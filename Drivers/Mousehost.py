import serial
import pyautogui
import time
import math

# --- CONFIGURATION ---
ARDUINO_PORT = 'COM3'   # CHECK YOUR PORT
BAUD_RATE = 9600
SENSITIVITY = 15        

# --- TUNING ---
RIGHT_CLICK_TIME = 0.8  # Time to hold for Right Click
DRAG_THRESHOLD = 30     # Pixels to move to trigger Drag
CENTER_X = 318          # Your Calibration
CENTER_Y = 318

pyautogui.FAILSAFE = False 
pyautogui.PAUSE = 0     

# --- STATE VARIABLES ---
current_state = "IDLE"
btn_prev = 1
press_start_time = 0
mouse_start_x = 0
mouse_start_y = 0

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.1)
    print(f"Connected to {ARDUINO_PORT}!")
    time.sleep(2) 
    ser.reset_input_buffer() 
    print("Analog Button System Active.")
except Exception as e:
    print(f"Error connecting: {e}")
    exit()

try:
    while True:
        # Flush buffer to prevent lag
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

        if line:
            data = line.split(',')
            if len(data) == 3:
                try:
                    raw_x = int(data[0]) 
                    raw_y = int(data[1]) 
                    btn_val = int(data[2]) 
                except ValueError:
                    continue 

                # --- MOVEMENT LOGIC ---
                diff_x = raw_x - CENTER_X
                diff_y = raw_y - CENTER_Y
                
                move_x = 0
                move_y = 0

                # Basic Movement
                if abs(diff_x) > 30: move_x = -(diff_x / SENSITIVITY) 
                if abs(diff_y) > 30: move_y = -(diff_y / SENSITIVITY) 

                # --- SMART BUTTON LOGIC ---
                
                # 1. BUTTON PRESSED (Transition from 1 -> 0)
                if btn_val == 0 and btn_prev == 1:
                    press_start_time = time.time()
                    mouse_start_x, mouse_start_y = pyautogui.position() 
                    current_state = "DECIDING"
                
                # 2. BUTTON HELD DOWN (0)
                elif btn_val == 0:
                    time_held = time.time() - press_start_time
                    
                    if current_state == "DECIDING":
                        # Did we move? -> DRAG
                        curr_x, curr_y = pyautogui.position()
                        dist = math.hypot(curr_x - mouse_start_x, curr_y - mouse_start_y)
                        
                        if dist > DRAG_THRESHOLD:
                            pyautogui.mouseDown()
                            current_state = "DRAGGING"
                        
                        # Did we hold still? -> RIGHT CLICK
                        elif time_held > RIGHT_CLICK_TIME:
                            pyautogui.rightClick()
                            print("Right Click!")
                            current_state = "RIGHT_CLICKED"

                # 3. BUTTON RELEASED (Transition from 0 -> 1)
                elif btn_val == 1 and btn_prev == 0:
                    if current_state == "DRAGGING":
                        pyautogui.mouseUp()
                    elif current_state == "DECIDING":
                        pyautogui.click() # Standard Click
                    
                    current_state = "IDLE"

                # --- EXECUTE MOVEMENT ---
                # Freeze movement if we are waiting for a Right Click
                if current_state != "RIGHT_CLICKED":
                    if move_x != 0 or move_y != 0:
                        pyautogui.move(int(move_x), int(move_y))

                btn_prev = btn_val

except KeyboardInterrupt:
    if current_state == "DRAGGING":
        pyautogui.mouseUp()
    print("\nStopped.")
    ser.close()
