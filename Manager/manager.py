#TODO: Implement return messages to clients; Implement Proper windows termination

import socket
import sys
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
		self.games = []
	def addPlayer(player): #work in progress
		self.

playerDB = []
port = 41009

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ssend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("listening")
s.bind(("",port))
while 1:
	data, addr = s.recvfrom(1024)
	print(addr)
	data = data.decode('utf-8')
	x = data.split(" ")
	x[-1] = x[-1].rstrip()
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
			print("registered",x[1],"at",x[2],"with ports",x[3],x[4],x[5], sep=" ")

		case "query":
			match x[1]:
				case "players":
					if len(playerDB) == 0:
						print("there are no registered users")
					else:
						for player in playerDB:
							print(player.player,player.ip,player.mPort,player.rPort,player.pPort,sep=" ")
				case "games":
					print("matching games!")
				case _:
					print("ERR: Unknown Command")

		case "start":
			#print("starting game from",x[2],"with",x[3],"additional players", sep=" ")
			print("Command not yet implemented")

		case "end":
			#print("ending game",x[1],"by",x[2],sep=" ")
			print("Command not yet implemented")

		case "de-register":
			found = False
			for i in range(len(playerDB)):
				if playerDB[i].player == x[1]:
					playerDB.pop(i)
					found = True
					break
			if found:
				print("de-registering ",x[1])
			else:
				print("Unknown Player")

		case "X": #Depreciated, used for testing with nc
			print("reciving connection from netcat...")
		case _:
			print("ERR: unknown command")
