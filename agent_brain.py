import statistics
from collections import deque

class AgentBrain:
    def __init__(self):
        # State Management
        self.state = "CALIBRATING" # Starts in learning mode
        self.calibration_buffer = []
        self.calibration_limit = 20 # How many samples to learn from
        
        # Dynamic Thresholds (Will be learned)
        self.baseline_temp = 0.0
        self.dynamic_threshold = 0.0
        
        # Hard Safety Limits (Failsafes)
        self.HARD_LIMIT_TEMP = 80.0
        
        # Short-term memory for trend analysis
        self.temp_history = deque(maxlen=20)
        
    def analyze(self, data):
        """
        Adaptive Analysis Logic.
        """
        temp = data.get('temp', 0)
        volt = data.get('volt', 0)
        
        result = {
            "status": "NORMAL",
            "actions": [],
            "reason": "System Stable"
        }
        
        # --- PHASE 1: CALIBRATION (LEARNING) ---
        if self.state == "CALIBRATING":
            self.calibration_buffer.append(temp)
            progress = len(self.calibration_buffer)
            result['status'] = "LEARNING"
            result['reason'] = f"Calibrating Agent... ({progress}/{self.calibration_limit})"
            
            if len(self.calibration_buffer) >= self.calibration_limit:
                # Learning Complete: Calculate Baseline
                self.baseline_temp = statistics.mean(self.calibration_buffer)
                # Set dynamic limit (e.g., Baseline + 20%)
                self.dynamic_threshold = self.baseline_temp * 1.2
                
                self.state = "MONITORING"
                print(f"✅ AI CALIBRATION COMPLETE. Baseline: {self.baseline_temp:.2f}C, Threshold: {self.dynamic_threshold:.2f}C")
            
            return result

        # --- PHASE 2: ACTIVE MONITORING ---
        self.temp_history.append(temp)
        
        # Rule 1: Dynamic Anomaly Detection (The "AI" part)
        # If temp exceeds the learned threshold, it's an anomaly, even if it's not "Critical" yet.
        if temp > self.dynamic_threshold:
            result['status'] = "WARNING"
            result['reason'] = f"Abnormal Deviation (>{self.dynamic_threshold:.1f}C)"
            result['actions'] = ["CHECK_LOAD"]

        # Rule 2: Hard Safety Limit (The "Hardware Protection" part)
        if temp > self.HARD_LIMIT_TEMP:
            result['status'] = "FAULT"
            result['reason'] = f"CRITICAL OVERHEAT ({temp}°C)"
            result['actions'] = ["EMERGENCY_STOP", "ALARM_ON", "FAN_MAX"]

        # Rule 3: Trend Analysis (Predictive)
        # Check if temperature is rising consistently
        if len(self.temp_history) >= 5:
            recent = list(self.temp_history)[-5:]
            is_rising = all(recent[i] < recent[i+1] for i in range(len(recent)-1))
            
            # Only trigger trend warning if we are also above baseline
            if is_rising and temp > self.baseline_temp + 5:
                # Don't overwrite FAULT, but upgrade NORMAL to WARNING
                if result['status'] == "NORMAL":
                    result['status'] = "WARNING"
                    result['reason'] = "Trend: Rapid Heating Detected"
                    result['actions'].append("PRE_EMPTIVE_COOLING")

        return result