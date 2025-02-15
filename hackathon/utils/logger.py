import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "../logs.txt")

def log_message(message):
    """Logs messages to a file and prints them."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}\n"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

    print(message)
