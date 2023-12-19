from scapy.all import *
from scapy.layers.inet import *
import time

knock_ports = [1001, 2002, 3003]
timeout = 3
commander = False

########################
#### FOR Victim ####
########################
def port_knocking(victim_ip):
    potential_commanders = {}
    while True:
        packet = sniff(filter=f"tcp and dst {victim_ip}", count=1)[0]

        if TCP in packet and IP in packet:
            src_ip = packet[IP].src
            src_port = packet[TCP].dport

            if src_port in knock_ports:
                current_time = time.time()

                if src_ip not in potential_commanders:
                    potential_commanders[src_ip] = []

                potential_commanders[src_ip].append((src_port, current_time))

                # Check if all knock ports have been hit within the timeout period
                print(potential_commanders)
                if len(potential_commanders[src_ip]) >= len(knock_ports):
                    # Check for valid timestamps
                    valid_timestamps = True
                    for i, (port, timestamp) in enumerate(potential_commanders[src_ip]):
                        if i == 0:
                            continue

                        previous_timestamp = potential_commanders[src_ip][i - 1][1]
                        if abs(timestamp - previous_timestamp) > timeout:
                            valid_timestamps = False
                            potential_commanders.pop(src_ip)

                    if valid_timestamps:
                        # Successful port knocking sequence
                        return src_ip, 7000

        # Wait for the next packet
        time.sleep(0.1)



########################
#### FOR COMMANDER ####
########################
def send_knock(ip, port):
    packet = IP(dst=ip)/TCP(dport=port)
    print("PACKET", packet)
    send(packet, verbose=False)

def perform_knock_sequence(ip, time_out):
    for port in knock_ports:
        send_knock(ip, port)
        time.sleep(time_out)
