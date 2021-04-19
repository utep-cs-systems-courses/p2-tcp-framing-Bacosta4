#! /usr/bin/env python3

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
from threading import Thread,Lock

buffer = b""
lock = Lock()

def Framedreceive(sock):
    action = "length"
    msglength = 0
    global buffer
    message = ""
    while 1:
        r = sock.recv(1000)
        buffer += r
        if len(r) == 0:
            if len(buffer) != 0:
                os.write(1, "Incorrect message")
            return None
        if action == "length":
            matching = re.match(b'([^:]+):(.*)',buffer,re.DOTALL | re.MULTILINE)
            if matching:
                lengthStr, buffer = matching.groups()
                print(lengthStr, buffer)
                try:
                    msglength = int(lengthStr)
                except:
                    os.write(2,("Invalid message lenght").encode())
                    return None
                action = "get data"
                print("Data get")
            if action == "get data":
                print("Action get lenght")
                if len(buffer) >= msglength:
                    message = buffer [0:msglength]
                    buffer = buffer [msglength:]
                return message

def run(sock):
    os.write(1,(b"Starting thread\n"))
    while 1:
        lock.acquire()
        filename = Framedreceive(sock).decode()
        print(filename)
        os.write(1,('filename is %s\n'%filename).encode())
        conf = "file name received checking if in server\n"
        os.write(1,conf.encode())
        path = os.getcwd()
        filepath = path+'/'+filename
        if os.path.isfile(filepath):
            os.write(1,('file exists now exiting\n').encode())
            sock.send(("file exists").encode())
            sys.exit(0)
        else:
            lock.release()
            sock.send(("file doesnt exit\n").encode())
            f = open(filename,"wb")
            os.write(1,b"writing file contents\n")
            message = Framedreceive(sock)
            f.write(message)
            f.close()
        sock.close()
        break

    
switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(2)              # allow only one outstanding request
# s is a factory for connected sockets

createfile = False
completepath = ''

while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    print("Connect to", addr)
    server = Thread(target = run, args =(conn,))
    server.start()
