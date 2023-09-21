import socket

UDP_IP = "localhost"
UDP_PORT = 41009
MESSAGE = "query players"



sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(bytes(MESSAGE,'utf-8'), (UDP_IP, UDP_PORT))