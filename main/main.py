#!/usr/bin/env python3
"""
System Monitoring Orchestrator
Main entry point for the system monitoring application.
"""

# 1. Import your modules
from stats import SysStat
from rules import RulesEngine
from actions import Actions
import time
import json
import os
from datetime import datetime

# 2. Initialize everything once
def initialize():
    """Initialize all monitoring components."""
    print("🔧 Initializing system monitor...")
    
    sys = SysStat()
    rules = RulesEngine()
    actions = Actions()
    
    print("✓ All components loaded\n")
    
    return sys, rules, actions

# 3. Load configuration
def load_config():
    """Load main configuration file."""
    config_file = 'monitor_config.json'
    
    if not os.path.exists(config_file):
        default_config = {
            "interval": 5,
            "verbose": True,
            "show_healthy_status": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"Created default config: {config_file}")
        return default_config
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}, using defaults")
        return {"interval": 5, "verbose": True, "show_healthy_status": True}

# 4. Main monitoring loop
def monitor(sys, rules, actions, config):
    """
    Main monitoring loop - coordinates all components.
    
    Args:
        sys: SysStat instance
        rules: RulesEngine instance
        actions: Actions instance
        config: Configuration dictionary
    """
    interval = config.get('interval', 5)
    verbose = config.get('verbose', True)
    show_healthy = config.get('show_healthy_status', True)
    
    print(f"📊 Starting monitoring loop (checking every {interval}s)")
    print("Press CTRL+C to stop\n")
    print("=" * 60)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get current system statistics
            stats = sys.get_stats()
            
            # Check stats against rules
            alerts = rules.check(stats)
            
            if alerts:
                # Print header for this check
                print(f"\n[{timestamp}] Check #{iteration}")
                print("-" * 60)
                
                # Process each triggered alert
                for alert in alerts:
                    # Print human-readable info (UI responsibility)
                    severity_icon = {
                        'critical': '🚨',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(alert['severity'], '•')
                    
                    print(f"{severity_icon} {alert['name']}: {alert['current_value']}")
                    
                    # Execute the alert actions
                    actions.execute(alert)
                
                print("-" * 60)
            
            else:
                # Optional: print or log that system is healthy
                if show_healthy and verbose:
                    if iteration % 10 == 0:  # Show every 10th check to reduce noise
                        print(f"[{timestamp}] ✓ System healthy (check #{iteration})")
            
            # Wait before next check
            time.sleep(interval)
    
    except KeyboardInterrupt:
        # 5. Clean shutdown (CTRL+C)
        print("\n" + "=" * 60)
        print("🛑 Shutting down monitor...")
        print("✓ Cleanup complete. Goodbye!")

# 6. Optional: Single check mode
def run_once(sys, rules, actions):
    """Run a single check and exit."""
    print("📊 Running single check...\n")
    
    stats = sys.get_stats()
    alerts = rules.check(stats)
    
    if alerts:
        print("Triggered Alerts:")
        print("-" * 60)
        for alert in alerts:
            print(f"[{alert['severity'].upper()}] {alert['name']}: {alert['current_value']}")
            actions.execute(alert)
        print("-" * 60)
    else:
        print("✓ No alerts triggered - system is healthy!")
    
    print("\nCurrent System Stats:")
    sys.display()

# 7. Optional: Show alert history
def show_history(actions, limit=20):
    """Display recent alert history."""
    print(f"📜 Recent Alert History (last {limit}):\n")
    
    history = actions.get_alert_history(limit=limit)
    
    if not history:
        print("No alerts in history.")
        return
    
    for record in history:
        severity_icon = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(record['severity'], '•')
        
        print(f"{record['timestamp']} {severity_icon} [{record['severity'].upper()}] "
              f"{record['name']}: {record['current_value']}")

# 8. Optional: Interactive menu
def show_menu():
    """Display interactive menu."""
    print("\n" + "=" * 60)
    print("System Monitor - Main Menu")
    print("=" * 60)
    print("1. Start continuous monitoring")
    print("2. Run single check")
    print("3. Show current stats")
    print("4. Show alert history")
    print("5. Exit")
    print("=" * 60)
    
    return input("\nSelect option: ").strip()

# Main entry point
def main():
    """Main entry point with optional menu system."""
    
    # Check for command-line arguments
    import sys as system
    
    # Initialize components
    sys, rules, actions = initialize()
    config = load_config()
    
    # Simple CLI arguments handling
    if len(system.argv) > 1:
        arg = system.argv[1]
        
        if arg == '--once':
            run_once(sys, rules, actions)
            return
        
        elif arg == '--history':
            show_history(actions)
            return
        
        elif arg == '--stats':
            print("Current System Statistics:\n")
            sys.display()
            return
        
        elif arg == '--help':
            print("Usage: python main.py [option]")
            print("\nOptions:")
            print("  --once      Run a single check and exit")
            print("  --history   Show alert history")
            print("  --stats     Show current system stats")
            print("  --menu      Show interactive menu")
            print("  --help      Show this help message")
            print("\n  (no option) Start continuous monitoring")
            return
        
        elif arg == '--menu':
            while True:
                choice = show_menu()
                
                if choice == '1':
                    monitor(sys, rules, actions, config)
                    break
                elif choice == '2':
                    run_once(sys, rules, actions)
                    input("\nPress Enter to continue...")
                elif choice == '3':
                    print("\nCurrent System Statistics:\n")
                    sys.display()
                    input("\nPress Enter to continue...")
                elif choice == '4':
                    show_history(actions)
                    input("\nPress Enter to continue...")
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option. Please try again.")
            return
    
    # Default: Start continuous monitoring
    monitor(sys, rules, actions, config)

if __name__ == "__main__":
    main()