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
                socks.send("{" +'"origin":"Reader","destination":"Server", "category":"register","message":"Im reader"} '+ "\n"  )
                registerInDictionary=True  

            message = socks.recv(2048) 
    
            print message
            if "takePic"  in message: 
                    
                    #Decode json 
                    dataJson = json.loads(message)

                    #Get datas from test
                    #kind_Test=dataJson["datas"]["kind"];
                    id_User=dataJson["message"]["datas"]["idUser"];

                    print (dataJson)
                    print ("User: "+id_User)

                    socks.send(setJsonFormat("Reader","Comenzando rutina de reader") )
                    print(setJsonFormat("Reader","Comenzando rutina de reader"))
                    try:
                           
                        if  camera == '':
                            camera=PiCamera()
                        camera.resolution =(1024,1024) #1080   972     
                        camera.start_preview(alpha=255)
                        #camera.framerate = 5
                        camera.sharpness = 10    #-100   100
                        camera.contrast = 40     #-100   100
                        camera.brightness = 50  #0   100
                        camera.saturation = 40  #-100   100
                        camera.ISO = 250        #0   1600          
                        camera.video_stabilization = False
                        camera.exposure_compensation = 15  #-25   25
                        camera.exposure_mode = 'backlight'
                        camera.meter_mode = 'average'
                        camera.awb_mode = 'off'
                        camera.awb_gains = 1.7
                        camera.image_effect = 'none'
                        camera.color_effects = None
                        camera.rotation = 0 
                        camera.hflip = False
                        camera.vflip = False
                        camera.crop = (0.0, 0.0, 1.0, 1.0)
                            
                        sleep(2)#Show the pic in the HealthBox 2 seconds
                        camera.stop_preview()
                        now=getDateNow()
                        camera.capture(id_User+"_"+now+".jpg")
                        print ("Name to save > " + id_User+"_"+now+".jpg")

                        print("<Reader>Muestra gurdada en HB") 
                        socks.send(setJsonFormat("Reader","Muestra guardada en HB.") )
                    except subprocess.CalledProcessError as e:
                        print("<Reader>Algo salio mal en la lectura.") 
                        socks.send(setJsonFormat("Reader","Algo salio mal en la lectura.")) 
             


        else: 
            message = sys.stdin.readline() 
            message=message[:-1]
            server.send(setJsonFormat("reader",message))
            sys.stdout.write("<Reader>") 
            sys.stdout.write(message) 
            sys.stdout.flush() 
server.close() 

