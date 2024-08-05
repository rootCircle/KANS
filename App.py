# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:17:14 2021
Requirements:
    PIL library,mysql.connector,SQL DATABASE WITH localhost,user=root,password=password
    local image files
Releases: Recently Brought,Transactions
@author: compaq
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from tkinter import messagebox,Radiobutton,PhotoImage,StringVar,filedialog,ttk
import tkinter.font as tkFont
import mysql.connector as mysqlcon
from PIL import Image, ImageTk
import random
import os
import errno

HOST="localhost"
USERNAME="root"
PASSWORD="password"
DATABASE="Kans"
savedir="C:\\Kans\\App\\ItemImage\\"

savlocimgbtn=""
itemtype=-1
chooseditemdetails=[]


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
            if error.errno==2003:
                ermsg="Failed to make a connection to the server."
                messagebox.showerror(ermsg, "You are Offline!\n"+ermsg+"\nError Code : 2003")
            else:
                messagebox.showerror("Error", error)
        finally:
            if sql_connection:
                sql_connection.close()

    def image_Show(self, Dir, xrow, ycolumn, width, height,mode="grid",rspan=1,cspan=1,px=0,py=0):
        try:
            Photo = Image.open(Dir)
        except Exception as e:
            print(e)
            Photo = Image.open("Additem.jpg")
        Photo = Photo.resize((width, height))
        render = ImageTk.PhotoImage(Photo)
        img = tk.Label(self, image=render)
        img.image = render
        if mode=='grid':
            img.grid(row=xrow, column=ycolumn,rowspan=rspan,columnspan=cspan,padx=px,pady=py)
        else:
            img.place(x=xrow,y=ycolumn,relx=0,rely=0)

    def openfilename(self):
        filetype=[('Image files', '*.jpg;*.jpeg;*.png;*.bmp'),('All files', '*')]
        filename = filedialog.askopenfilename(title ='Open',initialdir = os.getcwd(),filetypes=filetype)
        if filename:
            return filename

    def save_img(self,xdiry="",filename=""):
        if not(filename):
            filename = Apptools.openfilename(self)
        if filename:
            try:
                img = Image.open(filename)
                img = img.resize((300, 300), Image.ANTIALIAS)

                revfn = Apptools.rev(self,filename)
                extension=Apptools.rev(self,revfn[:revfn.find(".")+1])

                try:
                    os.makedirs(savedir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        print(e)

                if not(xdiry):
                    name=Apptools.imgnamegenerator(self,extension)
                    save_location=savedir+name+extension
                else:
                    save_location=xdiry
                    save_location=xdiry[:save_location.find(".")]+extension

                img.save(save_location)
                img = img.resize((100, 100))
                render = ImageTk.PhotoImage(img)
                imgbtn.config(image=render)
                imgbtn.image = render
                globals()['savlocimgbtn']=save_location
            except Exception as e:
                print(e)
                Apptools.save_img(self,"",filename="Additem.png")


    def imgnamegenerator(self,extension):
        name=Apptools.randomtxt(self, 8)
        diry=savlocimgbtn+name+extension

        while os.path.exists(diry):
            name=Apptools.randomtxt(self, 8)
        return name


    def imgsavebtn(self,diry,width,height,irow,icolumn,xdiry=""):

        try:
            Photo = Image.open(diry)
            Photo = Photo.resize((width, height))
            render = ImageTk.PhotoImage(Photo)
            global imgbtn

            imgbtn = tk.Button(self, image=render,command=lambda: Apptools.save_img(self,xdiry))
            imgbtn.image = render
            imgbtn.grid(row = irow,column=icolumn,padx=10,pady=10)
        except Exception as e:
            print(e)
            Apptools.imgsavebtn(self,"Additem.png",width,height,irow,icolumn)

    def defaultqueryrun(self,table):
        table=table.lower()
        if table=="logindataadmin":
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
        elif table=="logindatabuyer":
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

        elif table=="logindataseller":
            def_query="""Create table IF NOT exists logindataseller(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            OrgName varchar(64) not null,
            AddOrg varchar(250) not null,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            WalNo varchar(8) NOT NULL unique,
            PIN INT NOT NULL);"""

        elif table=="walletbank":
            def_query = """Create table IF NOT exists walletbank(
            WalNo varchar(8) NOT NULL primary KEY,
            UserType char(1) NOT NULL,
            Amt int NOT NULL,
            PIN INT NOT NULL);"""

        elif table=="tempbank":
            def_query = """Create table IF NOT exists tempbank(
            SecCode varchar(16) NOT NULL primary KEY,
            encode bigint);"""

        elif table=="cashinhandadmin":
            def_query="""Create table IF NOT exists cashinhandadmin(
            username varchar(32) PRIMARY KEY,
            bal int);"""

        elif table=="items":
            def_query="""Create table IF NOT EXISTS items(
            itemno int PRIMARY KEY,
            iname varchar(32) NOT NULL,
            iwhp int NOT NULL,
            irp int NOT NULL,
            idesc varchar(250) NOT NULL,
            icat varchar(32) NOT NULL,
            istock int NOT NULL,
            imgdir varchar(255) NOT NULL,
            SellerUsername varchar(32) NOT NULL);
            """
        elif table=="cart":
            def_query="""Create table IF NOT EXISTS cart(
            cartuc varchar(8) PRIMARY KEY,
            itemno int,
            iquantity int NOT NULL,
            BuyerUsername varchar(32) NOT NULL);"""

        elif table=="wishlist":
            def_query="""Create table IF NOT EXISTS wishlist(
            wishlistuc varchar(8) PRIMARY KEY,
            itemno int,
            BuyerUsername varchar(32) NOT NULL);"""

        elif table=="trecord":
            def_query="""Create table IF NOT EXISTS trecord(
            tuid int PRIMARY KEY,
            tid int PRIMARY KEY,
            tdate datetime NOT NULL,
            tqty int NOT NULL,
            titemno int NOT NULL,
            tpaidamt int NOT NULL,
            BuyerUsername varchar(32) NOT NULL);"""
        else:
            def_query=None
        rec=None
        if def_query is not None:
            rec=Apptools.sql_run(self,def_query)
        if rec is not None:
            return True
        return False

    def insertSQL(self,table,*values):
        rec=Apptools.defaultqueryrun(self,table)
        if rec:
            query="Insert into {0} values(".format(table)
            for val in values:
                if isinstance(val,int) or isinstance(val,float):
                    query+=str(val)+","
                else:
                    query+="'"+val+"',"
            query=query[:len(query)-1]+");"

            rec2=Apptools.sql_run(self,query)
            return rec2

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

    def generate_id(self, table, sp="id"):
        query = "Select "+sp+" from " + table+";"
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

    def generateuniquecode(self,table,idty):
        rec=Apptools.defaultqueryrun(self,table)
        if rec:
            query = "select {0} from {1};".format(idty,table)
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
        rec=Apptools.defaultqueryrun(self,"walletbank")
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
            if i!='2':
                encbal+=chr(37+int(i))
            else:
                encbal+='#'

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
            if i!='#':
                bal=bal*10+(ord(i)-37)
            else:
                bal=bal*10+2

        return walno,bal

    def rev(self,txt):
        rev=""
        for i in txt:
            rev=i+rev
        return rev

    def CashoutRequest(self,walno,bal):
        """Generate Key to initiate a cashout"""
        bal=int(bal)
        if bal<=10000000:
            key,seq=Apptools.keyencoder(self, walno, bal)
            rec=Apptools.insertSQL(self,"tempbank",key,int(seq))
            if rec:
                query_2="Update walletbank set amt=amt-"+str(bal)+" where walno = '"+walno+"';"
                rec2=Apptools.sql_run(self,query_2)
                if rec2:
                    return key
        else:
            messagebox.showwarning("Amount exceed limit","As per a guideline we only accept cashout request of only amount upto 1 Crore Rupees")

    def clearImgCache(self):
        Apptools.defaultqueryrun(self,"items")
        query="Select imgdir from items;"
        out=Apptools.sql_run(self,query)
        if out is not None:
            out=out[0]
            for i in range(len(out)):
                out[i]=out[i][0]

            onlyfiles = [savedir+f for f in os.listdir(savedir) if os.path.isfile(os.path.join(savedir, f))]
            dup=list(onlyfiles)
            for l in dup:
                if l in out:
                    onlyfiles.remove(l)
            for l in onlyfiles:
                if os.path.exists(l):
                    os.remove(l)

    def logout(self, master):
        G_NAME.set("")
        G_PIN.set("")
        G_USERNAME.set("")
        Apptools.clearImgCache(self)
        master.switch_frame(Homepage)

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None

        global G_NAME
        G_NAME = StringVar()
        global G_PIN
        G_PIN = StringVar()
        global G_USERNAME
        G_USERNAME = StringVar()

        self.switch_frame(Homepage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class ScrollableFrame(ttk.Frame):
    def __init__(self, container,cw=775,ch=500,*args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self,bg="#333333",highlightthickness = 0)
        canvas.config(scrollregion=(0,0,900,1000))
        vscrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        hscrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)


        s = ttk.Style()
        s.configure('TFrame', background='#333333')

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame,anchor="nw")
        self._canvasWidth=cw
        self._canvasHeight=ch
        canvas.config(width=self._canvasWidth,height=self._canvasHeight,scrollregion=(0,0, self._canvasWidth, self._canvasHeight))
        canvas.configure(yscrollcommand=vscrollbar.set,xscrollcommand=hscrollbar.set)

        canvas.grid(row=0,column=0)
        vscrollbar.grid(row=0,column=1,rowspan=2,sticky='nse')
        hscrollbar.grid(row=1,column=0,sticky='wse')

class Homepage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.image_Show(self, "logo.png", 0, 0, 300, 450,rspan=10)

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
            if usertype in ("Admin", "Buyer","Seller"):
                out = Apptools.defaultqueryrun(self, "logindata"+usertype)
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
                messagebox.showwarning("Invalid User Type!","Enter a valid User type")
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
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 650,rspan=15)

        Apptools.image_Show(self, "Part2.png", 0, 4, 100, 650,rspan=15)

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
            rec=Apptools.defaultqueryrun(self, "logindataadmin")
            query_2 = "select id from logindataadmin where username = '" + user + "';"
            query_3 = "select id from logindataadmin where mobno = '" + mobno + "';"
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
                        walno=Apptools.generateuniquecode(self,"walletbank","WalNo")
                        uid=str(Apptools.generate_id(self, "logindataadmin"))

                        rec2=Apptools.insertSQL(self,"logindataadmin",int(uid),name,float(age),gender,int(mobno),user,pswd,int(pin),walno)
                        if rec2 is not None:
                            rec4=Apptools.insertSQL(self,"walletbank",walno,'A',0,int(pin))
                            rec4=Apptools.insertSQL(self,"cashinhandadmin",user,0) and rec4
                            if rec4 is not None:
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
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 650,rspan=16)

        Apptools.image_Show(self, "Part2.png", 0, 4, 100, 650,rspan=16)

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
            rec=Apptools.defaultqueryrun(self, "logindatabuyer")
            query_2 = "select id from logindatabuyer where username = '" + user + "';"
            query_3 = "select id from logindatabuyer where mobno = '" + mobno + "';"

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
                        walno=Apptools.generateuniquecode(self,"walletbank","WalNo")
                        if walno:
                            rec = Apptools.insertSQL(self,"logindatabuyer",int(uid),name,float(age),gender,int(mobno),DelAdd,user,pswd,walno,int(pin),'N')
                            if rec is not None:
                                rec2=Apptools.insertSQL(self,"walletbank",walno,'B',0,int(pin))
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
        Apptools.image_Show(self, "Part1.png", 0, 0, 100, 650,rspan=17)

        Apptools.image_Show(self, "Part2.png", 0, 4, 100, 650,rspan=17)

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
            rec=Apptools.defaultqueryrun(self, "logindataseller")
            query_2 = "select id from logindataseller where username = '" + user + "';"
            query_3 = "select id from logindataseller where mobno = '" + mobno + "';"

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
                        walno=Apptools.generateuniquecode(self,"walletbank","WalNo")
                        if walno:
                            rec=Apptools.insertSQL(self,"logindataseller",int(uid),name,float(age),gender,int(mobno),OrgName,OrgAdd,user,pswd,walno,int(pin))
                            if rec is not None:
                                rec2=Apptools.insertSQL(self,"walletbank",walno,'S',0,int(pin))
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

        btn=tk.Button(self,text="Wallet Mangament",command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn=tk.Button(self,text="Items Management",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)

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

        btn=tk.Button(self,text="Profile Management",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn=tk.Button(self,text="Wallet Management",command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn=tk.Button(self,text="Premium Membership",command=lambda: master.switch_frame(Page3_BuyerPremium))
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
        btn.grid(row=0, column=2, sticky="e")

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
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Cashout Money",command=lambda: master.switch_frame(Page4_AdminCashout))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Self Cashout Request",command=lambda: master.switch_frame(Page4_AdminSelfCashoutRequest))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Top-up Wallet",command=lambda: master.switch_frame(Page4_AdminTopupWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Pending Cashouts",command=lambda: master.switch_frame(Page4_AdminPendingCashout))
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
        btn.grid(row=0, column=2, sticky="e")

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

        btn=tk.Button(self,text="Delete Account",command=lambda: master.switch_frame(Page4_SellerDeleteAccount))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


class Page3_SellerWalletManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Check Balance",command=lambda: master.switch_frame(Page4_SellerCheckBalance))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Cashout Request",command=lambda: master.switch_frame(Page4_SellerCashoutRequest))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Recharge Wallet Info",command=lambda: master.switch_frame(Page4_SellerWalletRecharge))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


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
        btn.grid(row=0, column=2, sticky="e")

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
        btn.grid(row=0, column=2, sticky="e")

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
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Delete Account",command=lambda: master.switch_frame(Page4_BuyerDeleteAccount))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)

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
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Premium Membership")
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
            lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
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
        rec=Apptools.defaultqueryrun(self, "logindatabuyer")
        query_2 = "select ispremium from logindatabuyer where username = '" + G_USERNAME.get() + "';"
        if rec:
            out=Apptools.sql_run(self, query_2)[0][0][0]
            if out.lower()=='y':
                return True
        return False

    def getmembership(self,master):
        rec=Apptools.defaultqueryrun(self, "logindatabuyer")
        query_2 = "Select WalNo from logindatabuyer where username='"+G_USERNAME.get()+"';"
        query_3 = "Update logindatabuyer set isPremium='Y' where username = '" + G_USERNAME.get() + "';"

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
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10)

        lbl = tk.Label(self, text="Start Shopping!")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, "Lighthouse.jpg", 3, 1, 200, 150)

        btn=tk.Button(self,text="Start Shopping",command=lambda: master.switch_frame(Page4_BuyerShopping))
        btn.config(bg="#1F8EE7",fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn=tk.Button(self,text="Search items",command=lambda: master.switch_frame(Page4_BuyerSearchItems))
        btn.config(bg="#1F8EE7",padx=6,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn=tk.Button(self,text="Wishlist",command=lambda: master.switch_frame(Page4_BuyerWishlist))
        btn.config(bg="#1F8EE7",padx=19,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn=tk.Button(self,text="Cart",command=lambda: master.switch_frame(Page4_BuyerCart))
        btn.config(bg="#1F8EE7",padx=29,fg="#E8E8E8",bd=0,activebackground="#3297E9")
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
        btn.grid(row=0, column=2, sticky="e")

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
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=20,pady=10,columnspan=2)

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
                lbl.grid(row=i+2, column=2,padx=5)

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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=20,pady=10)

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
            Entry_Obj[i].grid(row=i+2, column=2)
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
            rbtn.grid(row=i, column=2,padx=15)
            i += 1

        btn=tk.Button(self,text="Modify Profile")
        btn.config(command=lambda: self.modifyProfile(master,Entry_Obj[0].get(),Entry_Obj[1].get(),gender.get(),Entry_Obj[2].get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=3,pady=10)

    def modifyProfile(self,master,name,age,gender,mobno):
        cond1=Apptools.in_limit(self,10**9,10**10,mobno)
        cond2=Apptools.in_limit(self, 0, 150, age)
        cond3=Apptools.check_digit(self, age,mobno)
        cond4=mobno.find(".")==-1 and mobno.find("-")==-1
        cond5=Apptools.is_not_null(self, name, age, gender,mobno)
        if cond1 and cond2 and cond3 and cond4 and cond5:
            query="select username from logindataadmin where mobno = '" + mobno + "';"
            query_2 = "Update logindataadmin Set Name='"+name+"',age="+age+",MobNo="+mobno+",Gender='"+gender+"' where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            l=len(out[0])
            if out and (l==0 or (l==1 and out[0][0][0]==G_USERNAME.get())):
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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Check Balance")
        btn.config(command=lambda: self.checkBal(pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkBal(self,pin):
        if pin==G_PIN.get():
            query="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ "+str(bal))
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=1,columnspan=3,padx=20,pady=20)

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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

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
        lbl.grid(row=4, column=1,columnspan=3,pady=10)

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
                                query_3="Select bal from cashinhandadmin where username='"+G_USERNAME.get()+"';"
                                out2=Apptools.sql_run(self, query_3)
                                if out2 is not None:
                                    if out2[0]!=[]:
                                        cash=out2[0][0][0]
                                if cash!=0:
                                    msg2="Show this message to company before deleting your account for settling\nCash to be taken by company : "+str(cash)+"\nNegative value means cash to be given by company."
                                    messagebox.showwarning("Cash settlement",msg2)
                                else:
                                    choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                                    if choice:
                                        del_query1="Delete from logindataadmin where username = '" + G_USERNAME.get() + "';"
                                        del_query2="Delete from walletbank where walno = '" + walno + "';"
                                        del_query3="Delete from cashinhandadmin where username='"+G_USERNAME.get()+"';"
                                        rec=Apptools.sql_run(self,del_query1,del_query2,del_query3)
                                        if rec:
                                            messagebox.showinfo("Success", "Account Deleted Successfully")
                                            Apptools.logout(self,master)

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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Cash withdrawl")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,pady=10)

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
            rbtn.grid( row=i, column=2)
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
        btn.config(command=lambda: self.cashout(username.get(),user_type.get(),amt.get(),key.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=3,pady=10)

    def cashout(self,user,usertype,amt,key):
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

                    rec=Apptools.defaultqueryrun(self,"tempbank")
                    query="Select encode from tempbank where seccode='"+key+"';"
                    out=Apptools.sql_run(self,query)
                    if out is not None and rec:
                        if out[0]!=[]:
                            seq=out[0][0][0]
                            kwal,kbal=Apptools.keydecoder(self,key,seq)
                            if kwal==walno and amt==str(kbal):
                                query_2="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
                                out2=Apptools.sql_run(self,query_2)
                                if out2 is not None:
                                    if out2[0]!=[]:
                                        admwalno=out2[0][0][0]
                                        if admwalno != walno:
                                            query_3="Update walletbank set amt=amt+5 where walno = '"+admwalno+"';"
                                            query_4="Update cashinhandadmin set bal=bal-"+str(kbal-5)+" where username='"+G_USERNAME.get()+"';"
                                            rec2=Apptools.sql_run(self,query_3,query_4)
                                            if rec2 is not None:
                                                query_4="delete from tempbank where seccode='"+key+"';"
                                                rec3=Apptools.sql_run(self,query_4)
                                                if rec3:
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
                            messagebox.showwarning("Invalid Key","Key is not found in our servers\nMaybe already used or invalid")
                else:
                    messagebox.showerror("No such user exists!","Try entering correct username/details")
        else:
            messagebox.showwarning("Invalid Information","Try entering valid information")


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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Self Cashout Request")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

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
        No custom amount can't be put"""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1,columnspan=3,pady=10)

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

                                    lbl = tk.Label(self, text="Successful\nAmount : "+str(bal)+"\nKey : "+key+"\nNote it down(Not recoverable)")
                                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                                    lbl.grid(row=5, column=1,pady=10,columnspan=3)
                            else:
                                messagebox.showwarning("Insufficient fund","There is insufficient money in your wallet.")
                                master.switch_frame(Page3_DashboardAdmin)
                        else:
                            msg="As there are the only one admin on our system hence we can't do this transcation (for a cashout request to happen)\nInconvenience regretted"
                            messagebox.showerror("Access denied",msg)
                            master.switch_frame(Page3_DashboardAdmin)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")


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
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Top-Up Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

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
            rbtn.grid( row=i, column=2)
            i += 1

        lbl = tk.Label(self, text="Enter Topup Amount")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,padx=5,pady=10)

        amt=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=6, column=2)

        lbl = tk.Label(self, text="Enter your PIN")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=7, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.topup(username.get(),user_type.get(),amt.get(),pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=8, column=3,pady=10)

    def topup(self,username,usertype,amt,pin):
        if pin==G_PIN.get():
            cond1=Apptools.is_not_null(self, username,usertype)
            cond2=Apptools.in_limit(self,5,10**7,amt)
            cond3=Apptools.check_digit(self,amt)
            if cond1 and cond3 and cond2:
                query="select name,walno from logindata"+usertype+" where username='"+username+"';"
                out=Apptools.sql_run(self, query)
                if out is not None:
                    if out[0]!=[]:
                        walno=out[0][0][1]
                        name=out[0][0][0]
                        netamt=str(int(amt)-5)
                        choice = messagebox.askyesno("Sure", "Are you sure want to recharge the wallet of user "+name+" with Rs. "+netamt+"?\nPG & Other Charge = Rs. 5")
                        if choice:
                            query_2="Update walletbank set amt=amt+"+netamt+" where walno = '"+walno+"';"
                            query_3="select walno from logindataadmin where username='"+G_USERNAME.get()+"';"
                            out2=Apptools.sql_run(self,query_3)
                            if out2 is not None:
                                if out2[0]!=[]:
                                    admwalno=out2[0][0][0]
                                    if admwalno != walno:
                                        query_3="Update walletbank set amt=amt+5 where walno = '"+admwalno+"';"
                                        query_4="Update cashinhandadmin set bal=bal+"+amt+" where username='"+G_USERNAME.get()+"';"
                                        rec=Apptools.sql_run(self,query_2,query_3,query_4)
                                        if rec is not None:
                                            messagebox.showinfo("Transaction successful!","Transferred Rs. "+netamt+" to user "+name+" Successfully\nAsk user to check his account")
                                            msg="Transaction Receipt\nName : {0}\nNet Amount Recharged : {1}\nPG & Other Charge : 5\nCash Given by user : {2}".format(name,netamt,amt).strip()
                                            lbl = tk.Label(self, text=msg)
                                            lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
                                            lbl.grid(row=9, column=1,columnspan=3,pady=10,padx=5)
                                    else:
                                        messagebox.showerror("TopUp not possible!","You can take topup your own personal account")
                                else:
                                    messagebox.showerror("Your identity does not exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
                    else:
                        messagebox.showerror("No such user exists!","Try entering correct username/details")
            else:
                messagebox.showwarning("Invalid Information","Try entering valid information")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_AdminPendingCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Pending Cashout")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=30,pady=10)

        self.pendingcashout()


    def pendingcashout(self):
        rec=Apptools.defaultqueryrun(self,"tempbank")
        query="Select * from tempbank;"
        out=Apptools.sql_run(self,query)

        if out is not None and rec:
            out=out[0]
            if out!=[]:
                for i in range(len(out)):
                    out[i]=Apptools.keydecoder(self, out[i][0], out[i][1])
                self.output(out)
            else:
                messagebox.showinfo("No pending cashout(s)", "No records found")

                lbl = tk.Label(self, text="No pending cashout(s)")
                lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=2, column=1,padx=30,pady=10)

    def output(self, out):
        column = ("Wallet Number","Amount")
        listBox = ttk.Treeview(self,selectmode="extended",columns=column,show="headings")

        verscrlbar = ttk.Scrollbar(self, orient ="vertical",command = listBox.yview)
        verscrlbar.grid(row=2,column=2,sticky="nsw",rowspan=2)

        listBox.configure(yscrollcommand = verscrlbar.set)

        for i in range(len(column)):
            listBox.heading(column[i], text=column[i],command=lambda c=column[i]: self.sortby(listBox, c, 0))
            listBox.column(column[i], minwidth=0)
        for col in column:
            listBox.heading(col, text=col)
            listBox.column(col, width=tkFont.Font().measure(col.title()))
        listBox.grid(row=2, column=1,sticky="we")

        for i in out:
            listBox.insert("", "end", values=i)

            for indx, val in enumerate(i):
                ilen = tkFont.Font().measure(val)
                if listBox.column(column[indx], width=None) < ilen:
                    listBox.column(column[indx], width=ilen)

    def sortby(self,tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        x=True

        for a,b in data:
            x=x and Apptools.check_digit(self,a)
        if x:
            for i in range(len(data)):
                data[i]=list(data[i])
                data[i][0]=int(data[i][0])
        data.sort(reverse=descending)

        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        tree.heading(col,command=lambda col=col: self.sortby(tree, col, int(not descending)))

class Page4_SellerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=2,padx=60,pady=10)

        Fieldname=["Name","Age","Gender","Mobile No.","Name of Organisation","Address of Organisation"]
        query="select Name,age,Gender,MobNo,orgName,AddOrg from logindataseller where username='"+G_USERNAME.get()+"';"
        out=Apptools.sql_run(self, query)
        if out:
            out=list(out[0][0])
            if out[2] == "M":
                out[2] = "Male"
            elif out[2] == "F":
                out[2] = "Female"
            else:
                out[2] = "Not specified"

            for i in range(len(Fieldname)):
                lbl = tk.Label(self, text=Fieldname[i]+":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=1,padx=5)

                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=2,padx=5)

class Page4_SellerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=20,pady=10)

        query="select Name,age,MobNo,orgName,AddOrg,Gender from logindataseller where username='"+G_USERNAME.get()+"';"
        out = Apptools.sql_run(self, query)

        data=["" for i in range(6)]
        if out:
            data = out[0][0]

        Entry_Obj=[]
        Fieldname=["Name","Age","Mobile No.","Name of Organisation","Address of Organisation"]
        for i in range(4):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i+2, column=1,padx=20,pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i+2, column=2)
            Entry_Obj[i].insert(0, data[i])

        lbl = tk.Label(self, text=Fieldname[4])
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,padx=20,pady=5)

        Entry_Obj.append(tk.Text(self, fg="#E8E8E8", bg="#333333",height=5))
        Entry_Obj[4].config(width=15)
        Entry_Obj[4].grid(row=6, column=2)
        Entry_Obj[4].insert(tk.INSERT, data[4])

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1,padx=20)

        gender = StringVar(self, data[5])
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 7
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(row=i, column=2)
            i += 1

        btn=tk.Button(self,text="Modify Profile")
        btn.config(command=lambda: self.modifyProfile(master,Entry_Obj[0].get(),Entry_Obj[1].get(),gender.get(),Entry_Obj[2].get(),Entry_Obj[3].get(),Entry_Obj[4].get("1.0","end-1c")))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=10, column=3,pady=10)

    def modifyProfile(self,master,name,age,gender,mobno,orgname,addorg):
        cond1=Apptools.in_limit(self,10**9,10**10,mobno)
        cond2=Apptools.in_limit(self, 0, 150, age)
        cond3=Apptools.check_digit(self, age,mobno)
        cond4=mobno.find(".")==-1 and mobno.find("-")==-1
        cond5=Apptools.is_not_null(self, name, age, gender,mobno,orgname,addorg)
        if cond1 and cond2 and cond3 and cond4 and cond5:
            query="select username from logindataseller where mobno = '" + mobno + "';"
            query_2 = "Update logindataseller Set Name='"+name+"',age="+age+",MobNo="+mobno+",Gender='"+gender+"',orgname='"+orgname+"',addorg='"+addorg+"' where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            l=len(out[0])
            if out and (l==0 or (l==1 and out[0][0][0]==G_USERNAME.get())):
                rec=Apptools.sql_run(self, query_2)
                if rec is not None:
                    G_NAME.set("Welcome " + name)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardSeller)
            elif out is not None:
                messagebox.showwarning("Sorry! Mobile number is already taken", "Try a different mobile number")
        else:
            messagebox.showwarning("Error", "Fill all form(s) correctly to continue")

class Page4_SellerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Check Balance")
        btn.config(command=lambda: self.checkBal(pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkBal(self,pin):
        if pin==G_PIN.get():
            query="select walno from logindataseller where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ "+str(bal))
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=1,columnspan=3,padx=20,pady=20)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_SellerCashoutRequest(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Self Cashout Request")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter Balance")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        amt=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=3, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.Sellercashout(master,pin.get(),amt.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=3,pady=10)

        msg="""After generating of key write down key and amount safely
        and show it to our nearest admin.
        PG charges (Rs.5) is applicable."""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,columnspan=3,pady=10)

    def Sellercashout(self,master,pin,amt):
        if pin==G_PIN.get():
            query="select walno from logindataseller where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)
                    cond1=Apptools.check_digit(self,amt)
                    cond2=Apptools.in_limit(self,0,10**7,amt)
                    if cond1 and cond2:
                        if bal>=int(amt) and int(amt)>5:
                            key=Apptools.CashoutRequest(self,walno,amt)
                            if key is not None:
                                messagebox.showinfo("Action Initiated","Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                                lbl = tk.Label(self, text="Successful\nAmount : "+amt+"\nKey : "+key+"\nNote it down(Not recoverable)")
                                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                                lbl.grid(row=6, column=1,columnspan=3,pady=10)
                        else:
                            messagebox.showwarning("Insufficient fund","There is insufficient money in your wallet or amount withdrwn less than Rs. 5.")
                            master.switch_frame(Page3_DashboardSeller)
                    else:
                        messagebox.showwarning("Invalid entry","Enter a valid amount(Max 1 Crore).")
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")


class Page4_SellerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Wallet Recharge Info")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=30,pady=10)

        msg="""To recharge your wallet you must go to our admin locations,
        Admin will ask for your Username, Usertype, Amount to be topup
        PG Charges of Rs. 5 irrespective of amount is applicable.
        Never share your personal details like your PIN,Password etc with admin."""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=30,pady=10)

class Page4_SellerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.checkDel(master,pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkDel(self,master,pin):
        if pin==G_PIN.get():
            query="select walno from logindataseller where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    if bal==0:
                        choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                        if choice:
                            del_query1="Delete from logindataseller where username = '" + G_USERNAME.get() + "';"
                            del_query2="Delete from walletbank where walno = '" + walno + "';"
                            rec=Apptools.defaultqueryrun(self,"items")
                            del_query3="Delete from items where SellerUsername = '" + G_USERNAME.get() + "';"
                            rec2=Apptools.sql_run(self,del_query1,del_query2,del_query3)
                            if rec and rec2:
                                messagebox.showinfo("Success", "Account Deleted Successfully")
                                Apptools.logout(self,master)
                    else:
                        if bal>0:
                            msg="You have with us the precious money in your account,proceed for a cashout request before deleting account.\nInconvenience regretted"
                            messagebox.showwarning("Money is Precious",msg)
                            master.switch_frame(Page3_DashboardSeller)
                        else:
                            msg="You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from admin before deleting account.\nInconvenience regretted"
                            messagebox.showwarning("Money is Precious",msg)
                            master.switch_frame(Page3_DashboardSeller)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")


class Page4_SellerAddItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Add Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Item Name")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        Iname=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iname.grid(row=2, column=2)

        lbl = tk.Label(self, text="Wholesale Price")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5,pady=10)

        Iwhp=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iwhp.grid(row=3, column=2)

        lbl = tk.Label(self, text="Retail Price")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1,padx=5,pady=10)

        Irp=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Irp.grid(row=4, column=2)

        lbl = tk.Label(self, text="No. of Stocks")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=5,pady=10)

        Istock=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Istock.grid(row=5, column=2)

        lbl = tk.Label(self, text="Description")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,padx=5,pady=10)

        IDesc = tk.Text(self, fg="#E8E8E8", bg="#333333",height=5)
        IDesc.config(width=15)
        IDesc.grid(row=6, column=2)

        lbl = tk.Label(self, text="Category")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1,padx=5,pady=10)

        Category = ["Stationary","Electronics","Clothing","Beauty",
                    "Softwares","Sports","Daily Use","Grocery","Health","Others"]

        CategoryVar = StringVar(self, "Stationary")
        Menu = tk.OptionMenu(self, CategoryVar, *Category)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=7, column=2)

        lbl = tk.Label(self, text="Add Image")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1,padx=5,pady=10)

        globals()['savlocimgbtn']="Additem.png"
        Apptools.imgsavebtn(self,"Additem.png",100,100,8,2)

        btn=tk.Button(self,text="Add Item")
        btn.config(command=lambda: self.additem(master,Iname.get(),Iwhp.get(),Irp.get(),Istock.get(),IDesc.get("1.0","end-1c"),CategoryVar.get(),savlocimgbtn))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=9, column=3,pady=10)

    def additem(self,master,iname,iwp,irp,istock,idesc,icat,filedir):
        cond1=Apptools.is_not_null(self, iname, iwp, irp, istock, idesc,icat,filedir)
        cond2=Apptools.check_digit(self, iwp,irp,istock)
        filedir=filedir.replace("\\","\\\\")
        if cond1 and cond2:
            rec=Apptools.defaultqueryrun(self,"items")

            if rec:
                ino=Apptools.generate_id(self,"items","itemno")
                rec2=Apptools.insertSQL(self,"items",int(ino),iname,float(iwp),float(irp),idesc,icat,int(istock),filedir,G_USERNAME.get())

                if rec2 is not None:
                    messagebox.showinfo("Success!","Item added successfully")
                    master.switch_frame(Page3_SellerItemManagement)
        else:
            messagebox.showwarning("Invalid Input","Fill all the forms correctly to continue")


class Page4_SellerModifyItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Item Details")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        itemno=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn=tk.Button(self,text="Get Details")
        btn.config(command=lambda: self.modify(master,itemno.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=11, column=1,columnspan=3,padx=5,pady=10)

    def modify(self,master,itemno):
        cond1=Apptools.check_digit(self,itemno)
        if cond1:
            rec=Apptools.defaultqueryrun(self,"items")
            query="select iname,iwhp,irp,idesc,imgdir,icat from items where itemno="+itemno+" and SellerUsername='"+G_USERNAME.get()+"';"
            out = Apptools.sql_run(self,query)

            data=["" for i in range(4)]
            if out and rec:
                data = out[0]
                if data!=[]:
                    data=data[0]
                    Entry_Obj=[]
                    Fieldname=["Item Name","Wholesale Price","Retail Price","Description"]
                    for i in range(3):
                        lbl = tk.Label(self, text=Fieldname[i])
                        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                        lbl.grid(row=i+4, column=1,padx=20,pady=5)

                        Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
                        Entry_Obj[i].grid(row=i+4, column=2)
                        Entry_Obj[i].insert(0, data[i])

                    lbl = tk.Label(self, text=Fieldname[3])
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=7, column=1,padx=20,pady=5)

                    Entry_Obj.append(tk.Text(self, fg="#E8E8E8", bg="#333333",height=5))
                    Entry_Obj[3].config(width=15)
                    Entry_Obj[3].grid(row=7, column=2)
                    Entry_Obj[3].insert(tk.INSERT, data[3])

                    lbl = tk.Label(self, text="Category")
                    lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=8, column=1,padx=5,pady=10)

                    Category = ["Stationary","Electronics","Clothing","Beauty",
                                "Softwares","Sports","Daily Use","Grocery","Health","Others"]

                    CategoryVar = StringVar(self, data[5].title())
                    Menu = tk.OptionMenu(self, CategoryVar, *Category)
                    Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
                    Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
                    Menu.grid(row=8, column=2)

                    lbl = tk.Label(self, text="Add Image")
                    lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=9, column=1,padx=5,pady=10)

                    globals()['savlocimgbtn']=data[4]
                    Apptools.imgsavebtn(self,savlocimgbtn,100,100,9,2,data[4])

                    btn=tk.Button(self,text="Modify Details")
                    btn.config(command=lambda: self.modifyDetails(master,itemno,Entry_Obj[0].get(),Entry_Obj[1].get(),Entry_Obj[2].get(),Entry_Obj[3].get("1.0","end-1c"),CategoryVar.get(),savlocimgbtn))
                    btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
                    btn.grid(row=10, column=3,pady=10)

                else:
                    messagebox.showwarning("Invalid Item Code","Item Code is incorrect")
                    master.switch_frame(Page3_SellerItemManagement)
        else:
            messagebox.showwarning("Invalid Field","Fill all the forms correctly to continue")



    def modifyDetails(self,master,itemno,iname,iwhp,irp,idesc,icat,filedir):
        cond1=Apptools.is_not_null(self, iname, iwhp, irp, idesc,icat,filedir)
        cond2=Apptools.check_digit(self, iwhp,irp)
        Category = ["Stationary","Electronics","Clothing","Beauty",
                                "Softwares","Sports","Daily Use","Grocery","Health","Others"]
        cond3=icat.title() in Category
        filedir=filedir.replace("\\","\\\\")
        if cond1 and cond2 and cond3:
            rec=Apptools.defaultqueryrun(self,"items")
            if rec:
                query_2 = "Update items Set iname='"+iname+"',iwhp="+iwhp+",irp="+irp+",idesc='"+idesc+"',imgdir='"+filedir+"',icat='"+icat+"' where itemno="+str(itemno)+";"
                rec2=Apptools.sql_run(self, query_2)

                if rec2 is not None:
                    messagebox.showinfo("Success!", "Item's details updated successfully")
                    master.switch_frame(Page3_SellerItemManagement)

        else:
            messagebox.showwarning("Invalid Input","Fill all the forms correctly to continue")

class Page4_SellerAddStocks(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Add Stocks")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        itemno=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn=tk.Button(self,text="Get Details")
        btn.config(command=lambda: self.modify(master,itemno.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,columnspan=3,padx=5,pady=10)

    def modify(self,master,itemno):
        cond1=Apptools.check_digit(self,itemno)
        if cond1:
            rec=Apptools.defaultqueryrun(self,"items")
            query="select istock from items where itemno="+itemno+" and SellerUsername='"+G_USERNAME.get()+"';"
            out = Apptools.sql_run(self,query)
            if out and rec:
                data = out[0]
                if data!=[]:
                    data=data[0][0]
                    lbl = tk.Label(self, text="No. of Stocks")
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=1,padx=20,pady=5)

                    Stock=tk.Entry(self, fg="#E8E8E8", bg="#333333")
                    Stock.grid(row=4, column=2)
                    Stock.insert(0, data)

                    btn=tk.Button(self,text="Modify Details")
                    btn.config(command=lambda: self.modifyDetails(master,itemno,Stock.get()))
                    btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
                    btn.grid(row=5, column=3,pady=10)

                else:
                    messagebox.showwarning("Invalid Item Code","Item Code is incorrect")
                    master.switch_frame(Page3_SellerItemManagement)

        else:
            messagebox.showwarning("Invalid Field","Fill all the forms correctly to continue")

    def modifyDetails(self,master,itemno,istock):
        cond1=Apptools.check_digit(self, itemno,istock)
        if cond1:
            rec=Apptools.defaultqueryrun(self,"items")

            if rec:
                query_2 = "Update items Set istock="+istock+" where itemno="+str(itemno)+";"
                rec2=Apptools.sql_run(self, query_2)

                if rec2 is not None:
                    messagebox.showinfo("Success!", "Stocks Added successfully")
                    master.switch_frame(Page3_SellerItemManagement)
        else:
            messagebox.showwarning("Invalid Input","Fill all the forms correctly to continue")

class Page4_SellerSearchItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=5, sticky="e")

        lbl = tk.Label(self, text="Search Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=4,padx=30,pady=10)

        lbl = tk.Label(self, text="Search Criteria")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        Searchcr = ["Item Name","Wholesale Price","Retail Price","Description","Category"]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Value")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5,pady=10)

        val=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn=tk.Button(self,text="Search")
        btn.config(command=lambda: self.search(val.get(),SearchcrVar.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=3,pady=10)

        btn=tk.Button(self,text="Show All")
        btn.config(command=self.showAll)
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=3,pady=10)

        btn=tk.Button(self,text="Out of Stock")
        btn.config(command=self.outofstock)
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=4,padx=5)

    def search(self, text, criteria):
        Apptools.defaultqueryrun(self,"items")

        if Apptools.is_not_null(self, text):
            if criteria not in ("Wholesale Price","Retail Price"):
                query ="Select * from items where "+ self.dbeqv(criteria)+ " like '%"+ text+ "%' and SellerUsername='"+G_USERNAME.get()+"';"
                record = Apptools.sql_run(self, query)
            else:
                if Apptools.check_digit(self, text):
                    query ="Select * from items where " + self.dbeqv(criteria) + " = " + str(text)+";"
                    record = Apptools.sql_run(self, query)
                else:
                    messagebox.showwarning("Error", "Incorrect input!")
                    record = None
            if record is not None:
                out = record[0]
                if out != []:
                    self.output(out)
                else:
                    messagebox.showinfo("No data", "No records found")
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def dbeqv(self,colname):
        txt=""
        data = ["Item Name","Wholesale Price","Retail Price","Description","Category"]
        if colname==data[0]:
            txt="iname"
        elif colname==data[1]:
            txt="iwhp"
        elif colname==data[2]:
            txt="irp"
        elif colname==data[3]:
            txt="idesc"
        elif colname==data[4]:
            txt="icat"
        return txt

    def showAll(self):
        Apptools.defaultqueryrun(self,"items")
        sql_query = "Select * from items where SellerUsername='"+G_USERNAME.get()+"';"
        record = Apptools.sql_run(self, sql_query)
        if record is not None:
            out = record[0]
            if out != []:
                self.output(out)
        if out == []:
            messagebox.showinfo("No data", "No records found")

    def outofstock(self):
        Apptools.defaultqueryrun(self,"items")

        sql_query = "Select * from items where SellerUsername='"+G_USERNAME.get()+"' and istock=0;"
        record = Apptools.sql_run(self, sql_query)
        if record is not None:
            out = record[0]
            if out != []:
                self.output(out)
            if out == []:
                messagebox.showinfo("No data", "No records found")

    def output(self, out):
        screen = tk.Toplevel(self, bg="#333333")
        screen.iconphoto(False, Icon)
        screen.title("Search Results")
        screen.resizable(0, 0)

        lbl = tk.Label(screen, text="Search Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0,padx=30,pady=10)

        column=("Item no.","Item Name","Wholesale Price","Retail Price","Description","Category","Stock")
        listBox = ttk.Treeview(screen)

        verscrlbar = ttk.Scrollbar(screen, orient ="vertical",command = listBox.yview)
        verscrlbar.grid(row=1,column=1,sticky="nsw",rowspan=2)

        listBox.config(selectmode="extended",columns=column,show="headings")
        listBox.configure(yscrollcommand = verscrlbar.set)

        for i in range(0, len(column)):
            listBox.heading(column[i], text=column[i],command=lambda c=column[i]: self.sortby(listBox, c, 0))
            listBox.column(column[i], minwidth=0)

        for col in column:
            listBox.heading(col, text=col)
            listBox.column(col, width=tkFont.Font().measure(col.title()))
        listBox.grid(row=1, column=0)

        for i in out:
            listBox.insert("", "end", values=i[:len(column)])

            for indx, val in enumerate(i[:len(column)]):
                ilen = tkFont.Font().measure(val)
                if listBox.column(column[indx], width=None) < ilen:
                    listBox.column(column[indx], width=ilen)

    def sortby(self,tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        x=True

        for a,b in data:
            x=x and Apptools.check_digit(self,a)
        if x:
            for i in range(len(data)):
                data[i]=list(data[i])
                data[i][0]=int(data[i][0])
        data.sort(reverse=descending)

        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        tree.heading(col,command=lambda col=col: self.sortby(tree, col, int(not descending)))


class Page4_SellerRemoveItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Remove Item")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        itemno=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn=tk.Button(self,text="Delete Item")
        btn.config(command=lambda: self.deleteitem(master,itemno.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,columnspan=3,padx=5,pady=10)

    def deleteitem(self,master,itemno):
        cond1=Apptools.check_digit(self,itemno)
        if cond1:
            rec=Apptools.defaultqueryrun(self,"items")
            query="select iname,irp,idesc from items where itemno="+itemno+" and SellerUsername='"+G_USERNAME.get()+"';"
            out = Apptools.sql_run(self,query)
            if rec and out:
                data = out[0]
                if data!=[]:
                    data=data[0]
                    txt="Name = "+data[0]+"\nPrice = "+str(data[1])+"\nDescription = "+data[2]
                    choice = messagebox.askyesno("Alert", "Are you sure want to remove the item?\n"+txt)
                    if choice:
                        del_query="Delete from items where itemno = " + itemno + ";"
                        rec = Apptools.sql_run(self, del_query)
                        if rec is not None:
                            messagebox.showinfo("Success","Item Removed Successfully")
                            Apptools.clearImgCache(self)
                            master.switch_frame(Page3_SellerItemManagement)
                else:
                    messagebox.showwarning("Invalid Item Code","Item Code is incorrect")
        else:
            messagebox.showwarning("Invalid Field","Fill all the forms correctly to continue")


class Page4_BuyerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=2,padx=30,pady=10)

        Fieldname=["Name","Age","Gender","Mobile No.","Premium Member","Delivery Address"]
        query="select Name,age,Gender,MobNo,ispremium,deladd from logindatabuyer where username='"+G_USERNAME.get()+"';"
        out=Apptools.sql_run(self, query)
        if out:
            out=list(out[0][0])
            if out[2] == "M":
                out[2] = "Male"
            elif out[2] == "F":
                out[2] = "Female"
            else:
                out[2] = "Not specified"

            if out[4].upper()=='Y':
                out[4]="Yes"
            else:
                out[4]="No"
            for i in range(len(Fieldname)):
                lbl = tk.Label(self, text=Fieldname[i]+":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=1,padx=5)

                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i+2, column=2,padx=5)


class Page4_BuyerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=20,pady=10)

        query="select Name,age,MobNo,deladd,gender from logindatabuyer where username='"+G_USERNAME.get()+"';"
        out = Apptools.sql_run(self, query)

        data=["" for i in range(5)]
        if out:
            data = out[0][0]

        Entry_Obj=[]
        Fieldname=["Name","Age","Mobile No.","Delivery Address"]
        for i in range(3):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i+2, column=1,padx=20,pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i+2, column=2)
            Entry_Obj[i].insert(0, data[i])

        lbl = tk.Label(self, text=Fieldname[3])
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,padx=20,pady=5)

        Entry_Obj.append(tk.Text(self, fg="#E8E8E8", bg="#333333",height=5))
        Entry_Obj[3].config(width=15)
        Entry_Obj[3].grid(row=5, column=2)
        Entry_Obj[3].insert(tk.INSERT, data[3])

        lbl = tk.Label(self, text="Gender")
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1,padx=20)

        gender = StringVar(self, data[4])
        gen = {"Male": "M", "Female": "F", "Not specified": "N"}
        i = 6
        for (text, value) in gen.items():
            rbtn=Radiobutton(self,text=text,variable=gender,value=value)
            rbtn.config(activebackground="#333333",bg="#333333",fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(row=i, column=2)
            i += 1

        btn=tk.Button(self,text="Modify Profile")
        btn.config(command=lambda: self.modifyProfile(master,Entry_Obj[0].get(),Entry_Obj[1].get(),gender.get(),Entry_Obj[2].get(),Entry_Obj[3].get("1.0","end-1c")))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=9, column=3,pady=10)

    def modifyProfile(self,master,name,age,gender,mobno,deladd):
        cond1=Apptools.in_limit(self,10**9,10**10,mobno)
        cond2=Apptools.in_limit(self, 0, 150, age)
        cond3=Apptools.check_digit(self, age,mobno)
        cond4=mobno.find(".")==-1 and mobno.find("-")==-1
        cond5=Apptools.is_not_null(self, name, age, gender,mobno,deladd)
        if cond1 and cond2 and cond3 and cond4 and cond5:
            query="select username from logindatabuyer where mobno = '" + mobno + "';"
            query_2 = "Update logindatabuyer Set Name='"+name+"',age="+age+",MobNo="+mobno+",Gender='"+gender+"',deladd='"+deladd+"' where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            l=len(out[0])
            if out and (l==0 or (l==1 and out[0][0][0]==G_USERNAME.get())):
                rec=Apptools.sql_run(self, query_2)
                if rec is not None:
                    G_NAME.set("Welcome " + name)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardBuyer)
            elif out is not None:
                messagebox.showwarning("Sorry! Mobile number is already taken", "Try a different mobile number")
        else:
            messagebox.showwarning("Error", "Fill all form(s) correctly to continue")

class Page4_BuyerRecentlyBrought(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Recently Brought")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Page Under Construction")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2,padx=30,pady=10)

class Page4_BuyerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.checkDel(master,pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkDel(self,master,pin):
        if pin==G_PIN.get():
            query="select walno from logindatabuyer where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    if bal==0:
                        choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                        if choice:
                            del_query1="Delete from logindatabuyer where username = '" + G_USERNAME.get() + "';"
                            del_query2="Delete from walletbank where walno = '" + walno + "';"
                            rec=Apptools.sql_run(self,del_query1,del_query2)
                            if rec:
                                messagebox.showinfo("Success", "Account Deleted Successfully")
                                Apptools.logout(self,master)
                    else:
                        if bal>0:
                            msg="You have with us the precious money in your account,proceed for a cashout request before deleting account.\nInconvenience regretted"
                            messagebox.showwarning("Money is Precious",msg)
                            master.switch_frame(Page3_DashboardBuyer)
                        else:
                            msg="You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from admin before deleting account.\nInconvenience regretted"
                            messagebox.showwarning("Money is Precious",msg)
                            master.switch_frame(Page3_DashboardBuyer)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_BuyerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=2, column=2)

        btn=tk.Button(self,text="Check Balance")
        btn.config(command=lambda: self.checkBal(pin.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=3, column=3,pady=10)

    def checkBal(self,pin):
        if pin==G_PIN.get():
            query="select walno from logindatabuyer where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)

                    lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ "+str(bal))
                    lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=1,columnspan=3,padx=20,pady=20)
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_BuyerCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Self Cashout Request")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Enter Balance")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=20,pady=10)

        amt=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Chiller", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=20,pady=10)

        pin=tk.Entry(self, fg="#E8E8E8", bg="#333333",show="*")
        pin.grid(row=3, column=2)

        btn=tk.Button(self,text="Proceed")
        btn.config(command=lambda: self.buyercashout(master,pin.get(),amt.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=3,pady=10)

        msg="""After generating of key write down key and amount safely
        and show it to our nearest admin.
        PG charges (Rs.5) is applicable."""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1,columnspan=3,pady=10)

    def buyercashout(self,master,pin,amt):
        if pin==G_PIN.get():
            query="select walno from logindatabuyer where username='"+G_USERNAME.get()+"';"
            out=Apptools.sql_run(self, query)
            if out is not None:
                if out[0]!=[]:
                    walno=out[0][0][0]
                    bal=Apptools.checkBalance(self, walno, pin)
                    cond1=Apptools.check_digit(self,amt)
                    cond2=Apptools.in_limit(self,0,10**7,amt)
                    if cond1 and cond2:
                        if bal>=int(amt) and int(amt)>5:
                            key=Apptools.CashoutRequest(self,walno,amt)
                            if key is not None:
                                messagebox.showinfo("Action Initiated","Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                                lbl = tk.Label(self, text="Successful\nAmount : "+amt+"\nKey : "+key+"\nNote it down(Not recoverable)")
                                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                                lbl.grid(row=6, column=1,columnspan=3,pady=10)
                        else:
                            messagebox.showwarning("Insufficient fund","There is insufficient money in your wallet or amount withdrawn less than Rs. 5.")
                            master.switch_frame(Page3_DashboardBuyer)
                    else:
                        messagebox.showwarning("Invalid entry","Enter a valid amount(Max 1 Crore).")
                else:
                    messagebox.showerror("No such user exists!","Try relogin to our app(possible server glitch or your id is deleted by devs)")
        else:
            messagebox.showwarning("Incorrect PIN","Try entering correct PIN")

class Page4_BuyerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Wallet Recharge Info")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,padx=30,pady=10)

        msg="""To recharge your wallet you must go to our admin locations,
        Admin will ask for your Username, Usertype, Amount to be topup
        PG Charges of Rs. 5 irrespective of amount is applicable.
        Never share your personal details like your PIN,Password etc with admin."""
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=30,pady=10)


class Page4_BuyerShopping(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        frame = ScrollableFrame(self)

        btn=tk.Button(frame.scrollable_frame,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(frame.scrollable_frame,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(frame.scrollable_frame, text="Kans\nStart Shopping")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,pady=10,columnspan=3)

        Apptools.image_Show(frame.scrollable_frame, "Lighthouse.jpg", 2, 0, 700, 110,cspan=5)

        Dir=["Img1.jpg","Img2.png","Img3.jpg","Img4.jpg","Img5.png","Img6.png"]
        Dir+=["Img7.jpg","Img8.png","Img9.jpg","Img10.png","Img11.png","Img12.png"]
        r,c=3,1
        for i in range(len(Dir)):
            diry="CardsShop//"+Dir[i]
            try:
                Photo = Image.open(diry)
                Photo = Photo.resize((200, 200))
                render = ImageTk.PhotoImage(Photo)

                imgbtnfs = tk.Button(frame.scrollable_frame, image=render)
                imgbtnfs.image = render
                imgbtnfs.grid(row = r,column=c,padx=10,pady=10)
                imgbtnfs.config(command=lambda x=i: self.framechange(master,x))

            except Exception as e:
                print(e)
            if c==3:
                r+=1
                c=1
            else:
                c+=1


        frame.grid(row=0,column=0)

    def framechange(self,master,x):
        globals()['itemtype']=x
        master.switch_frame(Page5_BuyerItemPicker)


class Page5_BuyerItemPicker(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master,bg='#333333')
        self.makeWidgets(master)

    def makeWidgets(self,master):

        frame = ScrollableFrame(self)

        btn=tk.Button(frame.scrollable_frame,text="Go Back",command=lambda: master.switch_frame(Page4_BuyerShopping))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(frame.scrollable_frame,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(frame.scrollable_frame, text="Kans\nStart Shopping")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,pady=10,columnspan=3)

        cat=self.itemcategory(itemtype)

        lbl = tk.Label(frame.scrollable_frame, text="You Searched For Category:"+cat)
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,pady=10,columnspan=3)

        frame.grid(row=0,column=0)

    def itemcategory(self,i):
        Category = ["Stationary","Electronics","Clothing","Beauty",
                                "Softwares","Sports","Daily Use","Grocery","Health","Others"]
        if i<=9:
            return Category[i]

class Page4_BuyerSearchItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Search Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=4,padx=30,pady=10)

        lbl = tk.Label(self, text="Search Criteria")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1,padx=5,pady=10)

        Searchcr = ["Item Name","Description","Category"]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Value")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5,pady=10)

        val=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn=tk.Button(self,text="Search")
        btn.config(command=lambda: self.search(master,val.get(),SearchcrVar.get()))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=3,pady=10)

    def search(self,master, text, criteria):
        Apptools.defaultqueryrun(self,"items")

        if Apptools.is_not_null(self, text):
            query ="Select * from items where "+ self.dbeqv(criteria)+ " like '%"+ text+ "%';"
            record = Apptools.sql_run(self, query)

            if record is not None:
                out = record[0]
                self.output(master,out)
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def dbeqv(self,colname):
        txt=""
        data = ["Item Name","Description","Category"]
        if colname==data[0]:
            txt="iname"
        elif colname==data[1]:
            txt="idesc"
        elif colname==data[2]:
            txt="icat"
        return txt

    def output(self,master, out):
        sep = ttk.Separator(self,orient='horizontal')
        sep.grid(row=5,column=0,columnspan=5,sticky="ew")
        frame = ScrollableFrame(self,cw=500,ch=300)

        if out!=[]:
            r=0
            for ino,iname,iwp,irp,idesc,icat,istock,imgdir,selluser in out:

                orgname=self.sellerorgname(selluser)

                txt="Item name : "+iname.title()+"\n"+"Seller : "+orgname
                txt+="\nDescription : "+idesc.title()+"\nCategory : "+icat.title()
                txt+="\nPrice : ₹"+str(irp)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    print(e)

                    Photo = Image.open("Additem.png")
                    Photo = Photo.resize((250, 150))
                    render = ImageTk.PhotoImage(Photo)

                imgbtnfs = tk.Button(frame.scrollable_frame,text=txt ,image=render,compound =tk.LEFT)
                imgbtnfs.image = render
                imgbtnfs.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0)
                imgbtnfs.config(activebackground="#3297E9",font=("Segoe Print", 15))
                imgbtnfs.grid(row =r,column=0,padx=10,pady=10,sticky="ew")

                idata=[ino,iname,iwp,irp,idesc,icat,istock,imgdir,selluser,orgname]
                imgbtnfs.config(command = lambda x=idata: self.framechange(master,x))
                r+=1

        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2,columnspan=4,padx=100,pady=100)

        frame.grid(row=6,column=0,columnspan=5)

    def sellerorgname(self,suser):
        rec=Apptools.defaultqueryrun(self,"logindataseller")
        if rec:
            query="select OrgName from logindataseller where username='"+suser+"';"
            out=Apptools.sql_run(self,query)
            if out:
                if out[0]:
                    return out[0][0][0]

    def framechange(self,master,x):
        globals()['chooseditemdetails']=x
        master.switch_frame(Page6_BuyerProductView)

class Page6_BuyerProductView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Kans : Your Shopping Partner")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1,columnspan=4,padx=30,pady=10)

        itemdetails=chooseditemdetails

        ino,iname,iwp,irp,idesc,icat,istock,imgdir,selluser,orgname=itemdetails

        txt="Item name : "+iname.title()+"\n"+"Seller : "+orgname
        txt+="\nDescription : "+idesc.title()+"\nCategory : "+icat.title()
        txt+="\nPrice : ₹"+str(irp)

        try:
            Photo = Image.open(imgdir)
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        except Exception as e:
            print(e)

            Photo = Image.open("Additem.png")
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        lbl = tk.Label(self,text=txt ,image=render,compound =tk.LEFT)
        lbl.image = render
        lbl.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0)
        lbl.config(activebackground="#3297E9",font=("Segoe Print", 15))
        lbl.grid(row =2,column=1,columnspan=2,padx=10,pady=10)

        lbl = tk.Label(self, text="Enter Quantity")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1,padx=5,pady=10)

        qty=tk.Entry(self, fg="#E8E8E8", bg="#333333")
        qty.grid(row=3, column=2)
        qty.insert(0, 1)

        btn=tk.Button(self,text="Add to Cart",command=lambda: self.addtocart(ino,qty.get(),istock))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=2,pady=10)

        btn=tk.Button(self,text="Add to Wishlist",command=lambda: self.addtowishlist(ino))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=4, column=3,padx=10)

        btn=tk.Button(self,text="Proceed to Pay",command=lambda: self.paypage(master,ino,qty.get(),istock))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=5, column=2,padx=10,pady=10)

    def addtocart(self,ino,iqty,istock,showMsg=True):
        cond1=Apptools.check_digit(self, iqty)
        cond2=Apptools.in_limit(self, 1, istock, iqty)
        cond3=iqty.find(".")==-1 and iqty.find("-")==-1

        if cond1 and cond2 and cond3:
            cartuc=Apptools.generateuniquecode(self,"cart","cartuc")
            rec = Apptools.insertSQL(self,"cart",cartuc,ino,iqty,G_USERNAME.get())
            if rec is not None and showMsg:
                messagebox.showinfo("Success!","Added to Cart Successfully!")
        else:
            messagebox.showwarning("Invalid Input!","Enter Valid Input for Quantity 0<>"+str(istock))

    def addtowishlist(self,ino):

        wishlistuc=Apptools.generateuniquecode(self,"wishlist","wishlistuc")
        rec = Apptools.insertSQL(self,"wishlist",wishlistuc,ino,G_USERNAME.get())
        if rec is not None:
            messagebox.showinfo("Success!","Added to Wish List Successfully!")

    def paypage(self,master,ino,qty,istock):
        self.addtocart(ino,qty,istock,showMsg=False)
        master.switch_frame(Page7_BuyerPaymentProceed)

class Page7_BuyerPaymentProceed(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Payment Confirmation")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0,columnspan=3,padx=30,pady=10)

        lbl = tk.Label(self, text="Cart")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0,columnspan=2,padx=30,pady=10,sticky="w")

        sep = ttk.Separator(self,orient='horizontal')
        sep.grid(row=3,column=0,sticky="ew",columnspan=2)

        frame = ScrollableFrame(self,cw=550,ch=300)

        out=self.retrievedata()

        totalprice=0

        if out!=[]:
            r=0
            for ino,iname,iwp,irp,idesc,icat,istock,imgdir,selluser,iqty in out:

                orgname=self.sellerorgname(selluser)

                txt="Item name : "+iname.title()+"\n"+"Seller : "+orgname
                txt+="\nDescription : "+idesc.title()+"\nCategory : "+icat.title()
                txt+="\nPrice : ₹"+str(irp)+"\nQuantity : "+str(iqty)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    print(e)

                    Photo = Image.open("Additem.png")
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                lbl = tk.Label(frame.scrollable_frame,text=txt ,image=render,compound =tk.LEFT)
                lbl.image = render
                lbl.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0)
                lbl.config(activebackground="#3297E9",font=("Segoe Print", 15))
                lbl.grid(row =r,column=0,padx=10,pady=10,sticky="ew")

                btn=tk.Button(frame.scrollable_frame,text="Remove Item",command=lambda x=ino: self.deleteitemcart(master,ino))
                btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
                btn.grid(row=r, column=1)
                r+=1
                totalprice+=irp*iqty

        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2,columnspan=4,padx=100,pady=100)

        frame.grid(row=4,column=0,columnspan=2)

        userd=self.userdata()
        if userd is not None:
            lbl = tk.Label(self, text="Deliever to\n"+userd[0]+"\n"+userd[1])
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=3, column=2,rowspan=2,padx=10,pady=10,sticky="ns")

            if userd[2]=='Y':
                btn=tk.Button(self,text="Bargain",command=lambda: self.bargain(out))
                btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
                btn.grid(row=0, column=4, sticky="e")


        lbl = tk.Label(self, text="Amount to be Paid : "+str(totalprice))
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=0,columnspan=2,padx=10,pady=10,sticky="ns")

        btn=tk.Button(self,text="Proceed to Pay",command=lambda: self.payportal())
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")



    def retrievedata(self):
        Apptools.defaultqueryrun(self,"cart")
        Apptools.defaultqueryrun(self,"items")
        query="Select itemno,iquantity from cart where buyerusername ='"+G_USERNAME.get()+"';"
        out=Apptools.sql_run(self,query)

        data=[]
        if out is not None:
            if out[0]!=[]:
                out=out[0]
                for ino,iqty in out:
                    query2="Select * from items where itemno="+str(ino)+";"
                    out2=Apptools.sql_run(self,query2)

                    if out2 is not None and out2[0]!=[]:
                        out2=out2[0][0]
                        data.append(list(out2)+[iqty])
        return data

    def sellerorgname(self,suser):
        rec=Apptools.defaultqueryrun(self,"logindataseller")
        if rec:
            query="select OrgName from logindataseller where username='"+suser+"';"
            out=Apptools.sql_run(self,query)
            if out:
                if out[0]:
                    return out[0][0][0]

    def userdata(self):
        query="select Name,DelAdd,IsPremium from logindatabuyer where username='"+G_USERNAME.get()+"';"

        out=Apptools.sql_run(self,query)
        if out:
            if out[0]:
                return out[0][0]

    def bargain(self):
        pass

    def payportal(self):
        pass
        #remove stock
        #empty cart
        #check and deduct money


class Page4_BuyerWishlist(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2,padx=30,pady=10)

class Page4_BuyerCart(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
    def makeWidgets(self, master):
        btn=tk.Button(self,text="Go Back",command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn=tk.Button(self,text="Logout",command=lambda: Apptools.logout(self, master))
        btn.config(bg="#1F8EE7",padx=3,fg="#E8E8E8",bd=0,activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

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
