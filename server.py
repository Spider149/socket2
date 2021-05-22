import socket
import threading as thread
import tkinter as tk
import json
import datetime
import pickle

clients = {}  # danh sách client đã kết nối và trạng thái kết nối
addresses = {}  # danh sách client và địa chỉ
account = {} # danh sách tài khoản
data = {} #danh sách thông tin trận đấu
loginStatusList = {}  # những client đã login
timeMatch = {} # Ghi thời gian diễn ra trận đấu

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

def get_delta_time(start):
    now = datetime.datetime.now()
    if (str(now) < start):
        return -2
    start_time_obj = datetime.datetime.strptime(start[2:],"%y-%m-%d %H:%M:%S")
    during = now - start_time_obj
    if (str(type(during))==str(type(datetime.datetime.now()))):
        if (during.day > 0):
            return 1000
        res = int(during.hours)*60 + int(during.minutes)
        return res
    else:
        return int(during.total_seconds()/60.0)
    
    

def preProcess(pid):
    global data
    global timeMatch
    match = data[pid]
    start = match["start"]
    delta_time = get_delta_time(start)
    if (delta_time < 0):
        time_temp =  datetime.datetime.strptime(data[pid]["start"][2:],"%y-%m-%d %H:%M:%S")
        timeMatch[pid] = "{0:02d}:{1:02d}".format(time_temp.hour,time_temp.minute)
    else:
        if (delta_time < 45):
            timeMatch[pid] = str(delta_time) + "\'"
        elif (delta_time < 60):
            timeMatch[pid] = "HT"
        elif (delta_time < 105):
            timeMatch[pid] = str(delta_time - 15) + "\'"
        else:
            timeMatch[pid] = "FT"

def detailMatch(pid,state):
    global data
    loadMatch = data[pid]
    if (state=="FT"):
        return
    elif (":" in state):
        loadMatch["team1"]["scorer"] = []
        loadMatch["team1"]["red_card"] = []
        loadMatch["team1"]["yellow_card"] = []
        loadMatch["team2"]["scorer"] = []
        loadMatch["team2"]["red_card"] = []
        loadMatch["team2"]["yellow_card"] = []
    else:
        tempEvent = []
        for event in loadMatch["team1"]["scorer"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team1"]["scorer"] = tempEvent
        tempEvent = []
        for event in loadMatch["team1"]["red_card"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team1"]["red_card"] = tempEvent
        tempEvent = []
        for event in loadMatch["team1"]["yellow_card"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team1"]["yellow_card"] = tempEvent
        tempEvent = []
        for event in loadMatch["team1"]["scorer"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team2"]["scorer"] = tempEvent
        tempEvent = []
        for event in loadMatch["team1"]["red_card"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team2"]["red_card"] = tempEvent
        tempEvent = []
        for event in loadMatch["team1"]["yellow_card"]:
            if (int(event[1]) < int(state)):
                tempEvent.append(event)
        loadMatch["team2"]["yellow_card"] = tempEvent
    data[pid] = loadMatch
    
def handleClient(client):  # Takes client socket as argument.
    global account
    global data
    global loginStatusList
    global data
    isLogin = False

    while (True):

        message = client.recv(BUFSIZ).decode("utf8")

        if (message[0] == "l" and not isLogin):
            splitPoint = message.index(" ", 1)
            name = message[1:splitPoint]
            password = message[splitPoint+1:]
            if (name in account.keys()):
                if (loginStatusList[name]):
                    client.sendall(
                        bytes("F-Tài khoản đã được đăng nhập", "utf8"))
                else:
                    if (account[name] == password):
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
            if (name in account.keys()):
                client.sendall(
                    bytes("F-Tài khoản đã tồn tại, vui lòng chọn id khác", "utf8"))
            else:
                account[name] = password
                loginStatusList[name] = False
                with open('account.json', 'w') as f:
                    json.dump(account, f)
                    f.close()
                client.sendall(bytes("S-Đăng ký thành công", "utf8"))
        elif message == "see_match":
            Line = {}
            for ID in data.keys():
                preProcess(ID)
                detailMatch(ID,timeMatch[ID])
                if (":" in timeMatch[ID]):
                    Line[ID] = [timeMatch[ID],data[ID]["team1"]["name"],
                                "? : ?",data[ID]["team2"]["name"]]
                    print(Line[ID])
                else:
                    Line[ID] = [timeMatch[ID],data[ID]["team1"]["name"],
                                str(len(data[ID]["team1"]["scorer"]))+":"+
                                str(len(data[ID]["team2"]["scorer"])),
                                data[ID]["team2"]["name"]]
            client.sendall(pickle.dumps(Line))
        
        elif message == "detail_match":
            ID = client.recv(BUFSIZ).decode("utf8")
            if (ID not in data.keys()):
                client.sendall(bytes("get_fail"))
                continue
            client.sendall(bytes("get_success","utf8"))
            res = None
            preProcess(ID)
            detailMatch(ID,timeMatch[ID])
            if (":" in timeMatch[ID]):
                    res = [timeMatch[ID],data[ID]["team1"]["name"],
                                "? : ?",data[ID]["team2"]["name"]]
            else:
                res = [timeMatch[ID],data[ID]["team1"]["name"],
                            str(len(data[ID]["team1"]["scorer"]))+":"+
                            str(len(data[ID]["team2"]["scorer"])),
                            data[ID]["team2"]["name"]]
            
            details = data[ID]
            list_event = {}
            events = []
            for Eve in details["team1"]["scorer"]:
                Eve.append("score")
                Eve.append("1")
                events.append(Eve)
            for Eve in details["team1"]["red_card"]:
                Eve.append("red")
                Eve.append("1")
                events.append(Eve)
            for Eve in details["team1"]["yellow_card"]:
                Eve.append("yellow")
                Eve.append("1")
                events.append(Eve)
            for Eve in details["team2"]["scorer"]:
                Eve.append("score")
                Eve.append("2")
                events.append(Eve)
            for Eve in details["team2"]["red_card"]:
                Eve.append("red")
                Eve.append("2")
                events.append(Eve)
            for Eve in details["team2"]["yellow_card"]:
                Eve.append("yellow")
                Eve.append("2")
                events.append(Eve)
            for i in range(len(events) - 1):
                for j in range(i+1,len(events)):
                    if (int(events[i][1]) > int(events[j][1])):
                        events[i], events[j] = events[j], events[i]
            list_event["send"] = [res,events]
            client.sendall(pickle.dumps(list_event))
            
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
    global account
    global data
    global timeMatch
    with open("account.json") as f:
        accountLoad = json.load(f)
        for x in accountLoad:
            if x in account.keys():
                continue
            account[x] = accountLoad[x]
            loginStatusList[x] = False
        f.close()
    with open("data.json") as f:
        data = json.load(f)
        for ID in data.keys():
            timeMatch[ID] = None

def disConnect():
    for client in clients:
        client.sendall(bytes("disconnect","utf8"))
root = tk.Tk()

print("Chờ kết nối từ các client...")
tUI = thread.Thread(target=threadUI)
tUI.start()

loadData()
root.config(bg="#CECCBE")
root.protocol("WM_DELETE_WINDOW", onClosing)
root.mainloop()
