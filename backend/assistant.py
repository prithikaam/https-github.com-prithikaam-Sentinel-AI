import re
from datetime import datetime
from db import users_col, logs_col, alerts_col

class SecurityAssistant:
    def process_query(self, query):
        query = query.lower().strip()
        
        # 1. Show high-risk users
        if any(keyword in query for keyword in ["high risk", "risky", "suspicious", "threats", "alerts"]):
            return self._get_high_risk_users()
            
        # 2. Match specific username in query
        users = ["john", "alice", "david", "sam"]
        target_user = None
        for u in users:
            if u in query:
                target_user = u
                break
                
        if target_user:
            if any(keyword in query for keyword in ["mitigat", "remedi", "fix", "solve", "handle", "steps"]):
                return self._get_mitigation_steps(target_user)
            elif any(keyword in query for keyword in ["why", "reason", "explain", "block", "cause"]):
                return self._explain_user_risk(target_user)
            elif any(keyword in query for keyword in ["activity", "recent", "log", "history", "do"]):
                return self._get_user_recent_activity(target_user)
            else:
                # Default info on target user
                return self._get_user_summary(target_user)
                
        # 3. Help or general queries
        if "help" in query or "command" in query or "what can you do" in query:
            return self._get_help_menu()
            
        # Default response
        return (
            "I'm the **SentinelAI Security Assistant**. I can help you investigate privileged user behaviors. Try asking me:\n\n"
            "* *\"Why was David blocked?\"*\n"
            "* *\"Show high-risk users today\"*\n"
            "* *\"Suggest mitigation steps for Alice\"*\n"
            "* *\"What was John's recent activity?\"*"
        )

    def _get_high_risk_users(self):
        users = users_col.find()
        # Sort users by risk score descending
        users = sorted(users, key=lambda x: x.get("risk_score", 0), reverse=True)
        
        response = "### 🚨 Current Risk Scores for Privileged Users\n\n"
        response += "| User | Role | Risk Score | Status |\n"
        response += "| :--- | :--- | :--- | :--- |\n"
        
        for u in users:
            score = u.get("risk_score", 0)
            status = u.get("status", "ACTIVE")
            
            # Risk color indicators
            if score >= 70:
                color = "🔴 High Risk"
            elif score >= 30:
                color = "🟡 Medium Risk"
            else:
                color = "🟢 Low Risk"
                
            status_text = f"`{status}`"
            if status == "BLOCKED":
                status_text = "🚫 **BLOCKED**"
            elif status == "OTP_CHALLENGE":
                status_text = "🔑 **OTP PENDING**"
                
            response += f"| **{u['username'].capitalize()}** | {u.get('role')} | {color} ({score}) | {status_text} |\n"
            
        # Add quick mitigation note if David is high risk
        response += "\n> [!NOTE]\n> Analyst action needed: David is currently flagged as **Critical Threat**. You can type *\"mitigation steps for david\"* for mitigation options."
        return response

    def _explain_user_risk(self, username):
        user = users_col.find_one({"username": username})
        if not user:
            return f"User `{username}` not found in the administrative registry."
            
        score = user.get("risk_score", 0)
        status = user.get("status", "ACTIVE")
        
        # Get active alerts for user
        alerts = alerts_col.find({"username": username, "resolved": False})
        
        # Risk indicators
        if score >= 70:
            risk_desc = "🔴 **High Risk**"
        elif score >= 30:
            risk_desc = "🟡 **Medium Risk**"
        else:
            risk_desc = "🟢 **Safe / Low Risk**"

        response = f"## Risk Explanation for **{username.capitalize()}**\n\n"
        response += f"- **Current Risk Score:** {risk_desc} ({score}/100)\n"
        response += f"- **Account Status:** `{status}`\n\n"
        
        if status == "BLOCKED":
            response += "> [!CAUTION]\n> This account was automatically blocked due to critical risk score threshold breach (>= 70).\n\n"
            
        if alerts:
            response += "### 🔍 Anomaly Detection Reasons:\n"
            for alert in alerts:
                response += f"#### {alert['description']}\n"
                for reason in alert.get("reasons", []):
                    response += f"- {reason}\n"
                response += "\n"
        else:
            response += "No active alerts. The user's recent behaviors align with their historical profile.\n"
            
        return response

    def _get_mitigation_steps(self, username):
        user = users_col.find_one({"username": username})
        if not user:
            return f"User `{username}` not found."
            
        score = user.get("risk_score", 0)
        status = user.get("status", "ACTIVE")
        
        response = f"## 🛡 Recommended Mitigations: **{username.capitalize()}**\n\n"
        
        if score >= 70 or status == "BLOCKED":
            response += "### Critical Threat Protocol (Active)\n"
            response += "1. 🚫 **Confirm Blocked State**: The account is automatically set to `BLOCKED`. Keep it blocked during initial response.\n"
            response += "2. 🔑 **Revoke active JWT tokens**: Invalidate active sessions from API terminal.\n"
            response += "3. 🌐 **Network Isolation**: Block login attempts from Delhi location IPs.\n"
            response += "4. 🔐 **Quantum Key Revocation**: Rotate their CRYSTALS-Kyber key pair immediately to prevent decryption of administrative payloads.\n"
            response += "5. 📞 **Verify Identity**: Reach out to the user via verified phone/corporate channels to check for credential harvesting.\n"
            response += "\n*You can reset the user's block status from the Admin Table on the Dashboard.*"
        elif score >= 30 or status == "OTP_CHALLENGE":
            response += "### Medium Warning Protocol (Active)\n"
            response += "1. 📲 **Enforce Step-Up Authentication**: Enforce Multi-Factor OTP authentication.\n"
            response += "2. ⏱ **Session Rate Limit**: Limit administrative commands to 5 per minute.\n"
            response += "3. 📋 **Session Auditing**: Actively tail session logs for unauthorized database edits.\n"
        else:
            response += "### Low Risk Protocol\n"
            response += "1. 🟢 **Standard Access Granted**: Keep monitoring. No action needed."
            
        return response

    def _get_user_recent_activity(self, username):
        logs = logs_col.find({"username": username})
        if not logs:
            return f"No activity logs found for user `{username}`."
            
        # Sort logs by timestamp descending
        logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
        
        response = f"### 📋 Recent Administrative Activity: **{username.capitalize()}**\n\n"
        response += "| Timestamp | Hour | Location | Device | Commands | Files |\n"
        response += "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
        
        for log in logs:
            # Parse timestamp for clean display
            ts = log.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                clean_ts = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                clean_ts = ts
                
            response += f"| {clean_ts} | {log.get('login_hour')}:00 | {log.get('location')} | `{log.get('device')}` | {log.get('commands_count')} | {log.get('files_accessed')} |\n"
            
        return response

    def _get_user_summary(self, username):
        user = users_col.find_one({"username": username})
        if not user:
            return f"User `{username}` not found."
            
        return (
            f"### User Summary: **{username.capitalize()}**\n"
            f"- **Role:** {user.get('role')}\n"
            f"- **Risk Score:** {user.get('risk_score')}/100\n"
            f"- **Account Status:** `{user.get('status')}`\n"
            f"- **Last Login:** `{user.get('last_login')}`\n\n"
            f"Would you like me to *\"explain risk reasons for {username}\"* or *\"show mitigation steps for {username}\"*?"
        )

    def _get_help_menu(self):
        return (
            "### 🤖 SentinelAI Security Assistant Commands\n"
            "Ask me questions in plain English. Example queries:\n\n"
            "1. **Threat Status**:\n"
            "   - *\"Show high-risk users\"*\n"
            "   - *\"Who has alerts today?\"*\n\n"
            "2. **Specific User Investigation**:\n"
            "   - *\"Why is David's risk high?\"*\n"
            "   - *\"What was Alice's recent activity?\"*\n"
            "   - *\"Show summary for John\"*\n\n"
            "3. **Incident Mitigation**:\n"
            "   - *\"Suggest mitigation steps for David\"*\n"
            "   - *\"How do I remediate Alice?\"*"
        )

assistant = SecurityAssistant()
