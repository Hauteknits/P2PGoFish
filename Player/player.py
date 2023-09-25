#TODO: Pretty much done for the milestone, but the whole game needs to be implemented

import socket
import sys
if len(sys.argv) != 5:
	print("Error: program must be launched with the following format: python player.py <server-ip> <m-port> <r-port> <p-port>")
	print(sys.argv)
	exit(1)
UDP_IP = sys.argv[1]
UDP_PORT = 37009
MPORT = int(sys.argv[2])
RPORT = int(sys.argv[3])
PPORT = int(sys.argv[4])



sserv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rm = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rm.bind(("",MPORT))
rm.settimeout(5)
while 1:
	command = input("$: ")
	message = str(MPORT) + " " + str(RPORT) + " " + str(PPORT) + " " + command
	sserv.sendto(bytes(message,'utf-8'), (UDP_IP, UDP_PORT))
	try:
		data, addr = rm.recvfrom(1024)
	except socket.timeout:
		print("Error: Connection timeout from manager. (Hint: verify server IP?)\n")
		exit(1)
	data = data.decode('utf-8')
	print(data)
