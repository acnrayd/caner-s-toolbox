# Simple Python script that sends commands to a TCP server listening on port 33993

import socket

HOST = 'SERVER_IP'  # The server's hostname or IP address
PORT = 33993        # The port used by the server

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = (HOST, PORT)
print('Connecting to {} on port {}...'.format(*server_address))
sock.connect(server_address)

# Send a command to the server
command = 'whoami'  # Change this to the command you want to run
print('Sending command: {}'.format(command))
sock.sendall(command.encode('utf-8'))

# Receive the response from the server
response = sock.recv(1024).decode('utf-8')
print('Received response: {}'.format(response))

# Close the socket
