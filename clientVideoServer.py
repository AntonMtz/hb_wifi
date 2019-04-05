'''
Script. Client that represent to reader service.If this client received the message "action:takePic" so  Reader routine run.
@author A.Mtz
History.
    CREATED.2019/02/27. Release initial. By A.Mtz.
Execution.
    @console. python clientREADER.py IP_HEALTHBOX PORT 
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
import threading

import time
registerInDictionary=False
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
    print "Correct usage: script, IP address, port number"
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 
try:
    import Queue as queue
except ImportError:
    # Python 3
    import queue

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


def output_reader():


    comando12 = "ffserver    -f /etc/ffserver.conf & ffmpeg -r 25    -framerate 25   -s 640X480 -f video4linux2 -i /dev/video0 -threads 2  -r 25  http://localhost:8091/feed1.ffm"
    proc = subprocess.Popen(comando12, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)


    out, err = proc.communicate()
                         
    if not err:
        print('--No errors--\n')
        socks.send(setJsonFormat("VideoServer","Corriendo servidor")) 
    else:
        # print('--Error--\n', err.decode())
        print('--Errors--\n')
        socks.send(setJsonFormat("VideoServer","Ocurrio un error en la camara de exploracion")) 

                            



"""
Return actual moment with format: yyyy_mm_dd_hh_mm_ss
"""
def getDateNow():
    now = datetime.datetime.now()
    #print "Fecha completa>"+str(now) 
    dia = setZeroFormat(str(now.day))
    mes = setZeroFormat(str(now.month))
    anno = setZeroFormat(str(now.year))
    hora = setZeroFormat(str(now.hour))
    minuto =setZeroFormat (str(now.minute))
    segundo = setZeroFormat(str(now.second))

    return str(anno)+"_"+str(mes)+"_"+str(dia)+"_"+str(hora)+"_"+str(minuto)+"_"+str(segundo)

"""
Add a zero if a number in format string is less 10
"""
def setZeroFormat(data):
    if(len(data)==1): 
        return "0"+data
    return data


"""
Set in json format a string to send.
Created.2019/03/11
"""
def setJsonFormat(device,message):

    setJsonFormat= "{" + '"origin":"'+device+ '","destination":"App", "category":"Notification","message":"' + message  + '"} '+ "\n" ;
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
  
    for socks in read_sockets: 
        if socks == server: 

            #Send message to register dictionary in server HB
            if(registerInDictionary==False):
                socks.send("{" +'"origin":"VideoServer","destination":"Server", "category":"register","message":"Im videoServer"} '+ "\n"  )
                registerInDictionary=True  

            message = socks.recv(2048) 
    
            print message
            if "startVideoServer"  in message: 
                    
              

                    socks.send(setJsonFormat("VideoServer","Comenzando rutina de video") )
                    print(setJsonFormat("VideoServer","Reproduciendo camara de exploracion"))
                    try:
 
                        """comando11 = "lxterminal --command='/bin/bash --init-file /home/pi/HB/ejecutarServidorRTSP.sh'"

                        procExe = subprocess.Popen(comando11, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                        lastLine=""
                        while procExe.poll() is None:
                            line = procExe.stdout.readline().rstrip()
                            print("Print:" +line);
                            if(len(line)>2):
                                lastLine=line
                        """
                        """
                        lastLine=""

                        comando12 = "ffserver    -f /etc/ffserver.conf & ffmpeg -r 25    -framerate 25   -s 640X480 -f video4linux2 -i /dev/video0 -threads 2  -r 25  http://localhost:8091/feed1.ffm"
 

                        # first a command that works correctly
                        proc = subprocess.Popen(comando12 ,shell=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        out, err = proc.communicate()
                         
                        if not err:
                            print('--No errors--\n')
                        else:
                            # print('--Error--\n', err.decode())
                            socks.send(setJsonFormat("VideoServer","Error en el servidor de video")) 

                            
                        """  



                        outq = queue.Queue()
                        t = threading.Thread(target=output_reader, args=())
                        t.start()
                        
    
  
                    except subprocess.CalledProcessError as e:
                        print("<VideoServer>Algo salio mal en la lectura.") 
                        socks.send(setJsonFormat("VideoServer","Algo salio mal en la lectura.")) 
             


        else:  
            message = sys.stdin.readline() 
            message=message[:-1]
            server.send(setJsonFormat("VideoServer",message))
            sys.stdout.write("<VideoServer>") 
            sys.stdout.write(message) 
            sys.stdout.flush() 
server.close() 

