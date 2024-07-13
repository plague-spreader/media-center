# media-center

A VERY simple media center server in Python. It enables video reproduction on
a remote device while controlling it via this script.

## Usage

Run

    ./media_center.py <folder where the videos are> [--bind-host <host>]
    [--bind-port <port>] [--play-script "<script to use>"]

Then connect to that host:port (either use telnet or netcat) and type one of
these commands:

- `PLAY <video file 1> ... <video file n>`
  As the command name suggests, play the n video files

- `PLAY_NO_PREFIX `<video file 1> ... <video file n>`
  Just as above but don't prepend any prefix, useful for youtube videso
  (are there any other use cases? 🤔)

- `STOP`
  Stop all videos

To stop the server just send SIGINT
