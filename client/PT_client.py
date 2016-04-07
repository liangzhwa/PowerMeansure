import os
import socket
import struct
import time
import datetime
import string

powerFileSize = 0;
addr = ('10.239.206.7', 9985)

def MeansurePowerWithDuration(duration,newFileName):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    print 'client-s',datetime.datetime.now()
    sock.send('M-start-d#*#'+str(duration))
    buf = sock.recv(1024)
    if buf == "T-start-d":
        sock.close()
        TransformFile(newFileName,"d");

def StartMeansurePower():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send('M-start-s')
    sock.close()

def EndMeansurePower(newFileName):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send('M-start-e')
    buf = sock.recv(1024)
    if buf == "T-start":
        sock.close()
        TransformFile(newFileName,"m")
    elif buf == "T-nodata":
        print 'no data capture!'
        sock.close()

def TransformFile(newFileName,type):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send("T-start#*#"+type)
    print 'file transform start'
    fHead = sock.recv(20)
    BUFSIZE = 1024
    restSize = fileSize = string.atoi(fHead)
    file_dir = os.path.dirname(newFileName)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    fp = open(newFileName,'wb')
    while 1:
        if restSize > BUFSIZE:
            fData = sock.recv(BUFSIZE)
        else:
            fData = sock.recv(restSize)
        if not fData: break
        fp.write(fData)
        restSize = restSize-len(fData)
        if restSize == 0: break
    fp.close()
    print 'file transform end'
#    if(type == "d"):
#        time.sleep(10)
#        print 'restart powertool'
#        RestartPowerTool()
    sock.close()
    
def RestartPowerTool():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send("Tool-restart")
    sock.close()
    
def TransfromFile1(newFileName):
    global powerFileSize
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send('T-start')
    
    BUFSIZE = 1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    fhead = sock.recv(FILEINFO_SIZE)
    
    filename,temp1,filesize,temp2=struct.unpack('128s32sI8s',fhead)
    restsize = powerFileSize = powerFileSize = filesize
    file_dir = os.path.dirname(newFileName)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    fp = open(newFileName,'wb')
    while 1:
        if restsize > BUFSIZE:
            filedata = sock.recv(BUFSIZE)
        else:
            filedata = sock.recv(restsize)

        if not filedata: break
        fp.write(filedata)
        restsize = restsize-len(filedata)
        if restsize == 0: break
    print "revice complete..."
    fp.close()
    sock.close()
