# The server code that mimics what Harry's server will operate

import socket
import time
import json
import numpy as np
from InstrumentControl import acquire_waveform

# '127.0.0.1'  # Standard loopback interface address (localhost)
HOST = socket.gethostbyname(socket.gethostname())
PORT = 65433  # Port to listen on (non-privileged ports are > 1023)
HEADER = 64
FORMAT = 'utf-8'
SUCCESS_AND_DISCONNECT_MESSAGE = "!DISCONNECT"
# use 'SERVER_ERROR_DISCONNECT_MESSAGE' if there is a problem with the measuring instruments
SERVER_ERROR_DISCONNECT_MESSAGE = 'SERVER_ERROR_DISCONNECT_MESSAGE'
ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
ERROR = 'ERROR'

# this function will send text responses to the client
# every response will have a header size-so that everything  can be easily decoded on the client side


def respond(msg, server_socket):
    message = msg.encode(FORMAT)  # encode the string into bytes
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))  # padding
    server_socket.sendall(send_length)
    server_socket.sendall(message)

# This is a function that provides plot points in json format, similar to how server H outputs
# This particular example provides points that plot a sinusoid waveform


def plot_sin_points():
    # Get x values of the sine wave
    time = list(np.arange(0, 10, 0.1))
    amplitude = list(np.sin(time))
    json_time = json.dumps(time)
    json_amplitude = json.dumps(amplitude)
    return json_time, json_amplitude


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("Listening to {}".format(HOST))
    s.listen()
    conn, addr = s.accept()  # accept blocks and waits for a connection
    # The with statement is used with conn to automatically close the socket at the end of the block.
    with conn:  # conn is a socket object, addr is a tuple containing the address and port of the client
        print('Connected by', addr)

        msg_length = conn.recv(HEADER).decode(FORMAT)
        print("Length of the message is: {}".format(msg_length))
        if msg_length:
            # we always receive the length first
            msg_length = int(msg_length)
            print('Server H received the message length: {}'.format(msg_length))
            # the actual message of the fixed length
            msg = conn.recv(msg_length).decode(FORMAT)
            data = json.loads(msg)  # we know the message will be json
            print(data)

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------------------------------------------------------------------------#
            # say this is the time it takes to acquire the data from the oscilloscope
            time.sleep(5)

            # at this point, you run your own code and return the results
            # you have to account for errors, so make sure to have if statements and return an ERROR message in case
            # you cannot receive any responses from the instruments

            # We need to agree upon the protocol of how the data is sent:
            # The first set of data will be the oscilloscope input waveform for a particular frequency
            # First, we send the time points
            # Next, we send the amplitude points

            # The second set of data will be the oscilloscope output waveform for a particular frequency
            # First, we send the time points
            # Next, we send the amplitude points

            # The third set of data will be the frequency response-frequency vs gain
            # first we send the frequency range
            # second, we send the gain points

            # The fourth set of data will be the phase response
            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------------------------------------------------------------------------#
            time_vals, amplitude_vals = acquire_waveform()
            # This is an example of the points that are expected
            json_time, json_amplitude = plot_sin_points()

            respond(json_time, conn)
            respond(json_amplitude, conn)
            respond(SUCCESS_AND_DISCONNECT_MESSAGE, conn)


print('connection broken')
