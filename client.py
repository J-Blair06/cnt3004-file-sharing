# client.py

import socket
import sys

# function

def connect():
    # TODO (group 2) creates the socket and connects to the server. 
    # prints a clear error if the server can't be reached.

    #Creates socket, Host and Port
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"
    PORT = 5001

    #trys to connect to server, if it fails it will print an error and exit
    try:
        soc.connect((HOST, PORT))

    except:
        print("Connection Error")
        sys.exit()

    #socket is returned
    return soc

def login():
    # TODO (group 3) akss for the username and password, sends 
    # LOGIN without a clear-text password, and reports OK or ERR
    pass

def do_dir(soc):
    # TODO (group 2) sends DIR, reads the size, reads that many bytes, and
    # prints the listing
    
    #sends request to server
    soc.send(b'DIR')

    #reads the expected size and listing from server
    expectedsize = int(soc.recv(1024).decode())
    listing = soc.recv(1024)

    #if the listing is larger than 1024 bytes, it will keep receiving until it matches the expected size
    while len(listing) < expectedsize:
        moreListing = soc.recv(1024)

        #if the server sends no more data, it will break the loop
        if not moreListing:
            break

        listing += moreListing

    #checks if the received sizes matches the expected size, if it does not match it will print an error message
    if(len(listing) != expectedsize):
        print("Error: received size does not match expected size.")

    #prints the listing
    print(listing.decode())
        
        
        
        


def do_upload(soc, argument):
    # TODO (group 2) sends UPLOAD with the name and size, handles
    # OK or EXISTS (asks user yes or no), sends the file in chunks, and
    # reads the final reply

    filename = argument

    with open(filename, 'rb') as f:
        data = f.read()
    
    soc.send(f'UPLOAD {argument}'.encode())
    soc.send(len(data).to_bytes(4, byteorder='big'))
    soc.send(data)

    
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

    #connect to server
    soc = connect()

    #ask for command
    print("Please enter a command (DIR, UPLOAD, DOWNLOAD, DELETE, SUBFOLDER, QUIT):")

    #while loop that asks for commands until the user quits
    while True:
        message = input(" -> ")

        #splits the message into command and argument
        parts = message.split(maxsplit=1)

        if not parts:
            print("No command entered. Please try again.")
            continue

        command = parts[0].upper()

        argument = parts[1] if len(parts) > 1 else ""

        #checks if any of the commands match, if they do it will call that function, otherwise it will print an error message
        if command == "QUIT":
            break
        
        elif command == "DIR":
            do_dir(soc)

        elif command == "UPLOAD":
            do_upload(soc, argument)

        elif command  == "DOWNLOAD":
            do_download(argument)

        elif command == "DELETE":
            do_delete(argument)

        elif command == "SUBFOLDER":
            do_subfolder(argument)

        else:
            print("Invalid command. Please try again.")

    #closes connection to server
    soc.send(b'QUIT')
    soc.close()


if __name__=="__main__":
    main()
