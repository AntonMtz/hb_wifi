'''
Script. Client that represent to estetoscope service.If this client received the message "action:takeEstetoscope" so  Estetoscope routine run.
@author A.Mtz
History.
CREATED.2019/04/06. Release initial. By A.Mtz.
'''
import socket 
import select 
import sys 

import subprocess
import requests
import datetime
import time
import urllib2, urllib

#Cam libraries
from picamera import PiCamera
from time import sleep
import os
import psutil
import signal
#import subprocess

import json
camera=""  
registerInDictionary=False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
    print "Correct usage: script, IP address, port number"
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 

def obtenerFecha():
    now = datetime.datetime.now()
    #print "Fecha completa>"+str(now)
    dia = now.day
    mes = now.month
    anno = now.year
    hora = now.hour
    minuto = now.minute
    segundo = now.second

    return str(dia)+"_"+str(mes)+"_"+str(anno)+"_"+str(hora)+"_"+str(minuto)+"_"+str(segundo)

  
"""
Set in json format a string to send.
Created.2019/03/11
"""
def setJsonFormat(device,message):

    setJsonFormat= "{" + '"origin":"'+device+ '","destination":"App", "category":"notification","message":"' + message  + '"} '+ "\n" ;
    return setJsonFormat;  



while True: 
  
    # maintains a list of possible input streams 
    sockets_list = [sys.stdin, server] 
    """ There are two possible input situations. Either the 
    user wants to give  manual input to send to other people, 
    or the server is sending a message  to be printed on the 
    screen. Select returns from sockets_list, the stream that 
    is reader for input. So for example, if the server wants 
    to send a message, then the if condition will hold true 
    below.If the user wants to send a message, the else 
    condition will evaluate as true"""
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
    duracion=str(10)
    recordNameFull="anto"+obtenerFecha()+".wav"
    for socks in read_sockets: 
        if socks == server: 

            #Send message to register dictionary in server HB
            if(registerInDictionary==False):
                socks.send("{" +'"origin":"Estetoscope","destination":"Server", "category":"register","message":"Im estetoscope"} '+ "\n"  )
                registerInDictionary=True  

            message = socks.recv(2048) 
            print message
            if "action:takeEstetoscope"  in message:  
                    
                    socks.send(setJsonFormat("Estetoscope","Comenzando rutina de estetoscopio") ) 
                    print("<Estetoscope>Comenzando rutina de estetoscopio")
                    try:
                        try:
                            socks.send(setJsonFormat("Estetoscope","Grabando") )
                            s = subprocess.check_output("arecord -d "+duracion+" /home/pi/HB/"+recordNameFull+"  -f S16_LE -c 1 -r 44100  -D sysdefault:CARD=1",stderr=subprocess.STDOUT,shell=True)    
                            print "Grabando en tarjeta 0"
  
                        except subprocess.CalledProcessError as e:
                            socks.send(setJsonFormat("Estetoscope","Grabando") )
                            s = subprocess.check_output("arecord -d "+duracion+" /home/pi/HB/"+recordNameFull+"  -f S16_LE -c 1 -r 44100  -D sysdefault:CARD=2",stderr=subprocess.STDOUT,shell=True)    
                            print "Grabando en tarjeta 1"  
                        
                    except subprocess.CalledProcessError as e:
                        print("<Reader>Algo salio mal en la lectura.") 
                        socks.send(setJsonFormat("Estetoscope","Algo salio mal en la lectura.") ) 

        else: 
            message = sys.stdin.readline() 
            message=message[:-1]
            server.send(setJsonFormat("Estetoscope",message))
            sys.stdout.write("<Estetoscope>") 
            sys.stdout.write(message) 
            sys.stdout.flush() 
server.close() 

