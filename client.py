import socket
import threading as thread
from tkinter import *
import tkinter.messagebox as tkmes
import tkinter.ttk as ttk
import pickle
import datetime

isConnected = False
isLogin = False
isSee = False

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ket noi toi server
HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)


def showSuccess(mes):
    tkmes.showinfo(title="Success", message=mes)


def showErr(mes):
    tkmes.showerror(title="Error", message=mes)


def validate(register, username, password):
    username = username.get()
    password = password.get()
    if(username == "" or password == ""):
        showErr("Username và password không được để trống")
        return
    if(" " in username or " " in password or len(username) < 5 or len(password) < 5):
        showErr(
            "Username và password phải có 5 ký tự trở lên và không chứa khoảng trắng")
        return
    else:
        if(register):
            try:
                clientSocket.sendall(bytes('r'+username+' '+password, 'utf8'))
            except:
                showErr("Lỗi kết nối đến server")
                return
        else:
            try:
                clientSocket.sendall(bytes('l'+username+' '+password, 'utf8'))
            except:
                showErr("Lỗi kết nối đến server")
                return
        result = clientSocket.recv(BUFSIZ).decode("utf8")
        if(result[0] == 'F'):
            showErr(result[2:])
        else:
            if(not register):
                global isLogin
                isLogin = True
                showSuccess(result[2:])
                if (username != "admin"):
                    clientWindow()
                else:
                    adminWindow()
            else:
                showSuccess(result[2:])


def createNewWindow(newWindow, name):
    newWindow.minsize(340, 250)
    newWindow.title(name)


def loginConsole():
    # username label and text entry box
    usernameLabel = Label(tkWindow, text="User Name")
    usernameLabel.grid(row=1, column=0, pady=(0, 20), sticky=W +
                       S+N+E, padx=(20, 20))

    usernameEntry = Entry(tkWindow)
    usernameEntry.grid(row=1, column=1, pady=(0, 20), sticky=W +
                       S+N+E, padx=(0, 20))

    # password label and password entry box
    passwordLabel = Label(tkWindow, text="Password")
    passwordLabel.grid(row=2, column=0, pady=(0, 20), sticky=W +
                       S+N+E, padx=(20, 20))

    passwordEntry = Entry(tkWindow, show="*")
    passwordEntry.grid(row=2, column=1, pady=(0, 20), sticky=W +
                       S+N+E, padx=(0, 20))

    loginButton = Button(tkWindow, text="Login", command=lambda: validate(
        False, usernameEntry, passwordEntry))
    loginButton.grid(row=3, column=0, pady=(0, 20), sticky=W +
                     S+N+E, padx=(20, 20))

    RegisButton = Button(tkWindow, text="Register",
                         command=lambda: validate(True, usernameEntry, passwordEntry))
    RegisButton.grid(row=3, column=1, pady=(0, 20), sticky=W +
                     N+S, padx=(0, 20), ipadx=10)


def onClosing():
    global isConnected
    if (isConnected):
        try:
            clientSocket.sendall(bytes('-quit-', 'utf8'))
        except:
            pass
    clientSocket.close()
    tkWindow.destroy()


def onClosing2(parent, current):
    parent.grab_set()
    current.destroy()
    
def clientWindow():
    global isSee
    isSee = False

    def see():
        global isSee
        isSee = True
        tree.delete(*tree.get_children())
        try:
            clientSocket.sendall(bytes("-seematch-", "utf8"))
        except:
            showErr("Lỗi kết nối đến server")
            return
        match = clientSocket.recv(BUFSIZ*BUFSIZ)
        infoMatch = pickle.loads(match)
        currentDate = ""
        for tempMatch in infoMatch:
            if(tempMatch[1][:10] != currentDate):
                currentDate = tempMatch[1][:10]
                tree.insert("", 'end',
                            values=("", "", "", currentDate, ""), tags=("Date",))
            tree.insert("", 'end',
                        values=(tempMatch[0], tempMatch[2], tempMatch[3], tempMatch[4], tempMatch[5]))

    def detail():
        # pid parameter
        global isSee
        if (not isSee):
            return
        detailsWindow = Toplevel(newWindow)
        createNewWindow(detailsWindow, "Details")
        detailsWindow.minsize(30, 50)
        tree = ttk.Treeview(detailsWindow, selectmode='browse')
        tree.grid(row=1, column=0, columnspan=4, sticky=W+N +
                  S+E, padx=(20, 0), pady=20)

        vsb = ttk.Scrollbar(
            detailsWindow, orient="vertical", command=tree.yview)
        vsb.grid(row=1, column=4, sticky=W+N +
                 S, padx=(0, 20), pady=(20))
        tree.configure(yscrollcommand=vsb.set)
        tree["columns"] = ("1", "2", "3", "4")
        tree['show'] = 'headings'
        tree.column("1", width=50, anchor='c')
        tree.column("2", width=150, anchor='c')
        tree.column("3", width=50, anchor='c')
        tree.column("4", width=150, anchor='c')
        tree.heading("1", text="Time")
        tree.heading("2", text="Team1")
        tree.heading("3", text="Score")
        tree.heading("4", text="Team2")

        def sendID():
            try:
                clientSocket.sendall(bytes("-detailmatch-", "utf8"))

                IDdetails = ID.get("1.0", END)[:-1]
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                details = pickle.loads(
                    clientSocket.recv(BUFSIZ*BUFSIZ))["send"]
                tree.delete(*tree.get_children())
                i = 2
                t1Score = 0
                t2Score = 0
                tree.insert("", 'end', text="L"+str(0),
                            values=(details[0][0], details[0][1], details[0][2], details[0][3]))
                tree.insert("", 'end', text="L"+str(1))
                HTadded = False
                for event in details[1]:
                    if(event[3] == '1'):
                        if int(event[1]) > 45:
                            if(not HTadded):
                                tree.insert("", 'end', text="L"+str(i),
                                            values=("HT", "", str(t1Score)+":"+str(t2Score), ""))
                                HTadded = True
                                i += 1
                        if(event[2] == "score"):
                            t1Score += 1
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', event[0]+" ghi bàn", str(t1Score)+":"+str(t2Score), ""))
                        if(event[2] == "yellow"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', event[0]+" bị thẻ vàng", "", ""))
                        if(event[2] == "red"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', event[0]+" bị thẻ đỏ", "", ""))
                    if(event[3] == '2'):
                        if int(event[1]) > 45:
                            if(not HTadded):
                                tree.insert("", 'end', text="L"+str(i),
                                            values=("HT", "", str(t1Score)+":"+str(t2Score), ""))
                                HTadded = True
                                i += 1
                        if(event[2] == "score"):
                            t2Score += 1
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', "", str(t1Score)+":"+str(t2Score), event[0]+" ghi bàn"))
                        if(event[2] == "yellow"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', "", "", event[0]+" bị thẻ vàng"))
                        if(event[2] == "red"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(event[1]+'\'', "", "", event[0]+" bị thẻ đỏ"))
                    i += 1

            else:
                showErr("ID không tồn tại")
        ID = Text(detailsWindow, height=1, width=50)
        ID.grid(row=0, column=0, pady=10,
                padx=(20, 20), sticky=W+S +
                N+E)
        ID.insert(END, 'Nhập ID')
        sendBtn = Button(
            detailsWindow, height=1, width=12, text="Gửi", command=sendID)
        sendBtn.grid(row=0, column=1, sticky=W+N +
                     S+E, pady=10, padx=(0, 20))
        detailsWindow.protocol("WM_DELETE_WINDOW",
                               lambda: onClosing2(newWindow, detailsWindow))
        detailsWindow.grab_set()
        detailsWindow.mainloop()

    def onclosingClientWindow():
        if tkmes.askokcancel("Log out", "Bạn có muốn log out khỏi tài khoản?"):
            logout()

    def logout():
        try:
            clientSocket.sendall(bytes("-logout-", "utf8"))
        except:
            pass
        global isLogin
        isLogin = False
        newWindow.destroy()
        tkWindow.deiconify()

    newWindow = Toplevel(tkWindow)
    tkWindow.withdraw()
    createNewWindow(newWindow, "Client")
    newWindow.minsize(340, 360)
    newWindow.config(bg="#CECCBE")

    seeBtn = Button(newWindow, height=3, width=10,
                    text="Xem", command=see)
    seeBtn.grid(row=0, column=0, sticky=W+N +
                S+E, pady=20, padx=(110, 50))
    detailBtn = Button(newWindow, height=3, width=10,
                       text="Chi tiết", command=detail)
    detailBtn.grid(row=0, column=1, sticky=W+N +
                   S+E, pady=20, padx=(0, 50))
    logoutBtn = Button(newWindow, height=3, width=10,
                       text="Log out", command=logout)
    logoutBtn.grid(row=0, column=2, sticky=W+N +
                   S+E, pady=20, padx=(0, 50))
    tree = ttk.Treeview(newWindow, selectmode='browse')
    tree.grid(row=1, column=0, columnspan=5, sticky=W+N +
              S+E, padx=(20, 0))

    vsb = ttk.Scrollbar(newWindow, orient="vertical", command=tree.yview)
    vsb.grid(row=1, column=5, sticky=W+N +
             S, padx=(0, 20))
    tree.configure(yscrollcommand=vsb.set)
    tree["columns"] = ("1", "2", "3", "4", "5")
    tree['show'] = 'headings'
    tree.column("1", width=50, anchor='c')
    tree.column("2", width=50, anchor='c')
    tree.column("3", width=200, anchor='c')
    tree.column("4", width=100, anchor='c')
    tree.column("5", width=200, anchor='c')
    tree.heading("1", text="ID")
    tree.heading("2", text="State")
    tree.heading("3", text="Team1")
    tree.heading("4", text="Score")
    tree.heading("5", text="Team2")
    tree.tag_configure('Date', background='#e8e8e8')
    newWindow.protocol("WM_DELETE_WINDOW", onclosingClientWindow)
    newWindow.grab_set()
    newWindow.mainloop()

def adminWindow():
    global isSee
    isSee = False

    def see():
        global isSee
        isSee = True
        tree.delete(*tree.get_children())
        try:
            clientSocket.sendall(bytes("-seematch-", "utf8"))
        except:
            showErr("Lỗi kết nối đến server")
            return
        match = clientSocket.recv(BUFSIZ*BUFSIZ)
        infoMatch = pickle.loads(match)
        currentDate = ""
        for tempMatch in infoMatch:
            if(tempMatch[1][:10] != currentDate):
                currentDate = tempMatch[1][:10]
                tree.insert("", 'end',
                            values=("", "", "", currentDate, ""), tags=("Date",))
            tree.insert("", 'end',
                        values=(tempMatch[0], tempMatch[2], tempMatch[3], tempMatch[4], tempMatch[5]))

    def detail():
        # pid parameter
        global isSee
        if (not isSee):
            return
        detailsWindow = Toplevel(newWindow)
        createNewWindow(detailsWindow, "Details")
        detailsWindow.minsize(500, 600)
        detailsWindow.resizable(False,False)
        detailsWindow.config(bg="#CECCBE")
        
                
        def sendID():
            try:
                clientSocket.sendall(bytes("-detailmatch-", "utf8"))

                IDdetails = ID.get()
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                details = pickle.loads(
                    clientSocket.recv(BUFSIZ*BUFSIZ))["send"]
                tree.delete(*tree.get_children())
                i = 2
                t1Score = 0
                t2Score = 0
                tree.insert("", 'end', text="L"+str(0),
                            values=("",details[0][0], details[0][1], details[0][2], details[0][3]))
                tree.insert("", 'end', text="L"+str(1))
                HTadded = False
                for event in details[1]:
                    if(event[3] == '1'):
                        if int(event[1]) > 45:
                            if(not HTadded):
                                tree.insert("", 'end', text="L"+str(i),
                                            values=(str(i-1), "HT", "", str(t1Score)+":"+str(t2Score), ""))
                                HTadded = True
                                i += 1
                        if(event[2] == "score"):
                            t1Score += 1
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', event[0]+" ghi bàn", str(t1Score)+":"+str(t2Score), ""))
                        if(event[2] == "yellow"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', event[0]+" bị thẻ vàng", "", ""))
                        if(event[2] == "red"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', event[0]+" bị thẻ đỏ", "", ""))
                    if(event[3] == '2'):
                        if int(event[1]) > 45:
                            if(not HTadded):
                                tree.insert("", 'end', text="L"+str(i),
                                            values=(str(i-1),"HT", "", str(t1Score)+":"+str(t2Score), ""))
                                HTadded = True
                                i += 1
                        if(event[2] == "score"):
                            t2Score += 1
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', "", str(t1Score)+":"+str(t2Score), event[0]+" ghi bàn"))
                        if(event[2] == "yellow"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', "", "", event[0]+" bị thẻ vàng"))
                        if(event[2] == "red"):
                            tree.insert("", 'end', text="L"+str(i),
                                        values=(str(i-1),event[1]+'\'', "", "", event[0]+" bị thẻ đỏ"))
                    i += 1

            else:
                showErr("ID không tồn tại")
                
        def removeEve():
            try:
                clientSocket.sendall(bytes("-removeevent-", "utf8"))
                
                IDdetails = ID.get()
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                sTTRemove = removeEvent.get()
                if (sTTRemove.isnumeric()):
                    try:
                        clientSocket.sendall(bytes(sTTRemove, "utf8"))
                    except:
                        showErr("Lối kết nối đến server")
                        return
                    removeComplete = clientSocket.recv(BUFSIZ).decode("utf8")
                    if (removeComplete=="-removefail-"):
                        showError("Số thứ tự không hợp lệ")
                    else:
                        showSuccess("Đã xóa thành công")
                        details = pickle.loads(
                    clientSocket.recv(BUFSIZ*BUFSIZ))["send"]
                        tree.delete(*tree.get_children())
                        i = 2
                        t1Score = 0
                        t2Score = 0
                        tree.insert("", 'end', text="L"+str(0),
                                    values=("",details[0][0], details[0][1], details[0][2], details[0][3]))
                        tree.insert("", 'end', text="L"+str(1))
                        HTadded = False
                        for event in details[1]:
                            if(event[3] == '1'):
                                if int(event[1]) > 45:
                                    if(not HTadded):
                                        tree.insert("", 'end', text="L"+str(i),
                                                    values=(str(i-1), "HT", "", str(t1Score)+":"+str(t2Score), ""))
                                        HTadded = True
                                        i += 1
                                if(event[2] == "score"):
                                    t1Score += 1
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', event[0]+" ghi bàn", str(t1Score)+":"+str(t2Score), ""))
                                if(event[2] == "yellow"):
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', event[0]+" bị thẻ vàng", "", ""))
                                if(event[2] == "red"):
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', event[0]+" bị thẻ đỏ", "", ""))
                            if(event[3] == '2'):
                                if int(event[1]) > 45:
                                    if(not HTadded):
                                        tree.insert("", 'end', text="L"+str(i),
                                                    values=(str(i-1),"HT", "", str(t1Score)+":"+str(t2Score), ""))
                                        HTadded = True
                                        i += 1
                                if(event[2] == "score"):
                                    t2Score += 1
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', "", str(t1Score)+":"+str(t2Score), event[0]+" ghi bàn"))
                                if(event[2] == "yellow"):
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', "", "", event[0]+" bị thẻ vàng"))
                                if(event[2] == "red"):
                                    tree.insert("", 'end', text="L"+str(i),
                                                values=(str(i-1),event[1]+'\'', "", "", event[0]+" bị thẻ đỏ"))
                            i += 1
                    
                else:
                    showErr("Phải nhập vào một số")
            else:
                showErr("ID không tồn tại")
        
        def setStartTime():
            try:
                clientSocket.sendall(bytes("-settimestart-", "utf8"))
                
                IDdetails = ID.get()
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                checkTime = None
                newTimeStart = changeTimeStart.get()
                try:
                    checkTime = datetime.datetime.strptime(
                        newTimeStart.strip(" ")+":00", '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    showErr("Định dạng thời gian không hợp lệ")
                    return
                
                if (checkTime < datetime.datetime.now()):
                    showErr("Thời gian không hợp lệ")
                    return
                
                try:
                    clientSocket.sendall(bytes(str(checkTime),"utf8"))
                except:
                    showErr("Lỗi kết nối đến server")
                    return
                
            else:
                showErr("ID không tồn tại")
            
        
        def duringTime():
            try:
                clientSocket.sendall(bytes("-settimematch-", "utf8"))
                
                IDdetails = ID.get()
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                print("OKie")
            else:
                showErr("ID không tồn tại")
                
        def addEve():
            namePlayer = nameSoccer.get()
            timeEve = timeEvent.get()
            if (len(namePlayer)==0):
                showErr("Không được để trống tên cầu thủ")
                return
            if (not timeEve.isnumeric()):
                showErr("Thời gian phải là một con số")
                return
            try:
                clientSocket.sendall(bytes(namePlayer,"utf8"))
                clientSocket.sendall(bytes(timeEve,"utf8"))
            except:
                showErr("Lỗi kết nối đến server")
            try:
                clientSocket.sendall(bytes("-addevent-", "utf8"))
                
                IDdetails = ID.get()
                clientSocket.sendall(bytes(IDdetails, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            checkSelect = True
            complete = clientSocket.recv(BUFSIZ).decode("utf8")
            if (complete == "getsuccess"):
                teamSelected = teamChoice.current()
                eventSelected = eventChoice.current()
                
                if (teamSelected==0): # team 1
                    if (eventSelected==0):#ghi bàn
                        try:
                            clientSocket.sendall(bytes("-team1score-","utf8"))
                        except:
                            return
                    elif (eventSelected==1):#thẻ đỏ
                        try:
                            clientSocket.sendall(bytes("-team1red-","utf8"))
                        except:
                            return
                    elif (eventSelected==2):#thẻ vàng
                        try:
                            clientSocket.sendall(bytes("-team1yellow-","utf8"))
                        except:
                            return
                    else:
                        checkSelect = False
                elif (teamSelected==1):
                    if (eventSelected==0):#ghi bàn
                        try:
                            clientSocket.sendall(bytes("-team2score-","utf8"))
                        except:
                            return
                    elif (eventSelected==1):#thẻ đỏ
                        try:
                            clientSocket.sendall(bytes("-team2red-","utf8"))
                        except:
                            return
                    elif (eventSelected==2):#thẻ vàng
                        try:
                            clientSocket.sendall(bytes("-team2yellow-","utf8"))
                        except:
                            return
                    else:
                        checkSelect = False
                else:
                    checkSelect = False
            elif (complete == "nochange"):
                showErr("Không thể cập nhật cho trận đấu chưa diễn ra")
            else:
                showErr("ID không tồn tại")
            if (not checkSelect):
                showErr("Hãy chọn đội và sự kiện trước khi gửi")
            else:
                showSuccess("Thêm sự kiện thành công")
                
        
        labelID = Label(detailsWindow,text="Nhập ID")

        labelID.place(relx=0.033, rely=0.02, relwidth=0.15,relheight=0.05)
        
        ID = Entry(detailsWindow)
        ID.place(relx=0.2,rely=0.02,relwidth=0.6,relheight=0.05)
        
        sendIDBtn = Button(detailsWindow,text="Gửi",command=sendID)
        sendIDBtn.place(relx=0.825,rely=0.02,relwidth=0.15,relheight=0.05)
        
        labelRemove = Label(detailsWindow,text="STT Sự kiện")
        labelRemove.place(relx=0.033, rely=0.085, relwidth=0.25,relheight=0.05)
        
        removeEvent = Entry(detailsWindow)
        removeEvent.place(relx=0.3,rely=0.085,relwidth=0.5,relheight=0.05)
        
        removeEventBtn = Button(detailsWindow,text="Xóa",command=removeEve)
        removeEventBtn.place(relx=0.825,rely=0.085,relwidth=0.15,relheight=0.05)
        
        labelIimeMatch = Label(detailsWindow,text="Thời gian thi đấu")
        labelIimeMatch.place(relx=0.033, rely=0.15, relwidth=0.25,relheight=0.05)
        
        changeTimeMatch = Entry(detailsWindow)
        changeTimeMatch.place(relx=0.3,rely=0.15,relwidth=0.5,relheight=0.05)
        
        setTimeMatchtBtn = Button(detailsWindow,text="Cập nhật",command=duringTime)
        setTimeMatchtBtn.place(relx=0.825,rely=0.15,relwidth=0.15,relheight=0.05)
        
        labelIimeStart = Label(detailsWindow,text="Thời gian bắt đầu")
        labelIimeStart.place(relx=0.033, rely=0.215, relwidth=0.25,relheight=0.05)
        
        changeTimeStart = Entry(detailsWindow)
        changeTimeStart.place(relx=0.3,rely=0.215,relwidth=0.5,relheight=0.05)
        
        setTimeStartBtn = Button(detailsWindow,text="Cập nhật",command=setStartTime)
        setTimeStartBtn.place(relx=0.825,rely=0.215,relwidth=0.15,relheight=0.05)
        
        labelTeam = Label(detailsWindow,text="Chọn đội")
        labelTeam.place(relx=0.033, rely=0.28, relwidth=0.17,relheight=0.05)
        
        teamChoice = ttk.Combobox(detailsWindow,
                                        textvariable=StringVar())
        teamChoice.place(relx=0.22, rely=0.28, relwidth=0.28,relheight=0.05)
        teamChoice['values'] = ("Team1","Team2")
        
        labelEvent = Label(detailsWindow,text="Chọn sự kiện")
        labelEvent.place(relx=0.52, rely=0.28, relwidth=0.19,relheight=0.05)
        
        eventChoice = ttk.Combobox(detailsWindow,
                                        textvariable=StringVar())
        eventChoice.place(relx=0.73, rely=0.28, relwidth=0.24,relheight=0.05)
        eventChoice['values'] = ("Ghi bàn","Thẻ đỏ","Thẻ vàng")
        
        labelName = Label(detailsWindow,text="Tên cầu thủ")
        labelName.place(relx=0.033, rely=0.35, relwidth=0.17,relheight=0.05)
        
        nameSoccer = Entry(detailsWindow)
        nameSoccer.place(relx=0.22, rely=0.35, relwidth=0.28,relheight=0.05)
        
        labelTime = Label(detailsWindow,text="Phút")
        labelTime.place(relx=0.52, rely=0.35, relwidth=0.19,relheight=0.05)
        
        timeEvent = Entry(detailsWindow)
        timeEvent.place(relx=0.73, rely=0.35, relwidth=0.24,relheight=0.05)
        
        sendEventBtn = Button(detailsWindow,text="Cập nhật",command=addEve)
        sendEventBtn.place(relx=0.435,rely=0.415,relwidth=0.15,relheight=0.05)
        
        details = Frame(detailsWindow)
        details.place(relx=0.04,rely=0.48,relwidth=0.925,relheight=0.495)
        
        tree = ttk.Treeview(details, selectmode='browse')
        tree.pack(side=LEFT, fill=BOTH, expand=TRUE)
        
        vsb = ttk.Scrollbar(details, orient="vertical", command=tree.yview)
        vsb.pack(fill=Y, side=RIGHT, expand=FALSE)
        tree.configure(yscrollcommand=vsb.set)
        tree["columns"] = ("1", "2", "3", "4","5")
        tree['show'] = 'headings'
        tree.column("1", width=50, anchor='c')
        tree.column("2", width=50, anchor='c')
        tree.column("3", width=140, anchor='c')
        tree.column("4", width=50, anchor='c')
        tree.column("5", width=140, anchor='c')
        tree.heading("1", text="STT")
        tree.heading("2", text="Time")
        tree.heading("3", text="Team1")
        tree.heading("4", text="Score")
        tree.heading("5", text="Team2")
        
        detailsWindow.protocol("WM_DELETE_WINDOW",
                               lambda: onClosing2(newWindow, detailsWindow))
        detailsWindow.grab_set()
        detailsWindow.mainloop()
        

    def addNewMatch():
        addmatchWindow = Toplevel(newWindow)
        createNewWindow(addmatchWindow, "Add New Match")
        addmatchWindow.minsize(30, 50)
        addmatchWindow.config(bg="#CECCBE")

        labelNameTeam1 = Label(
            addmatchWindow, text="Nhập tên đội 1:")

        labelNameTeam1.grid(row=0, column=0, pady=20, sticky=W +
                            S+N+E, padx=20)
        NameTeam1 = Text(addmatchWindow, height=1, width=35)
        NameTeam1.grid(row=0, column=1, pady=20,
                       padx=(0, 20), sticky=W+S +
                       N+E)

        labelNameTeam2 = Label(
            addmatchWindow, text="Nhập tên đội 2:")

        labelNameTeam2.grid(row=1, column=0, pady=(0, 20), sticky=W +
                            S+N+E, padx=20)
        NameTeam2 = Text(addmatchWindow, height=1, width=35)
        NameTeam2.grid(row=1, column=1, pady=(0, 20),
                       padx=(0, 20), sticky=W+S +
                       N+E)

        labelTimeMatch = Label(
            addmatchWindow, text="Nhập thời gian thi đấu:")

        labelTimeMatch.grid(row=2, column=0, pady=(0, 20), sticky=W +
                            S+N+E, padx=20)
        TimeMatch = Text(addmatchWindow, height=1, width=35)
        TimeMatch.grid(row=2, column=1, pady=(0, 20),
                       padx=(0, 20), sticky=W+S +
                       N+E)

        def sendInfo():
            Name1 = NameTeam1.get("1.0", END)[:-1]
            Name2 = NameTeam2.get("1.0", END)[:-1]
            newTimeStart = TimeMatch.get("1.0", END)[:-1]
            if (len(Name1) == 0 or len(Name2) == 0):
                showErr("Tên đội không được để trống")
                return

            checkTime = None
            try:
                checkTime = datetime.datetime.strptime(
                    newTimeStart.strip(" ")+":00", '%Y-%m-%d %H:%M:%S')
            except ValueError:
                showErr("Định dạng thời gian không hợp lệ")
                return

            if (checkTime < datetime.datetime.now()):
                showErr("Thời gian không hợp lệ")
                return

            try:
                clientSocket.sendall(bytes("-addmatch-", "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return

            matchInfo = {}
            matchInfo["info"] = [Name1, Name2, str(checkTime)]
            clientSocket.sendall(pickle.dumps(matchInfo))
            showSuccess("Thêm trận đấu thành công")

        sendBtn = Button(addmatchWindow, height=1, width=10, text="Gửi",
                         command=sendInfo)
        sendBtn.grid(row=3, column=0, pady=(0, 20), sticky=W +
                     S+N+E, padx=20)

        addmatchWindow.protocol("WM_DELETE_WINDOW",
                                lambda: onClosing2(newWindow, addmatchWindow))
        addmatchWindow.grab_set()
        addmatchWindow.mainloop()

    def removeMatch():
        # pid parameter
        global isSee
        if (not isSee):
            return
        removeWindow = Toplevel(newWindow)
        createNewWindow(removeWindow, "Details")
        removeWindow.minsize(30, 50)
        removeWindow.config(bg="#CECCBE")
        
        def sendID():
            try:
                clientSocket.sendall(bytes("-removematch-", "utf8"))
                IDremove = ID.get("1.0", END)[:-1]
                clientSocket.sendall(bytes(IDremove, "utf8"))
            except:
                showErr("Lỗi kết nối đến server")
                return
            
            removeMessage = clientSocket.recv(1024).decode("utf8")
            if (removeMessage=="-notexist-"):
                showErr("ID không tồn tại")
            elif (removeMessage=="-removefail-"):
                showErr("Không thể xóa thông tin các trận đã hoặc đang đấu")
            else:
                showSuccess("Xóa thành công")
        
        ID = Text(removeWindow, height=1, width=50)
        ID.grid(row=0, column=0, pady=10,
                padx=(20, 20), sticky=W+S +
                N+E)
        ID.insert(END, 'Nhập ID')
        sendBtn = Button(
            removeWindow, height=1, width=12, text="Gửi", command=sendID)
        sendBtn.grid(row=0, column=1, sticky=W+N +
                     S+E, pady=10, padx=(0, 20))
        removeWindow.protocol("WM_DELETE_WINDOW",
                               lambda: onClosing2(newWindow, removeWindow))
        removeWindow.grab_set()
        removeWindow.mainloop()

    def onclosingClientWindow():
        if tkmes.askokcancel("Log out", "Bạn có muốn log out khỏi tài khoản?"):
            logout()

    def logout():
        try:
            clientSocket.sendall(bytes("-logout-", "utf8"))
        except:
            pass
        global isLogin
        isLogin = False
        newWindow.destroy()
        tkWindow.deiconify()

    newWindow = Toplevel(tkWindow)
    tkWindow.withdraw()
    createNewWindow(newWindow, "Admin")
    newWindow.minsize(340, 360)
    newWindow.config(bg="#CECCBE")
    seeBtn = Button(newWindow, height=3, width=10,
                    text="Xem", command=see)
    seeBtn.grid(row=0, column=0, sticky=W+N +
                S+E, pady=20, padx=(30, 50))
    detailBtn = Button(newWindow, height=3, width=10,
                       text="Chi tiết", command=detail)
    detailBtn.grid(row=0, column=1, sticky=W+N +
                   S+E, pady=20, padx=(0, 50))
    logoutBtn = Button(newWindow, height=3, width=10,
                       text="Log out", command=logout)
    logoutBtn.grid(row=0, column=2, sticky=W+N +
                   S+E, pady=20, padx=(0, 50))

    addBtn = Button(newWindow, height=3, width=10,
                    text="Thêm trận", command=addNewMatch)
    addBtn.grid(row=0, column=3, sticky=W+N +
                S+E, pady=20, padx=(0, 50))

    delBtn = Button(newWindow, height=3, width=10,
                    text="Xóa trận", command=removeMatch)
    delBtn.grid(row=0, column=4, sticky=W+N +
                S+E, pady=20, padx=(0, 50))

    tree = ttk.Treeview(newWindow, selectmode='browse')
    tree.grid(row=1, column=0, columnspan=5, sticky=W+N +
              S+E, padx=(20, 0))

    vsb = ttk.Scrollbar(newWindow, orient="vertical", command=tree.yview)
    vsb.grid(row=1, column=5, sticky=W+N +
             S, padx=(0, 20))
    tree.configure(yscrollcommand=vsb.set)
    tree["columns"] = ("1", "2", "3", "4", "5")
    tree['show'] = 'headings'
    tree.column("1", width=50, anchor='c')
    tree.column("2", width=50, anchor='c')
    tree.column("3", width=200, anchor='c')
    tree.column("4", width=100, anchor='c')
    tree.column("5", width=200, anchor='c')
    tree.heading("1", text="ID")
    tree.heading("2", text="State")
    tree.heading("3", text="Team1")
    tree.heading("4", text="Score")
    tree.heading("5", text="Team2")
    tree.tag_configure('Date', background='#e8e8e8')
    newWindow.protocol("WM_DELETE_WINDOW", onclosingClientWindow)
    newWindow.grab_set()
    newWindow.mainloop()


def submitIP():
    host = entryIP.get()
    port = 33000
    serverAddress = (host, port)
    global clientSocket
    try:
        clientSocket.connect(serverAddress)
        data = clientSocket.recv(1024).decode("utf8")
        if data == "-connected-":
            showSuccess("Kết nối thành công")
            global isConnected
            isConnected = True
            loginConsole()
        else:
            showErr("Kết nối thất bại")
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except:
        showErr("Kết nối thất bại")


def threadSubmit():
    global isConnected
    if (isConnected):
        return
    # tkWindow1.attributes('-alpha',0)
    # tkWindow.mainloop()
    tConnect = thread.Thread(target=submitIP)
    tConnect.start()


def threadUISubmit():
    ipBtn = Button(tkWindow, text="Kết nối", command=threadSubmit)
    ipBtn.grid(row=0, column=2, sticky=W+S +
               N+E, pady=20, padx=(0, 10))


tkWindow = Tk()
tkWindow.title("Connect")

tkWindow.config(bg="#CECCBE")
#tkWindow.title('Log in')


def fixed_map(option):
    return [elm for elm in style.map('Treeview', query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]


style = ttk.Style()
style.map('Treeview', foreground=fixed_map('foreground'),
          background=fixed_map('background'))


# connect button
labelIP = Label(tkWindow, text="Nhập IP:")
labelIP.grid(row=0, column=0, pady=20, sticky=W +
             S+N+E, padx=(20, 20))

entryIP = Entry(tkWindow)
entryIP.grid(row=0, column=1, pady=20, sticky=W +
             S+N+E, padx=(0, 20))

entryIP.insert(END, '127.0.0.1')

tkWindow.protocol("WM_DELETE_WINDOW", onClosing)

submitThread = thread.Thread(target=threadUISubmit)
submitThread.start()
tkWindow.mainloop()  # Starts GUI execution.
