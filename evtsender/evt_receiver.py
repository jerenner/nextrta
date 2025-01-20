#!/usr/bin/env python3
# (Written by ChatGPT o1)

import socket
import struct

def receive_gdc_file_over_tcp(
    output_filename="received_data.rd",
    listen_host="0.0.0.0",
    listen_port=12345
):
    """
    Listens on TCP for incoming events, each preceded by a 4-byte size field.
    Writes all received data (in correct event order) to 'output_filename'.

    The protocol assumed:
    1) The sender sends 4 bytes (little-endian uint32) -> eventSize
    2) Then sends eventSize - 4 bytes of the event body
    3) Repeats until connection closes
    """

    # Create a TCP server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((listen_host, listen_port))
        server_sock.listen(1)

        print(f"Listening on {listen_host}:{listen_port}...")
        print(f"Will write received data to: {output_filename}")

        # Accept a single connection (for testing)
        conn, addr = server_sock.accept()
        print(f"Accepted connection from {addr}")

        event_count = 0

        # Open the output file in 'wb' mode
        with conn, open(output_filename, "wb") as out_f:
            while True:
                # --- Step 1: Read 4 bytes => eventSize ---
                size_data = recv_exactly(conn, 4)
                if not size_data:
                    # No more data => likely sender closed connection
                    break

                # Unpack eventSize (little-endian 32-bit int)
                event_size = struct.unpack("<I", size_data)[0]
                if event_size < 4:
                    print(f"Invalid event size {event_size}, stopping.")
                    break

                # --- Step 2: Read the rest of the event (event_size - 4) ---
                event_rest = recv_exactly(conn, event_size - 4)
                if not event_rest:
                    print("Connection closed or error reading event body, stopping.")
                    break

                # Combine into the full event
                full_event = size_data + event_rest

                # --- Step 3: Write to file ---
                out_f.write(full_event)

                event_count += 1
                print(f"Received event #{event_count} (size={event_size} bytes).")

        print(f"Finished receiving. Total events: {event_count}")


def recv_exactly(conn, num_bytes):
    """
    Helper to receive exactly 'num_bytes' from the connection.
    Returns the bytes if successful, or None/empty if there's a disconnect.
    """
    chunks = []
    bytes_remaining = num_bytes

    while bytes_remaining > 0:
        chunk = conn.recv(bytes_remaining)
        if not chunk:
            # Remote end closed connection or error
            return None
        chunks.append(chunk)
        bytes_remaining -= len(chunk)

    return b"".join(chunks)


if __name__ == "__main__":
    receive_gdc_file_over_tcp(
        output_filename="received_run_14711.ldc1next.rd",
        listen_host="0.0.0.0",
        listen_port=12345
    )

