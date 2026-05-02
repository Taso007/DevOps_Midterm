import os
import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        sys.exit(1)

def main():
    print("Starting environment setup...")
    
    # 1. Create directories
    directories = ["logs", "config"]
    for d in directories:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")
        else:
            print(f"Directory {d} already exists")
            
    # 2. Create default configuration if not exists
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("PORT=3000\n")
            f.write("NODE_ENV=development\n")
        print("Created .env file")
    else:
        print(".env already exists")
        
    config_file = "config/active_env.json"
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write('{"port": 8001, "env": "blue"}\n')
        print(f"Created {config_file}")
        
    # 3. Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install")
    
    print("Environment setup completed successfully!")

if __name__ == "__main__":
    main()
