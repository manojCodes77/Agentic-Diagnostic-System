import serial
import time
import json
import random

class HardwareInterface:
    def __init__(self, port='COM3', baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.connection = None
        self.is_connected = False
        
        # --- SIMULATION STATE ---
        self.sim_temp = 45.0
        self.sim_volt = 5.0
        self.sim_curr = 1.2
        
        # Tracks if the fault is currently happening
        self.fault_active = False 

    def connect(self):
        """Attempts to connect to the physical Arduino."""
        try:
            self.connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)
            self.is_connected = True
            print(f"✅ SUCCESS: Connected to real hardware on {self.port}")
            return True
        except serial.SerialException:
            print(f"⚠️ HARDWARE NOT FOUND on {self.port}. Switching to Simulation Mode.")
            self.is_connected = False
            return False

    def get_data(self):
        """Reads real data OR generates simulated data."""
        if self.is_connected and self.connection:
            try:
                if self.connection.in_waiting > 0:
                    line = self.connection.readline().decode('utf-8').strip()
                    # We might get empty lines or garbage data occasionally
                    if line: 
                        return json.loads(line)
            except Exception as e:
                print(f"Serial Error: {e}")
        
        return self._generate_simulated_data()

    def send_command(self, command):
        """Sends command to hardware or prints to console in sim mode."""
        
        # 1. IF REAL HARDWARE IS CONNECTED
        if self.is_connected and self.connection:
            # This sends the actual bytes down the USB cable
            self.connection.write(f"{command}\n".encode())
            print(f"📡 [SENT TO USB]: {command}")
            
        # 2. IF IN SIMULATION MODE
        else:
            # We print this so you can verify the Agent is trying to act
            print(f"🤖 [AGENT ACTION]: {command}")

    def _generate_simulated_data(self):
        """Physics-based simulation of temperature."""
        
        # 1. Physics Logic: Heating vs Cooling
        if self.fault_active:
            # If fault is ON, heat up gradually
            if self.sim_temp < 95.0:
                self.sim_temp += 1.5
        else:
            # If fault is OFF, cool down naturally
            if self.sim_temp > 45.0:
                self.sim_temp -= 0.8
            elif self.sim_temp < 45.0:
                self.sim_temp += 0.5

        # 2. Add realistic sensor noise
        noise_t = random.uniform(-0.3, 0.3)
        noise_v = random.uniform(-0.05, 0.05)
        
        return {
            "temp": round(self.sim_temp + noise_t, 2),
            "volt": round(self.sim_volt + noise_v, 2),
            "curr": round(self.sim_curr, 2)
        }
    
    def inject_sim_fault(self):
        """Toggles the fault state."""
        self.fault_active = not self.fault_active
        return self.fault_active