import urllib.request
import time
import datetime
import os

PROXY_URL = "http://127.0.0.1:8000/health"
LOG_FILE = "logs/health.log"

def check_health():
    try:
        req = urllib.request.Request(PROXY_URL)
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            response_time = (time.time() - start_time) * 1000
            return status_code, response_time, "OK"
    except urllib.error.URLError as e:
        return 500, 0, str(e.reason)
    except Exception as e:
        return 500, 0, str(e)

def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    print(f"Starting health monitor for {PROXY_URL}. Logging to {LOG_FILE}...")
    try:
        while True:
            status_code, resp_time, msg = check_health()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Status: {status_code} | Time: {resp_time:.2f}ms | Msg: {msg}\n"
            
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
            
            # Print to console as well for demonstration purposes
            print(log_entry.strip())
            
            # Wait for 5 seconds before next check
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()
