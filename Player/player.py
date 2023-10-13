#TODO: Pretty much done for the milestone, but the whole game needs to be implemented

import socket
import sys
from io import StringIO
import time
import multiprocessing

if len(sys.argv) != 5:
	print("Error: program must be launched with the following format: python player.py <server-ip> <m-port> <r-port> <p-port>")
	print(sys.argv)
	exit(1)
UDP_IP = sys.argv[1]
UDP_PORT = 37009
MPORT = int(sys.argv[2])
RPORT = int(sys.argv[3])
PPORT = int(sys.argv[4])

players = []

class Player:
	def __init__(self, player, ip, mPort, rPort, pPort):
		self.player = player
		self.ip = ip
		self.mPort = mPort
		self.rPort = rPort
		self.pPort = pPort





def waitForGame():
	rr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rr.bind(("",RPORT))
	data, addr = rr.recvfrom(1024)

def cli():
	sserv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rm = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rm.bind(("",MPORT))
	rm.settimeout(5)
	stdin = open(0)
	while 1:
		print("?: ", end='')
		command = stdin.readline()
		if command == "recvfromr":
			print("UYEAYH BOYYS")
			break
		message = str(MPORT) + " " + str(RPORT) + " " + str(PPORT) + " " + command
		sserv.sendto(bytes(message,'utf-8'), (UDP_IP, UDP_PORT))
		try:
			data, addr = rm.recvfrom(1024)
			dataArr = data.decode('utf-8').split(" ")
			if dataArr[0] == "startnewgame":
				buildPlayers(sserv, rm, int(dataArr[1]))
		except socket.timeout:
			print("Error: Connection timeout from manager. (Hint: verify server IP?)\n")
			exit(1)
		data = data.decode('utf-8')
		print(data)
def buildPlayers(sserv, rm , count):
	sserv.sendto(bytes("secondstartotheright",'utf-8'), (UDP_IP,UDP_PORT))
	for x in range(count):
		try:
			data, addr = rm.recvfrom(1024)
			dataArr = data.decode('utf-8').split(" ")
			if dataArr[0] != x:
				print("Warning: player count mismatch, manually verify")
			tempPlayer = player(dataArr[1],dataArr[2],dataArr[3],dataArr[4],dataArr[5])
			players.append(tempPlayer)
		except socket.timeout:
			print("Error: timeout from manager while recieving players. (The programmer f**ked something up)")
			break
	sserv.sendto(bytes("straightontillmorning", 'utf-8'), (UDP_IP, UDP_PORT))

def game():
	#setup socket
	rp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rp.bind(("",PPORT))
	
	#local variables
	gameInfo = None

	exit(0)


# Setting up threads or processes idk which but the functionality is there
if __name__ == "__main__":
	tCli = multiprocessing.Process(target=cli)
	tInt = multiprocessing.Process(target=waitForGame)
	tGame = multiprocessing.Process(target=game)
	# Starts 2 processes, one of which runs the CLI and the other that waits for a connection on the R port
	# Once a request to initiate a game is recieved, tInt terminates and will kill tCli, which will then go into the game function
	while(1)
		tInt.start()
		tCli.start()
		tInt.join() #exit code checking somewhere in here would be good
		tCli.terminate()
		print("You are being connected to a game, please wait while the session is setup...")
		tGame.start()
		tGame.join()