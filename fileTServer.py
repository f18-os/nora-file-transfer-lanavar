#! /usr/bin/env python3

# Threaded file send server

# import necessary utilities
import sys, re, os, socket, params, time
from threading import Thread
from framedSock import FramedStreamSock
sys.path.append("../lib")

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=False)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        while True:
            print("Starting thread")
            print("trying to receive")
            msg = self.fsock.receivemsg()
            fileName = ""
            fileText = ""
            state = "get filename"
            while msg:
                msg = msg.decode()
                print(msg)
                if (state == "get filename"):
                    fileName = msg
                    state = "get msg"
                elif (state == "get msg"):
                    fileText += msg
                msg = self.fsock.receivemsg()
                
            # Write to file
            oF = open(fileName, "w+")
            for line in fileText:
                oF.write(line)
            oF.close
            print("Done transfering")
            return
                

while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
