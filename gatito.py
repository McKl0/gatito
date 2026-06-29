# By Anghelo Villalba
# Inspired from the Python for hackers book by Black Hat
# I do not consent to this code being used maliciously
# This code has been made solely for academic purposes and penetration testing environments
# The main objective of gatito is to be a lightweight more portable netcat version for computers without direct access to internet
# By Anghelo Villalba
# Inspired from the Python for hackers book by Black Hat
# I do not consent to this code being used maliciously
# This code has been made solely for academic purposes and penetration testing environments
# The main objective of this code is to be a lightweight, portable gatito version for computers without direct access to internet
import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
        # Clean up the command before trying to run it.
        cmd = cmd.strip()
        if not cmd:
                return ''
        try:
                output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
                # Return command errors to the caller instead of killing the session.
                output = e.output
        except FileNotFoundError as e:
                output = str(e).encode()
        return output.decode(errors='replace')


class Gatito:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # Create a TCP socket and allow quick reuse of the same address.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send(self):
        # Connect to the target host and send any initial input from stdin.
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    if not data:
                        break
                    response += data.decode(errors='replace')
                    if recv_len < 4096:
                        break
                if response:
                    print(response, end='')
                # Keep reading commands from the local user until interrupted.
                buffer = input('> ')
                buffer += '\n'
                self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("Session terminated keyboard interrupt")
            self.socket.close()
            sys.exit()

    def listen(self):
        # Start listening and handle each incoming connection in a new thread.
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                        target=self.handle, args=(client_socket,)
                    )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            # Run a single command and send its output back to the client.
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            # Receive file data until the client closes the connection.
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:
            # Keep a remote command shell open for this client.
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    # Read until the remote user sends a complete command line.
                    while '\n' not in cmd_buffer.decode(errors='replace'):
                        chunk = client_socket.recv(64)
                        if not chunk:
                            return
                        cmd_buffer += chunk
                    response = execute(cmd_buffer.decode(errors='replace'))
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

    def run(self):
        # Choose server mode or client mode based on the command-line options.
        if self.args.listen:
            self.listen()
        else:
            self.send()


if __name__ == '__main__':
        # Usage examples:
        # - Use -l to listen for incoming connections.
        # - Use -c with -l to provide a remote command shell.
        # - Use -u with -l to save uploaded data to a file.
        # - Without -l, the script connects to the target as a client.
        parser = argparse.ArgumentParser(description='Gatito ', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example gatito.py -t 192.168.1.100 -p 7777 -l -c # command shell\nExample gatito.py -t 192.168.1.100 -p 7777 -l -u=test.txt # upload a file \nExample gatito.py -t 192.168.1.100 -p 7777 -l -e="cat /etc/passwd" # execute command\nExample echo 'abc' | ./gatito.py -t 192.168.1.100 -p 7777 # echo text to server port 123 \n Example gatito.py -t 192.168.1.100 -p 7777 # connect to server'''))
        # Command-line flags control the target, port, and selected mode.
        parser.add_argument('-c', '--command', action='store_true', help='command shell')
        parser.add_argument('-e', '--execute', help='execute command')
        parser.add_argument('-l', '--listen', action='store_true', help='listen')
        parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
        parser.add_argument('-t', '--target', default='192.168.1.100', help='specified IP address')
        parser.add_argument('-u', '--upload', help='upload file')
        args = parser.parse_args()
        if args.listen:
                buffer = ''
        else:
                # Read piped input so it can be sent immediately after connecting.
                buffer = sys.stdin.read()
        nc = Gatito(args, buffer.encode())
        nc.run()
