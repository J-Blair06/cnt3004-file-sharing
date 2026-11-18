# server.py
import os
import socket
import threading

# constants
HOST = "0.0.0.0" # start off with this beacuse it means to listen on every network interface.
PORT = 5001 # start here arbitrarily, as long as >= 1024 (they need admin rights).
STORAGE_DIR = "server_storage" # the folder the server keeps files in. Relative to where script is run.
CHUNK_SIZE = 65536 # bytes to send or receive at a time (64 KB) needed for task B10.

# functions
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
    command = line.decode().strip()
    return command

def handle_client(conn, addr):
    # TODO (group 1) run once per client in its own thread. Track the
    # clients logged-in state, read one command line at a time, pass it
    # to handle_command, and close the connection on QUIT or disconnect.
    session = {"logged_in": True, "username": None} #TODO set to false once do _login works ****************************************************** This is super important
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
    conn.close()

        
def handle_command(conn, line, session):
    # TODO (group 1) split the line into a command and args, refuse
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
    # TODO (group 3): check the username and credential without ever
    # receiving a clear-text password. Reply OK or ERR login failed.
    # this i think has to wait for handle_command to finish ^
    pass

def do_dir(conn):
    # TODO (group 2): send the directory listing as OK size, then size
    # of bytes of listing text.

    #saves directory to dir variable
    dir = os.listdir(STORAGE_DIR)

    #checks if directory is empty
    #if it is, then it will send an error message to the client
    if dir is None:
        conn.sendall(b"ERR could not list directory\n")
        return

    #saves the size of the directory
    size = len("\n".join(dir).encode())

    #sends OK and size of directory, then sends directory listing
    conn.sendall(f"OK {size}\n".encode())
    conn.sendall("\n".join(dir).encode())



def do_upload(conn, args):
    # TODO (group 1): handle UPLOAD name size. Reply OK or EXISTS, handle
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

    if "/" in filename or "\\" in filename or ".." in filename:
        conn.sendall(b"ERR invalid path\n")
        return

    path = os.path.join(STORAGE_DIR, filename)

    if os.path.exists(path):
        conn.sendall(b"EXISTS\n")
        answer = read_line(conn)
        if answer is None:
            return
        if answer.upper() == "NO": #check if the file doesn't previously exist 
            conn.sendall(b"OK cancelled\n")
            return
        elif answer.upper() != "YES": #check if the file has a answer other than yes or no
            conn.sendall(b"ERR bad command\n")
            return
        #must be yes if not the previous two
    else:
        conn.sendall(b"OK\n")
    
    # receive size bytes and write them to path
    remaining = size
    temp_path = path + ".part"

    with open(temp_path, "wb") as f:
        while remaining > 0:
            chunk = conn.recv(min(CHUNK_SIZE, remaining))
            if chunk == b"":
                print("The caller hung up")
                break
            f.write(chunk)
            remaining -= len(chunk)
    if remaining == 0:
        os.replace(temp_path, path)
        print("received", size, "bytes") 
    else:
        os.remove(temp_path)
        print("upload incomplete, removed", temp_path)
        return       


def do_download(conn, args):
    # TODO (group 1): reply ERR file not found, or OK size followed by
    # the file's bytes sent in chunks.

    #check if the number of args is not equal to 1
    if len(args) != 1:
        conn.sendall(b"ERR bad command\n")
        return

    filename = args[0]

    #checks if filename contains /, \\, or ..
    if "/" in filename or "\\" in filename or ".." in filename:
        conn.sendall(b"ERR invalid path\n")
        return

    path = os.path.join(STORAGE_DIR, filename)

    #checks if the file exists, if not will send an error
    if not os.path.exists(path):
        conn.sendall(b"ERR file not found\n")
        return

    #finds size and sends OK and size to client
    size = os.path.getsize(path)

    conn.sendall(f"OK {size}\n".encode())

    #opens file and sends in chunks to client, if fails will send an error
    try:
        with open(path, "rb") as file:
            while True:
                chunk = file.read(CHUNK_SIZE)

                if not chunk:
                    break

                conn.sendall(chunk)

    except OSError:
        conn.sendall(b"ERR could not read file\n")
    


def do_delete(conn, args):
    # TODO (group 1) remove the file. reply ERR file not found, or 
    # ERR file in use if another thread is transferring it.
    pass 

def do_subfolder(conn, args):
    # TODO (group 2): handle SUBFOLDER create/delete path. Reject paths 
    # with .. or a leading / (ERR invalid path), then reply OK or ERR.
    
    #splits args into foldername and action
    parts = args[0].split()

    foldername = parts[0]
    action = parts[1].upper()

    #checks if foldername starts with / or has .. in it
    #if it does then it will send an error message
    if foldername.startswith("/") or ".." in foldername:

        conn.sendall(b"ERR invalid path\n")
        return

    # creates the path to the folder in the directory
    dir = os.path.join(STORAGE_DIR, foldername)

    #checks what the action is
    #if create it will create the folder
    #if delete it will delete the folder
    #if it cant do either it will send an error message
    if action == "CREATE":
        try:
            os.makedirs(dir, exist_ok=True)
            conn.sendall(b"OK\n")
        except OSError:
            conn.sendall(b"ERR could not create folder\n")

    elif action == "DELETE":
        try:
            os.rmdir(dir)
            conn.sendall(b"OK\n")
        except OSError:
            conn.sendall(b"ERR could not delete folder\n")

    return
    



def main():
    # TODO (group 1): create the listening socket, bind to HOST and PORT,
    # start the analysis module, then accept clients and start a
    # handle_client thread for each.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #getting the phone
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT)) #getting the phone number
    os.makedirs(STORAGE_DIR, exist_ok=True)
    server.listen() #server starts to listen
    print("server is ready and listening")
    while True:
        conn, addr = server.accept() #returns new line to the caller and the caller's address
        print("server accepted", addr)
        threading.Thread(target = handle_client, args = (conn, addr), daemon=True).start()
        

if __name__=="__main__":
    main()
