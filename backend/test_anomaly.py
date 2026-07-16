import db
from anomaly_detector import detector

def test_anomaly_classification():
    print("==================================================")
    print("Testing Isolation Forest Anomaly Detection")
    print("==================================================")
    
    # Ensure database is seeded
    print("[1] Initializing and seeding Database...")
    db.seed_database()
    
    # 1. Test Normal behavior for David
    # David's normal time is ~14:00 (2 PM), location Bangalore, device IT-Support-Host, low files, low failed attempts
    normal_activity = {
        "login_hour": 14,
        "location": "Bangalore",
        "device": "IT-Support-Host",
        "failed_logins": 0,
        "commands_count": 15,
        "files_accessed": 5
    }
    
    print("\n[2] Evaluating Normal Scenario for David...")
    risk_score_norm, reasons_norm = detector.evaluate_activity("david", normal_activity)
    print("Risk Score:", risk_score_norm)
    print("Reasons Flagged:", reasons_norm)
    
    # Assert normal risk is low
    assert risk_score_norm < 30, f"Error: Normal activity has high risk score {risk_score_norm}"
    print("[SUCCESS] Normal behavior classified as Safe.")

    # 2. Test Critical Anomaly (Delhi login at 2 AM, downloads 5000 files)
    anomalous_activity = {
        "login_hour": 2,
        "location": "Delhi",
        "device": "Delhi-VM-01",
        "failed_logins": 8,
        "commands_count": 95,
        "files_accessed": 5200
    }
    
    print("\n[3] Evaluating Anomalous Scenario for David...")
    risk_score_anom, reasons_anom = detector.evaluate_activity("david", anomalous_activity)
    print("Risk Score:", risk_score_anom)
    print("Reasons Flagged:", reasons_anom)
    
    # Assert anomaly risk is high
    assert risk_score_anom >= 70, f"Error: Anomalous activity has low risk score {risk_score_anom}"
    assert len(reasons_anom) > 0, "Error: No explainable reasons generated for anomaly"
    print("[SUCCESS] Anomalous behavior classified as High Risk with explanation.")
    print("==================================================")

if __name__ == "__main__":
    test_anomaly_classification()
