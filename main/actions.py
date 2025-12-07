import json
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class Actions:
    def __init__(self):
        self.config = self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """Load action configuration from JSON file."""
        config_file = 'actions_config.json'
        
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _create_default_config(self, config_file):
        """Create default actions_config.json file."""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your-email@gmail.com",
                "sender_password": "your-app-password",
                "recipient_email": "admin@example.com"
            },
            "log_file": "system_alerts.log",
            "alert_history": "alert_history.json"
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"Created default config file: {config_file}")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.config.get('log_file', 'system_alerts.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def execute(self, alert):
        """
        Execute appropriate actions based on alert severity or name.
        
        Args:
            alert: Dictionary containing alert information
                   {name, severity, current_value}
        """
        severity = alert.get("severity", "info")
        name = alert.get("name", "Unknown Alert")
        
        # Match based on severity
        if severity == "critical":
            self._handle_critical(alert)
        elif severity == "warning":
            self._handle_warning(alert)
        elif severity == "info":
            self._handle_info(alert)
        
        # Match based on specific alert names
        if "CPU" in name:
            self._handle_cpu_alert(alert)
        elif "Memory" in name or "RAM" in name:
            self._handle_memory_alert(alert)
        elif "Disk" in name:
            self._handle_disk_alert(alert)
    
    def _handle_critical(self, alert):
        """Handle critical severity alerts."""
        print(f"🚨 CRITICAL ALERT: {alert['name']}")
        print(f"   Current Value: {alert['current_value']}")
        
        # Log to file
        logging.critical(f"{alert['name']} - Value: {alert['current_value']}")
        
        # Send email notification
        self._send_email(alert)
        
        # Save to alert history
        self._save_to_history(alert)
        
        # Play system beep or notification sound
        self._system_notification(alert)
    
    def _handle_warning(self, alert):
        """Handle warning severity alerts."""
        print(f"⚠️  WARNING: {alert['name']}")
        print(f"   Current Value: {alert['current_value']}")
        
        # Log to file
        logging.warning(f"{alert['name']} - Value: {alert['current_value']}")
        
        # Save to alert history
        self._save_to_history(alert)
    
    def _handle_info(self, alert):
        """Handle info severity alerts."""
        print(f"ℹ️  INFO: {alert['name']}")
        print(f"   Current Value: {alert['current_value']}")
        
        # Log to file
        logging.info(f"{alert['name']} - Value: {alert['current_value']}")
    
    def _handle_cpu_alert(self, alert):
        """Specific actions for CPU-related alerts."""
        print(f"   → CPU-specific action: Checking top processes...")
        # Could integrate with SysStat to get top CPU processes
        # Could attempt to kill or throttle high-CPU processes
    
    def _handle_memory_alert(self, alert):
        """Specific actions for memory-related alerts."""
        print(f"   → Memory-specific action: Clearing cache recommended...")
        # Could trigger cache clearing
        # Could restart memory-intensive services
    
    def _handle_disk_alert(self, alert):
        """Specific actions for disk-related alerts."""
        print(f"   → Disk-specific action: Check for large files...")
        # Could trigger cleanup scripts
        # Could archive old logs
    
    def _send_email(self, alert):
        """Send email notification for critical alerts."""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = f"🚨 System Alert: {alert['name']}"
            
            body = f"""
System Alert Triggered
======================

Alert: {alert['name']}
Severity: {alert['severity']}
Current Value: {alert['current_value']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the system immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print("   ✓ Email notification sent")
        except Exception as e:
            print(f"   ✗ Failed to send email: {e}")
    
    def _save_to_history(self, alert):
        """Save alert to history file for tracking."""
        history_file = self.config.get('alert_history', 'alert_history.json')
        
        # Load existing history
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                history = []
        
        # Add new alert with timestamp
        alert_record = {
            "timestamp": datetime.now().isoformat(),
            "name": alert['name'],
            "severity": alert['severity'],
            "current_value": alert['current_value']
        }
        
        history.append(alert_record)
        
        # Keep only last 1000 alerts
        if len(history) > 1000:
            history = history[-1000:]
        
        # Save updated history
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"   ✗ Failed to save alert history: {e}")
    
    def _system_notification(self, alert):
        """Send system notification (platform-dependent)."""
        try:
            # For Linux
            if os.name == 'posix':
                os.system(f'notify-send "System Alert" "{alert["name"]}: {alert["current_value"]}"')
            # For Windows
            elif os.name == 'nt':
                # Could use win10toast or plyer for notifications
                print("   → System notification (Windows implementation needed)")
            # For macOS
            elif os.uname().sysname == 'Darwin':
                os.system(f'osascript -e \'display notification "{alert["name"]}: {alert["current_value"]}" with title "System Alert"\'')
        except Exception as e:
            print(f"   ✗ System notification failed: {e}")
    
    def get_alert_history(self, limit=10):
        """Retrieve recent alert history."""
        history_file = self.config.get('alert_history', 'alert_history.json')
        
        if not os.path.exists(history_file):
            return []
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
                return history[-limit:] if limit else history
        except Exception as e:
            print(f"Error reading history: {e}")
            return []


# Example usage
if __name__ == "__main__":
    actions = Actions()
    
    # Test with different alert types
    test_alerts = [
        {
            "name": "Critical CPU Usage",
            "severity": "critical",
            "current_value": 97.5
        },
        {
            "name": "High Memory Usage",
            "severity": "warning",
            "current_value": 87.3
        },
        {
            "name": "Low CPU Frequency",
            "severity": "info",
            "current_value": 800.0
        }
    ]
    
    print("=== Testing Actions ===\n")
    for alert in test_alerts:
        actions.execute(alert)
        print()
    
    # Show recent history
    print("\n=== Recent Alert History ===")
    history = actions.get_alert_history(limit=5)
    for record in history:
        print(f"{record['timestamp']} - [{record['severity']}] {record['name']}: {record['current_value']}")