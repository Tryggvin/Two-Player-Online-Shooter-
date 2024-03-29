import socket
from _thread import *
import sys
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = ""
port = 4050
running = True
connected = 0
currentId = "0"
pos = ["0:50,50", "1:100,100"]

def threaded_client(conn):
    global currentId, pos, running, connected, currentId, pos
    conn.send(str.encode(currentId))
    currentId = "1"
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]

            conn.sendall(str.encode(reply))
        except:
            break
    print("Connection Closed")
    running = False
    #connected -= 1
    conn.close()

def host_server():
    global s,server,port,running,connected

    server_ip = socket.gethostbyname(server)

    try:
        s.bind((server_ip, port))

    except socket.error as e:
        print(str(e))

    s.listen(2)
    print("Waiting for a connection")

    

    while running:
        if connected < 2:
            connected += 1
            conn, addr = s.accept()
            print("Connected to: ", addr)
            start_new_thread(threaded_client, (conn,))
        time.sleep(10) # reduces lag, since it will only check once every 10 seconds if there is a pending connection.

    print("jobs done")