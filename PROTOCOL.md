# message protocol

## Overview
- client and server will talk over TCP using text commands and raw file bytes

## general rules
- commands are one line ending in \n
- filenames cannot contain spaces
- every servery reply starts with OK or ERR
(add as you go)

## login
Order: client connects, login happens first, server replies OK or ERR, no commands are accepted until login succeeds.

## Commands
(add as you go, one short block per command: what the client sends, what the server replies.)

- DIR
- UPLOAD

## Upload flow
4 steps
1. UPLOAD name size
2. either EXISTS or OK
3. then YES or NO
4. then the data

## Sending file data
- size in bytes first
- then send exactly that many bytes

## Errors
(list error messages as you go)
- file not found
- file in use
- not logged in
- bad command
