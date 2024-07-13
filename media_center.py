#!/usr/bin/env python

import subprocess
import threading
import argparse
import pathlib
import socket

PLAY_CMD = None
MEDIA_FOLDER = None
PROCESSES = []

def send_str(conn: socket.socket, to_send: object):
    conn.send(f'{to_send}\r\n'.encode("utf-8"))

def play_videos(video_files, folder=None):
    global PLAY_CMD
    video_files_with_media_folder = []
    if folder is None:
        video_files_with_media_folder = video_files[:]
    else:
        for video_file in video_files:
            video_files_with_media_folder.append(folder / video_file)
    proc = subprocess.Popen([*PLAY_CMD, *video_files_with_media_folder])
    PROCESSES.append(proc)
    returnCode = proc.wait()
    return returnCode

def stop_videos():
    global PROCESSES
    for proc in PROCESSES:
        proc.terminate()
    return 0

def list_files(conn: socket.socket, folder: pathlib.Path):
    to_send = []
    for file in folder.rglob("*"):
        to_send.append(file.name)
    send_str(conn, to_send)
    return 0

def handle_sent_data(conn: socket.socket, addr: tuple, data: str):
    to_send = "Invalid command"
    action = None
    args = None

    cmd, *args = data.split()
    kwargs = None
    if cmd == "PLAY":
        action = play_videos
        args = [args]
        kwargs = {"folder": MEDIA_FOLDER}
    elif cmd == "STOP":
        action = stop_videos
        args = None
        kwargs = None
    elif cmd == "PLAY_NO_PREFIX":
        action = play_videos
        args = [args]
        kwargs = None
    elif cmd == "LS":
        action = list_files
        args = [conn, MEDIA_FOLDER]
        kwargs = None

    print(f'Sending to "{addr}": "{to_send}"')
    if action is not None:
        print(f'Executing action "{action.__name__}"', end="")
        if args is None and kwargs is None:
            print()
            return_code = action()
        elif args is not None and kwargs is not None:
            print(f' with args "{args}" and kwargs "{kwargs}"')
            return_code = action(args, **kwargs)
        elif args is not None:
            print(f' with args "{args}"')
            return_code = action(args)
        elif kwargs is not None:
            print(f' with kwargs "{kwargs}"')
            return_code = action(**kwargs)
        # no elses, all 2**2 cases are covered

        if return_code == 0:
            to_send = "OK"
        else:
            to_send = f"Error with code {return_code}"
    send_str(conn, to_send)

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
    global PLAY_CMD, MEDIA_FOLDER
    PLAY_CMD = args.play_script.split()
    MEDIA_FOLDER = args.media_folder

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
    ap.add_argument("media_folder", type=pathlib.Path)
    ap.add_argument("--bind-host", default="")
    ap.add_argument("--bind-port", type=int, default=2999)
    ap.add_argument("--play-script", default="mpv")
    main(ap.parse_args())
