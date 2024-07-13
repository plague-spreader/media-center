#!/usr/bin/env python

import subprocess
import threading
import argparse
import pathlib
import socket

def send_str(conn: socket.socket, to_send: str):
    conn.send(f'{to_send}\r\n'.encode("utf-8"))

def play_video(video_file):
    pass

def handle_sent_data(conn: socket.socket, addr: tuple, data: str):
    to_send = "Invalid command"
    action = None
    args = None

    cmd, *args = data.split()
    if cmd == "PLAY":
        pass

    print(f'Sending to "{addr}": "{to_send}"')
    send_str(conn, to_send)
    if action is not None:
        print(f'Executing action "{action}"', end="")
        if args is not None:
            print(f' with args "{args}"')
            action(*args)
        else:
            print()
            action()

def handle_connection(conn: socket.socket, addr: tuple):
    with conn:
        print("Accepted connection by", addr)
        send_str(conn, f'Hello "{addr}"')
        while True:
            data = conn.recv(1024)
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError:
                print(f"Received invalid UTF-8 data {data}")
                send_str(conn, "Invalid data")
                continue

            if data:
                print(f'{addr} sent: {repr(data)}')
                handle_sent_data(conn, addr, data)
            else:
                print(f'Connection closed by "{addr}"')
                break

def main(args: argparse.Namespace):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((args.bind_host, args.bind_port))
            print(f'Listening on "{args.bind_host}:{args.bind_port}"')
            print("Send SIGINT to close the program")
            while True:
                sock.listen(1)
                conn_addr = sock.accept()
                t = threading.Thread(target=handle_connection, args=conn_addr)
                t.start()
    except KeyboardInterrupt:
        print("Bye")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=pathlib.Path)
    ap.add_argument("--bind-host", default="")
    ap.add_argument("--bind-port", type=int, default=2999)
    ap.add_argument("--test-mode", action="store_true")
    main(ap.parse_args())
