import json
import os

class RulesEngine:
    def __init__(self):
        self.rules = self.load_rules()
    
    def load_rules(self):
        """Load rules from JSON file. Create default rules if file doesn't exist."""
        rules_file = 'rules.json'
        
        if not os.path.exists(rules_file):
            self._create_default_rules(rules_file)
        
        try:
            with open(rules_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading rules: {e}")
            return {}
    
    def _create_default_rules(self, rules_file):
        """Create default rules.json file."""
        default_rules = {
            "cpu_high": {
                "name": "High CPU Usage",
                "condition": "cpu.usage > 80",
                "severity": "warning"
            },
            "cpu_critical": {
                "name": "Critical CPU Usage",
                "condition": "cpu.usage > 95",
                "severity": "critical"
            },
            "ram_high": {
                "name": "High Memory Usage",
                "condition": "ram.percent > 85",
                "severity": "warning"
            },
            "ram_critical": {
                "name": "Critical Memory Usage",
                "condition": "ram.percent > 95",
                "severity": "critical"
            },
            "disk_high": {
                "name": "High Disk Usage",
                "condition": "disk.percent > 80",
                "severity": "warning"
            },
            "disk_critical": {
                "name": "Critical Disk Usage",
                "condition": "disk.percent > 90",
                "severity": "critical"
            },
            "disk_free_low": {
                "name": "Low Free Disk Space",
                "condition": "disk.free < 10",
                "severity": "warning"
            }
        }
        
        with open(rules_file, 'w') as f:
            json.dump(default_rules, f, indent=4)
        
        print(f"Created default rules file: {rules_file}")
    
    def check(self, stats):
        """Check stats against all rules and return triggered alerts."""
        triggered = []
        
        for rule_name, rule in self.rules.items():
            if self.evaluate(rule["condition"], stats):
                triggered.append({
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "current_value": self.extract_value(rule["condition"], stats)
                })
        
        return triggered
    
    def evaluate(self, condition, stats):
        """
        Evaluate a condition string against stats.
        
        Args:
            condition: String like "cpu.usage > 80" or "ram.percent > 85"
            stats: Dictionary containing system statistics
            
        Returns:
            Boolean indicating if condition is met
        """
        # Parse condition string
        parts = condition.split()
        if len(parts) != 3:
            return False
        
        metric_path, operator, threshold = parts
        threshold = float(threshold)
        
        # Get current value
        current_value = self._get_nested_value(stats, metric_path)
        
        if current_value is None:
            return False
        
        # Evaluate based on operator
        operators = {
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y
        }
        
        op_func = operators.get(operator)
        if op_func:
            return op_func(current_value, threshold)
        
        return False
    
    def extract_value(self, condition, stats):
        """
        Extract the current value from stats based on condition.
        
        Args:
            condition: String like "cpu.usage > 80"
            stats: Dictionary containing system statistics
            
        Returns:
            Current value of the metric (rounded if float)
        """
        metric_path = condition.split()[0]
        value = self._get_nested_value(stats, metric_path)
        
        if isinstance(value, float):
            return round(value, 2)
        
        return value
    
    def _get_nested_value(self, data, path):
        """
        Get value from nested dictionary using dot notation.
        
        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., 'cpu.usage', 'ram.percent')
            
        Returns:
            Value at the specified path or None if not found
        """
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value


# Example usage
if __name__ == "__main__":
    from pprint import pprint
    
    # Create rules engine
    engine = RulesEngine()
    
    # Example stats (simulate high CPU and RAM usage)
    example_stats = {
        "cpu": {
            "usage": 85.5,
            "per_core": [82.0, 88.0, 85.0, 87.0],
            "frequency": 2400.0
        },
        "ram": {
            "total": 16.0,
            "used": 14.5,
            "available": 1.5,
            "percent": 90.6
        },
        "disk": {
            "total": 500.0,
            "used": 420.0,
            "free": 80.0,
            "percent": 84.0
        }
    }
    
    # Check for triggered rules
    triggered = engine.check(example_stats)
    
    print("\n=== Triggered Rules ===")
    if triggered:
        for alert in triggered:
            print(f"[{alert['severity'].upper()}] {alert['name']}: {alert['current_value']}")
    else:
        print("No rules triggered - system is healthy!")