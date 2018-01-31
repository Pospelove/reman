# reman.py
# Copyright (C) 2018, Sirius
# All rights reserved.

import sys

sTip = "Start client: reman.py client <host> <port> \n\
Start server: reman.py server <port> <workingdir> <executable>"

try:
    sMode = sys.argv[1]
    if sMode != "client" and sMode != "server":
        print (sTip)
        sys.exit()

    bIsClient = (sMode == "client")

    sRemanServerIP = ""
    iRemanServerPort = 0
    sSkympServerFolder = ""
    sSkympServer = ""
    sLogsDir = "logs"
    if bIsClient:
        sRemanServerIP = sys.argv[2]
        iRemanServerPort = int(sys.argv[3])
        if sRemanServerIP == "" or sRemanServerIP == None:
            print (sTip)
            sys.exit()
    else:
        iRemanServerPort = int(sys.argv[2])
        sSkympServerFolder = sys.argv[3]
        sSkympServer = sys.argv[4]
        if sSkympServerFolder == "" or sSkympServerFolder == None or sSkympServer == "" or sSkympServer == None:
            print (sTip)
            sys.exit()

    if iRemanServerPort == 0 or iRemanServerPort == None:
        print (sTip)
        sys.exit()
except:
        print (sTip)
        sys.exit()

# common
sInternalPassword = "__!Hello*Tamri201!--"
sDummy = "Dummy"

gConn = None

import random
import time
import socket
import subprocess
import os
from shutil import copyfile
import signal
import datetime

from threading import Thread
from time import sleep

time.clock()

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        pass
    def kill(self):
        self.p.kill()
    def prepare(self):
        os.chdir(sSkympServerFolder)
        try:
            gConn.send(b"Building " + sSkympServer)
            time.sleep(1)
        except:
            pass
        try:
            process = subprocess.Popen(["git", "pull", "origin", "master"], stdout=subprocess.PIPE)
            output = process.communicate()[0]
        except:
            try:
                gConn.send(b"REMAN PANIC: Unable to git pull skymp server")
            except:
                pass
        try:
            os.chdir(sSkympServerFolder + "gamemodes\\")
            process = subprocess.Popen(["git", "pull", "origin", "master"], stdout=subprocess.PIPE)
            output = process.communicate()[0]
        except:
            try:
                gConn.send(b"REMAN PANIC: Unable to git pull gamemodes")
            except:
                pass
        os.chdir(sSkympServerFolder)
        try:
            process = subprocess.Popen(["make"], stdout=subprocess.PIPE)
            output = process.communicate()[0]
        except:
            try:
                gConn.send(b"REMAN PANIC: Unable to make")
            except:
                pass
        try:
            gConn.send(b"Done")
            time.sleep(1)
        except:
            pass
    def run(self):
        self.prepare()
        try:
            os.mkdir(sLogsDir)
        except:
            pass
        f = open("server_log.txt", "r")
        p = subprocess.Popen([sSkympServer],stdout=subprocess.PIPE)
        self.p = p
        print(sSkympServer + " was started")
        while True:
            line = f.readline().rstrip()
            if not not line:
                print(line)
                if gConn != None:
                    while len(line) < 2048:
                        line = line + " "
                    bLine = line.encode()
                    try:
                        gConn.send(bLine)
                    except:
                        pass


def StartExe():
    server = Server()
    server.start()
    return server
    pass

def StopExe(server):
    server.kill()
    print(sSkympServer + " was terminated")
    copyfile(sSkympServerFolder + "server_log.txt", sSkympServerFolder + "\\" + sLogsDir + "\\" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d.%H-%M-%S') + ".txt")
    f = open(sSkympServerFolder + "server_log.txt", "w")
    f.write("\n")
    f.close()
    pass

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def EnableRemanTitle(bEnable):
    if sys.platform.startswith("win"):
        if bEnable:
            os.popen("title Reman")
        else:
            os.popen("title skymp_server")

if bIsClient:
    print("Starting reman client")

    EnableRemanTitle(False)

    sock = socket.socket()
    print("Started")
    bConnected = False
    while not bConnected:
        try:
            print("Connecting to ", sRemanServerIP, ":", iRemanServerPort)
            sock.connect((sRemanServerIP, iRemanServerPort))
            bConnected = True
        except ConnectionRefusedError:
            print("Connection failed, retrying")
            time.sleep(1)
    sock.send(sInternalPassword.encode())

    while True:
        try:
            bData = sock.recv(2048)
            sData = bData.decode("windows-1252")
            for i in range(0, 100):
                sData = sData.replace("         ", " ")
                sData = sData.replace("  ", " ")
                pass
            print(sData)
        except:
            pass
        try:
            sock.send(sDummy.encode())
        except:
            EnableRemanTitle(True)
            print("")
            print("Remote reman closed the connection")
            break


else:
    print("Starting reman server")
    copyfile("server.cfg", sSkympServerFolder + "server.cfg")
    sock = socket.socket()
    try:
        sock.bind(('', iRemanServerPort))
    except:
        print("Port ", iRemanServerPort, " is already in use")
        sys.exit()

    print("Started")

    while True:
        while 1:
            try:
                sock.listen(1)
                break
            except:
                print("Something gone wrong")
        conn, addr = sock.accept()
        gConn = conn
        print("Connected reman")

        svr = StartExe()

        sExcepted = sInternalPassword
        fTime = time.clock()
        while True:
            try:
                bData = conn.recv(1024)
                sData = (bData.decode("windows-1252"))
                fTime = time.clock()
                if sExcepted != sData:
                    print("Wrong internal password")
                    break
                else:
                    sExcepted = sDummy
            except:
                if time.clock() - fTime > 2:
                    break

        conn.close()

        print("Disconnected reman")
        StopExe(svr)
