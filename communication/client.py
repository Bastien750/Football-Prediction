import socket

HEADER = 64
PORT = 5050 # The port that we are going to listen
FORMAT = "utf-8" # The format in which we are going to decode our client message
DISCONNECT_MESSAGE = "!DISCONNECT" # Message when the user disconnect from the server
SERVER = "192.168.1.31" # The server that we want to listening
ADDR = (SERVER, PORT) # Define the address that our client is gonna use to connect

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR) # Establish the connexion with the server

def send(msg):
    message = msg.encode(FORMAT) # We are encoding our message for it to be in bytes format
    msg_length = len(message) # The size in bytes
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))# Here we add the byte representation for a blank to be sure that we send the right number of bytes
    client.send(send_length) # Here is our complement of message
    client.send(message) # Here is our message

send("Hello World !")