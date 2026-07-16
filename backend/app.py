from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

from db import users_col, logs_col, alerts_col, seed_database
import kyber_crypto
from anomaly_detector import detector
from assistant import assistant

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for React frontend

JWT_SECRET = "SENTINEL_AI_SUPER_SECRET_JWT_KEY"

# In-memory store for active cryptographic handshakes during login
# Structure: { username: { "sk": sk, "pk": pk, "timestamp": datetime } }
handshake_store = {}

# In-memory store for generated OTPs for verification
# Structure: { username: { "otp": "123456", "expires": datetime } }
otp_store = {}

@app.route('/')
def index():
    return jsonify({
        "status": "ONLINE",
        "message": "SentinelAI Security API Endpoint is operational.",
        "version": "1.0.0"
    })

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested API endpoint does not exist."
    }), 404

@app.route('/api/auth/login-init', methods=['POST'])
def login_init():
    """
    Step 1 of Authentication:
    Initiate CRYSTALS-Kyber KEM handshake. Generate a public/secret keypair.
    """
    data = request.get_json() or {}
    username = data.get("username", "").lower().strip()
    
    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "Administrative account not found"}), 404
        
    if user.get("status") == "BLOCKED":
        return jsonify({
            "status": "BLOCKED",
            "error": "Account blocked due to security restrictions. Contact security operations."
        }), 403

    # Generate Kyber key pair
    pk, sk, trace = kyber_crypto.generate_keypair()
    
    # Store secret key for decapsulation step
    handshake_store[username] = {
        "sk": sk,
        "pk": pk,
        "timestamp": datetime.utcnow()
    }
    
    # Return public key and key generation trace details for UI visualization
    return jsonify({
        "publicKey": pk,
        "trace": trace
    })

@app.route('/api/auth/login-complete', methods=['POST'])
def login_complete():
    """
    Step 2 of Authentication:
    Verify password, decapsulate secret key, run anomaly detection, and apply policy.
    """
    data = request.get_json() or {}
    username = data.get("username", "").lower().strip()
    password = data.get("password", "")
    ciphertext = data.get("ciphertext")  # Dict containing 'u' and 'v'
    
    # Optional parameters to simulate anomalies
    login_hour = data.get("login_hour")
    location = data.get("location", "Coimbatore")
    device = data.get("device", "Workstation-Admin-01")
    failed_logins = int(data.get("failed_logins", 0))
    commands_count = int(data.get("commands_count", 10))
    files_accessed = int(data.get("files_accessed", 5))

    # Fallback to current local hour if not specified
    if login_hour is None:
        login_hour = datetime.now().hour
    else:
        login_hour = int(login_hour)

    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "Account not found"}), 404

    # 1. Verify Kyber Handshake State
    handshake = handshake_store.get(username)
    if not handshake or not ciphertext:
        return jsonify({"error": "Cryptographic handshake session expired or missing"}), 400
        
    # Decapsulate Kyber shared secret
    try:
        shared_secret, decaps_trace = kyber_crypto.decapsulate(ciphertext, handshake["sk"], handshake["pk"])
    except Exception as e:
        return jsonify({"error": f"Quantum key decapsulation failed: {str(e)}"}), 400
        
    # 2. Check Password
    if not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        # Log failed login attempt
        current_failed = user.get("failed_logins_count", 0) + 1
        users_col.update_one({"username": username}, {"$set": {"failed_logins_count": current_failed}})
        
        # Insert log of failed attempt
        logs_col.insert_one({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "login_hour": login_hour,
            "location": location,
            "device": device,
            "commands_count": 0,
            "files_accessed": 0,
            "failed_logins": current_failed
        })
        
        return jsonify({"error": "Invalid password credentials"}), 401

    # Reset failed login count on password success (the model will evaluate the attempts parameter)
    users_col.update_one({"username": username}, {"$set": {"failed_logins_count": 0}})

    # 3. Collect and Analyze Activity Logs using Isolation Forest
    activity = {
        "login_hour": login_hour,
        "location": location,
        "device": device,
        "failed_logins": failed_logins,
        "commands_count": commands_count,
        "files_accessed": files_accessed
    }
    
    risk_score, reasons = detector.evaluate_activity(username, activity)
    
    # Save the login activity to logs
    logs_col.insert_one({
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "login_hour": login_hour,
        "location": location,
        "device": device,
        "commands_count": commands_count,
        "files_accessed": files_accessed,
        "failed_logins": failed_logins
    })
    
    # Update risk score in DB
    users_col.update_one({"username": username}, {
        "$set": {
            "risk_score": risk_score,
            "last_login": datetime.now().isoformat()
        }
    })

    # Clear handshake session
    del handshake_store[username]

    # 4. Enforce Access Policy based on Risk Score
    if risk_score >= 70:
        # High Risk -> BLOCK Account & Trigger Alert
        users_col.update_one({"username": username}, {"$set": {"status": "BLOCKED"}})
        
        alerts_col.insert_one({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "severity": "CRITICAL",
            "description": f"Administrative access blocked: High risk threshold breached ({risk_score}%)",
            "reasons": reasons,
            "resolved": False
        })
        
        return jsonify({
            "status": "BLOCKED",
            "risk_score": risk_score,
            "reasons": reasons,
            "decaps_trace": decaps_trace,
            "shared_secret": shared_secret
        }), 403
        
    elif risk_score >= 30:
        # Medium Risk -> Require MFA (OTP)
        users_col.update_one({"username": username}, {"$set": {"status": "OTP_CHALLENGE"}})
        
        # Generate 6-digit OTP
        otp_code = "123456"  # Static for prototype ease-of-use
        otp_store[username] = {
            "otp": otp_code,
            "expires": datetime.utcnow() + timedelta(minutes=5)
        }
        
        # Log Warning Alert
        alerts_col.insert_one({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "severity": "WARNING",
            "description": f"Step-up MFA enforced: Anomalous administrative login ({risk_score}%)",
            "reasons": reasons,
            "resolved": False
        })
        
        return jsonify({
            "status": "OTP_CHALLENGE",
            "risk_score": risk_score,
            "reasons": reasons,
            "decaps_trace": decaps_trace,
            "shared_secret": shared_secret
        })
        
    else:
        # Low Risk -> Grant Access
        token_payload = {
            'username': username,
            'role': user.get("role"),
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        
        users_col.update_one({"username": username}, {"$set": {"status": "ACTIVE"}})
        
        return jsonify({
            "status": "ACTIVE",
            "token": token,
            "risk_score": risk_score,
            "decaps_trace": decaps_trace,
            "shared_secret": shared_secret
        })

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Step 3 of Authentication (Medium Risk only):
    Verify standard OTP code.
    """
    data = request.get_json() or {}
    username = data.get("username", "").lower().strip()
    otp = data.get("otp", "").strip()
    
    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    otp_record = otp_store.get(username)
    if not otp_record or datetime.utcnow() > otp_record["expires"]:
        return jsonify({"error": "OTP has expired or does not exist"}), 400
        
    if otp_record["otp"] != otp:
        return jsonify({"error": "Incorrect OTP code. Try again."}), 400
        
    # Success -> Clear OTP and activate user
    del otp_store[username]
    users_col.update_one({"username": username}, {"$set": {"status": "ACTIVE"}})
    
    # Generate Token
    token_payload = {
        'username': username,
        'role': user.get("role"),
        'exp': datetime.utcnow() + timedelta(hours=8)
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
    
    return jsonify({
        "status": "ACTIVE",
        "token": token
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Retrieve aggregated dashboard statistics.
    """
    users = users_col.find()
    active_admins = len(users)
    high_risk_users = sum(1 for u in users if u.get("risk_score", 0) >= 70 or u.get("status") == "BLOCKED")
    today_alerts = alerts_col.count_documents({"resolved": False})
    
    # Compile chart graph of current risks
    risk_graph = []
    for u in users:
        risk_graph.append({
            "username": u["username"].capitalize(),
            "role": u.get("role", "Admin"),
            "risk_score": u.get("risk_score", 15),
            "status": u.get("status", "ACTIVE")
        })
        
    return jsonify({
        "activeAdmins": active_admins,
        "highRiskUsers": high_risk_users,
        "todayAlerts": today_alerts,
        "riskGraph": risk_graph
    })

@app.route('/api/dashboard/alerts', methods=['GET'])
def get_dashboard_alerts():
    """
    Fetch all recent threat alerts.
    """
    alerts = alerts_col.find()
    # Sort alerts by timestamp descending
    alerts = sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify(alerts)

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Fetch list of administrative users.
    """
    users = users_col.find()
    # Remove sensitive fields
    for u in users:
        u.pop("password_hash", None)
        u.pop("mfa_secret", None)
    return jsonify(users)

@app.route('/api/users/override', methods=['POST'])
def security_override():
    """
    Action by Security Analyst to manually unblock an account or reset user risk score.
    """
    data = request.get_json() or {}
    username = data.get("username", "").lower().strip()
    
    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Reset user state
    users_col.update_one({"username": username}, {
        "$set": {
            "status": "ACTIVE",
            "risk_score": 12,  # Baseline safe score
        }
    })
    
    # Mark user's alerts as resolved
    alerts_col.update_one({"username": username}, {
        "$set": {
            "resolved": True
        }
    })
    
    # Log the analyst override event
    logs_col.insert_one({
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "login_hour": datetime.now().hour,
        "location": "SEC-OPS-Coimbatore",
        "device": "Analyst-Workstation",
        "commands_count": 1,
        "files_accessed": 0,
        "failed_logins": 0,
        "notes": "Analyst manual risk reset and unblock override"
    })
    
    return jsonify({
        "message": f"Successfully overridden account block. {username.capitalize()} is now ACTIVE."
    })

@app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    """
    AI Security Assistant Query Endpoint.
    """
    data = request.get_json() or {}
    message = data.get("message", "")
    response_text = assistant.process_query(message)
    return jsonify({
        "reply": response_text
    })

@app.route('/api/logs/simulate', methods=['POST'])
def simulate_activity():
    """
    Simulate a custom runtime activity event post-login to dynamically adjust risk scores and trigger alerts.
    """
    data = request.get_json() or {}
    username = data.get("username", "").lower().strip()
    location = data.get("location", "Coimbatore")
    device = data.get("device", "Workstation-Admin-01")
    login_hour = int(data.get("login_hour", 12))
    failed_logins = int(data.get("failed_logins", 0))
    commands_count = int(data.get("commands_count", 15))
    files_accessed = int(data.get("files_accessed", 5))

    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    activity = {
        "login_hour": login_hour,
        "location": location,
        "device": device,
        "failed_logins": failed_logins,
        "commands_count": commands_count,
        "files_accessed": files_accessed
    }

    risk_score, reasons = detector.evaluate_activity(username, activity)

    # Insert into log history
    logs_col.insert_one({
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "login_hour": login_hour,
        "location": location,
        "device": device,
        "commands_count": commands_count,
        "files_accessed": files_accessed,
        "failed_logins": failed_logins,
        "is_simulated": True
    })

    # Update risk score
    users_col.update_one({"username": username}, {
        "$set": {
            "risk_score": risk_score
        }
    })

    # Enforce policies
    severity = "INFO"
    status_update = "ACTIVE"
    if risk_score >= 70:
        severity = "CRITICAL"
        status_update = "BLOCKED"
        users_col.update_one({"username": username}, {"$set": {"status": "BLOCKED"}})
        alerts_col.insert_one({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "severity": "CRITICAL",
            "description": f"Simulated high risk activity threshold breach ({risk_score}%)",
            "reasons": reasons,
            "resolved": False
        })
    elif risk_score >= 30:
        severity = "WARNING"
        status_update = "OTP_CHALLENGE"
        users_col.update_one({"username": username}, {"$set": {"status": "OTP_CHALLENGE"}})
        alerts_col.insert_one({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "severity": "WARNING",
            "description": f"Simulated medium risk activity trigger ({risk_score}%)",
            "reasons": reasons,
            "resolved": False
        })
    else:
        users_col.update_one({"username": username}, {"$set": {"status": "ACTIVE"}})

    return jsonify({
        "username": username,
        "risk_score": risk_score,
        "status": status_update,
        "reasons": reasons
    })

if __name__ == '__main__':
    # Initialize DB seeding
    seed_database()
    
    # Run the server on port 5000, disabling the auto-reloader to prevent restarts on SQLite database writes
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
