import sqlite3
import json
import os
import uuid
from datetime import datetime, timedelta
import bcrypt

class Collection:
    def __init__(self, db_path, name):
        self.db_path = db_path
        self.name = name

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def insert_one(self, document):
        doc = dict(document)
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO collections (collection_name, doc_id, data) VALUES (?, ?, ?)",
            (self.name, doc['_id'], json.dumps(doc))
        )
        conn.commit()
        conn.close()
        return doc

    def find(self, filter_dict=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM collections WHERE collection_name = ?", (self.name,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            doc = json.loads(row[0])
            match = True
            if filter_dict:
                for k, v in filter_dict.items():
                    if k not in doc or doc[k] != v:
                        match = False
                        break
            if match:
                results.append(doc)
        return results

    def find_one(self, filter_dict):
        docs = self.find(filter_dict)
        return docs[0] if docs else None

    def update_one(self, filter_dict, update_dict):
        doc = self.find_one(filter_dict)
        if not doc:
            return None
        
        # Support both standard dict updates and MongoDB $set operators
        if '$set' in update_dict:
            doc.update(update_dict['$set'])
        else:
            doc.update(update_dict)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE collections SET data = ? WHERE collection_name = ? AND doc_id = ?",
            (json.dumps(doc), self.name, doc['_id'])
        )
        conn.commit()
        conn.close()
        return doc

    def delete_many(self, filter_dict=None):
        docs = self.find(filter_dict)
        conn = self._connect()
        cursor = conn.cursor()
        for doc in docs:
            cursor.execute(
                "DELETE FROM collections WHERE collection_name = ? AND doc_id = ?",
                (self.name, doc['_id'])
            )
        conn.commit()
        conn.close()
        return len(docs)

    def count_documents(self, filter_dict=None):
        return len(self.find(filter_dict))


class Database:
    def __init__(self, db_path='sentinel.db'):
        # Keep path relative to backend folder or absolute path
        # Let's ensure it's created relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                collection_name TEXT,
                doc_id TEXT,
                data TEXT,
                PRIMARY KEY (collection_name, doc_id)
            )
        ''')
        conn.commit()
        conn.close()

    def get_collection(self, name):
        return Collection(self.db_path, name)


# Initialize DB Instance
db = Database()
users_col = db.get_collection('users')
logs_col = db.get_collection('activity_logs')
alerts_col = db.get_collection('alerts')

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    # Only seed if database users are empty
    if users_col.count_documents() > 0:
        return

    print("Seeding SQLite simulated MongoDB...")

    # Create Users
    admins = [
        {"username": "john", "password": "password123", "role": "Administrator", "status": "ACTIVE", "risk_score": 12},
        {"username": "alice", "password": "password123", "role": "Database Administrator", "status": "ACTIVE", "risk_score": 15},
        {"username": "david", "password": "password123", "role": "IT Support Specialist", "status": "ACTIVE", "risk_score": 18},
        {"username": "sam", "password": "password123", "role": "Security Auditor", "status": "ACTIVE", "risk_score": 8}
    ]

    for a in admins:
        users_col.insert_one({
            "username": a["username"],
            "password_hash": hash_password(a["password"]),
            "role": a["role"],
            "status": a["status"],
            "risk_score": a["risk_score"],
            "mfa_secret": "SENTINELOTPSECRET",
            "last_login": datetime.now().isoformat()
        })

    # Seed historical logs to build a profile for each admin
    # Isolation Forest needs some normal data points.
    # Locations: Coimbatore (0), Chennai (1), Bangalore (2), Delhi (3)
    # Devices: Workstation-Admin-01 (0), DBA-Terminal-A (1), IT-Support-Host (2), Audit-Sec-01 (3)
    
    # John's normal profile: Coimbatore (0), Workstation-Admin-01 (0), login between 8 AM and 10 AM, low commands, low files
    # Alice's normal profile: Chennai (1), DBA-Terminal-A (1), login between 9 AM and 11 AM, moderate commands
    # David's normal profile: Bangalore (2), IT-Support-Host (2), login between 13:00 and 16:00
    # Sam's normal profile: Coimbatore (0), Audit-Sec-01 (3), login between 10 AM and 12 PM

    # Generate 50 normal logs for each user
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(50):
        # John
        logs_col.insert_one({
            "username": "john",
            "timestamp": (base_time + timedelta(days=i/2, hours=9)).isoformat(),
            "login_hour": 9,
            "location": "Coimbatore",
            "device": "Workstation-Admin-01",
            "commands_count": 8 + (i % 5),
            "files_accessed": 3 + (i % 3),
            "failed_logins": 0
        })

        # Alice
        logs_col.insert_one({
            "username": "alice",
            "timestamp": (base_time + timedelta(days=i/2, hours=10)).isoformat(),
            "login_hour": 10,
            "location": "Chennai",
            "device": "DBA-Terminal-A",
            "commands_count": 15 + (i % 8),
            "files_accessed": 10 + (i % 5),
            "failed_logins": 0
        })

        # David
        logs_col.insert_one({
            "username": "david",
            "timestamp": (base_time + timedelta(days=i/2, hours=14)).isoformat(),
            "login_hour": 14,
            "location": "Bangalore",
            "device": "IT-Support-Host",
            "commands_count": 12 + (i % 6),
            "files_accessed": 5 + (i % 4),
            "failed_logins": 0
        })

        # Sam
        logs_col.insert_one({
            "username": "sam",
            "timestamp": (base_time + timedelta(days=i/2, hours=11)).isoformat(),
            "login_hour": 11,
            "location": "Coimbatore",
            "device": "Audit-Sec-01",
            "commands_count": 5 + (i % 3),
            "files_accessed": 2 + (i % 2),
            "failed_logins": 0
        })

    # Seed some recent alerts
    alerts_col.insert_one({
        "username": "david",
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "severity": "CRITICAL",
        "description": "David initiated massive data download (5000 files) from IT Support Host",
        "reasons": ["Large data download detected", "Access to payroll system database"],
        "resolved": False
    })

    alerts_col.insert_one({
        "username": "alice",
        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
        "severity": "WARNING",
        "description": "Alice logged in from an unknown device in Delhi",
        "reasons": ["New device: Delhi-VM-01", "Unusual login location: Delhi (Chennai expected)"],
        "resolved": False
    })

    alerts_col.insert_one({
        "username": "david",
        "timestamp": (datetime.now() - timedelta(hours=8)).isoformat(),
        "severity": "CRITICAL",
        "description": "David logged in at 2:43 AM from unknown location",
        "reasons": ["Unusual login hour (2:43 AM)", "Unknown location: Delhi (Bangalore expected)"],
        "resolved": False
    })

    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
