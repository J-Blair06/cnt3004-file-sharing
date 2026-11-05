# message protocol

## Overview
- client and server will talk over TCP using text commands and raw file bytes

## general rules
- commands are one line ending in \n
- filenames cannot contain spaces
- every server reply starts with OK or ERR
(add as you go)

## login
Order: client connects, login happens first, server replies OK or ERR, no commands are accepted until login succeeds.

## Commands
(add as you go, one short block per command: what the client sends, what the server replies.)

- DIR
    client sends: DIR
    server replies: OK size (or ERR...and then no data), then size bytes of listing text
- UPLOAD
- DOWNLOAD
    client sends: DOWNLOAD name
    server replies: OK size (or ERR file not found, and no data), then size bytes of file data.
- DELETE
- SUBFOLDER
- QUIT

## Upload flow
4 steps
1. Client sends: UPLOAD name size
2. Server replies: 
    EXISTS -> go to step 3 (file already exists)
    OK -> go to step 4 (new file)
3. then YES or NO
    YES -> go to step 4
    NO -> server replies OK (with some message, we can figure that out) and the upload ends
4. Client sends exactly size bytes of data
5. when all bytes have arrived, server replied OK (or ERR...)

## Sending file data
Anything of unknown length (file contents, directory listings) is sent the same way:
- size in bytes first
- then send exactly that many bytes

## Errors
(list error messages as you go)
- file not found
- file in use
- not logged in
- bad command
