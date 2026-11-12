# client.py

import socket
import sys
import os

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
    soc.send(b'DIR\n')

    #reads the expected size and listing from server
    part1 = soc.recv(1024).decode().strip()
    part2 = part1.split()

    if len(part2) < 2 or part2[0] != "OK":
        print(f"Error: server responded with {part1}")
        return
    
    expectedsize = int(part2[1])
    listing = b''

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

    #get size and change it to bytes
    size = os.path.getsize(filename)
    size = size.to_bytes(4, byteorder='big')

    #send upload request and filename and size to server
    message = b'UPLOAD ' + filename.encode() +b' ' + size + b'\n'
    soc.send(message)

    #response from server
    response =soc.recv(1024).decode().strip()

    #if response is EXISTS, ask user if they want to overwrite the file
    #if yes it will overwrite the file, if no it will cancel the upload
    if response == "EXISTS":
        answer = input(f"{filename} already exists on the server. Do you want to overwrite it? (yes/no): ")
        if answer.lower() != "yes":
            print("Upload cancelled.")
            return
        else:
            soc.send(b'OVERWRITE\n')

    #if neither OK or EXISTS, then it will print an error message
    elif response != "OK" and response != "EXISTS":
        print(f"Error: server responded with {response}")
        return

    #opens file and sends it to the server
    file = open(filename, 'rb')
    while True:
        section = file.read(1024)
        if not section:
            break
        soc.send(section)
    file.close()

    #response from server after upload, if ok it will print successful
    #if not it will print an error message
    final_response = soc.recv(1024).decode().strip()
    if final_response == "OK":
        print(f"{filename} uploaded successfully.")

    else:
        print(f"Error: server responded with {final_response}")


    

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

        #before other commands, it will check if argument contains spaces
        elif ' ' in argument:
            print("Error: file names cannot contain spaces.")
            continue

        elif command == "DIR":
            do_dir(soc)

        elif command == "UPLOAD":
            do_upload(soc, argument)

        elif command  == "DOWNLOAD":
            do_download(soc, argument)

        elif command == "DELETE":
            do_delete(soc, argument)

        elif command == "SUBFOLDER":
            do_subfolder(soc,argument)

        else:
            print("Invalid command. Please try again.")

    #closes connection to server
    soc.send(b'QUIT\n')
    soc.close()


if __name__=="__main__":
    main()
