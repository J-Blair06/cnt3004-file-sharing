# analysis.py
import threading
import csv
from datetime import datetime

# empty list that collects the results, each entry is one transfer
results = []
# CSV file that stores the transfer results
RESULTS_FILE = "transfer_results.csv"


def start():
    # Reset results and create a new results file with a timestamp
    global RESULTS_FILE
    RESULTS_FILE = "transfer_results_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    with results_lock:
        results.clear()

results_lock = threading.Lock() # protects results

def record_transfer(direction, filename, size_bytes, seconds, active_clients):
    # Convert size to megabytes and calculate transfer rate
    size_mb = size_bytes / (1024 * 1024)
    rate_mbs = size_mb / seconds if seconds > 0 else 0

    #Create dictionary of transfer data
    transfer = {
        "direction": direction,
        "filename": filename,
        "size_bytes": size_bytes,
        "size_mb": size_mb,
        "seconds": seconds,
        "rate_mbs": rate_mbs,
        "active_clients": active_clients,
    }

    # Add transfer to results list under lock
    with results_lock:
        results.append(transfer)

    # Save results to CSV file
    save_results()

def save_results():
    # Save results to CSV file
    with results_lock:
        rows = list(results)

    # Open CSV file for writing
    with open(RESULTS_FILE, "w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "direction",
                "filename",
                "size_bytes",
                "size_mb",
                "seconds",
                "rate_mbs",
                "active_clients",
            ],
        )
        # Write header and data rows
        writer.writeheader()
        writer.writerows(rows)



