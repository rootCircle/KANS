# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:17:14 2021
Requirements:
    PIL library,mysql.connector,SQL DATABASE WITH localhost,user=root,password=password
@author: compaq
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from tkinter import messagebox,Radiobutton,Toplevel,PhotoImage,StringVar,OptionMenu
import mysql.connector as mysqlcon
#from time import ctime, time
from PIL import Image, ImageTk
import random

HOST="localhost"
USERNAME="root"
PASSWORD="password"
DATABASE="Kans"

class Apptools:
    def sql_run(self, *sql_query):
        """
        Parameters
        ----------
        self :- object
            Object which Hold the function.
        sql_query :- a tuple of string
            Queries to be run.

        Returns
        -------
        output :- nested list
            Each index contains the output of each query if possible empty list.

        Example
        -------
        >>> print(sql_run(None,'Select * from base;'))
        [[(1, 'a'), (2, 'B'), (3, 'C'), (4, 'D'), (5, 'D')]]
        >>> print(sql_run(None,'Insert into base values(6,"d");'))
        [[]]

        Info
        ----
        It return None(nothing) in case of any error

        Warning
        -------
        It can't run few sql commands(especially
        those which are non-void and doesn't start with SELECT or DESC/DESCRIBE).
        """
        output = []
        sql_connection = None
        try:
            sql_connection = mysqlcon.connect(host=HOST,user=USERNAME,passwd=PASSWORD)
            cursor = sql_connection.cursor()
            sql_query=list(sql_query)
            sql_query.insert(0, "Create database if not exists "+DATABASE+";")
            sql_query.insert(1, "Use "+DATABASE+";")
            for query in sql_query:
                cursor.execute(query)
                if query.upper().startswith(("SELECT","DESC")):
                    output.append(cursor.fetchall())
                else:
                    sql_connection.commit()
                    output.append([])
            cursor.close()
            return output[2:]
        except (mysqlcon.Error, mysqlcon.Warning) as error:
            messagebox.showwarning("Error", error)
        finally:
            if sql_connection:
                sql_connection.close()

    def image_Show(self, Dir, xrow, ycolumn, width, height,mode="grid"):

        Photo = Image.open(Dir)
        Photo = Photo.resize((width, height))
        render = ImageTk.PhotoImage(Photo)
        img = tk.Label(self, image=render)
        img.image = render
        if mode=='grid':
            img.grid(row=xrow, column=ycolumn, pady=3)
        else:
            img.place(x=xrow,y=ycolumn,relx=0,rely=0)

    def defaultquerylogindata(self,usertype):
        if usertype=="Admin":
            def_query = """Create table IF NOT exists logindataadmin(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            PIN INT NOT NULL,
            WalNo varchar(8) NOT NULL unique);"""
        elif usertype=="Buyer":
            def_query = """Create table IF NOT exists logindatabuyer(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            DelAdd varchar(250) not null,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            WalNo varchar(8) NOT NULL unique,
            PIN INT NOT NULL,
            IsPremium char(1) NOT NULL DEFAULT 'N');"""
        elif usertype=="Seller":
            def_query="""Create table IF NOT exists logindataseller(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            OrgName varchar(48) not null,
            AddOrg varchar(48) not null,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            WalNo varchar(8) NOT NULL unique,
            PIN INT NOT NULL);"""
        else:
            messagebox.showwarning("Invalid User Type!","Enter a valid User type")
            return
        return def_query

    def defaultquerywalletbank(self):
        def_query = """Create table IF NOT exists walletbank(
        WalNo varchar(8) NOT NULL primary KEY,
        UserType char(1) NOT NULL,
        Amt int NOT NULL,
        PIN INT NOT NULL);"""
        return def_query

    def defaultquerytempbank(self):
        def_query = """Create table IF NOT exists tempbank(
        SecCode varchar(16) NOT NULL primary KEY,
        encode bigint);"""
        return def_query

    def is_not_null(self, *text):
        if len(text)!=0:
            for msg in text:
                if msg == "":
                    return False
            return True
        else:
            return False

    def check_digit(self, *text):
        if len(text)!=0:
            for msg in text:
                counter = counter_2 = 0
                for i in msg:
                    if i == ".":
                        counter += 1
                    elif i == "-":
                        counter_2 += 1
                    elif not (i.isdigit()):
                        return False
                if counter > 1 or counter_2 > 1 or (counter_2==1 and msg[0]!="-") or msg=="":
                    return False
            return True
        else:
            return False

    def in_limit(self, lower, upper, *text):
        if len(text)!=0:
            for msg in text:
                if Apptools.check_digit(self,msg):
                    val = float(msg)
                    if val > upper or val < lower:
                        return False
                else:
                    return False
            return True
        else:
            return False

    def generate_id(self, table):
        query = "Select id from " + table+";"
        out = Apptools.sql_run(self, query)[0]
        k = 1
        list_id = []
        for i in range(len(out)):
            list_id.append(out[i][0])
        while k in list_id:
            k += 1
        return k

    def randomtxt(self,length):
        txt=""
        for i in range(length):
            n=random.randint(1,62)
            if n<=26:
                txt+=chr(64+n)
            elif n<=52:
                txt+=chr(70+n)
            else:
                txt+=chr(n-5)
        return txt

    def generatewalletno(self):
        def_query=Apptools.defaultquerywalletbank(self)
        rec=Apptools.sql_run(self, def_query)
        if rec:
            query = "select WalNo from walletbank;"
            out=Apptools.sql_run(self, query)
            if out:
                list_wal = []
                if out!=[[]]:
                    for i in range(len(out)):
                        list_wal.append(out[i][0])

                txt=Apptools.randomtxt(self, 8)

                while txt in list_wal:
                    txt=Apptools.randomtxt(self, 8)

                return txt

    def checkBalance(self,walno,pin):
        rec=Apptools.sql_run(self,Apptools.defaultquerywalletbank(self))
        if rec:
            query = "Select Amt from walletbank where walno='"+walno+"' and pin="+str(pin)+";"
            bal=Apptools.sql_run(self,query)[0][0][0]
            #It return integer not string
            return bal

    def keyencoder(self,walno,bal):

        bal=str(bal)

        if len(bal)<len(walno):
            bal="0"*(len(walno)-len(bal))+bal
        elif len(bal) > len(walno):
            walno="$"*(len(bal)-len(walno))+walno

        encbal=""
        for i in bal:
            encbal+=chr(33+int(i))

        data=list(encbal)+list(walno)
        l=len(data)
        key=""
        seq=0
        for i in range(l):
            rnd=random.randint(0,min(9,len(data)-1))
            key+=data[rnd]
            seq=seq*10+rnd
            del data[rnd]
        return key,seq

    def keydecoder(self,key,seq):
        l=[]
        seq=str(seq)
        seq="0"*(len(key)-len(seq))+seq

        seq=Apptools.rev(self,seq)
        key=Apptools.rev(self,key)

        for i in range(len(key)):
            n=int(seq[i])
            l.insert(n, key[i])

        data=""

        for i in range(len(key)):
            data+=l[i]

        walno=data[len(key)//2:]

        bal=0

        for i in data[:len(key)//2]:
            bal=bal*10+(ord(i)-33)

        return walno,bal

    def rev(self,txt):
        rev=""
        for i in txt:
            rev=i+rev
        return rev

    def CashoutRequest(self,walno,bal):
        """Generate Key to initiate a cashout"""
        if bal<=10000000:
            def_query=Apptools.defaultquerytempbank(self)
            rec=Apptools.sql_run(self,def_query)
            key,seq=Apptools.keyencoder(self, walno, bal)
            if rec:
                query="Insert into tempbank values('"+key+"',"+str(seq)+");"
                query_2="Update walletbank set amt=amt-"+str(bal)+" where walno = '"+walno+"';"
                rec2=Apptools.sql_run(self,query_2,query)
                if rec2:
                    return key
        else:
            messagebox.showwarning("Amount exceed limit","As per a guideline we only accept cashout request of only amount upto 1 Crore Rupees")

    def logout(self, master):
        G_NAME.set("")
        G_PIN.set("")
        G_USERNAME.set("")
        master.switch_frame(Homepage)

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(Homepage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class Homepage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
        global G_NAME
        G_NAME = StringVar()
        global G_PIN
        G_PIN = StringVar()
        global G_USERNAME
        G_USERNAME = StringVar()

    def makeWidgets(self, master):
        Apptools.image_Show(self, "blank.png", 0, 0, 300, 1)
        Apptools.image_Show(self, "logo.png", 0, 0, 300, 450,mode="place")

        lbl=tk.Label(self,text="Welcome to\nKans")
        lbl.config(font=("Chiller", 30),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=1, column=2)

        lbl=tk.Label(self,text="Login")
        lbl.config(font=("Chiller", 30),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=2, column=2)

        lbl=tk.Label(self,text="Username")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=3, column=1,padx=5)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=3, column=2)

        lbl=tk.Label(self,text="Password")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=4, column=1,padx=5)

        password = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        password.grid(row=4, column=2)

        lbl=tk.Label(self,text="Login As")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=5, column=1)

        user_type = StringVar(self, "Admin")
        user = {"Admin": "Admin", "Buyer": "Buyer", "Seller": "Seller"}
        i = 5
        for (text, value) in user.items():
            rbtn=Radiobutton(self,text=text,variable=user_type,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2)
            i += 1

        btn=tk.Button(self,text="Login",command=lambda: self.login_check(master,username.get(),password.get(),user_type.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=3, padx=5)

        lbl=tk.Label(self,text="Not Registered?\nSignup Here")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>",lambda e:master.switch_frame(Page2_Signup))
        lbl.grid(row=9, column=2)

    def login_check(self, master, user, pswd, usertype):
        if Apptools.is_not_null(self,user,pswd):
            def_query=Apptools.defaultquerylogindata(self, usertype)
            if def_query:
                out = Apptools.sql_run(self, def_query)
                if out:
                    sql_query = "Select Name, Username, Password, Pin from logindata"+usertype+";"
                    record = Apptools.sql_run(self, sql_query)[0]
                    for (name, usern, pas, pin) in record:
                        if user == usern and pswd == pas:
                            G_PIN.set(pin)
                            G_USERNAME.set(user)
                            G_NAME.set("Welcome " + name)
                            if usertype=="Admin":
                                master.switch_frame(Page3_DashboardAdmin)
                            elif usertype=="Seller":
                                master.switch_frame(Page3_DashboardSeller)
                            elif usertype=="Buyer":
                                master.switch_frame(Page3_DashboardBuyer)
                            return
                    messagebox.showerror("Invalid credentials", "Invalid username/usertype or password!")
        else:
            messagebox.showwarning("Empty fields!", "Fill all the fields correctly to proceed.")


class Page2_Signup(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        lbl=tk.Label(self,text="Kans: You shopping partner")
        lbl.config(font=("Chiller", 30),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=0, column=0,padx=10)

        lbl=tk.Label(self,text="Signup as")
        lbl.config(font=("Segoe Print", 20),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=1, column=0,pady=10)

        user_type = StringVar(self, "Admin")
        user = {"Admin": "Admin", "Buyer": "Buyer", "Seller": "Seller"}
        i = 2
        for (text, value) in user.items():
            rbtn=Radiobutton(self,text=text,variable=user_type,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(row=i, column=0)
            i += 1

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.chooseUserSignup(master,user_type.get()))
        btn.config(bg="#1F8EE7",padx=5,pady=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=0, padx=5,pady=10)

        lbl=tk.Label(self,text="Already Registered?\nLogin Here")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>",lambda e:master.switch_frame(Homepage))
        lbl.grid(row=7, column=0)


    def chooseUserSignup(self,master,usertype):
        if usertype=="Admin":
            master.switch_frame(Page2_SignupAdmin)
        elif usertype=="Seller":
            master.switch_frame(Page2_SignupSeller)
        elif usertype=="Buyer":
            master.switch_frame(Page2_SignupBuyer)
        else:
            messagebox.showwarning("Invalid User Type!","Enter a valid User type")


class Page2_SignupAdmin(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.image_Show(self, "blank.png", 0, 0, 100, 1)
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 520,mode="place")

        Apptools.image_Show(self, "blank.png", 0, 4, 100, 1)
        Apptools.image_Show(self, "Part2.png", 482, 0, 100, 520,mode="place")

        lbl = tk.Label(self, text="Kans")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(self, text="Admin Signup")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(self, text="Name")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5)

        name = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(self, text="Age")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1,padx=5)

        age = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        age.grid(row=4, column=2)

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=5)

        gender = StringVar(self, "M")
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 5
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2,padx=15)
            i += 1

        lbl = tk.Label(self, text="Mobile no.")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1,padx=5)

        MobNo = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        MobNo.grid(row=8, column=2)

        lbl = tk.Label(self, text="PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1,padx=5)

        Pin = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=9, column=2)

        lbl = tk.Label(self, text="Username")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=10, column=1,padx=5)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=10, column=2)

        lbl = tk.Label(self, text="Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=11, column=1,padx=5)

        Password = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Password.grid(row=11, column=2)

        lbl = tk.Label(self, text="Retype Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=12, column=1,padx=5)

        Repassword = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=12, column=2)

        button = tk.Button(self, text="Register")
        button.config(command=lambda: self.RegisterAdmin(master,name.get(),age.get(),gender.get(),MobNo.get(),username.get(),Password.get(),Repassword.get(),Pin.get()))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5,pady=3)
        button.grid(row=13, column=3, pady=10,padx=20)

        lbl=tk.Label(self,text="Already Registered?\nLogin Here")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>",lambda e:master.switch_frame(Homepage))
        lbl.grid(row=14, column=2)

    def RegisterAdmin(self,master,name,age,gender,mobno,user,pswd,repass,pin):
        if pswd == repass:
            def_query=Apptools.defaultquerylogindata(self, "Admin")
            if def_query:
                query_2 = "select id from logindataadmin where username = '" + user + "';"
                query_3 = "select id from logindataadmin where mobno = '" + mobno + "';"
                rec = Apptools.sql_run(self, def_query)
                if rec:
                    out = Apptools.sql_run(self, query_2,query_3)
                    cond1=Apptools.in_limit(self,10**9,10**10,mobno)
                    cond2=Apptools.in_limit(self, 0, 150, age)
                    cond3=Apptools.check_digit(self, age, pin,mobno)
                    cond4=mobno.find(".")==-1 and mobno.find("-")==-1
                    cond5=Apptools.is_not_null(self, name, age, gender,mobno, user, pswd, repass, pin)
                    cond6=len(pin)>=6
                    if cond1 and cond2 and cond3 and cond4 and cond5:
                        if out == [[],[]]:
                            if not(cond6):
                                messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                                return
                            walno=Apptools.generatewalletno(self)
                            uid=str(Apptools.generate_id(self, "logindataadmin"))
                            VALUE = "("+uid+ ", '"+ name+ "', "+ age+ ", '"+ gender+"',"
                            VALUE+=mobno+",'"+ user+ "', '"+ pswd + "', "+ pin+ ",'"+walno+"');"

                            sql_query ="Insert into logindataadmin values"
                            sql_query+=VALUE
                            rec=Apptools.sql_run(self, sql_query)
                            if rec is not None:
                                Apptools.sql_run(self,Apptools.defaultquerywalletbank(self))
                                query_2="Insert into walletbank Values('"+walno+"','A',0,"+pin+");"
                                rec2=Apptools.sql_run(self, query_2)
                                if rec2 is not None:
                                    messagebox.showinfo("Registration done", "Registered user successfully")
                                    master.switch_frame(Homepage)
                        else:
                            if out[0]!=[]:
                                messagebox.showinfo("Sorry! Username already taken", "Try a different username")
                            if out[1]!=[]:
                                messagebox.showinfo("Sorry! Mobile number is already taken", "Try a different mobile number")
                    else:
                        messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Re-enter Password")

class Page2_SignupBuyer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.image_Show(self, "blank.png", 0, 0, 100, 1)
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 600,mode="place")

        Apptools.image_Show(self, "blank.png", 0, 4, 100, 1)
        Apptools.image_Show(self, "Part2.png", 496, 0, 100, 600,mode="place")

        lbl = tk.Label(self, text="Kans")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(self, text="Buyer's Signup")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(self, text="Name")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5)

        name = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(self, text="Age")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1,padx=5)

        age = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        age.grid(row=4, column=2)

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=5)

        gender = StringVar(self, "M")
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 5
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2,padx=15)
            i += 1

        lbl = tk.Label(self, text="Mobile no.")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1,padx=5)

        MobNo = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        MobNo.grid(row=8, column=2)

        lbl = tk.Label(self, text="PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1,padx=5)

        Pin = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=9, column=2)

        lbl = tk.Label(self, text="Username")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=10, column=1,padx=5)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=10, column=2)

        lbl = tk.Label(self, text="Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=11, column=1,padx=5)

        Password = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Password.grid(row=11, column=2)

        lbl = tk.Label(self, text="Retype Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=12, column=1,padx=5)

        Repassword = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=12, column=2)

        lbl = tk.Label(self, text="Delivery Address")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=13, column=1,padx=5)

        DelAdd = tk.Text(self, fg="#E8E8E8", bg="#333333",height=5)
        DelAdd.config(width=15)
        DelAdd.grid(row=13, column=2)

        button = tk.Button(self, text="Register")
        button.config(command=lambda: self.RegisterBuyer(master,name.get(),age.get(),gender.get(),MobNo.get(),username.get(),Password.get(),Repassword.get(),Pin.get(),DelAdd.get("1.0","end-1c")))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5,pady=3)
        button.grid(row=14, column=3, pady=10,padx=20)

        lbl=tk.Label(self,text="Already Registered?\nLogin Here")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>",lambda e:master.switch_frame(Homepage))
        lbl.grid(row=15, column=2)

    def RegisterBuyer(self,master,name,age,gender,mobno,user,pswd,repass,pin,DelAdd):
        if pswd == repass:
            def_query=Apptools.defaultquerylogindata(self, "Buyer")
            if def_query:
                query_2 = "select id from logindatabuyer where username = '" + user + "';"
                query_3 = "select id from logindatabuyer where mobno = '" + mobno + "';"

                rec = Apptools.sql_run(self, def_query)

                if rec:
                    out = Apptools.sql_run(self, query_2,query_3)
                    cond1=Apptools.in_limit(self,10**9,10**10,mobno)
                    cond2=Apptools.in_limit(self, 0, 150, age)
                    cond3=Apptools.check_digit(self, age, pin,mobno)
                    cond4=mobno.find(".")==-1 and mobno.find("-")==-1
                    cond5=Apptools.is_not_null(self, name, age, gender,mobno, user, pswd, repass, pin,mobno,DelAdd)
                    cond6=len(pin)>=6

                    if cond1 and cond2 and cond3 and cond4 and cond5:
                        if out == [[],[]]:
                            if not(cond6):
                                messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                                return
                            uid=str(Apptools.generate_id(self, "logindatabuyer"))
                            walno=Apptools.generatewalletno(self)
                            if walno:
                                VALUE = "("+uid+ ", '"+ name+ "', "+ age+ ", '"+ gender+"',"
                                VALUE+= mobno+",'"+DelAdd+"','"+ user+ "', '"+ pswd + "', '"+walno+"',"+ pin+ ",'N');"

                                sql_query ="Insert into logindatabuyer values"
                                sql_query+=VALUE
                                rec=Apptools.sql_run(self, sql_query)
                                if rec is not None:
                                    Apptools.sql_run(self,Apptools.defaultquerywalletbank(self))
                                    query_2="Insert into walletbank Values('"+walno+"','B',0,"+pin+");"
                                    rec2=Apptools.sql_run(self, query_2)
                                    if rec2 is not None:
                                        messagebox.showinfo("Registration done", "Registered user successfully")
                                        master.switch_frame(Homepage)
                        else:
                            if out[0]!=[]:
                                messagebox.showinfo("Sorry! Username already taken", "Try a different username")
                            if out[1]!=[]:
                                messagebox.showinfo("Sorry! Mobile number is already taken", "Try a different mobile number")
                    else:
                        messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Re-enter Password")



class Page2_SignupSeller(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.image_Show(self, "blank.png", 0, 0, 100, 1)
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 650,mode="place")

        Apptools.image_Show(self, "blank.png", 0, 4, 100, 1)
        Apptools.image_Show(self, "Part2.png", 528, 0, 100, 650,mode="place")

        lbl = tk.Label(self, text="Kans")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(self, text="Seller's Signup")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(self, text="Name")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5)

        name = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(self, text="Age")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1,padx=5)

        age = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        age.grid(row=4, column=2)

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=5)

        gender = StringVar(self, "M")
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 5
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2,padx=15)
            i += 1

        lbl = tk.Label(self, text="Mobile no.")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1,padx=5)

        MobNo = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        MobNo.grid(row=8, column=2)

        lbl = tk.Label(self, text="PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1,padx=5)

        Pin = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=9, column=2)

        lbl = tk.Label(self, text="Username")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=10, column=1,padx=5)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=10, column=2)

        lbl = tk.Label(self, text="Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=11, column=1,padx=5)

        Password = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Password.grid(row=11, column=2)

        lbl = tk.Label(self, text="Retype Password")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=12, column=1,padx=5)

        Repassword = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=12, column=2)

        lbl = tk.Label(self, text="Name of Organisation")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=13, column=1,padx=5)

        orgname = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        orgname.grid(row=13, column=2)

        lbl = tk.Label(self, text="Address of Organisation")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=14, column=1,padx=5)

        OrgAdd = tk.Text(self, fg="#E8E8E8", bg="#333333",height=5)
        OrgAdd.config(width=15)
        OrgAdd.grid(row=14, column=2)

        button = tk.Button(self, text="Register")
        button.config(command=lambda: self.RegisterSeller(master,name.get(),age.get(),gender.get(),MobNo.get(),username.get(),Password.get(),Repassword.get(),Pin.get(),orgname.get(),OrgAdd.get("1.0","end-1c")))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5,pady=3)
        button.grid(row=15, column=3, pady=10,padx=20)

        lbl=tk.Label(self,text="Already Registered?\nLogin Here")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>",lambda e:master.switch_frame(Homepage))
        lbl.grid(row=16, column=2)

    def RegisterSeller(self,master,name,age,gender,mobno,user,pswd,repass,pin,OrgName,OrgAdd):
        if pswd == repass:
            def_query=Apptools.defaultquerylogindata(self, "Seller")
            if def_query:
                query_2 = "select id from logindataseller where username = '" + user + "';"
                query_3 = "select id from logindataseller where mobno = '" + mobno + "';"

                rec = Apptools.sql_run(self, def_query)

                if rec:
                    out = Apptools.sql_run(self, query_2,query_3)
                    cond1=Apptools.in_limit(self,10**9,10**10,mobno)
                    cond2=Apptools.in_limit(self, 0, 150, age)
                    cond3=Apptools.check_digit(self, age, pin,mobno)
                    cond4=mobno.find(".")==-1 and mobno.find("-")==-1
                    cond5=Apptools.is_not_null(self, name, age, gender,mobno, user, pswd, repass, pin,mobno,OrgName,OrgAdd)
                    cond6=len(pin)>=6

                    if cond1 and cond2 and cond3 and cond4 and cond5:
                        if out == [[],[]]:
                            if not(cond6):
                                messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                                return
                            uid=str(Apptools.generate_id(self, "logindataseller"))
                            walno=Apptools.generatewalletno(self)
                            if walno:
                                VALUE = "("+uid+ ", '"+ name+ "', "+ age+ ", '"+ gender+"',"
                                VALUE+= mobno+",'"+OrgName+"','"+OrgAdd+"','"+ user+ "', '"+ pswd + "', '"+walno+"',"+ pin+ ");"

                                sql_query ="Insert into logindataseller values"
                                sql_query+=VALUE
                                rec=Apptools.sql_run(self, sql_query)
                                if rec is not None:
                                    Apptools.sql_run(self,Apptools.defaultquerywalletbank(self))
                                    query_2="Insert into walletbank Values('"+walno+"','S',0,"+pin+");"
                                    rec2=Apptools.sql_run(self, query_2)
                                    if rec2 is not None:
                                        messagebox.showinfo("Registration done", "Registered user successfully")
                                        master.switch_frame(Homepage)
                        else:
                            if out[0]!=[]:
                                messagebox.showinfo("Sorry! Username already taken", "Try a different username")
                            if out[1]!=[]:
                                messagebox.showinfo("Sorry! Mobile number is already taken", "Try a different mobile number")
                    else:
                        messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Re-enter Password")

class Page3_DashboardAdmin(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0,padx=20,pady=10)

        lbl = tk.Label(self, text="Admin Console")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        lbl = tk.Label(self, text=G_NAME.get())
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0,pady=20)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 0, 300, 200)

        btn=tk.Button(self,text="Profile",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn=tk.Button(self,text="Wallet Mangament",command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)


class Page3_DashboardSeller(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0,padx=20,pady=10)

        lbl = tk.Label(self, text="Seller's Console")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        lbl = tk.Label(self, text=G_NAME.get())
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0,pady=20)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 0, 300, 200)

        btn=tk.Button(self,text="Profile",command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn=tk.Button(self,text="Items Mangament",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

class Page3_DashboardBuyer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0,padx=20,pady=10)

        lbl = tk.Label(self, text="Buyer's Dashboard")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        lbl = tk.Label(self, text=G_NAME.get())
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0,pady=20)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 0, 300, 200)

        btn=tk.Button(self,text="Profile",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn=tk.Button(self,text="Wallet",command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn=tk.Button(self,text="Apply for Premium Membership",command=lambda: master.switch_frame(Page3_BuyerPremium))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn=tk.Button(self,text="Start Shopping",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=0, pady=3)

class Page3_AdminProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardAdmin))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Show Profile",command=lambda: master.switch_frame(Page4_AdminShowProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=5)

        btn=tk.Button(self,text="Edit Profile",command=lambda: master.switch_frame(Page4_AdminEditProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Check Balance",command=lambda: master.switch_frame(Page4_AdminCheckBalance))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Delete Account",command=lambda: master.switch_frame(Page4_AdminDeleteAccount))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_AdminWalletManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardAdmin))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Cashout",command=lambda: master.switch_frame(Page4_AdminCashout))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Self Cashout Request",command=lambda: master.switch_frame(Page4_AdminSelfCashoutRequest))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Top-up Wallet",command=lambda: master.switch_frame(Page4_AdminTopupWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Pending Top-ups",command=lambda: master.switch_frame(Page4_AdminPendingTopup))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)

class Page3_SellerProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Show Profile",command=lambda: master.switch_frame(Page4_SellerShowProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Edit Profile",command=lambda: master.switch_frame(Page4_SellerEditProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Check Balance",command=lambda: master.switch_frame(Page4_SellerCheckBalance))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Cashout Request",command=lambda: master.switch_frame(Page4_SellerCashout))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)

        btn=tk.Button(self,text="Recharge Wallet",command=lambda: master.switch_frame(Page4_SellerWalletRecharge))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=1, pady=3)

        btn=tk.Button(self,text="Delete Account",command=lambda: master.switch_frame(Page4_SellerDeleteAccount))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=9, column=1, pady=3)


class Page3_SellerItemManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Item Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Add Items",command=lambda: master.switch_frame(Page4_SellerAddItems))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Edit Items",command=lambda: master.switch_frame(Page4_SellerModifyItems))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Add stocks",command=lambda: master.switch_frame(Page4_SellerAddStocks))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Search items",command=lambda: master.switch_frame(Page4_SellerSearchItem))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)

        btn=tk.Button(self,text="Remove items",command=lambda: master.switch_frame(Page4_SellerRemoveItem))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=1, pady=3)

        btn=tk.Button(self,text="Recent trasactions",command=lambda: master.switch_frame(Page4_SellerRecentTransactions))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=9, column=1, pady=3)

class Page3_BuyerProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Show Profile",command=lambda: master.switch_frame(Page4_BuyerShowProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Edit Profile",command=lambda: master.switch_frame(Page4_BuyerEditProfile))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Recently brought",command=lambda: master.switch_frame(Page4_BuyerRecentlyBrought))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Delete Account",command=lambda: master.switch_frame(Page4_BuyerDeleteAccount))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=1, pady=3)

class Page3_BuyerPremium(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Premium Mebership")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        txt='''Get Enjoying Benefits like
        Free Delivery
        Exclusive Bargains
        No Transaction Charge on Payments'''
        lbl = tk.Label(self, text=txt)
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,pady=10)

        if self.CheckIsPremium():
            lbl = tk.Label(self, text="You already have our Premium Membership\nStart Shopping")
            lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=4, column=1,pady=10)
        else:
            txt='''You are going to be charged Rs 100 from your wallet for
            activating Lifetime Premium membership'''
            lbl = tk.Label(self, text=txt)
            lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=4, column=1,pady=10)

            btn=tk.Button(self,text="Go Premium",command=lambda: self.getmembership(master))
            btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
            btn.grid(row=5, column=1,pady=3)

    def CheckIsPremium(self):
        def_query=Apptools.defaultquerylogindata(self, "Buyer")
        if def_query:
            query_2 = "select ispremium from logindatabuyer where username = '" + G_USERNAME.get() + "';"
            rec=Apptools.sql_run(self, def_query)
            if rec:
                out=Apptools.sql_run(self, query_2)[0][0][0]
                if out.lower()=='y':
                    return True
        return False

    def getmembership(self,master):
        def_query=Apptools.defaultquerylogindata(self, "Buyer")
        if def_query:
            query_2 = "Select WalNo from logindatabuyer where username='"+G_USERNAME.get()+"';"
            query_3 = "Update logindatabuyer set isPremium='Y' where username = '" + G_USERNAME.get() + "';"

            rec=Apptools.sql_run(self, def_query)
            if rec:
                Walno=Apptools.sql_run(self, query_2)[0][0][0]
                out = Apptools.checkBalance(self,Walno,G_PIN.get())
                if out is not None and out>=100:
                    query_4 = "Update walletbank set amt=amt-100 where WalNo='"+Walno+"';"
                    rec2=Apptools.sql_run(self, query_4)
                    if rec2:
                        rec3=Apptools.sql_run(self, query_3)
                        if rec3 is not None:
                            messagebox.showinfo("You are now a premium member","Get exclusive discount and benefits.\nStart Shooping")
                            master.switch_frame(Page3_DashboardBuyer)
                elif out is not None and out<100:
                    messagebox.showwarning("Insufficient fund in wallet","Please recharge your wallet to continue.")




class Page3_BuyerShoppe(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Start Shopping!")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Start Shopping",command=lambda: master.switch_frame(Page4_BuyerShopping))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Search items",command=lambda: master.switch_frame(Page4_BuyerSearchItems))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Wishlist",command=lambda: master.switch_frame(Page4_BuyerWishlist))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Cart",command=lambda: master.switch_frame(Page4_BuyerCart))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_BuyerWallet(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Check Balance",command=lambda: master.switch_frame(Page4_BuyerCheckBalance))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Cashout Request",command=lambda: master.switch_frame(Page4_BuyerCashout))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Recharge Wallet",command=lambda: master.switch_frame(Page4_BuyerWalletRecharge))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

class Page4_AdminShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=20,pady=10)

        Fieldname=["Name","Age","Gender","Mobile No."]
        query="select Name,age,Gender,MobNo from logindataadmin where username='"+G_USERNAME.get()+"';"
        out=Apptools.sql_run(self, query)
        if out:
            out=list(out[0][0])
            if out[2] == "M":
                out[2] = "Male"
            elif out[2] == "F":
                out[2] = "Female"
            else:
                out[2] = "Not specified"

            for i in range(4):
                lbl = tk.Label(self, text=Fieldname[i]+":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=1,padx=5)

                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=3,padx=5)

class Page4_AdminEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=5, sticky="w")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=20,pady=10)

        query="select Name,age,MobNo,Gender from logindataadmin where username='"+G_USERNAME.get()+"';"
        out = Apptools.sql_run(self, query)

        data=["" for i in range(4)]
        if out:
            data = out[0][0]

        Entry_Obj=[]
        Fieldname=["Name","Age","Mobile No."]
        for i in range(3):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i+2, column=1,padx=20,pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i+2, column=3)
            Entry_Obj[i].insert(0, data[i])

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=20)

        gender = StringVar(self, data[3])
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 5
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=3,padx=15)
            i += 1

        btn=tk.Button(self,text="Modify Profile")
        btn.config(command=lambda: self.modifyProfile(master,Entry_Obj[0].get(),Entry_Obj[1].get(),gender.get(),Entry_Obj[2].get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=4,pady=10)

    def modifyProfile(self,master,name,age,gender,mobno):
        cond1=Apptools.in_limit(self,10**9,10**10,mobno)
        cond2=Apptools.in_limit(self, 0, 150, age)
        cond3=Apptools.check_digit(self, age,mobno)
        cond4=mobno.find(".")==-1 and mobno.find("-")==-1
        cond5=Apptools.is_not_null(self, name, age, gender,mobno)
        if cond1 and cond2 and cond3 and cond4 and cond5:
            query="select id from logindataadmin where mobno = '" + mobno + "';"
            query_2 = "Update logindataadmin Set Name='"+name+"',age="+age+",MobNo="+mobno+",Gender='"+gender+"' where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out and len(out[0])<=1:
                rec=Apptools.sql_run(self, query_2)
                if rec is not None:
                    G_NAME.set("Welcome " + name)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardAdmin)
            elif out is not None:
                messagebox.showwarning("Sorry! Mobile number is already taken", "Try a different mobile number")
        else:
            messagebox.showwarning("Error", "Fill all form(s) correctly to continue")

class Page4_AdminCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Check Balance")
        btn.config(command=lambda: self.checkBal(master,pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkBal(self,master,pin):
        if pin==G_PIN.get():
            query="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ "+str(bal))
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=2,padx=20,pady=20)

                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_AdminDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.checkDel(master,pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

        msg="""Make sure you settle your account before deleting your account
        Failing to do so may cause a fraud case be filed against you
        as per Company's Terms of Service"""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=2,pady=10)

    def checkDel(self,master,pin):
        if pin==G_PIN.get():
            query="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)
                    query_2="select count(*) from logindataadmin;"
                    rec3=Apptools.sql_run(self, query_2)
                    if rec3 is not None:
                        noofadmin=rec3[0][0][0]
                        if noofadmin>1:
                            if bal==0:
                                choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                                if choice:
                                    rec=Apptools.sql_run(self, "Delete from logindataadmin where username = '" + G_USERNAME.get() + "';")
                                    rec2=Apptools.sql_run(self, "Delete from walletbank where walno = '" + walno + "';")
                                    if rec and rec2:
                                        messagebox.showinfo("Success", "Account Deleted Successfully")
                                        master.switch_frame(Homepage)

                            else:
                                if bal>0:
                                    msg="You have with us the precious money in your account,proceed for a self cashout request before deleting account.\nInconvenience regretted"
                                    messagebox.showwarning("Money is Precious",msg)
                                    master.switch_frame(Page3_DashboardAdmin)
                                else:
                                    msg="You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from another admin before deleting account.\nInconvenience regretted"
                                    messagebox.showwarning("Money is Precious",msg)
                                    master.switch_frame(Page3_DashboardAdmin)
                        else:
                            msg="As you are the only admin on our system hence we can't lose you\nIf you want to leave us contact System administrator or wait for another admin to Sign in (for a cashout request to happen)\nInconvenience regretted"
                            messagebox.showerror("Access denied",msg)
                            master.switch_frame(Page3_DashboardAdmin)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_AdminSelfCashoutRequest(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Self Cashout Request")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.AdmSelfcashout(master,pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

        msg="""This service is availed for a full cashout.
        No custom amount can't be put
        (for our no PG Charge service for Admin to work)"""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=2,pady=10)

    def AdmSelfcashout(self,master,pin):
        if pin==G_PIN.get():
            query="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)
                    query_2="select count(*) from logindataadmin;"
                    rec=Apptools.sql_run(self, query_2)
                    if rec is not None:
                        noofadmin=rec[0][0][0]
                        if noofadmin>1:
                            if bal>0:
                                key=Apptools.CashoutRequest(self,walno,bal)
                                if key is not None:
                                    messagebox.showinfo("Action Initiated","Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                                    lbl = tk.Label(self, text="Successful\nKey:"+key+"\nNote it down(Not recoverable)")
                                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                                    lbl.grid(row=5, column=2,pady=10)
                            else:
                                messagebox.showwarning("Insufficient fund","There is insufficient money in your wallet.")
                                master.switchframe(Page3_DashboardAdmin)
                        else:
                            msg="As there are the only one admin on our system hence we can't do this transcation (for a cashout request to happen)\nInconvenience regretted"
                            messagebox.showerror("Access denied",msg)
                            master.switch_frame(Page3_DashboardAdmin)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")


class Page4_AdminCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Cash withdrawl")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,pady=10)

        lbl = tk.Label(self, text="Enter Username")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        username=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=2, column=2)

        lbl=tk.Label(self,text="User Type")
        lbl.config(font=("Chiller", 20),fg="#E8E8E8",bg="#333333")
        lbl.grid(row=3, column=1)

        user_type = StringVar(self, "Admin")
        user = {"Admin": "Admin", "Buyer": "Buyer", "Seller": "Seller"}
        i = 3
        for (text, value) in user.items():
            rbtn=Radiobutton(self,text=text,variable=user_type,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2,padx=50)
            i += 1

        lbl = tk.Label(self, text="Enter Withdrawl amount")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,padx=5,pady=10)

        amt=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=6, column=2)

        lbl = tk.Label(self, text="Enter KEY")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1,padx=5,pady=10)

        key=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        key.grid(row=7, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.cashout(master,username.get(),user_type.get(),amt.get(),key.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=3,pady=10)

    def cashout(self,master,user,usertype,amt,key):
        cond1=Apptools.is_not_null(self, user,usertype,key)
        cond2=Apptools.in_limit(self,0,10**7,amt)
        cond3=len(key)==16
        cond4=Apptools.check_digit(self,amt)
        if cond1 and cond4 and cond2 and cond3:
            query="select walno from logindata"+usertype+" where username='"+user+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]

                    def_query=Apptools.defaultquerytempbank(self)
                    query="Select encode from tempbank where seccode='"+key+"';"
                    out=Apptools.sql_run(self,def_query,query)
                    if out is not None:
                        if out[1]!=[]:
                            seq=out[1][0][0]
                            kwal,kbal=Apptools.keydecoder(self,key,seq)
                            if kwal==walno and amt==str(kbal):
                                query_2="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
                                out2=Apptools.sql_run(self,query_2)
                                if out2 is not None:
                                    if out2[0]!=[]:
                                        admwalno=out2[0][0][0]
                                        if admwalno != walno:
                                            query_3="Update walletbank set amt=amt+5 where walno = '"+admwalno+"';"
                                            rec=Apptools.sql_run(self,query_3)
                                            if rec is not None:
                                                query_4="delete from tempbank where seccode='"+key+"';"
                                                rec2=Apptools.sql_run(self,query_4)
                                                if rec2:
                                                    messagebox.showinfo("Success!","Cashout Successful")

                                                    lbl = tk.Label(self, text="Withdrawl Amount : "+amt+"\nAmount to be Paid : "+str(kbal-5)+"\nPG & Service Charges : 5")
                                                    lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
                                                    lbl.grid(row=9, column=2,padx=5,pady=10)
                                        else:
                                             messagebox.showerror("Cashout not possible!","You can take cashout of your own personal account")
                                    else:
                                        messagebox.showerror("Your identity does not exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
                            else:
                                messagebox.showwarning("Invalid Credentials","Either Username/type or withdrawl amount is incorrect.")
                        else:
                            messagebox.showwarning("Invalid Key","Key is not found in your servers\nMaybe already used or invalid")
                else:
                    messagebox.showerror("No such user exists!","Try entering correct username/details")
        else:
            messagebox.showwarning("Invalid Information","Try entering valid information")


class Page4_AdminTopupWallet(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Top-Up Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)



class Page4_AdminPendingTopup(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


class Page4_SellerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerAddItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerModifyItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


class Page4_SellerAddStocks(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerSearchItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerRemoveItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_SellerRecentTransactions(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


class Page4_BuyerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerRecentlyBrought(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


class Page4_BuyerShopping(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerSearchItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerWishlist(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerCart(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


class Page4_BuyerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="w")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)


# Main Program
if __name__ == "__main__":
    app = App()
    app.title("Kans:Your shopping partner")
    app.resizable(0, 0)
    Icon = PhotoImage(file="logo.png")
    app.iconphoto(False, Icon)
    app.mainloop()