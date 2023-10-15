#TODO: Implement return messages to clients; Implement Proper windows termination

import socket
import sys
import random
import time
assert sys.version_info >= (3,10)
class Player:
	def __init__(self, player, ip, mPort, rPort, pPort):
		self.player = player
		self.ip = ip
		self.mPort = mPort
		self.rPort = rPort
		self.pPort = pPort
class Game:
	def __init__(self):
		self.player = []
		self.started = False
		self.finished = False
	def addPlayer(player): #work in progress
		self.games.append(player)

playerDB = []
gameDB = []
port = 37009

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ssend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("listening")
s.bind(("",port))
try:
	while 1:

		#Timeout allows for sigint catching
		s.settimeout(1)
		try:
			data, addr = s.recvfrom(1024)
		except socket.timeout:
			continue
		print("INFO: Incoming connection from",addr,":",data,sep=" ")
		data = data.decode('utf-8')
		x = data.split(" ")
		x[-1] = x[-1].rstrip()
		print(x)
		clientM = int(x.pop(0)) #remove ports from command array
		clientR = int(x.pop(0))
		clientP = int(x.pop(0))
		rep = ""
		match x[0]:
			case "register":
				found = False
				for rp in playerDB: #checks player DB for dupe names
					if rp.player == x[1]:
						found = True
						break
				if found:
					print("ERR: Duplicate Player")
					continue

				np = Player(x[1],x[2],x[3],x[4],x[5])
				playerDB.append(np)
				rep = "registered " + x[1] + " at " + x[2] + " with ports " +x[3] +" "+x[4] +" "+ x[5]
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))
			case "query":
				match x[1]:
					case "players":
						if len(playerDB) == 0:
							rep = "there are no registered users"
						else:
							for player in playerDB:
								rep += player.player + " " + player.ip+ " " +player.mPort+ " " +player.rPort+ " " +player.pPort + "\n"
					case "games":
						rep = "there are no active games"
					case _:
						rep = "ERR: Unknown command"
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))
			case "start":
				#print("starting game from",x[2],"with",x[3],"additional players", sep=" ")

				#Basic idea, Send start game command to requesting player. Individually send each player and pass into local array
					#Select players
					#Send start game
						#wait for client to jump into recPlayer SR
					#send each player [player count, name, ip, m, r, p] Not sleeping in between, going to ACK the responses instead
					#send end command to terminate player's thing
				#TODO: check if enough players
				curPlayer = None
				for rp in playerDB: #checks player DB for dupe names
					if rp.ip == addr[0]:
						curPlayer = rp
						break
				if curPlayer == None:
					rep = "Error: user not registered"
					print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
					ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))
					continue
				else:
					playerDB.remove(curPlayer)

				rep = "startnewgame " + x[2]
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))

				s.settimeout(10)
				try:
					data2, addr2 = s.recvfrom(1024)
					data2 = data2.decode('utf-8')
					if data2 == "secondstartotheright":
						
						random.shuffle(playerDB)
						playerDB.insert(0, curPlayer) #by inserting curPlayer at index 0 again, ensures the user is always sent themselves first

						for i in range(0,int(x[2])):
							rep = [str(i),playerDB[i].player , str(playerDB[i].ip) , str(playerDB[i].mPort),str(playerDB[i].rPort),str(playerDB[i].pPort)]
							rep = " ".join(rep)
							ssend.sendto(bytes(rep, 'utf-8'), (addr[0], clientM))
							data2, addr2 = s.recvfrom(1024)
							data2 = data2.decode('utf-8')
							if data2 != 'neverland':
								break
						data2, addr2 = s.recvfrom(1024)
						data2 = data2.decode('utf-8')
						if data2 != 'straightontillmorning':
							break
						else:
							print("INFO: Transmission complete")
					else:
						continue
				except socket.timeout:
					print("ERROR: No response from client... aborting")
					continue
				#TODO: start game

			case "end":
				#print("ending game",x[1],"by",x[2],sep=" ")
				print("Command not yet implemented")
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))

			case "de-register":
				found = False
				for i in range(len(playerDB)):
					if playerDB[i].player == x[1]:
						playerDB.pop(i)
						found = True
						break
				if found:
					rep = "de-registering " + x[1]
				else:
					rep = "ERR: unknown user"
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))

			case "X": #Depreciated, used for testing with nc
				print("reciving connection from netcat...")
			case _:
				rep = "ERR: Unknown command"
				print("RESPONSE TO",addr[0],"ON PORT",clientM,rep,sep=" ")
				ssend.sendto(bytes(rep,'utf-8'), (addr[0], clientM))
except KeyboardInterrupt:
	print("--SIGINT--")
	print("See you space cowboy...")
	exit(0)