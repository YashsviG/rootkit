import psutil
import random

def analyze_existing_process_names():
    """
    Analyze existing process names and generate a custom name.

    Returns:
        str: Custom process name.
    """
    processes = psutil.process_iter(attrs=['pid', 'name'])
    process_names = [p.info['name'] for p in processes]

    custom_name = random.choice(process_names) + "_custom_" + str(random.randint(1000, 9999))
    return custom_name

def choose_process_name():
    """
    Choose a process name based on existing process names.

    Returns:
        str: Chosen process name.
    """
    # Get a list of all existing process names
    existing_process_names = [p.name() for p in psutil.process_iter()]

    if existing_process_names:
        chosen_name = analyze_existing_process_names()
    else:
        chosen_name = "nvme-update-wq"

    print(f"Process name chosen {chosen_name}")
    return chosen_name
