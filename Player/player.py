#TODO: Pretty much done for the milestone, but the whole game needs to be implemented

import socket
import sys
from io import StringIO
import time
import multiprocessing
import threading


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





def waitForGame(q):
	rr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rr.bind(("",RPORT))
	while 1:
		try:
			data, addr = rr.recvfrom(1024) #r-port, count, ring ring
			data = data.decode('utf-8').split(" ")
		except KeyboardInterrupt:
			exit(0)
		if data[2] == "ringring":
			shost = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print("from wait", UDP_IP, UDP_PORT, sep=" ")
			q.put("nothost")
			buildPlayers(shost, rr, int(data[1]),q, addr[0],int(data[0]))
			break
	exit(0)

def cli(q):
	sserv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rm = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rm.bind(("",MPORT))
	rm.settimeout(5)
	stdin = open(0)
	while 1:
		sys.stdout.write("?: ")
		sys.stdout.flush()
		try:
			command = stdin.readline()
		except KeyboardInterrupt:
			exit(0)
		message = str(MPORT) + " " + str(RPORT) + " " + str(PPORT) + " " + command
		sserv.sendto(bytes(message,'utf-8'), (UDP_IP, UDP_PORT))
		try:
			data, addr = rm.recvfrom(1024)
			dataArr = data.decode('utf-8').split(" ")
			if dataArr[0] == "startnewgame":
				buildPlayers(sserv, rm, int(dataArr[1]),q)
				exit(0)
		except socket.timeout:
			print("Error: Connection timeout from manager. (Hint: verify server IP?)\n")
			exit(1)
		data = data.decode('utf-8')
		print(data)

def buildPlayers(sserv, rm , count, q, sIP = UDP_IP, sPort = UDP_PORT):
	print("from build", sIP, sPort, sep=" ")
	sserv.sendto(bytes("secondstartotheright",'utf-8'), (sIP, sPort))
	for x in range(count):
		try:
			data, addr = rm.recvfrom(1024)
			dataArr = data.decode('utf-8').split(" ")
			if int(dataArr[0]) != x:
				print("Warning: player count mismatch, manually verify")
			tempPlayer = Player(dataArr[1],dataArr[2],dataArr[3],dataArr[4],dataArr[5])
			q.put(tempPlayer, block=True)
			players.append(tempPlayer)
			sserv.sendto(bytes("neverland", 'utf-8'), (sIP, sPort))
		except socket.timeout:
			print("Error: timeout from manager while recieving players. (The programmer f**ked something up)")
			break
	sserv.sendto(bytes("straightontillmorning", 'utf-8'), (sIP, sPort))
	pPlayers()

def game(q):
	rr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rsend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rr.bind(("",RPORT))

	temp = q.get()
	isHost = False
	if temp != "nothost":
		isHost = True
		players.append(temp)
	for i in range(q.qsize()):
		players.append(q.get())
	if isHost:
		for it in range(1, len(players)):
			msg = str(RPORT) + " " + str(len(players)) + " ringring"
			rsend.sendto(bytes(msg,'utf-8'), (players[it].ip, int(players[it].rPort)))

			data, addr = rr.recvfrom(1024)
			data = data.decode('utf-8')
			if data == "secondstartotheright":
				for i in range(0,len(players)):
					rep = [str(i),players[i].player , str(players[i].ip) , str(players[i].mPort),str(players[i].rPort),str(players[i].pPort)]
					rep = " ".join(rep)
					rsend.sendto(bytes(rep, 'utf-8'), (addr[0], int(players[it].rPort)))
					data, addr = rr.recvfrom(1024)
					data = data.decode('utf-8')
					if data != 'neverland':
						break
				data, addr = rr.recvfrom(1024)
				data = data.decode('utf-8')
				if data != 'straightontillmorning':
					exit(1)
	pPlayers()
	#setup socket
	# rp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# rp.bind(("",PPORT))


	exit(0)


def cliExits(pCli, pInt):
	pCli.join()
	pInt.terminate()
def intExits(pCli, pInt):
	pInt.join()
	pCli.terminate()

def pPlayers():
	for x in players:
		print(x.player, x.ip, x.mPort, x.rPort, x.pPort, sep=" ")

# Setting up threads or processes idk which but the functionality is there
if __name__ == "__main__":
	q = multiprocessing.Queue()
	pCli = multiprocessing.Process(target=cli, args=(q,))
	pInt = multiprocessing.Process(target=waitForGame, args=(q,))
	pGame = multiprocessing.Process(target=game, args=(q,))

	ce = threading.Thread(target=cliExits, args=(pCli, pInt,))
	ie = threading.Thread(target=intExits, args=(pCli, pInt,))
	# Starts 2 processes, one of which runs the CLI and the other that waits for a connection on the R port
	# Once a request to initiate a game is recieved, tInt terminates and will kill tCli, which will then go into the game function
	try:
		pInt.start()
		pCli.start()
		ce.start()
		ie.start()
		ce.join()
		ie.join()
		print("You are being connected to a game, please wait while the session is setup...")
		pGame.start()
		pGame.join()
	except KeyboardInterrupt:
		pInt.terminate()
		print("\n--SIGINT--")
		exit(0)
	
