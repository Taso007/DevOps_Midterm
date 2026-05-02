import json
import os
import sys

CONFIG_FILE = "config/active_env.json"

def main():
    print("Initiating Rollback...")
    
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found.")
        sys.exit(1)
        
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        
    current_port = config.get("port", 8001)
    current_env = config.get("env", "blue")
    
    # Switch back to the previous env
    previous_port = 8002 if current_port == 8001 else 8001
    previous_env = "green" if current_env == "blue" else "blue"
    
    print(f"Rolling back from {current_env} (Port {current_port}) to {previous_env} (Port {previous_port})...")
    
    new_config = {"port": previous_port, "env": previous_env}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(new_config, f)
        
    print(f"Rollback successful. Traffic is now routing to {previous_env}.")

if __name__ == "__main__":
    main()
