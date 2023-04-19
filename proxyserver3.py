from socket import *
import sys
import _thread
import time

port = 3406
proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(("", port))

flag = False
threadId = 0

cacheData = dict()

def threadFunc(conn):
    global flag
    global threadId
    threadId += 1
    global cacheData

    try:
        webserverSocket = socket(AF_INET, SOCK_STREAM)
        data = conn.recv(2048).decode()
        filename = data.split()[1][1:]
        if cacheData.keys().__contains__(filename) and (time.time() - cacheData[filename][1] < 120 ):
            # conn.send("HTTP/1.1 200 OK\r\n".encode())
            # conn.send("Content-Type: text/html\r\n".encode())
            conn.sendall(cacheData[filename][0].encode())
            # time.sleep(4)
            # print(f'proxy-cache, client, {_thread.get_ident()}, {time.strftime("%H:%M:%S", time.localtime())}\n')
        else:
            webserverSocket.connect(("", 3405))
            webserverSocket.sendall(data.encode())
            response = webserverSocket.recv(2048).decode()
            # time.sleep(5)
            # print(f'\nproxy-forward, server, {_thread.get_ident()}, {time.strftime("%H:%M:%S", time.localtime())}')
            cacheData[filename] = [response, time.time()]
            conn.sendall(response.encode())
            # print(f'proxy-forward, client, {_thread.get_ident()}, {time.strftime("%H:%M:%S", time.localtime())}\n')
        conn.close()
        webserverSocket.close()
    except KeyboardInterrupt:
        conn.close()
        webserverSocket.close()
        flag = True
    except:
        conn.close()
        webserverSocket.close()

    _thread.exit()

def threadUDP():
    serverIp = ""
    serverPort = 3407
    # create client socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # set timeout to socket to check if the packet is timedout or not
    clientSocket.settimeout(1)

    # initilize sequence number
    sequenceNum = 1

    # to send packet in every 3 seconds needed a timer
    passedTime = 0

    # flag to check if time out happend or not
    # if happened i need to wait 2 seconds because i already waited a second
    # while waiting response from server
    flag = False

    # data variables
    minRRT = 100000
    maxRRT = 0
    RRTtotal = 0
    totalNumRRT = 0
    packetLossRate = 0
    averageRRTs = 0
    totalNumPing = 60 # because we ping every 3 seconds until it is 180 seconds
    currentNumPing = 0

    # calculate needed data
    def calculateData(rrt):
        global minRRT
        global maxRRT
        global RRTtotal
        global totalNumRRT
        global averageRRTs
        global totalNumPing
        global currentNumPing
        global packetLossRate

        if (RRT < minRRT): minRRT = RRT
        if (RRT > maxRRT): maxRRT = RRT
        totalNumRRT+=1
        RRTtotal += RRT
        averageRRTs = RRTtotal / totalNumRRT
        packetLossRate = ((currentNumPing - totalNumRRT) * 100)/ currentNumPing

        print(f'\nThe minimum RRT:  {minRRT}')
        print(f'The maximum RRT:  {maxRRT}')
        print(f'The total number of RRTs:  {totalNumRRT}')
        print(f'ThePacket loss rate: {packetLossRate}%')
        print(f'The average RRTs:   {averageRRTs}\n')
        return

    # loop through until counter reaches 180 seconds which means 3 minutes
    # so needed to terminate program
    while( passedTime < 180 ):
        # start time to calculate RRT
        currentNumPing += 1
        startTime = time.time()
        try:
            # send ping message to the server
            clientSocket.sendto(
                f'ping, {sequenceNum}, {time.strftime("%H:%M:%S", time.localtime())}'.encode(),
                (serverIp, serverPort)
            )
            response, addr = clientSocket.recvfrom(1024)
            endTime = time.time()
            # got response from server and calculated RRT
            print(f'echo, {sequenceNum}, {time.strftime("%H:%M:%S", time.localtime())}')
            if (sequenceNum == int(response.decode().split(", ")[1])):
                RRT = endTime - startTime
                calculateData(RRT)
            sequenceNum += 1
        except timeout:
            # time out occured so packet lost
            flag = True
            print(f'Client ping timed out.\n')

        if (flag):
            time.sleep(2)
        else: time.sleep(3)

        passedTime += 3
        flag = False

    clientSocket.close()
    _thread.exit()

# main
try:
    proxySocket.listen(10)
    print(f'\nProxy Server Started...\n')

    while not flag:
        client, addr = proxySocket.accept()
        # print(f'\r\nCurrent number of threads { _thread._count()}\r\n')
        _thread.start_new_thread(threadFunc, (client, ))
        # print(f'\n\n{cacheData}\n\n')

        _thread.start_new_thread(threadUDP, ())

except KeyboardInterrupt:
    proxySocket.close()
    sys.exit()

proxySocket.close()