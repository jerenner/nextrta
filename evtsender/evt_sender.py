#!/usr/bin/env python3
# (Written by ChatGPT o1)

import socket
import struct
import time

def send_gdc_file_over_tcp(
    filename,
    tcp_host="192.168.1.50",   # IP or hostname of FPGA board
    tcp_port=12345,
    event_delay=0.01          # seconds to wait between events
):
    """
    Reads a raw DAQ file event by event and sends each event over TCP.
    :param filename: Path to the raw GDC file (e.g. 'run_14711.ldc1next.next-100.045.rd')
    :param tcp_host: IP/hostname of the FPGA board or test receiver
    :param tcp_port: TCP port on the FPGA/receiver
    :param event_delay: Delay (in seconds) inserted after sending each event
    """

    # 1. Open the file in binary mode
    with open(filename, "rb") as f:

        # 2. Create a TCP socket and connect
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to {tcp_host}:{tcp_port} ...")
            s.connect((tcp_host, tcp_port))
            print("Connected.")

            event_count = 0

            while True:
                # 3. Read the first 4 bytes -> eventSize (little-endian 32-bit)
                size_data = f.read(4)
                if not size_data or len(size_data) < 4:
                    # End of file or incomplete header => stop
                    break

                event_size = struct.unpack("<I", size_data)[0]

                # 4. Now read the rest of the event (event_size - 4 bytes)
                event_rest = f.read(event_size - 4)
                if len(event_rest) < (event_size - 4):
                    print("WARNING: Incomplete event found at EOF. Stopping.")
                    break

                # Reconstruct the full event (4 bytes + rest)
                event_data = size_data + event_rest

                # 5. Send the full event over TCP
                s.sendall(event_data)
                event_count += 1

                # 6. Optional delay to mimic real-time rate or avoid saturating the link
                if event_delay > 0:
                    time.sleep(event_delay)

            print(f"Finished sending {event_count} events.")
            # Socket closes automatically here.

if __name__ == "__main__":
    # Example usage
    send_gdc_file_over_tcp(
        filename="run_14711.ldc1next.next-100.045.rd",
        tcp_host="192.168.2.1",  # Put your FPGA or dev board IP here
        tcp_port=60000,
        event_delay=0.01         # 10 ms between events (adjust as needed)
    )

