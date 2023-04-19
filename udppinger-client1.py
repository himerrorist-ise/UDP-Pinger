from socket import *
import time
import sys

serverIp = "localhost"
serverPort = 3405

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

# loop through until counter reaches 180 seconds which means 3 minutes
# so needed to terminate program
while( passedTime < 180 ):
    # start time to calculate RRT
    startTime = time.time()
    try:
        # send ping message to the server
        clientSocket.sendto(
            f'ping, {sequenceNum}, {time.strftime("%H:%M:%S", time.localtime())}'.encode(),
            (serverIp, serverPort)
        )
        response, addr = clientSocket.recvfrom(1024)
        endTime = time.time()
        if (sequenceNum == response.decode().split(",")[1]):
            RRT = endTime - startTime
        # got response from server and calculated RRT
        print(f'echo, {sequenceNum}, {time.strftime("%H:%M,%S", time.localtime())}')
        sequenceNum += 1
    except timeout:
        # time out occured so packet lost
        flag = True
        print(f'Client ping timed out.')

    if (flag):
        time.sleep(2)
    else: time.sleep(3)

    passedTime += 3
    flag = False

clientSocket.close()
sys.exit()