import socket
import threading as thread
from tkinter import *
import json
import datetime
import pickle
import tkinter.messagebox as tkmes

clients = {}  # danh sách client đã kết nối và trạng thái kết nối
addresses = {}  # danh sách client và địa chỉ
account = {}  # danh sách tài khoản
data = {}  # danh sách thông tin trận đấu
loginStatusList = {}  # những client đã login
timeMatch = {}  # Ghi thời gian diễn ra trận đấu

HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

isConnected = False
maxNumberOfClient = 0


def showSuccess(mes):
    tkmes.showinfo(title="Success", message=mes)


def showErr(mes):
    tkmes.showerror(title="Error", message=mes)


def acceptIncomingConnections():
    while True:
        try:
            client, clientAddress = SERVER.accept()
            global maxNumberOfClient
            if(len(clients) >= maxNumberOfClient):
                client.sendall(bytes("-fail-", "utf8"))
                client.close()
                continue
            client.sendall(bytes("-connected-", "utf8"))
            print("%s:%s has connected." % clientAddress)
            clients[client] = True
            addresses[client] = clientAddress
            thread.Thread(target=handleClient, args=(client,)).start()
            # có kết nối tới thì gưi qua 1 tin nhắn
        except:
            break


def getDeltaTime(start):
    now = datetime.datetime.now()
    startTimeObj = datetime.datetime.strptime(start[2:], "%y-%m-%d %H:%M:%S")
    if (now < startTimeObj):
        return -2

    during = now - startTimeObj
    if (str(type(during)) == str(type(datetime.datetime.now()))):
        if (during.day > 0):
            return 1000
        res = int(during.hours)*60 + int(during.minutes)
        return res
    else:
        return int(during.total_seconds()/60.0)


def updateState(pid):
    global data
    global timeMatch
    match = data[pid]
    start = match["start"]
    deltaTime = getDeltaTime(start)
    if (deltaTime < 0):
        timeTemp = datetime.datetime.strptime(
            data[pid]["start"][2:], "%y-%m-%d %H:%M:%S")
        timeMatch[pid] = "{0:02d}:{1:02d}".format(
            timeTemp.hour, timeTemp.minute)
    else:
        if (deltaTime < 45):
            timeMatch[pid] = str(deltaTime+1) + "\'"
        elif (deltaTime < 60):
            timeMatch[pid] = "HT"
        elif (deltaTime < 105):
            timeMatch[pid] = str(deltaTime - 15 + 1) + "\'"
        else:
            timeMatch[pid] = "FT"


def getMaxID():
    global data
    maxID = 0
    for KEY in data.keys():
        temp = int(KEY)
        if (temp > maxID):
            maxID = temp

    return maxID


def handleClient(client):  # Takes client socket as argument.
    global account
    global data
    global loginStatusList
    isLogin = False
    currentName = None

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
                        currentName = name
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
        elif message == "-seematch-":
            Line = []
            loadMatchData()
            for ID in data.keys():
                updateState(ID)
                if (":" in timeMatch[ID]):
                    Line.append([ID, data[ID]["start"], timeMatch[ID], data[ID]["team1"]["name"],
                                 "? : ?", data[ID]["team2"]["name"]])
                else:
                    Line.append([ID, data[ID]["start"], timeMatch[ID], data[ID]["team1"]["name"],
                                 str(len(data[ID]["team1"]["scorer"]))+":" +
                                 str(len(data[ID]["team2"]["scorer"])),
                                 data[ID]["team2"]["name"]])
            newLine = sorted(Line, key=lambda k: datetime.datetime.strptime(
                k[1], '%Y-%m-%d %H:%M:%S'))
            client.sendall(pickle.dumps(newLine))

        elif message == "-detailmatch-" or message == "-removeevent-":
            ID = client.recv(BUFSIZ).decode("utf8").strip(" ")
            if (ID not in data.keys()):
                client.sendall(bytes("getfail", "utf8"))
                continue
            client.sendall(bytes("getsuccess", "utf8"))
            res = None
            loadMatchData()
            updateState(ID)
            if (":" in timeMatch[ID]):
                res = [timeMatch[ID], data[ID]["team1"]["name"],
                       "? : ?", data[ID]["team2"]["name"]]
            else:
                res = [timeMatch[ID], data[ID]["team1"]["name"],
                       str(len(data[ID]["team1"]["scorer"]))+":" +
                       str(len(data[ID]["team2"]["scorer"])),
                       data[ID]["team2"]["name"]]

            details = data[ID]
            listEvent = {}
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
                for j in range(i+1, len(events)):
                    if (int(events[i][1]) > int(events[j][1])):
                        events[i], events[j] = events[j], events[i]
            listEvent["send"] = [res, events]
            if (message == "-detailmatch-"):
                client.sendall(pickle.dumps(listEvent))
            else:
                sTTRemove = int(client.recv(1024).decode("utf8").strip(" "))
                if (sTTRemove > len(events)+1 or len(events) == 0):
                    client.sendall(bytes("-removefail-", "utf8"))
                else:
                    client.sendall(bytes("-removesuccess-", "utf8"))

                    if (sTTRemove == len(events)+1):
                        del events[sTTRemove - 2]
                    elif (int(events[sTTRemove - 1][1]) > 45):
                        del events[sTTRemove - 2]
                    else:
                        del events[sTTRemove - 1]
                    details["team1"]["scorer"] = []
                    details["team1"]["red_card"] = []
                    details["team1"]["yellow_card"] = []
                    details["team2"]["scorer"] = []
                    details["team2"]["red_card"] = []
                    details["team2"]["yellow_card"] = []
                    for Eve in events:
                        if Eve[3] == "1":
                            if (Eve[2] == "score"):
                                details["team1"]["scorer"].append(
                                    [Eve[0], Eve[1]])
                            elif (Eve[2] == "red"):
                                details["team1"]["red_card"].append(
                                    [Eve[0], Eve[1]])
                            else:
                                details["team1"]["yellow_card"].append(
                                    [Eve[0], Eve[1]])
                        else:
                            if (Eve[2] == "score"):
                                details["team2"]["scorer"].append(
                                    [Eve[0], Eve[1]])
                            elif (Eve[2] == "red"):
                                details["team2"]["red_card"].append(
                                    [Eve[0], Eve[1]])
                            else:
                                details["team2"]["yellow_card"].append(
                                    [Eve[0], Eve[1]])
                    data[ID] = details

                    with open('data.json', 'w') as f:
                        json.dump(data, f)
                        f.close()
                    updateState(ID)
                    if (":" in timeMatch[ID]):
                        res = [timeMatch[ID], data[ID]["team1"]["name"],
                               "? : ?", data[ID]["team2"]["name"]]
                    else:
                        res = [timeMatch[ID], data[ID]["team1"]["name"],
                               str(len(data[ID]["team1"]["scorer"]))+":" +
                               str(len(data[ID]["team2"]["scorer"])),
                               data[ID]["team2"]["name"]]
                    listEvent["send"] = [res, events]
                    client.sendall(pickle.dumps(listEvent))

        elif message == "-quit-":
            client.close()
            del clients[client]
            print("%s:%s has disconnected." % addresses[client])
            del addresses[client]
            break
        elif message == "-addmatch-":
            matchInfo = pickle.loads(client.recv(1024))["info"]
            maxID = getMaxID()
            newMatch = {}
            Team1 = {"name": matchInfo[0], "scorer": [
            ], "red_card": [], "yellow_card": []}
            Team2 = {"name": matchInfo[1], "scorer": [
            ], "red_card": [], "yellow_card": []}
            newMatch["start"] = matchInfo[2]
            newMatch["team1"] = Team1
            newMatch["team2"] = Team2
            data[str(maxID+1)] = newMatch

            with open('data.json', 'w') as f:
                json.dump(data, f)
                f.close()

        elif message == "-removematch-":
            ID = client.recv(BUFSIZ).decode("utf8").strip(" ")
            if (ID not in data.keys()):
                client.sendall(bytes("-notexist-", "utf8"))
                continue
            loadMatchData()
            updateState(ID)

            if (":" not in timeMatch[ID]):
                client.sendall(bytes("-removefail-", "utf8"))
            else:
                client.sendall(bytes("-removesuccess-", "utf8"))
                del data[ID]
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                    f.close()

        elif message == "-addevent-":
            ID = client.recv(BUFSIZ).decode("utf8").strip(" ")
            if (ID not in data.keys()):
                client.sendall(bytes("getfail", "utf8"))
                continue
            loadMatchData()
            updateState(ID)
            if (":" in timeMatch[ID]):
                client.sendall(bytes("nochange", "utf8"))
                continue
            client.sendall(bytes("getsuccess", "utf8"))
            eventAdded = pickle.loads(client.recv(BUFSIZ))
            addIn = eventAdded["addIn"]
            namePlayer = eventAdded["name"]
            timeEve = eventAdded["time"]
            details = data[ID]
            checkAdded = True
            if (addIn == "-team1score-"):
                if (timeMatch[ID] == "FT"):
                    details["team1"]["scorer"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team1"]["scorer"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False
                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team1"]["scorer"].append([namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            elif (addIn == "-team1red-"):
                if (timeMatch[ID] == "FT"):
                    details["team1"]["red_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team1"]["red_card"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False
                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team1"]["red_card"].append([namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            elif (addIn == "-team1yellow-"):
                if (timeMatch[ID] == "FT"):
                    details["team1"]["yellow_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team1"]["yellow_card"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False
                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team1"]["yellow_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            elif (addIn == "-team2score-"):
                if (timeMatch[ID] == "FT"):
                    details["team2"]["scorer"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team2"]["scorer"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False

                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team2"]["scorer"].append([namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            elif (addIn == "-team2red-"):
                if (timeMatch[ID] == "FT"):
                    details["team2"]["red_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team2"]["red_card"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False
                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team2"]["red_card"].append([namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            elif (addIn == "-team2yellow-"):
                if (timeMatch[ID] == "FT"):
                    details["team2"]["yellow_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                elif (timeMatch[ID] == "HT"):
                    if(int(timeEve) <= 45):
                        details["team2"]["yellow_card"].append(
                            [namePlayer, timeEve])
                        client.sendall(bytes("-addcomplete-", "utf8"))
                    else:
                        client.sendall(bytes("-addfail-", "utf8"))
                        checkAdded = False
                elif (int(timeMatch[ID][0:timeMatch[ID].find("'")]) >= int(timeEve)):
                    details["team2"]["yellow_card"].append(
                        [namePlayer, timeEve])
                    client.sendall(bytes("-addcomplete-", "utf8"))
                else:
                    client.sendall(bytes("-addfail-", "utf8"))
                    checkAdded = False
            else:
                client.sendall(bytes("-addfail-", "utf8"))
                checkAdded = False
            if (checkAdded):
                data[ID] = details
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                    f.close()
                res = None
                loadMatchData()
                updateState(ID)
                if (":" in timeMatch[ID]):
                    res = [timeMatch[ID], data[ID]["team1"]["name"],
                           "? : ?", data[ID]["team2"]["name"]]
                else:
                    res = [timeMatch[ID], data[ID]["team1"]["name"],
                           str(len(data[ID]["team1"]["scorer"]))+":" +
                           str(len(data[ID]["team2"]["scorer"])),
                           data[ID]["team2"]["name"]]

                details = data[ID]
                listEvent = {}
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
                    for j in range(i+1, len(events)):
                        if (int(events[i][1]) > int(events[j][1])):
                            events[i], events[j] = events[j], events[i]
                listEvent["send"] = [res, events]
                client.sendall(pickle.dumps(listEvent))

        elif message == "-settimestart-":
            ID = client.recv(BUFSIZ).decode("utf8").strip(" ")
            if (ID not in data.keys()):
                client.sendall(bytes("getfail", "utf8"))
                continue
            client.sendall(bytes("getsuccess", "utf8"))
            newTimeStart = client.recv(BUFSIZ).decode("utf8")
            updateState(ID)
            if (":" not in timeMatch[ID] or newTimeStart == "None"):
                client.sendall(bytes("-changefail-", "utf8"))
            else:
                data[ID]["start"] = newTimeStart
                updateState(ID)
                res = [timeMatch[ID], data[ID]["team1"]["name"],
                       "? : ?", data[ID]["team2"]["name"]]
                client.sendall(bytes("-changecompleted-", "utf8"))
                objRes = {}
                objRes["send"] = res
                client.sendall(pickle.dumps(objRes))
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                    f.close()

        elif message == "-logout-":
            isLogin = False
            loginStatusList[currentName] = False


def threadConnect(maxClientEntry):
    global isConnected
    if isConnected:
        return
    maxClient = maxClientEntry.get()
    if maxClient.isnumeric() and int(maxClient) > 0:
        SERVER.listen(0)
        global maxNumberOfClient
        maxNumberOfClient = int(maxClient)
        isConnected = True
        tConnect = thread.Thread(target=acceptIncomingConnections, daemon=True)
        tConnect.start()
        showSuccess("Mở server thành công")
    else:
        showErr("Vui lòng nhập số nguyên dương")


def threadUI():
    root.title("Server")
    labelMaxClient = Label(
        root, text="Nhập số lượng client có thể kết nối đồng thời:")
    labelMaxClient.grid(row=0, column=0, pady=20, sticky=W +
                        S+N+E, padx=(20, 20))
    maxClient = Entry(root)
    maxClient.grid(row=0, column=1, pady=20, sticky=W +
                   S+N+E, padx=(0, 20))
    openServerBtn = Button(root, text="Mở server",
                           command=lambda: threadConnect(maxClient))
    openServerBtn.grid(row=0, column=2, pady=20, sticky=W +
                       S+N+E, padx=(0, 20))


def onClosing():
    SERVER.close()
    root.destroy()


def loadAccountData():
    global account
    global loginStatusList
    with open("account.json") as f:
        accountLoad = json.load(f)
        for x in accountLoad:
            account[x] = accountLoad[x]
            loginStatusList[x] = False
        f.close()


def loadMatchData():
    global data
    global timeMatch
    with open("data.json") as f:
        data = json.load(f)
        for ID in data.keys():
            timeMatch[ID] = None
        f.close()


root = Tk()

tUI = thread.Thread(target=threadUI)
tUI.start()

loadMatchData()
loadAccountData()
root.config(bg="#CECCBE")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", onClosing)
root.mainloop()
