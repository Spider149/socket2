# -*- coding: utf-8 -*-
"""
Created on Sat May 15 06:51:27 2021

@author: LENOVO
"""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter import *
from functools import partial
import tkinter.messagebox as tkmes
import tkinter.filedialog as tkdilg
import tkinter.ttk as ttk
import tkinter.font as font

def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            #msg_list.insert(tkinter.END, msg)
            print(msg)
        except OSError:  # Possibly client has left the chat.
            break
        except:
            break
def Show_Login_Success():
    tkmes.showinfo(title="Success",message="Kết nối thành công")

def Show_Login_Error():
    tkmes.showerror(
        title="Error", message="Lỗi kết nối")
    

check_login = False
def validateLogin(username, password):
    global check_login
    if (check_login):
        return
    check_login = True
    client_socket.sendall(bytes(username.get(),'utf8'))
    client_socket.sendall(bytes(password.get(),'utf8'))
    success_or_not = client_socket.recv(BUFSIZ).decode("utf8")
    print(success_or_not, " ngay cho nay")
    if (success_or_not=="Login Success"):
        Show_Login_Success()
    else:
        Show_Login_Error()

isConnected = False
def Thread_Connect():
    global isConnected
    if (isConnected):
        return
    isConnected = True
    tConnect = Thread(target=validateLogin)
    tConnect.start()
    
def thread_UI():
    loginButton = Button(tkWindow, text="Login", command=Thread_Connect)
    loginButton.place(relx=0.43,rely=0.67)
        
def send(event=None):  # event is passed by binders.
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        tkWindow.quit()


def on_closing(event=None):
    my_msg.set("{quit}")
    print("Vao dc ne hihi")
    send()

tkWindow = tkinter.Tk()
tkWindow.title("Chatter")

#messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Nhập tên của bạn!.")

tkWindow.geometry('350x150')
tkWindow.minsize(350,150)  
tkWindow.title('Log in')

#username label and text entry box
usernameLabel = Label(tkWindow, text="User Name")
usernameLabel.place(relx=0.11, rely=0.25)
username = StringVar()
usernameEntry = Entry(tkWindow, textvariable=username)
usernameEntry.place(relx=0.35,rely=0.25)

#password label and password entry box
passwordLabel = Label(tkWindow,text="Password") 
passwordLabel.place(relx=0.11,rely=0.45)

password = StringVar()
passwordEntry = Entry(tkWindow, textvariable=password, show='*')  
passwordEntry.place(relx=0.35,rely=0.45)

validateLogin = partial(validateLogin, username, password)

#login button


'''
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Gửi", command=send)
send_button.pack()
'''
tkWindow.protocol("WM_DELETE_WINDOW", on_closing)

#Ket noi toi server
HOST = '127.0.0.1'
PORT = 33000
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(ADDR)
except:
    print("Error connection")
print("toi day luon")
receive_thread = Thread(target=thread_UI)
receive_thread.start()
tkWindow.mainloop()  # Starts GUI execution.