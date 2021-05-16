# -*- coding: utf-8 -*-
"""
Created on Sat May 15 06:51:21 2021

@author: LENOVO
"""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk

def accept_incoming_connections():
    while True:
        try:
            client, client_address = SERVER.accept()
            print("accepted")
        except:
            break
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    try:
        name = client.recv(BUFSIZ).decode("utf8")
        pass_w = client.recv(BUFSIZ).decode("utf8")
    except:
        client.send(bytes("Login Error","utf8"))
        return
    
    client.send(bytes("Login Success","utf8"))
    '''    
    print("username: ",name)
    print("password: ",pass_w)
    welcome = 'Xin chào %s! Nếu bạn muốn thoát gõ, {quit} để thoát.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s đã tham gia phòng chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name + ": ")
        else:
            #client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s đã thoát phòng chat." % name, "utf8"))
            break
        '''

def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


clients = {}
addresses = {}

HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

isConnected = False
def threadConnect():
    global isConnected
    if isConnected:
        return
    isConnected = True
    SERVER.listen(5)
    tConnect = Thread(target=accept_incoming_connections)
    tConnect.start()

def threadUI():
    global root
    global SERVER
    root.title("Server")
    root.minsize(200, 200)
    openServerBtn = tk.Button(root, text="Mở server",
                              command=threadConnect, width=10, height=5)
    openServerBtn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


def onClosing():
    global SERVER
    SERVER.close()
    root.destroy()


root = tk.Tk()
print("Chờ kết nối từ các client...")
tUI = Thread(target=threadUI)
tUI.start()
root.protocol("WM_DELETE_WINDOW", onClosing)
root.mainloop()