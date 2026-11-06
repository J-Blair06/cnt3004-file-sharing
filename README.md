# cnt3004-file-sharing

#Cloud File Sharing System

A multithreaded client-server file sharing system written in Python, deployed on Google Cloud Platform, with built-in network performance analysis.

> Team project for CNT3004 (Computer Networks), Florida Polytechnic University, Fall 2026.

## Overview

Clients connect to a central cloud server over TCP to upload, download, and manage files. The server handles several clients at once using threads. A separate analysis module records transfer speeds and timings so the system's performance can be measured under different loads.

## Features

- [ ] TCP socket server and client
- [ ] Multithreaded server (concurrent clients)
- [ ] Secure authentication (no plaintext passwords)
- [ ] File operations: upload, download, delete, directory listing
- [ ] Subfolder creation and deletion
- [ ] Large file support (text, audio, video)
- [ ] Network analysis: transfer rate (MB/s), transfer time, plus one additional metric
- [ ] Deployment on Google Compute Engine
- [ ] LLM-based transfer time prediction (extra credit)

## Architecture

```
  Client 1 ─┐
  Client 2 ─┼──── TCP ────►  Server (GCP Compute Engine)
  Client 3 ─┘                 ├── one thread per client
                              ├── file storage
                              └── analysis module (stats)
```

## Tech Stack

- Python 3
- `socket` and `threading` (standard library)
- Google Cloud Platform (Compute Engine)
- Git and GitHub for version control

## Project Structure

```
server.py      # Multithreaded server and file operations
client.py      # Command-line client
analysis.py    # Performance statistics collection
```



## Getting Started

### Prerequisites
- Python 3.10 or newer
- Git

### Setup
```
git clone https://github.com/J-Blair06/cnt3004-file-sharing.git
cd cnt3004-file-sharing
```

### Usage


## Results



## What We Learned

*testing
*testing
**Testing!

## Team

| Name | GitHub | Focus |
|------|--------|-------|
| Jaci Blair | [@J-Blair06](https://github.com/J-Blair06) | |
| Lillian MaGill | [@L-MaGill](https://github.com/L-MaGill) | |
| Gabriela Sosa | [@GSosa36](https://github.com/GSosa36) | |
| Connor Brown | [@cbrown0794](https://github.com/cbrown0794) |Testing, AI & Results|

## Security Note

Credentials and keys are never stored in this repository.

