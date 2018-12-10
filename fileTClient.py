#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import params, os
from framedSock import FramedStreamSock
from threading import Thread
import time
sys.path.append("../lib")


switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)

        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()



    def run(self):
       s = None
       for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

       if s is None:
           print('could not open socket')
           sys.exit(1)

       
       fs = FramedStreamSock(s, debug=debug)
       cF, oF = self.getCommand()
       fT = self.getPayload(cF)
       fs.getLock()
       oF = self.getOutputFile(oF)
       
       fs.sendmsg(oF)   # sending output file
       #while fT:
       #    curSend = fT[0:100]
        #   fT = fT[100:]
       fs.sendmsg(fT)   # sending payload
       
       fs.clearLock()
       



    def getCommand(self):
        # First get input from user, loop until a valid entry is selected
        command = input("Please enter the command for file transfer: ")

        # Loop to get valid entry
        while(True):
            # Check for correct information provided
            # Split the imput
            wordSplit = command.split()
            length = len(wordSplit)
            if(length == 0):             # event nothing is entered
                print("No commands entered.")
                command = input("Please enter a valid command, or exit: ")
                continue
            if(length ==  1):           # if only one word is entered check for exit
                if (command == "exit"): # Exit clause
                    print("Finished with file transfer.")
                    exit(1)
                else:
                    print("Invalid command.") # One word other than exit is entered
                    command = input("Please enter a valid command, or exit: ")
                continue
            if(length > 2):           # if there are too many comands entered
                print("Invalid command, it can only have 2 words.")
                command = input("Please enter a valid command, or exit: ")
                continue

            # If all the tests pass it splits the input to the command and the file name 
            commandPart = wordSplit[0]
            commandFile = wordSplit[1]
    
            # Checks if command was to put or get file and assigns a value.
            if(commandPart == "put"): 
                print ("Valid command")
                choice = 1
                break
            elif(commandPart == "get"):
                print("Valid command")
                choice = 2
                break
        
            command = input("Please enter a new command or exit to finish: ")

        # Checks choice to determine if the file locatinos need to be fixed
        if choice == 2:
            outputFile = commandFile
            commandFile = "serverfiles/"+outputFile
        elif choice == 1:
            outputFile = "serverfiles/" + commandFile

        # Check for a valid file to transfer
        if not os.path.isfile(commandFile):
            print("File does not exist!")
            exit(1)

        # Check for empty file
        sizeFile = os.path.getsize(commandFile)
        if (sizeFile == 0):
            print("Zero size file!")
            exit(1)

        return commandFile, outputFile

    # Makes sure the file has not been created if it is adds _ with a number 1 if doesnt have one, if it does increments by one. 
    def getOutputFile(self, outFile):
        print("testing " + outFile)
        newFile = outFile
        num = 0
        while os.path.isfile(newFile):
            print("File name already exists, changing it")
            outFile = newFile
            # removing the ending .txt
            outFile = outFile[:-4]
            print(outFile)
            ind = outFile.find('_')
            if (ind>0):
                outFile = outFile[:ind]
            num += 1
            newFile = outFile + '_' + str(num) + '.txt'

        print (newFile)
        return newFile
    # Get the contents of the input file
    def getPayload(self, infile):
        fullText = ""
        # Open the file
        inF = open(infile, "r+")
        
        # Get contents from file
        with open(infile, "r") as textFile:
            for line in textFile:
                fullText += line
                
        inF.close()
        
        return fullText
        

ClientThread(serverHost, serverPort, debug)
