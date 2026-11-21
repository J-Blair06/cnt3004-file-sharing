# server.py
import os
import socket
import threading
import auth
import time
import analysis

# constants
HOST = "0.0.0.0" # start off with this beacuse it means to listen on every network interface.
PORT = 5001 # start here arbitrarily, as long as >= 1024 (they need admin rights).
STORAGE_DIR = "server_storage" # the folder the server keeps files in. Relative to where script is run.
CHUNK_SIZE = 65536 # bytes to send or receive at a time (64 KB) needed for task B10.
REPORT_EVERY = 10 * 1024 * 1024 # this is 10 MB in bytes

active_clients = 0 # number of clients currently connected to the server
clients_lock = threading.Lock() # protects active_clients

files_in_use = set() # stores files being transfered
files_lock = threading.Lock() # protects files_in_use


# functions


# helper function reads client count safely
def get_active_clients():
    with clients_lock:
        return active_clients

# helper function checks that a filename is a plain name inside the storage folder
def is_safe_name(name):
    if name in ("", ".", ".."):
        return False
    if "/" in name or "\\" in name or ":" in name or ".." in name:
        return False
    if name.endswith(".part"): # .part files are the server's own temp files
        return False
    return True

def read_line(conn):
    line = b""
    while True:
        byte = conn.recv(1)
        if byte == b"":
            print("connection closed")
            return None
        if byte == b"\n":
            print("end of line reached")
            break
        line = line + byte
    command = line.decode(errors="replace").strip()
    return command

def handle_client(conn, addr):
    # (group 1) run once per client in its own thread. Track the
    # clients logged-in state, read one command line at a time, pass it
    # to handle_command, and close the connection on QUIT or disconnect.
    global active_clients
    with clients_lock:
        active_clients += 1
    try:
        session = {"logged_in": False, "username": None, "pending_user": None} 
        while True:
            command = read_line(conn)
            if command is None:
                break
            elif command.upper() == "QUIT":
                conn.sendall(b"OK\n")
                break
            else:
                print(command)
                handle_command(conn, command, session)
    finally:
        with clients_lock:
            active_clients -= 1
        conn.close()

        
def handle_command(conn, line, session):
    # (group 1) split the line into a command and args, refuse
    # everything except LOGIN and PASS until the client is logged in, then call
    # the matching do_function. Reply ERR bad command for unknown ones.
    parts = line.split()
    if not parts:
        conn.sendall(b"ERR bad command\n")
        return
    command = parts[0].upper()
    args = parts[1:]
    print(command, args)

    if not session["logged_in"] and command not in ("LOGIN", "PASS"):
        conn.sendall(b"ERR not logged in\n")
        return

    if command in ("LOGIN", "PASS"):
        do_login(conn, command, args, session)

    elif command == "DIR":
        do_dir(conn)
    
    elif command == "UPLOAD":
        do_upload(conn, args)

    elif command == "DOWNLOAD":
        do_download(conn, args)

    elif command == "DELETE":
        do_delete(conn, args)

    elif command == "SUBFOLDER":
        do_subfolder(conn, args)

    else:
        conn.sendall(b"ERR bad command\n")
    
def do_login(conn, command, args, session):
    # (group 3): check the username and credential without ever
    # receiving a clear-text password. Reply OK or ERR login failed.
    # this i think has to wait for handle_command to finish ^
    if command == "LOGIN":
        if len(args) != 1:
            conn.sendall(b"ERR bad command\n")
            return
        username = args[0]
        salt = auth.get_salt(username)
        if salt is None:
            conn.sendall(b"ERR login failed\n")
            return
        session["pending_user"] = args[0]
        conn.sendall(f"OK {salt}\n".encode())

    elif command == "PASS":
        if len(args) != 1 or session["pending_user"] is None:
            conn.sendall(b"ERR login failed\n")
            return
        username = session["pending_user"]
        session["pending_user"] = None
        password_hash = args[0]
        if auth.check_hash(username, password_hash):
            session["logged_in"] = True
            session["username"] = username
            conn.sendall(b"OK\n")
        else:
            conn.sendall(b"ERR login failed\n")

def do_dir(conn):
    # (group 2): send the directory listing as OK size, then size
    # of bytes of listing text.

    # saves directory to dir variable
    dir = os.listdir(STORAGE_DIR)

    # checks if directory is empty
    # if it is, then it will send an error message to the client
    if len(dir) == 0:
        conn.sendall(b"ERR directory is empty\n")
        return

    # saves the size of the directory
    size = len("\n".join(dir).encode())

    # sends OK and size of directory, then sends directory listing
    conn.sendall(f"OK {size}\n".encode())
    conn.sendall("\n".join(dir).encode())
    return



def do_upload(conn, args):
    # (group 1): handle UPLOAD name size. Reply OK or EXISTS, handle
    # YES/NO, receive exactly size bytes in chunks, then reply OK or ERR.
    if len(args) != 2:
        conn.sendall(b"ERR bad command\n")
        return
    try:
        size = int(args[1]) 
    except ValueError:
        conn.sendall(b"ERR bad size\n")
        return
    if size < 0:
        conn.sendall(b"ERR bad size\n")
        return

    filename = args[0]

    if not is_safe_name(filename):
        conn.sendall(b"ERR invalid path\n")
        return

    path = os.path.join(STORAGE_DIR, filename)
    
    claimed = False
    with files_lock:
        if filename not in files_in_use:
            files_in_use.add(filename)
            claimed = True
        
        
    if not claimed:
        conn.sendall(b"ERR file in use\n")
        return

    done = False

    try:
        if os.path.exists(path):
            conn.sendall(b"EXISTS\n")
            answer = read_line(conn)
            if answer is None:
                return
            if answer.upper() == "NO": # check if the file doesn't previously exist 
                conn.sendall(b"OK cancelled\n")
                return
            elif answer.upper() != "YES": # check if the file has a answer other than yes or no
                conn.sendall(b"ERR bad command\n")
                return
            # must be yes if not the previous two
        else:
            conn.sendall(b"OK\n")
    
        # receive size bytes and write them to path
        remaining = size
        next_report = REPORT_EVERY
        temp_path = path + ".part"

        start = time.perf_counter()
        try:
            with open(temp_path, "wb") as f:
                while remaining > 0:
                    chunk = conn.recv(min(CHUNK_SIZE, remaining))
                    if chunk == b"":
                        print("The caller hung up")
                        break
                    f.write(chunk)
                    remaining -= len(chunk)
                    if size - remaining >= next_report:
                        print("received", size - remaining, "of", size, "bytes")
                        next_report += REPORT_EVERY
                        
        except OSError:
            conn.sendall(b"ERR could not write file\n")
            try:
                os.remove(temp_path)
            except OSError:
                pass
            return

        seconds = time.perf_counter() - start
        if remaining == 0:
            os.replace(temp_path, path)
            conn.sendall(b"OK\n")
            done = True
            print("received", size, "bytes") 
            print("took", seconds, "seconds")
        else:
            os.remove(temp_path)
            print("upload incomplete, removed", temp_path)
            return
    finally:
        with files_lock:
            files_in_use.discard(filename)       
    if done:
        analysis.record_transfer("upload", filename, size, seconds, get_active_clients())


def do_download(conn, args):
    # (group 1): reply ERR file not found, or OK size followed by
    # the file's bytes sent in chunks.

    # check if the number of args is not equal to 1
    if len(args) != 1:
        conn.sendall(b"ERR bad command\n")
        return

    filename = args[0]

    # checks if filename contains /, \\, or ..
    if not is_safe_name(filename):
        conn.sendall(b"ERR invalid path\n")
        return

    path = os.path.join(STORAGE_DIR, filename)

    # checks if the file exists, if not will send an error
    if not os.path.isfile(path):
        conn.sendall(b"ERR file not found\n")
        return

    # lock block 1, claim the name
    claimed = False
    with files_lock:
        if filename not in files_in_use:
            files_in_use.add(filename)
            claimed = True
    
    if not claimed:
        conn.sendall(b"ERR file in use\n")
        return

    done = False

    # finds size and sends OK and size to client
    size = os.path.getsize(path)
    total_sent = 0
    next_report = REPORT_EVERY

    # lock block 2
    try:
        conn.sendall(f"OK {size}\n".encode())

    # opens file and sends in chunks to client, if fails will send an error
        try:
            with open(path, "rb") as file:
                start = time.perf_counter()
                while True:
                    chunk = file.read(CHUNK_SIZE)

                    if not chunk:
                        break

                    conn.sendall(chunk)
                    total_sent += len(chunk)
                    if total_sent >= next_report:
                        print("sent", total_sent, "of", size, "bytes")
                        next_report += REPORT_EVERY
                seconds = time.perf_counter() - start
                done = total_sent == size
        except OSError:
            conn.sendall(b"ERR could not read file\n")

    finally:
        with files_lock:
            files_in_use.discard(filename)

    if done:
        analysis.record_transfer("download", filename, size, seconds, get_active_clients())
    

def do_delete(conn, args):
    # (group 1) remove the file. reply ERR file not found, or 
    # ERR file in use if another thread is transferring it.
    reply = b"" # variable to save responses to the client
    if len(args) != 1: # check if the filename isn't 1 word
        conn.sendall(b"ERR bad command\n")
        return
    filename = args[0] # we take the filename from the args and assign it to filename
    if not is_safe_name(filename): # check for characters that could be file paths not filenames
        conn.sendall(b"ERR invalid path\n")
        return
    with files_lock: 
        path = os.path.join(STORAGE_DIR, filename) # look for the path
        if filename in files_in_use: # checking if the file is in use or not
            reply = b"ERR file in use\n"
        elif os.path.isfile(path): # check if file exists
            try:
                os.remove(path)
                reply = b"OK\n"
            except OSError:
                reply = b"ERR could not delete file\n"
        else: # file wasn't found and doesn't exist
            reply = b"ERR file not found\n"
    conn.sendall(reply)



def do_subfolder(conn, args):
    # (group 2): handle SUBFOLDER create/delete path. Reject paths 
    # with .. or a leading / (ERR invalid path), then reply OK or ERR.
    
    # checks if the number of args is equal to 2
    if len(args) != 2:
        conn.sendall(b"ERR bad command\n")
        return    

    foldername = args[1]
    action = args[0].upper()

    # checks if foldername starts with / or has .. in it
    # if it does then it will send an error message
    if foldername.startswith("/") or ".." in foldername or "\\" in foldername:
        conn.sendall(b"ERR invalid path\n")
        return

    root = os.path.realpath(STORAGE_DIR)

    # creates the path to the folder in the directory
    folder_path = os.path.realpath(os.path.join(STORAGE_DIR, foldername))

    if not folder_path.startswith(root + os.sep):
        conn.sendall(b"ERR invalid path\n")
        return

    
    # checks what the action is
    # if create it will create the folder
    # if delete it will delete the folder
    # if it cant do either it will send an error message
    if action == "CREATE":
        try:
            os.makedirs(folder_path, exist_ok=True)
            conn.sendall(b"OK\n")
        except OSError:
            conn.sendall(b"ERR could not create folder\n")

    elif action == "DELETE":
        try:
            os.rmdir(folder_path)
            conn.sendall(b"OK\n")
        except OSError:
            conn.sendall(b"ERR could not delete folder\n")

    else:
        conn.sendall(b"ERR not a valid action\n")
        return

    return
    



def main():
    # (group 1): create the listening socket, bind to HOST and PORT,
    # start the analysis module, then accept clients and start a
    # handle_client thread for each.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # getting the phone
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT)) # getting the phone number
    os.makedirs(STORAGE_DIR, exist_ok=True)
    analysis.start() # start the analysis module
    server.listen() # server starts to listen
    print("server is ready and listening")
    while True:
        conn, addr = server.accept() # returns new line to the caller and the caller's address
        print("server accepted", addr)
        threading.Thread(target = handle_client, args = (conn, addr), daemon=True).start()
        

if __name__=="__main__":
    main()
