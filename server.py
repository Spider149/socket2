import socket
import threading as thread
import tkinter as tk
import json


clients = {}  # danh sách client đã kết nối và trạng thái kết nối
addresses = {}  # danh sách client và địa chỉ
data = {}
loginStatusList = {}  # những client đã login


HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

isConnected = False


def acceptIncomingConnections():
    while True:
        try:
            client, clientAddress = SERVER.accept()
            client.sendall(bytes("-connected-", "utf8"))
            # có kết nối tới thì gưi qua 1 tin nhắn
        except:
            break
        print("%s:%s has connected." % clientAddress)
        clients[client] = True
        addresses[client] = clientAddress
        thread.Thread(target=handleClient, args=(client,)).start()


def handleClient(client):  # Takes client socket as argument.
    global data
    global loginStatusList
    isLogin = False

    while (True):

        message = client.recv(BUFSIZ).decode("utf8")

        if (message[0] == "l" and not isLogin):
            splitPoint = message.index(" ", 1)
            name = message[1:splitPoint]
            password = message[splitPoint+1:]
            if (name in data.keys()):
                if (loginStatusList[name]):
                    client.sendall(
                        bytes("F-Tài khoản đã được đăng nhập", "utf8"))
                else:
                    if (data[name] == password):
                        client.sendall(bytes("S-Đăng nhập thành công", "utf8"))
                        loginStatusList[name] = True
                        isLogin = True
                    else:
                        client.sendall(
                            bytes("F-Sai mật khẩu hoặc tài khoản", "utf8"))
            else:
                client.sendall(
                    bytes("F-Sai mật khẩu hoặc tài khoản", "utf8"))
        elif (message[0] == "r"):
            splitPoint = message.index(" ", 1)
            name = message[1:splitPoint]
            password = message[splitPoint+1:]
            if (name in data.keys()):
                client.sendall(
                    bytes("F-Tài khoản đã tồn tại, vui lòng chọn id khác", "utf8"))
            else:
                data[name] = password
                loginStatusList[name] = False
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                    f.close()
                client.sendall(bytes("S-Đăng ký thành công", "utf8"))
        elif message == "quit":
            client.close()
            del clients[client]
            del addresses[client]
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.sendall(bytes(prefix, "utf8") + msg)


def threadConnect():
    global isConnected
    if isConnected:
        return
    isConnected = True
    SERVER.listen(5)
    tConnect = thread.Thread(target=acceptIncomingConnections, daemon=True)
    tConnect.start()


def threadUI():
    root.title("Server")
    root.minsize(200, 200)
    openServerBtn = tk.Button(root, text="Mở server",
                              command=threadConnect, width=10, height=5)
    openServerBtn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


def onClosing():
    SERVER.close()
    root.destroy()


def loadData():
    global data
    with open("data.json") as f:
        dataLoad = json.load(f)
        for x in dataLoad:
            if x in data.keys():
                continue
            data[x] = dataLoad[x]
            loginStatusList[x] = False
        f.close()

def disConnect():
    for client in clients:
        client.sendall(bytes("disconnect","utf8"))
root = tk.Tk()

print("Chờ kết nối từ các client...")
tUI = thread.Thread(target=threadUI)
tUI.start()

loadData()
root.protocol("WM_DELETE_WINDOW", onClosing)
root.mainloop()
