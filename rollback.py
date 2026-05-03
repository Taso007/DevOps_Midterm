import json
import os
import sys
import time
import urllib.request

CONFIG_FILE = "config/active_env.json"

def check_health(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
            return response.getcode() == 200
    except Exception:
        return False

def main():
    print("Initiating Safety Rollback...")
    
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found.")
        sys.exit(1)
        
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        
    current_port = config.get("port", 8001)
    current_env = config.get("env", "blue")
    
    # Calculate target rollback env
    target_port = 8002 if current_port == 8001 else 8001
    target_env = "green" if current_env == "blue" else "blue"
    
    print(f"Checking health of the previous environment ({target_env} on port {target_port})...")
    
    if check_health(target_port):
        print(f"Health check passed. Rolling back from {current_env} to {target_env}...")
        
        new_config = {"port": target_port, "env": target_env}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f)
            
        print(f"Rollback successful. Traffic is now routing to {target_env}.")
    else:
        print(f"Error: Target environment ({target_env}) is NOT healthy.")
        print("Rollback aborted to prevent breaking the live site.")
        sys.exit(1)

if __name__ == "__main__":
    main()
