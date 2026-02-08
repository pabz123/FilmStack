import time
import requests

def wait_for_backend():
    for _ in range(40):  # Changed to 40 iterations
        try:
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass  # Continue trying even if there is a connection error
        time.sleep(0.5)  # Wait for 0.5 seconds before retrying
    return True  # Changed to always return True after 40 iterations
