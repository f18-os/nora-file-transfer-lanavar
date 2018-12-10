import re, sys
import threading

class FramedStreamSock:
     sockNum = 0
     def __init__(self, sock, debug=False, name=None):
          self.sock, self.debug = sock, debug
          self.rbuf = b""       # receive buffer
          self.lck = threading.Lock()
          if name:
               self.name = name
          else:                 # make default name
               self.name = "FramedStreamSock-%d" % FramedStreamSock.sockNum
               FramedStreamSock.sockNum += 1
     def __repr__(self):
          return self.name
     def getLock(self):
          self.lck.acquire()
          print("Lock acquired")
     def clearLock(self):
          self.lck.release()
          print("Lock Released")
     def sendmsg(self, payload):
          if self.debug: print("%s:framedSend: sending %d byte message" % (self, len(payload)))
          msg = str(len(payload)).encode("utf-8") + b':' + payload.encode("utf-8")
          while len(msg):
               nsent = self.sock.send(msg)
               msg = msg[nsent:]
     def receivemsg(self):
          state = "getLength"
          msgLength = -1
          while True:
               if (state == "getLength"):
                    match = re.match(b'([^:]+):(.*)', self.rbuf) # look for colon
                    if match:
                         lengthStr, self.rbuf = match.groups()
                         try: 
                              msgLength = int(lengthStr)
                         except:
                              if len(self.rbuf):
                                   print("badly formed message length:", lengthStr)
                                   return None
                         state = "getPayload"
               if state == "getPayload":
                    if len(self.rbuf) >= msgLength:
                         payload = self.rbuf[0:msgLength]
                         self.rbuf = self.rbuf[msgLength:]
                         return payload
               r = self.sock.recv(100)
               self.rbuf += r
               if len(r) == 0:  # zero length read
                    if (self.rbuf.decode("utf-8") == '\n'):
                         print("Transfer complete!")
                         return(None)
                    if len(self.rbuf) != 0:
                         print("FramedReceive: incomplete message. \n  state=%s, length=%d, self.rbuf=%s" % (state, msgLength, self.rbuf))
                    return None
               if self.debug: print("%s:FramedReceive: state=%s, length=%d, self.rbuf=%s" % (self, state, msgLength, self.rbuf))
