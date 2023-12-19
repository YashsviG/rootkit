# Linux Rootkit
## Overview
This repository contains two Python programs, `Commander` and `Victim`, designed for **covert communication and control over a network**. The Commander initiates a session by port knocking on the Victim, allowing the two programs to communicate through covert channels. The Victim responds to the Commander's commands, which include various actions like starting/stopping a keylogger, transferring files, watching files or directories, running programs, and more.

## Key Points
- All communication between the Commander and Victim is done through covert channels.
- Communication is encrypted to ensure secure data transfer.
- The session initiated by port knocking continues until the Commander selects the Disconnect option.
- Output from programs run on the Victim is displayed on the Commander.

### Dependencies
- Both programs use Python and various libraries such as `multiprocessing, inotify, and psutil`.
- Install all these dependencies using: `pip install -r requirements.txt`

## Commander Program
### Usage
Run the Commander program with the following command:
`python commander.py -ip <victim_ip_addr> -p <port_number>`
(Replace <victim_ip_addr> with the victim's IP address, <port_number> with the desired port number for communication.)

Follow the on-screen menu to interact with the Victim.

#### Menu Options
- Disconnect from the Victim: End the current session and disconnect from the Victim.
- Uninstall from the Victim: Uninstall the program from the Victim.
- Start Keylogger on the Victim: Initiate the keylogger on the Victim.
- Stop Keylogger on the Victim: Stop the keylogger on the Victim.
- Transfer Keylog File from the Victim: Retrieve the keylog file from the Victim.
- Transfer a File to the Victim: Send a file to the Victim.
- Transfer a File from the Victim: Receive a file from the Victim.
- Watch a File on the Victim: Monitor changes to a specific file on the Victim.
- Watch a Directory on the Victim: Monitor changes to files within a directory on the Victim.
- Run a Program on the Victim: Execute a command on the Victim, and view the output on the Commander.

## Victim Program
### Usage
Run the Victim program with the following command:
`python victim.py -p <port_number>`
(Replace <port_number> with the port number used by the Commander for communication.)

Wait for the Commander to initiate a session through port knocking.

## Screenshot of the Rootkit running
### Commander
![image](https://github.com/YashsviG/rootkit/assets/45160510/32f45dfe-0de8-480f-a9e1-98654252f6d4)

### Victim
![image](https://github.com/YashsviG/rootkit/assets/45160510/40411eaf-1eb1-471c-893c-bd48a315da39)

## Demo
https://github.com/YashsviG/rootkit/assets/45160510/220476a1-a49f-45b5-9950-34a11f548d6d

