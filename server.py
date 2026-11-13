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
    while True:
        command = read_line(conn)
        if command is None:
            break
        elif command.upper() == "QUIT":
            conn.sendall(b"OK\n")
            break
        else:
            print(command)
            conn.sendall(b"OK\n")
    conn.close()

        
def handle_command(conn, line):
    # TODO (group 1) split the line into a command and args, refuse
    # everything except LOGIN until the client is logged in, then call
    # the matching do_function. Reply ERR bad command for unknown ones.
    pass

def do_login(conn, args):
    # TODO (group 3): check the username and credential without ever
    # receiving a clear-text password. Reply OK or ERR login failed.
    # this i think has to wait for handle_command to finish ^
    pass

def do_dir(conn):
    # TODO (group 2): send the directory listing as OK size, then size
    # of bytes of listing text.
    pass 

def do_upload(conn, args):
    # TODO (group 1): handle UPLOAD name size. Reply OK or EXISTS, handle
    # YES/NO, receive exactly size bytes in chunks, then reply OK or ERR.
    pass 

def do_download(conn, args):
    # TODO (group 1): reply ERR file not found, or OK size followed by
    # the file's bytes sent in chunks.
    pass 

def do_delete(conn, args):
    # TODO (group 1) remove the file. reply ERR file not found, or 
    # ERR file in use if another thread is transferring it.
    pass 

def do_subfolder(conn, args):
    # TODO (group 2): handle SUBFOLDER create/delete path. Reject paths 
    # with .. or a leading / (ERR invalid path), then reply OK or ERR.
    pass



def main():
    # TODO (group 1): create the listening socket, bind to HOST and PORT,
    # start the analysis module, then accept clients and start a
    # handle_client thread for each.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #getting the phone
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT)) #getting the phone number
    server.listen() #server starts to listen
    print("server is ready and listening")
    while True:
        conn, addr = server.accept() #returns new line to the caller and the caller's address
        print("server accepted", addr)
        threading.Thread(target = handle_client, args = (conn, addr), daemon=True).start()
        

if __name__=="__main__":
    main()
