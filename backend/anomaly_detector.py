import numpy as np
from sklearn.ensemble import IsolationForest
from db import logs_col
import os

# Feature mapping dictionaries
LOCATION_MAP = {"Coimbatore": 0, "Chennai": 1, "Bangalore": 2, "Delhi": 3}
DEVICE_MAP = {"Workstation-Admin-01": 0, "DBA-Terminal-A": 1, "IT-Support-Host": 2, "Audit-Sec-01": 3}

def map_location(loc):
    return LOCATION_MAP.get(loc, 4)

def map_device(dev):
    return DEVICE_MAP.get(dev, 4)

class AnomalyDetector:
    def __init__(self):
        self.models = {}

    def _prepare_data(self, logs):
        X = []
        for log in logs:
            X.append([
                int(log.get("login_hour", 9)),
                map_location(log.get("location", "Coimbatore")),
                map_device(log.get("device", "Workstation-Admin-01")),
                int(log.get("failed_logins", 0)),
                int(log.get("commands_count", 0)),
                int(log.get("files_accessed", 0))
            ])
        return np.array(X)

    def train_user_model(self, username):
        # Fetch historical logs for user
        logs = logs_col.find({"username": username})
        if len(logs) < 10:
            # Not enough data, return None
            return None
        
        X = self._prepare_data(logs)
        # Isolation Forest configuration
        # Contamination is set low because training data is assumed mostly normal
        model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
        model.fit(X)
        self.models[username] = model
        return model

    def get_user_model(self, username):
        if username in self.models:
            return self.models[username]
        return self.train_user_model(username)

    def evaluate_activity(self, username, activity):
        """
        Evaluate user activity and return a risk score (0-100) and explanation reasons.
        activity: dict containing login_hour, location, device, failed_logins, commands_count, files_accessed
        """
        model = self.get_user_model(username)
        logs = logs_col.find({"username": username})
        
        # Calculate historical stats for explanation
        hist_hours = [log.get("login_hour", 9) for log in logs]
        hist_locations = [log.get("location", "") for log in logs]
        hist_devices = [log.get("device", "") for log in logs]
        hist_commands = [log.get("commands_count", 0) for log in logs]
        hist_files = [log.get("files_accessed", 0) for log in logs]
        
        current_hour = int(activity.get("login_hour", 9))
        current_loc = activity.get("location", "Coimbatore")
        current_dev = activity.get("device", "Workstation-Admin-01")
        current_failed = int(activity.get("failed_logins", 0))
        current_commands = int(activity.get("commands_count", 0))
        current_files = int(activity.get("files_accessed", 0))

        # Check anomalies manually to build the explanation list
        reasons = []
        
        # 1. Unusual login hour (e.g. outside 7am - 8pm or different from hist mean by 4+ hours)
        is_unusual_hour = False
        if len(hist_hours) > 0:
            hist_mean_hour = np.mean(hist_hours)
            if abs(current_hour - hist_mean_hour) > 4 and (current_hour < 6 or current_hour > 22):
                is_unusual_hour = True
                reasons.append(f"Unusual login hour ({current_hour}:00)")
        
        # 2. Location anomaly
        if len(hist_locations) > 0 and current_loc not in hist_locations:
            reasons.append(f"Unusual login location: {current_loc} (Expected: {', '.join(set(hist_locations))})")
        
        # 3. Device anomaly
        if len(hist_devices) > 0 and current_dev not in hist_devices:
            reasons.append(f"New device detected: {current_dev}")
        
        # 4. Failed login attempts
        if current_failed >= 3:
            reasons.append(f"{current_failed} failed login attempts detected")
        
        # 5. Excessive commands
        if len(hist_commands) > 0 and current_commands > np.max(hist_commands) * 1.5:
            reasons.append(f"High command volume: {current_commands} executed (Historical max: {np.max(hist_commands)})")
            
        # 6. Large files download
        if len(hist_files) > 0 and current_files > np.max(hist_files) * 2.0:
            reasons.append(f"Large data access/download: {current_files} files (Historical max: {np.max(hist_files)})")

        # Fallback if no model is trained
        if model is None:
            # Rule-based fallback score calculation
            score = 15
            if current_loc != "Coimbatore" and current_loc != "Chennai" and current_loc != "Bangalore":
                score += 30
            if current_failed > 0:
                score += current_failed * 10
            if current_files > 100:
                score += 40
            score = min(score, 100)
            return score, reasons

        # Evaluate using Isolation Forest
        X_test = np.array([[
            current_hour,
            map_location(current_loc),
            map_device(current_dev),
            current_failed,
            current_commands,
            current_files
        ]])
        
        # decision_function returns float in [-0.5, 0.5] approx.
        # lower values are more anomalous
        decision_val = model.decision_function(X_test)[0]
        
        # Map decision value to risk score (0 to 100)
        # Isolation Forest boundary is at 0.0 (positive: inlier/normal, negative: outlier/anomaly)
        if decision_val >= 0.0:
            # Inlier (Normal behavior) -> Map to Safe range (5% - 25%)
            risk_score = int(max(5, 25 - (decision_val * 100)))
        else:
            # Outlier (Anomalous behavior) -> Map to Warning/Critical range (45% - 95%)
            risk_score = int(45 + min(50, abs(decision_val) * 200))
            
        # Guarantee minimum risk score if reasons are triggered
        if current_failed >= 5 or current_files > 1000:
            risk_score = max(risk_score, 90)
        elif len(reasons) >= 2:
            risk_score = max(risk_score, 45)
            
        # Cap risk score
        risk_score = min(max(risk_score, 5), 100)
        
        return risk_score, reasons

# Instantiate global detector
detector = AnomalyDetector()
