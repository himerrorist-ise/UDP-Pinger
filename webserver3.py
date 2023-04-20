from socket import *
import sys
import _thread
import base64
import time
import random

port = 3405

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(("", port))

# Prepare a sever socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocketUDP.bind(('', 3407))
serverSocketUDP.settimeout(30)

flag = False

threadId = 0

def threadedClient(conn, addr):
  global flag
  global threadId
  threadId += 1
  # print (f'Connected to the proxy server with the address: {addr}')
  serverresponse = ""
  statusCode = 0
  try:
      
    data = conn.recv(2048).decode()

    filename = data.split()[1]
    filetype = filename.split(".")[1]

    # print(data)

    if filetype=="pdf":
       
      with open(filename[1:], 'rb') as f:

        # lines = f.read()
        pdf = f.read()
        # pdf = base64.b64encode(f.read())

        serverresponse = "OK"
        statusCode = 200
        conn.sendall("HTTP/1.1 200 OK\r\n".encode())
        # conn.sendall("Content-Type: application/pdf\r\n".encode())
        conn.sendall("Content-Type: application/pdf\n".encode())
        conn.sendall(f'Content-Disposition: attachment; filename={filename[1:]}\r\n'.encode())
        # conn.sendall("\r\n".encode())

        # for i in range(0, len(lines)):
        #   conn.sendall(lines[i])

        # conn.sendall(lines)
        conn.sendall(pdf)
        conn.sendall("\r\n".encode())

    else:
      with open(filename[1:], 'r') as f:
        lines = f.readlines()
        serverresponse = "OK"
        statusCode = 200
        conn.sendall("HTTP/1.1 200 OK\r\n".encode())
        conn.sendall("Content-Type: text/html\r\n".encode())
        conn.sendall("\r\n".encode())
        # conn.sendall(responseHeader.encode())

        for i in range(0, len(lines)):
          conn.sendall(lines[i].encode())
        conn.sendall("\r\n".encode())
    # time.sleep(4)
    # print(f'server-response, {statusCode}, {_thread.get_ident()}, {time.strftime("%H:%M:%S", time.localtime())}')

  except IOError:
    serverresponse = "Not Found"
    statusCode = 404
    conn.sendall(("HTTP/1.1 404 Not Found\r\n").encode())
    # conn.sendall(responseHeader.encode())
    # conn.send("HTTP/1.1 200 OK\r\n".encode())
    conn.close()

    # print(f'server-response, {statusCode}, {_thread.get_ident()}, {time.strftime("%H:%M:%S", time.localtime())}')

  except KeyboardInterrupt:
      flag = True
      conn.close()
  except:
    conn.close()

  conn.close()
  # print("Connection closed!\n\nNow Listening...")
  _thread.exit()


def threadUDP(conn):
    while True:
        try:
          # Generate random number in the range of 0 to 10
          rand = random.randint(0, 10)

          # Receive the client packet along with the address it is coming from
          message, address = conn.recvfrom(1024)

          # If rand is less is than 4, we consider the packet lost and do not respond
          if rand < 4:
              continue

          # Otherwise, prepare the server response

          # The server responds
          conn.sendto(message, address)
          print(f'echo, {message.decode().split(", ")[1]}, {time.strftime("%H:%M:%S", time.localtime())}')
        except timeout:
          print(f'Server echo timed out.\n')
          break
    
    _thread.exit()


# main
try:
  serverSocket.listen(10)
  print("\nServer has been started. Now listening...")

  while not flag:
    client, address = serverSocket.accept()

    # print('Connected to: ' + address[0] + ':' + str(address[1]))
    _thread.start_new_thread(threadedClient, (client, address))
    # print(f'number of thread: {_thread._count()}')

    _thread.start_new_thread(threadUDP, (serverSocketUDP, ))
    
    
except KeyboardInterrupt:
    serverSocket.close()
    serverSocketUDP.close()
    sys.exit()

serverSocket.close()
serverSocketUDP.close()