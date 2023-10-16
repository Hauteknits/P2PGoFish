#TODO: Pretty much done for the milestone, but the whole game needs to be implemented

import socket
import sys
from io import StringIO
import time
import multiprocessing
import threading
import re
from random import shuffle
from copy import deepcopy
from os import system, name


if len(sys.argv) != 5:
	print("Error: program must be launched with the following format: python player.py <server-ip> <m-port> <r-port> <p-port>")
	print(sys.argv)
	exit(1)
UDP_IP = sys.argv[1]
UDP_PORT = 37009
MPORT = int(sys.argv[2])
RPORT = int(sys.argv[3])
PPORT = int(sys.argv[4])

deckDefault = [chr(i) for i in range(ord('A'), ord('Z') + 1)] + [chr(i) for i in range(ord('a'), ord('z') + 1)]
regexs = [r'^(?=.*A)(?=.*N)(?=.*a)(?=.*n)', r'^(?=.*B)(?=.*O)(?=.*b)(?=.*o)', r'^(?=.*C)(?=.*P)(?=.*c)(?=.*p)', r'^(?=.*D)(?=.*Q)(?=.*d)(?=.*q)', r'^(?=.*E)(?=.*R)(?=.*e)(?=.*r)', r'^(?=.*F)(?=.*S)(?=.*f)(?=.*s)', r'^(?=.*G)(?=.*T)(?=.*g)(?=.*t)', r'^(?=.*H)(?=.*U)(?=.*h)(?=.*u)', r'^(?=.*I)(?=.*V)(?=.*i)(?=.*v)', r'^(?=.*J)(?=.*W)(?=.*j)(?=.*w)', r'^(?=.*K)(?=.*X)(?=.*k)(?=.*x)', r'^(?=.*L)(?=.*Y)(?=.*l)(?=.*y)', r'^(?=.*M)(?=.*Z)(?=.*m)(?=.*z)']
letterGroups = [['A', 'N', 'a', 'n'], ['B', 'O', 'b', 'o'], ['C', 'P', 'c', 'p'], ['D', 'Q', 'd', 'q'], ['E', 'R', 'e', 'r'], ['F', 'S', 'f', 's'], ['G', 'T', 'g', 't'], ['H', 'U', 'h', 'u'], ['I', 'V', 'i', 'v'], ['J', 'W', 'j', 'w'], ['K', 'X', 'k', 'x'], ['L', 'Y', 'l', 'y'], ['M', 'Z', 'm', 'z']]
deck = None
players = []
username = ""

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
			if dataArr[0] == "registered":
				q.put(dataArr[1])
				username = dataArr[1]
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

	global username
	global deck
	global players
	username = q.get()
	#			print(username)
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
	#			pPlayers()
	#setup socket
	rp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rp.bind(("",PPORT))
	psend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clearScreen()
	myHand = None
	if isHost:
		#shuffle deck
		deck = deepcopy(deckDefault)
		shuffle(deck)
		#deal cards
			#1, deal each players their cards locally
		playerDecks = []
		for i in range(len(players)):
			count = 5
			tempDeck = ""
			if len(players) <= 3:
				count = 7
			for n in range(count):
				tempDeck += deck.pop(0)
			playerDecks.append(tempDeck)
			#2, send resulting deck and player's cards to them
		#host deck config
		myHand = list(playerDecks.pop(0))
		time.sleep(.2)
		for i in range(1,len(players)):
			message = playerDecks.pop(0) + " " + ''.join(deck)
			print(message,players[i].ip, players[i].pPort,sep=" ")
			psend.sendto(bytes(message,'utf-8'), (players[i].ip, int(players[i].pPort)))
		#start game
	else:
		data, addr = rp.recvfrom(1024)
		data = data.decode('utf-8').split(' ')
		myHand = list(data[0])
		deck = list(data[1])

	###The actual game###
	turn = 0
	deckSize = len(deck)
	whenTurn = -1
	for i in range(len(players)):
		if players[i].player == username:
			whenTurn = i
	playerBooks = ['' for _ in range(len(players))]
	while 1:
		rp.settimeout(None)
		sys.stdin.flush()
		#render the screen
		renderScreen(playerBooks, myHand)
		#wait to recieve a message OR wait to send a message and wait
		#if your turn
		if turn%3 == whenTurn:

			#check if you have a book
			joinedHand = ''.join(myHand)
			stdin = open(0)
			matched = False
			for i in range(len(regexs)):
				r = regexs[i]
				match = re.search(r, joinedHand)
				if match:
					matched = True
					deletionArr = letterGroups[i]
					for d in deletionArr:
						myHand.remove(d)
					playerBooks[whenTurn]+= chr(i+65)
					msg = str(turn) + " " + str(deckSize) + " BOOK " + chr(i+65)
					for n in range(len(players)):
						if n == whenTurn:
							continue
						psend.sendto(bytes(msg,'utf-8'), (players[n].ip, int(players[n].pPort)))
					break
			if matched:
				continue
		#Prompt for command bc MY turn
			#ask player for card OR draw card if empty
			#Draw card
			if len(myHand) == 0:
				#if decksize=0, turn++
				if deckSize == 0:
					turn+=1
					msg = str(turn) + " " + str(deckSize) + " ET"
					psend.sendto(bytes(msg,'utf-8'), (players[nextPlayer(whenTurn)].ip, int(players[nextPlayer(whenTurn)].pPort)))
				#else, deckSize--
				else:
					myHand.append(deck.pop(0))
					deckSize -= 1
			else:
			#Ask for card
				while 1:
					sys.stdout.write("Ask for a card <player> <card (A-K)>: ")
					sys.stdout.flush()
					query = stdin.readline()
					query = query.split(" ")
					if len(query) != 2:
						print("Invalid format!")
						time.sleep(1)
						continue
					#Make sure valid Card && make sure card is in hand, otherwise reprompt
					num = -1
					try:
						num = int(query[1])
						if num < 2 or num > 10:
							print("That is an invalid card!")
							time.sleep(1)
							continue
						
					except ValueError: #Is a letter
						ltr = query[1].rstrip().upper()
						print(ltr)
						print(len(ltr))
						match ltr:
							case "A":
								num = 1
							case "J":
								num = 11
							case "Q":
								num = 12
							case "K":
								num = 13
							case _:
								print("That is an invalid card!")
								time.sleep(1)
								continue
					index = num-1
					valid = False
					group = letterGroups[index]
					for c in group:
						if c in myHand:
							valid = True
							break
					if not(valid):
						print("You can only ask for cards you have!")
						time.sleep(1)
						continue

					#ask player for card
					pAsking = None
					for i in range(len(players)):
						if players[i].player == query[0]:
							if i == whenTurn:
								print("You cant ask yourself for a card!")
								time.sleep(1)
								break
							pAsking = players[i]
					if pAsking is None:
						print("Unknown player!")
						time.sleep(1)
						continue
					msg = str(turn)+" "+str(deckSize)+" REQ "+ str(index)
					psend.sendto(bytes(msg, 'utf-8'), (pAsking.ip, int(pAsking.pPort)))
					#await response
					data2, addr2 = rp.recvfrom(1024)
					data2 = data2.decode('utf-8').split(" ")
					turnResp = data2.pop(0)
					deckSizeResp = data2.pop(0)
					
					#If get card, add to deck, do not update turn variable
					if data2[0] == "REP":
						data2.pop()
						data2.pop(0)
						for c in data2:
							myHand.append(c)
						break
					#Else, draw card, if get requested card, deckSize--. If not, deckSize--, turn++, if deckSize = 0, turn++
					else:
						print("Go Fish!!")
						if deckSize == 0:
							print("No more cards left to draw!")
							time.sleep(1)
							turn+=1
							msg = str(turn)+" "+str(deckSize)+" ET"
							psend.sendto(bytes(msg,'utf-8'),(players[nextPlayer(whenTurn)].ip, int(players[nextPlayer(whenTurn)].pPort)))
							break
						deckSize -= 1
						drawnCard = deck.pop(0)
						myHand.append(drawnCard)
						if getNum(decodeCard(drawnCard)) == query[1]:
							print("You drew what you were asking for!:",decodeCard(drawnCard),"Go again!",sep=" ")
							time.sleep(1)
							break
						else:
							print("You drew",decodeCard(drawnCard),sep=" ")
							time.sleep(1)
							turn+=1
							msg = str(turn)+" "+str(deckSize)+" ET"
							psend.sendto(bytes(msg,'utf-8'),(players[nextPlayer(whenTurn)].ip, int(players[nextPlayer(whenTurn)].pPort)))
							break



					
				
		else:
			#wait for message
			print("Waiting for turn...")
			data, addr = rp.recvfrom(1024)
			data = data.decode('utf-8').split(" ")
			time.sleep(0.1)
			print(data)
			#turn = <turn>
			turn = int(data.pop(0))
			#remove (deckSize - <deck_size>) amount of cards from deck
			deckDiff = deckSize - int(data[0])
			for i in range(deckDiff):
				deck.pop(0)
			deckSize = int(data.pop(0))
			#SWITCH:
			match data[0]:
				#ET - Do nothing (loop again)
				case "ET":
					print("")

				#REQ - Query and respond with REP or GOFISH
				case "REQ":
					#toRemove = []
					toSend = ""
					group = letterGroups[int(data[1])]
					for c in group:
						for i in range(len(myHand)):
							if myHand[i] == c:
								toSend += c + " "
								myHand.pop(i)
								break
					if toSend == "":
						msg = str(turn) + " " + str(deckSize) + " GOFISH"
						psend.sendto(bytes(msg,'utf-8'),(players[turn%len(players)].ip, int(players[turn%len(players)].pPort)))
					else:
						msg = str(turn) + " " + str(deckSize) + " REP " + toSend
						psend.sendto(bytes(msg,'utf-8'),(players[turn%len(players)].ip, int(players[turn%len(players)].pPort)))

				#BOOK - Update Books
				case "BOOK":
					updatingPlayer = turn%3
					playerBooks[updatingPlayer] += data[1]

				#GAMEOVERWINNER - Process Winner
				case "GAMEOVERWINNER":
					turn += 1
					msg = str(turn) + " " + str(deckSize) + " GAMEOVERWINNER "+data[1]
					psend.sendto(bytes(msg,'utf-8'), (players[turn%len(players)].ip, int(players[turn%len(players)].pPort)))
					#if host, send game over to manager
					if isHost:
						msg = str(mPort) + " "+str(rPort) + " " + str(pPort) + " end " + username
						psend.sendto(bytes(msg, 'utf-8'), (UDP_IP, UDP_PORT))
					print("Game Over!",data[1],"won the game!",sep=" ")
					input("Press any key to continue...")
					exit(0)



def cliExits(pCli, pInt):
	pCli.join()
	pInt.terminate()
def intExits(pCli, pInt):
	pInt.join()
	pCli.terminate()
def nextPlayer(whenTurn):
	global players
	if whenTurn == len(players)-1:
		return 0
	else:
		return whenTurn+1
def renderScreen(playerBooks, myHand):
	global username
	global deck
	global players
	clearScreen()
	#Print Remaining Deck
	print("Deck("+str(len(deck))+"): " + '*'*len(deck))
	#print player books

	for i in range(len(playerBooks)):
		print(players[i].player + ": ",end="")
		book = list(playerBooks[i])
		for i in book:
			print(getNum(decodeCard(i)) + "\'s ",end="")
		print("")
	#\n - don't need to print since will carry over from the decks
	#print your hand
	print("Your Hand: ",end="")
	#print(myHand)
	for c in myHand:
		print(decodeCard(c) + " ",end="")
	print("")

def pPlayers():
	for x in players:
		print(x.player, x.ip, x.mPort, x.rPort, x.pPort, sep=" ")
def decodeCard(card):
	lookup = ['AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '10C', 'JC', 'QC', 'KC', 'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '10S', 'JS', 'QS', 'KS', 'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '10H', 'JH', 'QH', 'KH', 'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '10D', 'JD', 'QD', 'KD']
	return lookup[deckDefault.index(card)]

def getNum(card):
	cl = list(card)
	cl.pop()
	return ''.join(cl)


def clearScreen():
	if name == 'nt':
		_ = system('cls')
	else:
		_ = system('clear')

# Setting up threads or processes idk which but the functionality is there
if __name__ == "__main__":
	clearScreen()
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
	
