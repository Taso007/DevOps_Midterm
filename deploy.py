import json
import os
import subprocess
import time
import sys

CONFIG_FILE = "config/active_env.json"

def main():
    print("Starting Blue-Green Deployment...")
    
    # 1. Read current active env
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Have you run setup.py?")
        sys.exit(1)
        
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        
    current_port = config.get("port", 8001)
    current_env = config.get("env", "blue")
    
    # 2. Determine target env
    target_port = 8002 if current_port == 8001 else 8001
    target_env = "green" if current_env == "blue" else "blue"
    
    print(f"Current Active Env: {current_env} (Port {current_port})")
    print(f"Deploying to Target Env: {target_env} (Port {target_port})...")
    
    # 3. Start target application
    env = os.environ.copy()
    env["PORT"] = str(target_port)
    env["NODE_ENV"] = "production"
    
    # Start the node server in the background
    subprocess.Popen(["node", "server.js"], env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    print(f"Application started on port {target_port}. Verifying health...")
    
    # Health check loop
    import urllib.request
    max_retries = 5
    is_healthy = False
    
    for i in range(max_retries):
        try:
            time.sleep(2)
            print(f"Health check attempt {i+1}/{max_retries}...")
            with urllib.request.urlopen(f"http://127.0.0.1:{target_port}/health", timeout=2) as response:
                if response.getcode() == 200:
                    is_healthy = True
                    break
        except Exception:
            continue
            
    if not is_healthy:
        print("Error: Target environment failed health check. Deployment aborted.")
        sys.exit(1)
        
    # 4. Switch Proxy Traffic
    new_config = {"port": target_port, "env": target_env}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(new_config, f)
        
    print(f"Traffic successfully switched to {target_env} environment.")
    print("Blue-Green deployment complete!")

if __name__ == "__main__":
    main()
