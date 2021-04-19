#! /usr/bin/env python3

# Echo client program
import socket, sys, re, time

sys.path.append("../lib")       # for params
import params
import os

next = 0
limit =  0
count = 0

def Framedsend(socket,payload):
    print("Framesend error")
    msg = str(len(payload)).encode()+b':'+payload.encode()
    while len(msg):
        sent = socket.send(msg)
        msg = msg[sent:] # sends everything on the left
        
def getChar():
    global next
    global limit
    fd = os.open(filename, os.O_RDONLY)
    if next == limit:
        next = 0
        limit = os.read(fd, 1024)
        
        if limit == 0:
            return 'EOF'
        
        if next < len(limit):
            c = chr(limit[next])
            next += 1
            os.close(fd)
            return c
        else:
            os.close(fd)
            return 'EOF'

def readLine():
    global next
    global limit

    line = ""
    c = getChar()
    while (c != '' and c != "EOF"):
        line += c
        c = getChar()
    next = 0
    limit = 0
    return line
    
switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

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

delay = float(paramMap['delay']) # delay before reading (default = 0s)
if delay != 0:
    print(f"sleeping for {delay}s")
    time.sleep(delay)
    print("done sleeping")

filename = input('File you wish to run\n')
data = 0 #error checkers
sfilename = False
writeContent = False
print("error")

if filename == 'exit':
    Framedsend(s,filename)
    sys.exit(0)
if os.path.isfile(filename):
    print(filename)
    if sfilename == False:
        Framedsend(s,filename)
        createfile = True
        data = s.recv(1024).decode()
        print(data)
        if data == "file exists\n":
             os.write(1,("file exists now exiting\n").encode())
             sys.exit(0)
        else:
            os.write(1,("Received '%s'\n" %data).encode())
else:
    os.write(1,("File not found exiting now\n").encode())
    sys.exit(0)
    
content = readLine()
Framedsend(s,content)
received = s.recv(1024)
os.write(1,received)

os.write(1,("End of file reached now closing\n").encode())
s.close()
