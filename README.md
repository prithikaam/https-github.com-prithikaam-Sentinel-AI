# SentinelAI – AI-Powered Privileged Access & Insider Threat Detection

SentinelAI is an advanced, real-time security intelligence platform designed for banking operations to monitor administrative sessions, detect privileged credential compromises, enforce risk-based step-up authentication, and encapsulate sessions using post-quantum secure algorithms.

---

## 🚀 Key Features

1. **🧠 Personalized AI Behavioral Profiles**
   - Learns the unique routine of each administrator (hour of access, city location, terminal device type, command volumes, and file downloads).
   - Trains personalized **Isolation Forest** classifiers using `scikit-learn` to establish clean behavioral baselines and flag outliers.

2. **🎯 Real-Time Risk Scoring**
   - Translates raw outlier distances from the Isolation Forest model into a live risk index:
     - `🟢 Safe (5% - 25%)` → Allow standard access.
     - `🟡 Medium Risk (30% - 65%)` → Require step-up Multi-Factor Authentication (OTP).
     - `🔴 High Risk (70% - 100%)` → Block session and trigger critical console alarms.

3. **📊 Explainable AI (XAI) Diagnostics**
   - Breaks down exactly which criteria caused a session score to rise (e.g. *Delhi login at 2:00 AM on Delhi-VM-01, executing 95 database queries and exfiltrating 5200 payroll records*).

4. **🔐 CRYSTALS-Kyber Post-Quantum Tunneling**
   - Implements a simulated CRYSTALS-Kyber-512 KEM (Key Encapsulation Mechanism) over modular polynomial rings $\mathbb{Z}_{3329}[X]/(X^{256} + 1)$ to shield administrative credentials and secrets against Shor's-algorithm attacks.

5. **🤖 Natural Language Security Assistant**
   - An NLP-driven security chatbot where analysts can query threat stats, ask for user summaries, or request mitigation steps in plain English.

6. **🎛️ Administrator Threat Simulator**
   - A sandbox interface enabling security engineers to inject custom audit logs and test the response of the Isolation Forest classifier on-the-fly.

---

## 🛠️ Technology Stack

- **Frontend**: React.js, Vite, Vanilla CSS, Lucide Icons, Chart.js
- **Backend**: Flask (Python), PyJWT, bcrypt, Scikit-Learn (Isolation Forest), Numpy
- **Database**: SQLite document collection model (zero-setup MongoDB interface)
- **Quantum KEM**: CRYSTALS-Kyber (simulated ring polynomial arithmetic)

---

## 📁 Repository Layout

```
sentinel_ai/
├── backend/
│   ├── app.py                   # Main Flask API and endpoints
│   ├── db.py                    # SQLite collection store (Seeds John, Alice, David, Sam)
│   ├── anomaly_detector.py      # Personalized Isolation Forest models
│   ├── kyber_crypto.py          # CRYSTALS-Kyber KEM mathematics
│   ├── assistant.py             # Chatbot NLP query processor
│   ├── test_crypto.py           # Cryptographic unit test
│   ├── test_anomaly.py          # Isolation Forest unit test
│   └── requirements.txt         # Backend Python requirements
├── frontend/
│   ├── index.html               # Frontend HTML Entry
│   ├── package.json             # NPM package scripts and configurations
│   ├── src/
│   │   ├── App.jsx              # Main React routing container
│   │   ├── main.jsx             # React entry point
│   │   ├── components/          # Reusable dashboard panel sheets
│   │   │   ├── Login.jsx        # Login gateway with Kyber handshakes
│   │   │   ├── Dashboard.jsx    # Real-time statistics and user tables
│   │   │   ├── KyberVisualizer.jsx # Interactive matrix register traces
│   │   │   ├── Assistant.jsx    # Security operations chatbot interface
│   │   │   ├── Simulator.jsx    # Audit log injection control board
│   │   │   └── AlertDetails.jsx # Anomaly details overlay sheet
│   │   └── styles/
│   │       └── index.css        # Obsidian dark theme and glassmorphic stylesheet
│   └── vite.config.js           # Vite compiler configurations
└── .gitignore                   # Excludes caches, packages, and database logs
```

---

## ⚡ Installation & Local Startup

### Prerequisites
Make sure you have **Python 3.10+** and **Node.js 18+** installed on your system.

### 1. Configure the Python Backend
Navigate to the root directory and install dependencies:
```bash
pip install -r backend/requirements.txt
```
Start the Flask server:
```bash
python backend/app.py
```
> The API server boots on **http://127.0.0.1:5000** and seeds the SQLite collections database.

### 2. Configure the React Frontend
Open a separate terminal window and navigate to the frontend directory:
```bash
cd frontend
npm install
```
Start the development server:
```bash
npm run dev
```
> Open **http://localhost:5173** in your web browser to view the console.

---

## 🔬 Automated Testing

Audit KEM parameters and classifier thresholds using the unit test suite:

- Run KEM key agreement consistency checks:
  ```bash
  python backend/test_crypto.py
  ```
- Run behavioral anomaly classifiers:
  ```bash
  python backend/test_anomaly.py
  ```
