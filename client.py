import socket
import threading as thread
from tkinter import *
from functools import partial
import tkinter.messagebox as tkmes
import tkinter.ttk as ttk
import tkinter.font as font

isConnected = False
isLogin = False

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ket noi toi server
HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)


def receive():
    while True:
        try:
            msg = clientSocket.recv(BUFSIZ).decode("utf8")
            #msg_list.insert(tkinter.END, msg)
            print(msg)
        except OSError:  # Possibly client has left the chat.
            break
        except:
            break


def showSuccess(mes):
    tkmes.showinfo(title="Success", message=mes)


def showErr(mes):
    tkmes.showinfo(title="Error", message=mes)


def validate(register):
    username = usernameEntry.get()
    password = passwordEntry.get()
    if(username == "" or password == ""):
        showErr("Username và password không được để trống")
        return
    if(" " in username or " " in password or len(username) < 6 or len(password) < 6):
        showErr(
            "Username và password phải có 6 ký tự trở lên và không chứa khoảng trắng")
        return
    else:
        if(register):
            clientSocket.sendall(bytes('r'+username+' '+password, 'utf8'))
        else:
            clientSocket.sendall(bytes('l'+username+' '+password, 'utf8'))

        result = clientSocket.recv(BUFSIZ).decode("utf8")
        if(result[0] == 'F'):
            showErr(result[2:])
        else:
            if(not register):
                global isLogin
                isLogin = True
            showSuccess(result[2:])


def threadConnectLogin():
    global isConnected
    if(not isConnected):
        showErr("Hãy kết nối đến server trước")
        return
    global isLogin
    if(isLogin):
        return
    tConnect = thread.Thread(target=validate, args=(False,))
    tConnect.start()


def threadConnectRegister():
    global isConnected
    if (not isConnected):
        showErr("Hãy kết nối đến server trước")
        return
    tConnect = thread.Thread(target=validate, args=(True,))
    tConnect.start()


def threadUILogin():
    loginButton = Button(tkWindow, text="Login", command=threadConnectLogin)
    loginButton.place(relx=0.35, rely=0.75)


def threadUIRegis():
    RegisButton = Button(tkWindow, text="Register",
                         command=threadConnectRegister)
    RegisButton.place(relx=0.55, rely=0.75)


def onClosing():
    global isConnected
    if (isConnected):
        clientSocket.sendall(bytes("quit", 'utf8'))
    clientSocket.close()
    tkWindow.destroy()


def submitIP():
    host = entryIP.get()
    port = 33000
    serverAddress = (host, port)
    try:
        clientSocket.connect(serverAddress)
        data = clientSocket.recv(1024).decode("utf8")
        if data == "-connected-":
            tkmes.showinfo(title="Success",
                           message="Kết nối thành công")
            global isConnected
            isConnected = True
    except:
        tkmes.showerror(title="Error", message="Kết nối thất bại")


def threadSubmit():
    global isConnected
    if (isConnected):
        return
    tConnect = thread.Thread(target=submitIP)
    tConnect.start()


def threadUISubmit():
    ipBtn = Button(tkWindow, text="Kết nối", command=threadSubmit)
    ipBtn.grid(row=0, column=2, sticky=W+S +
               N+E, pady=20, padx=(0, 10))


tkWindow = Tk()
tkWindow.title("Chatter")

tkWindow.geometry('350x250')
tkWindow.minsize(350, 250)
tkWindow.title('Log in')

# username label and text entry box
usernameLabel = Label(tkWindow, text="User Name")
usernameLabel.place(relx=0.11, rely=0.46)

usernameEntry = Entry(tkWindow)
usernameEntry.place(relx=0.35, rely=0.46)

# password label and password entry box
passwordLabel = Label(tkWindow, text="Password")
passwordLabel.place(relx=0.11, rely=0.6)

passwordEntry = Entry(tkWindow, show="*")
passwordEntry.place(relx=0.35, rely=0.6)

# login button
labelIP = Label(tkWindow, text="Nhập IP:")
labelIP.grid(row=0, column=0, pady=20, sticky=W +
             S+N+E, padx=(20, 10))

entryIP = Entry(tkWindow)
entryIP.grid(row=0, column=1, pady=20, sticky=W +
             S+N+E, padx=(0, 10))

entryIP.insert(END, '127.0.0.1')

tkWindow.protocol("WM_DELETE_WINDOW", onClosing)

loginThread = thread.Thread(target=threadUILogin)
loginThread.start()

regisThread = thread.Thread(target=threadUIRegis)
regisThread.start()

submitThread = thread.Thread(target=threadUISubmit)
submitThread.start()
tkWindow.mainloop()  # Starts GUI execution.
