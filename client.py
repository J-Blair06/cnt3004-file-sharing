# client.py

import socket

# function

def connect():
    # TODO (group 2) creates the socket and connects to the server. 
    # prints a clear error if the server can't be reached.
    pass

def login():
    # TODO (group 3) akss for the username and password, sends 
    # LOGIN without a clear-text password, and reports OK or ERR
    pass

def do_dir():
    # TODO (group 2) sends DIR, reads the size, reads that many bytes, and
    # prints the listing
    pass

def do_upload():
    # TODO (group 2) sends UPLOAD with the name and size, handles
    # OK or EXISTS (asks user yes or no), sends the file in chunks, and
    # reads the final reply
    pass

def do_download():
    # TODO (group 2) sends DOWNLOAD, reads the size, receives that many bytes
    # in chunks, and saves the file. prints any error.
    pass

def do_delete():
    # TODO (group 2) sends DELETE and prints the server's reply
    pass

def do_subfolder():
    # TODO (group 2) sends SUBFOLDER create or delete with the path
    # and prints the reply
    pass

def predict_transfer_time():
    # TODO (group 4) extra credit. calls the LLM API and shows the
    # prediction next to the measured time
    pass

def main():
    # TODO (group 2) the input loop: reads what the user types, splits it into a
    # command and arguments, calls the right function, and stops on QUIT
    pass

if __name__=="__main__":
    main()