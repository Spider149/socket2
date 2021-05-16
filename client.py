import socket
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
    tkmes.showinfo(title="Success", message="Đăng nhập thành công")


def Show_Login_Error():
    tkmes.showerror(
        title="Error", message="Lỗi kết nối")


def validateLogin(username, password):
    client_socket.sendall(bytes(username.get(), 'utf8'))
    client_socket.sendall(bytes(password.get(), 'utf8'))
    success_or_not = client_socket.recv(BUFSIZ).decode("utf8")
    print(success_or_not, " ngay cho nay")
    if (success_or_not == "Login Success"):
        Show_Login_Success()
    else:
        Show_Login_Error()


isConnected = False
isSend = False


def Thread_Connect():
    global isSend
    global isConnected
    if (isSend or not isConnected):
        return
    isSend = True
    tConnect = Thread(target=validateLogin)
    tConnect.start()


def thread_UI():
    loginButton = Button(tkWindow, text="Login", command=Thread_Connect)
    loginButton.place(relx=0.43, rely=0.75)


def send(event=None):  # event is passed by binders.
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        tkWindow.quit()


def on_closing(event=None):
    client_socket.close()
    tkWindow.quit()


def submitIP():
    host = entryIP.get()
    port = 33000
    server_address = (host, port)
    try:
        client_socket.connect(server_address)
        #client_socket.sendall(bytes("-hello-", "utf8"))
        data = client_socket.recv(1024).decode("utf8")
        print(data)
        if data == "-connected-":
            tkmes.showinfo(title="Success",
                           message="Kết nối thành công")
            global isConnected
            isConnected = True
    except:
        tkmes.showerror(title="Error", message="Kết nối thất bại")


isSubmit = False


def Thread_Submit():
    global isSubmit
    if (isSubmit):
        return
    isSubmit = True
    tConnect = Thread(target=submitIP)
    tConnect.start()


def Thread_UI_Submit():
    ipBtn = Button(tkWindow, text="Kết nối", command=Thread_Submit)
    ipBtn.grid(row=0, column=2, sticky=W+S +
               N+E, pady=20, padx=(0, 10))


tkWindow = tkinter.Tk()
tkWindow.title("Chatter")

#messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Nhập tên của bạn!.")

tkWindow.geometry('350x250')
tkWindow.minsize(350, 250)
tkWindow.title('Log in')

# username label and text entry box
usernameLabel = Label(tkWindow, text="User Name")
usernameLabel.place(relx=0.11, rely=0.46)
username = StringVar()
usernameEntry = Entry(tkWindow, textvariable=username)
usernameEntry.place(relx=0.35, rely=0.46)

# password label and password entry box
passwordLabel = Label(tkWindow, text="Password")
passwordLabel.place(relx=0.11, rely=0.6)

password = StringVar()
passwordEntry = Entry(tkWindow, textvariable=password, show='*')
passwordEntry.place(relx=0.35, rely=0.6)

validateLogin = partial(validateLogin, username, password)

# login button
labelIP = Label(tkWindow, text="Nhập IP:")
labelIP.grid(row=0, column=0, pady=20, sticky=W +
             S+N+E, padx=(20, 10))

entryIP = Entry(tkWindow)
entryIP.grid(row=0, column=1, pady=20, sticky=W +
             S+N+E, padx=(0, 10))

entryIP.insert(END, '127.0.0.1')

tkWindow.protocol("WM_DELETE_WINDOW", on_closing)

# Ket noi toi server
HOST = '127.0.0.1'
PORT = 33000
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

print("toi day luon")
receive_thread = Thread(target=thread_UI)
receive_thread.start()

submit_thread = Thread(target=Thread_UI_Submit)
submit_thread.start()
tkWindow.mainloop()  # Starts GUI execution.
