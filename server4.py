# Python program to implement server side of chat room. 
import socket 
import select 
import sys 
import json
from _thread import *
import traceback

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

# checks whether sufficient arguments have been provided 
if len(sys.argv) != 3: 
	print ("Correct usage: script, IP address, port number")
	exit() 

# takes the first argument from command prompt as IP address 
IP_address = str(sys.argv[1]) 

# takes second argument from command prompt as port number 
Port = int(sys.argv[2]) 

""" 
binds the server to an entered IP address and at the 
specified port number. 
The client must be aware of these parameters 
"""
server.bind((IP_address, Port)) 

""" 
listens for 10 active connections. This number can be 
increased as per convenience. 
""" 
server.listen(10) 

list_of_clients = [] 
my_dict_clients = {}

"""
Variables for Control threads;
"""
id_thread=0 
threads = dict()



def clientthread(conn, addr,idThread): 

	# sends a message to the client whose user object is conn 
	message='{"origin":"Server","destination":"App","category":"Notification", "message":"Se ha establecido enlace correctamente."}'+ "\n"
	byt=message.encode()
	conn.send (byt) #Message to send to client  never change this label




	my_name=""
	isLive=True  
	while isLive==True:  
			try: 
				message = conn.recv(2048) 
				message=message.decode("utf-8") 	
				if message: 

					''' 
					When client_android or client_ios sends a connection request this is accept.
					the client service must send a message "Im" + name client_service.
					If this message is readed this scrip register the ip in dictionary my_dict_clients.
					'''
					print("------------------------");
					print("Message received:");
					print (message)
					print("------------------------");

					#Get destination from message	
					origin=None
					#If category message is "register" so add this to dictionary
					try:
						#Decode json 
						dataJson = json.loads(message)
						if(dataJson["category"]=="register"):
							name_client=dataJson["origin"];
							print ((conn))
							print (type(conn))
							print (type(addr[0]))
							my_dict_clients[name_client] =(addr[0],conn) #Saving ip adress and socket id for ever client in the dictionary. Add 2019/02/27
							print ("Diciiorio")
							print (my_dict_clients[name_client] )
							print ("end Diciiorio")
							print (my_dict_clients)
							print (list_of_clients)
							my_name=name_client
							messageConnection='{"origin":"Server","destination":"App","category":"Notification", "message":"'+name_client +' se ha conectado."}'+ "\n"
							print('SE HA ENVIADO MENSAJE DE CONEXION'+messageConnection)
							broadcast(messageConnection) 
					except:
						print ("Error en registro.")
						origin=None

					'''
					The client_android or client_ios can send a request to specifyc client_device				    
					destination:Reader         #run code in service READER. Take a pic.
					destination:Ecg         #run code in service ECG. Take a ecg.
					destination:Endoscope   #run code in service ENDOSCOPE. Take a endoscope.
					destination:Estetoscope #run code in service ESTETOSCOPE. Take a estetospe.
					All server received all actions but only process if the action is specifically for him.
					'''
					"""
					Verify if a client is live.
					If device is not alive an error message is broadcast.
					"""



					#Get destination from message	
					destination=None
					try: 
						#Decode json 
						dataJson = json.loads(message) 
						print ("Object Json > ")
						print (dataJson)
						destination=dataJson["destination"]
						print("Destination > "+destination)
						sockTemp=my_dict_clients.get(str(destination))
						#Verify if a specific client is alive
						if(sockTemp==None and not ("Server"  in destination)):
						   message='{"origin":"Server","destination":"App","category":"Error", "message": {"code":"200","description":"El lector '+ str(destination)+' no se encuentra habilitado."} }'+ "\n"
						   destination="App"
										
						if "App"  in destination: 
						   sockTemp=my_dict_clients.get('App')
						   if(sockTemp==None):
						   		message='{"origin":"Server","destination":"All","category":"Error", "message": {"code":"001","description":"El cliente APP no se encuentra habilitado."} }'+ "\n"
						   		destination=''#Force to send message to all clients if android device is disconected
										
					except:
						print("Error al decodificar Json")
						destination=""



					"""	if(sockTemp!=None):
							try:
								sockTemp[1].send(""+ "\n") 	
											
							except: 
								message="error:Reader no esta activo" + "\n"  
						else:
						   message="error:Reader no esta activo" + "\n" 
					"""

					"""prints the message and address of the 
					user who just sent the message on the server 
					terminal"""
					
					print ("<" + addr[0] + "> " + message) 

					# Calls broadcast function to send message to all 
					#message_to_send = "<" + addr[0] + "> " + message  + "\n" 
					message_to_send = message  + "\n"
					
					if(destination != ''):
						print ("Enviando mensaje a " + destination)
						broadcastToClient(message_to_send, conn,destination) 
					else:
						broadcast(message_to_send, conn) 

				else: 
					"""message may have no content if the connection 
					is broken, in this case we remove the connection"""
					
					#Delete the id in the dictionary
					print ("Se ha perdio la conexion con " + name_client)
					del my_dict_clients[name_client]

					message='{"origin":"Server","destination":"App","category":"Error", "message": {"code":"201","description":"El lector '+ str(name_client)+' se desconecto. Presiona el boton con el nombre del dispositivo en HB e intenda de nuevo."} }'

					broadcast(message+ "\n")
					print(threads)

					#Close thread 
					threads[idThread].exit() 

			except: 
					isLive=False;

"""Using the below function, we broadcast the message to all 
clients who's object is not the same as the one sending 
the message """
def broadcast(message, connection): 
 
	#Send message only to device registered in the dictionary.

	for key, datas in my_dict_clients.items():
			
			#datas[1] is ip_address, datas[2] is socket_id
			try:
				#datas[1].send( "{" + '"from":"'+key + '","message":' + message  + "} }"+ "\n" )
				print ("Enviando mensaje a ->")
				print (key, datas) 	
				print("sock", datas) 
				datas[1].send(message.encode())			
			except: 
				del my_dict_clients[key]
				print ("Error en el diccionario ->")

	"""
	#Send mesaage to all clients 
	for clients in list_of_clients: 
		if clients!=connection: 
			try: 
				clients.send(message) 
			except: 
				clients.close() 

				# if the link is broken, we remove the client 

				remove(clients) 
	"""


def broadcast(message): 
 
 	#Send message only to device registered in the dictionary.
    
	for key, datas in my_dict_clients.items() :
			
			#datas[1] is ip_address, datas[2] is socket_id
			try:
				#datas[1].send( "{" + '"from":"'+key + '","message":' + message  + "} }"+ "\n" )
				print ("Enviando mensaje a ->")
				print (key, datas )	
				print ( datas[1])
				datas[1].send(message.encode())			
			except: 
				del my_dict_clients[key]
				print ("Error en el diccionario B ->")

"""Using the below function, we broadcast the message to specific
clients """
def broadcastToClient(message, connection,keyDestination): 
 	#Send message only to device registered in the dictionary.
	print ("Entrando en el ciclo.")
	for key, datas in my_dict_clients.items() :
			print ("Nuevo elemento cliente")
			print (key, datas)
			#If name of sockets destination is equal to dictionary element so send the message.
			if(key==keyDestination):
				try:	
					print ("Enviando mensaje a ->")
					print (key, datas) 
					datas[1].send(message.encode())			
				except: 
					del my_dict_clients[key]
					print ("Error en el diccionario btc ->")

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove(connection): 
	if connection in list_of_clients: 
		list_of_clients.remove(connection) 

while True: 

	"""Accepts a connection request and stores two parameters, 
	conn which is a socket object for that user, and addr 
	which contains the IP address of the client that just 
	connected"""
	conn, addr = server.accept() 

	"""Maintains a list of clients for ease of broadcasting 
	a message to all available people in the chatroom"""
	list_of_clients.append(conn) 

	# prints the address of the user that just connected 
	print (addr[0] + " connected")

	# creates and individual thread for every user 
	# that connects 
	try:
		threads[id_thread]=start_new_thread(clientthread,(conn,addr,id_thread))	
		id_thread=id_thread+1;

	except:
		print("Thread did not start.")
		traceback.print_exc()
	 

conn.close() 
server.close() 
