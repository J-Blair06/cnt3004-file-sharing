# analysis.py
import threading

# empty list that collects the results, each entry is one transfer
results = []

results_lock = threading.Lock() # protects results

def record_transfer(direction, filename, size_bytes, seconds, active_clients):
    # TODO (group 3) calculates the rate in MB/s, builds one dictionary from the 
    # inputs plus the rate, and appends it to results under the lock. called by
    # the server's do_upload and do_download
    pass

def save_results():
    # TODO (group 3) write results to a file for offline review, holding
    # results_lock while reading the list. Add the output file to
    # .gitignore
    pass

