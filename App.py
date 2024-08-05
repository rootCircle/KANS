"""
Created on Tue Jan 12 18:17:14 2021
Requirements:
    PIL library,mysql.connector,SQL DATABASE WITH localhost,user=root,password=password
    local image files
@author: compaq
"""

try:
    try:
        import tkinter as tk
    except ImportError:
        import Tkinter as tk
    from tkinter import (
        messagebox,
        Radiobutton,
        PhotoImage,
        StringVar,
        filedialog,
        ttk,
        simpledialog,
    )
    import tkinter.font as tkFont
    import mysql.connector as mysqlcon
    from PIL import Image, ImageTk
    import random
    import os
    import errno
    from datetime import datetime

except Exception as e:
    import sys

    print("Import Error", e, sep="\n")
    print("Part/Complete of Program may malfunction severely.")
    print("Strongly Recommended to install module before starting")
    sys.exit()

"""
Database and File saving Directories
"""
HOST = "localhost"
USERNAME = "root"
PASSWORD = "password"
DATABASE = "KansDB"
savedir = "C:\\KansLite\\"


"""
Some Custom Variable(Not to be modified)
"""
savlocimgbtn = ""
itemtype = -1
chooseditemdetails = []

"""
Image Files Directories
"""
LOGOImgDir = "logo.png"
DEFAULTIMAGEDir = "Additem.png"
HOMEPAGEImgDir = "logo.png"
DASHBOARDImgDir = "Lighthouse.jpg"
# Files in Directory CATEGORYCARDFOLDERNAME Var
CATEGORYCARDFOLDERNAME = "CardsShop"
CATEGORYCARDImgDir = [
    "Img1.jpg",
    "Img2.jpg",
    "Img3.jpg",
    "Img4.jpg",
    "Img5.jpg",
    "Img6.jpg",
]
CATEGORYCARDImgDir += ["Img7.jpg", "Img8.jpg", "Img9.jpg", "Img10.jpg"]


class Apptools:
    def sql_run(self, *sql_query):
        output = []
        sql_connection = None
        try:
            sql_connection = mysqlcon.connect(host=HOST, user=USERNAME, passwd=PASSWORD)
            cursor = sql_connection.cursor()
            sql_query = list(sql_query)
            sql_query.insert(0, ["Create database if not exists " + DATABASE + ";", ()])
            sql_query.insert(1, ["Use " + DATABASE + ";", ()])
            for l in sql_query:
                if isinstance(l, (list, tuple)):
                    if len(l) == 2:
                        query, val = l
                    else:
                        query = l[0]
                        val = ()
                else:
                    query = l
                    val = ()
                cursor.execute(query, val)
                if query.upper().startswith(("SELECT", "DESC", "SHOW")):
                    output.append(cursor.fetchall())
                else:
                    sql_connection.commit()
                    output.append([])
            cursor.close()
            return output[2:]
        except (mysqlcon.Error, mysqlcon.Warning) as error:
            if error.errno == 2003:
                ermsg = "Failed to make a connection to the server."
                messagebox.showerror(
                    ermsg, "You are Offline!\n" + ermsg + "\nError Code : 2003"
                )

            elif error.errno == 1045:
                ermsg = "Failed to make a connection to the server."
                messagebox.showerror(
                    ermsg,
                    "Invalid Credential for Database\nRequires Database Configuration.",
                )
                user = simpledialog.askstring(
                    "Input", "Enter Database Username", parent=self
                )
                if user is not None:
                    pswd = simpledialog.askstring(
                        "Input", "Enter Database Password", parent=self
                    )
                    if pswd is not None:
                        globals()["USERNAME"] = user
                        globals()["PASSWORD"] = pswd
                        messagebox.showinfo(
                            "Success", "Retry to see if credentials are correct or not."
                        )
            elif error.errno == 2005:
                ermsg = "Failed to make a connection to the server."
                messagebox.showerror(
                    ermsg,
                    "Invalid Credential for Database\nRequires Database Configuration.",
                )
                host = simpledialog.askstring(
                    "Input", "Enter Database Hostname", parent=self
                )
                if host is not None:
                    globals()["HOST"] = host
                    messagebox.showinfo(
                        "Success", "Retry to see if credentials are correct or not."
                    )
            else:
                messagebox.showerror("Error", error)
        finally:
            if sql_connection:
                sql_connection.close()

    def image_Show(
        self,
        Dir,
        xrow,
        ycolumn,
        width,
        height,
        mode="grid",
        rspan=1,
        cspan=1,
        px=0,
        py=0,
    ):
        try:
            Photo = Image.open(Dir)
        except Exception as e:
            print(e)
            Photo = Image.open(DEFAULTIMAGEDir)
        Photo = Photo.resize((width, height))
        render = ImageTk.PhotoImage(Photo)
        img = tk.Label(self, image=render)
        img.image = render
        if mode == "grid":
            img.grid(
                row=xrow,
                column=ycolumn,
                rowspan=rspan,
                columnspan=cspan,
                padx=px,
                pady=py,
                sticky="ns",
            )
        else:
            img.place(x=xrow, y=ycolumn, relx=0, rely=0)

    def openfilename(self):
        filetype = [("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*")]
        filename = filedialog.askopenfilename(
            title="Open", initialdir=os.getcwd(), filetypes=filetype
        )
        if filename:
            return filename

    def save_img(self, xdiry="", filename=""):
        if not (filename):
            filename = Apptools.openfilename(self)
        if filename:
            try:
                img = Image.open(filename)
                img = img.resize((300, 300), Image.ANTIALIAS)

                revfn = Apptools.rev(self, filename)
                extension = Apptools.rev(self, revfn[: revfn.find(".") + 1])

                try:
                    os.makedirs(savedir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        print(e)

                if not (xdiry):
                    name = Apptools.imgnamegenerator(self, extension)
                    save_location = savedir + name + extension
                else:
                    save_location = xdiry
                    save_location = xdiry[: save_location.find(".")] + extension

                img.save(save_location)
                img = img.resize((100, 100))
                render = ImageTk.PhotoImage(img)
                imgbtn.config(image=render)
                imgbtn.image = render
                globals()["savlocimgbtn"] = save_location
            except Exception as e:
                if e.errno == 2:
                    msg = "Unable to find {} Drive".format(savedir[:2])
                    globals()["savedir"] = os.getcwd()[:2] + savedir[2:]

                    messagebox.showinfo(
                        msg, "Switching to Current Working Directory Drive."
                    )
                    Apptools.save_img(self, xdiry, filename)
                else:
                    print(e)
                    Apptools.save_img(self, "", filename=DEFAULTIMAGEDir)

    def imgnamegenerator(self, extension):
        name = Apptools.randomtxt(self, 8)
        diry = savlocimgbtn + name + extension

        while os.path.exists(diry):
            name = Apptools.randomtxt(self, 8)
            diry = savlocimgbtn + name + extension
        return name

    def imgsavebtn(self, diry, width, height, irow, icolumn, xdiry=""):
        try:
            Photo = Image.open(diry)
            Photo = Photo.resize((width, height))
            render = ImageTk.PhotoImage(Photo)
            global imgbtn

            imgbtn = tk.Button(
                self, image=render, command=lambda: Apptools.save_img(self, xdiry)
            )
            imgbtn.image = render
            imgbtn.grid(row=irow, column=icolumn, padx=10, pady=10)
        except Exception as e:
            print(e)
            Apptools.imgsavebtn(self, DEFAULTIMAGEDir, width, height, irow, icolumn)

    def defaultqueryrun(self, table):
        table = table.lower()
        if table == "logindatabuyer":
            def_query = """Create table IF NOT exists logindatabuyer(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            DelAdd varchar(250) not null,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            PIN INT NOT NULL,
            IsPremium char(1) NOT NULL DEFAULT 'N');"""

        elif table == "logindataseller":
            def_query = """Create table IF NOT exists logindataseller(
            id int NOT NULL primary KEY,
            Name varchar(50) NOT NULL,
            Age int NOT NULL,
            Gender char(1) NOT NULL,
            MobNo bigint NOT NULL UNIQUE,
            OrgName varchar(64) not null,
            AddOrg varchar(250) not null,
            Username varchar(32) NOT NULL UNIQUE,
            Password varchar(32) NOT NULL,
            PIN INT NOT NULL);"""
        elif table == "items":
            def_query = """Create table IF NOT EXISTS items(
            itemno int PRIMARY KEY,
            iname varchar(64) NOT NULL,
            iwhp int NOT NULL,
            irp int NOT NULL,
            idesc varchar(250) NOT NULL,
            icat varchar(32) NOT NULL,
            istock int NOT NULL,
            imgdir varchar(255) NOT NULL,
            SellerUsername varchar(32) NOT NULL);
            """
        elif table == "cart":
            def_query = """Create table IF NOT EXISTS cart(
            cartuc varchar(8) PRIMARY KEY,
            itemno int,
            iquantity int NOT NULL,
            BuyerUsername varchar(32) NOT NULL);"""
        elif table == "trecord":
            def_query = """Create table IF NOT EXISTS trecord(
            tuid varchar(8) PRIMARY KEY,
            tid varchar(8) ,
            tdate datetime NOT NULL,
            iname varchar(64) NOT NULL,
            tqty int NOT NULL,
            tpaidamt DECIMAL(20,2) NOT NULL,
            BuyerName varchar(50) NOT NULL,
            SellerOrg varchar(64) NOT NULL,
            titemno int NOT NULL,
            BuyerUsername varchar(32) NOT NULL,
            SellerUsername varchar(32) NOT NULL);"""
        else:
            def_query = None
        rec = None
        if def_query is not None:
            rec = Apptools.sql_run(self, def_query)
        if rec is not None:
            return True
        return False

    def insertSQL(self, table, *values):
        rec = Apptools.defaultqueryrun(self, table)
        if rec:
            query = "Insert into {0} values(".format(table)
            for val in values:
                query += "%s,"
            query = query[: len(query) - 1] + ");"

            rec2 = Apptools.sql_run(self, [query, values])
            return rec2

    def is_not_null(self, *text):
        if len(text) != 0:
            for msg in text:
                if msg == "":
                    return False
            return True
        else:
            return False

    def check_digit(self, *text):
        if len(text) != 0:
            for msg in text:
                counter = counter_2 = 0
                for i in msg:
                    if i == ".":
                        counter += 1
                    elif i == "-":
                        counter_2 += 1
                    elif not (i.isdigit()):
                        return False
                if (
                    counter > 1
                    or counter_2 > 1
                    or (counter_2 == 1 and msg[0] != "-")
                    or msg == ""
                ):
                    return False
            return True
        else:
            return False

    def in_limit(self, lower, upper, *text):
        if len(text) != 0:
            for msg in text:
                if Apptools.check_digit(self, msg):
                    val = float(msg)
                    if val > upper or val < lower:
                        return False
                else:
                    return False
            return True
        else:
            return False

    def generate_id(self, table, sp="id"):
        query = "Select " + sp + " from " + table + ";"
        out = Apptools.sql_run(self, query)[0]
        k = 1
        list_id = []
        for i in range(len(out)):
            list_id.append(out[i][0])
        while k in list_id:
            k += 1
        return k

    def randomtxt(self, length):
        txt = ""
        for i in range(length):
            n = random.randint(1, 62)
            if n <= 26:
                txt += chr(64 + n)
            elif n <= 52:
                txt += chr(70 + n)
            else:
                txt += chr(n - 5)
        return txt

    def generateuniquecode(self, table, idty):
        rec = Apptools.defaultqueryrun(self, table)
        if rec:
            query = "select {0} from {1};".format(idty, table)
            out = Apptools.sql_run(self, query)
            if out:
                list_wal = []
                if out != [[]]:
                    for i in range(len(out)):
                        list_wal.append(out[i][0])

                txt = Apptools.randomtxt(self, 8)

                while txt in list_wal:
                    txt = Apptools.randomtxt(self, 8)

                return txt

    def rev(self, txt):
        rev = ""
        for i in txt:
            rev = i + rev
        return rev

    def tkLabel(self, txt, ro, col, fsize=15, fon="Segoe UI", px=0, py=0, cs=1, rs=1):
        lbl = tk.Label(self, text=txt)
        lbl.config(font=(fon, fsize), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=ro, column=col, padx=px, pady=py, columnspan=cs, rowspan=rs)

    def clearImgCache(self):
        Apptools.defaultqueryrun(self, "items")
        query = "Select imgdir from items;"
        out = Apptools.sql_run(self, query)
        if out is not None:
            out = out[0]
            for i in range(len(out)):
                out[i] = out[i][0]
            try:
                os.makedirs(savedir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    if os.system("cd " + savedir[:2]) != 0:
                        msg = "Unable to find {} Drive".format(savedir[:2])
                        globals()["savedir"] = os.getcwd()[:2] + savedir[2:]
                        messagebox.showinfo(
                            msg, "Switching to Current Working Directory Drive."
                        )
                    else:
                        print(e)
            onlyfiles = [
                savedir + f
                for f in os.listdir(savedir)
                if os.path.isfile(os.path.join(savedir, f))
            ]
            dup = list(onlyfiles)
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
    def __init__(self, container, cw=775, ch=500, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg="#333333", highlightthickness=0)
        canvas.config(scrollregion=(0, 0, 900, 1000))
        vscrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        hscrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)

        s = ttk.Style()
        s.configure("TFrame", background="#333333")

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self._canvasWidth = cw
        self._canvasHeight = ch
        canvas.config(
            width=self._canvasWidth,
            height=self._canvasHeight,
            scrollregion=(0, 0, self._canvasWidth, self._canvasHeight),
        )
        canvas.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

        canvas.grid(row=0, column=0)
        vscrollbar.grid(row=0, column=1, rowspan=2, sticky="nse")
        hscrollbar.grid(row=1, column=0, sticky="wse")


class Homepage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.image_Show(self, HOMEPAGEImgDir, 0, 0, 300, 450, rspan=10)

        Apptools.tkLabel(self, "Welcome to\nKans", 1, 2, 15, "Segoe UI", 0, 0)
        Apptools.tkLabel(self, "Login", 2, 2, 15, "Segoe UI", 0, 0)
        Apptools.tkLabel(self, "Username", 3, 1, 10, "Segoe UI", 5, 0)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=3, column=2)

        Apptools.tkLabel(self, "Password", 4, 1, 10, "Segoe UI", 5, 0)

        password = tk.Entry(self, show="*", fg="#E8E8E8", bg="#333333")
        password.grid(row=4, column=2)

        Apptools.tkLabel(self, "Login As", 5, 1, 10, "Segoe UI", 0, 0)

        user_type = StringVar(self, "Buyer")
        user = {"Buyer": "Buyer", "Seller": "Seller"}
        i = 5
        for text, value in user.items():
            rbtn = Radiobutton(self, text=text, variable=user_type, value=value)
            rbtn.config(activebackground="#333333", bg="#333333", fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(sticky="W", row=i, column=2)
            i += 1

        btn = tk.Button(
            self,
            text="Login",
            command=lambda: self.login_check(
                master, username.get(), password.get(), user_type.get()
            ),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=3, padx=5)

        lbl = tk.Label(self, text="Not Registered?\nSignup Here")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: self.signup(master))
        lbl.grid(row=8, column=2)

    def login_check(self, master, user, pswd, usertype):
        if Apptools.is_not_null(self, user, pswd):
            if usertype in ("Buyer", "Seller"):
                out = Apptools.defaultqueryrun(self, "logindata" + usertype)
                if out:
                    sql_query = (
                        "Select Name, Username, Password, Pin from logindata"
                        + usertype
                        + ";"
                    )
                    record = Apptools.sql_run(self, sql_query)[0]
                    for name, usern, pas, pin in record:
                        if user == usern and pswd == pas:
                            G_PIN.set(pin)
                            G_USERNAME.set(user)
                            G_NAME.set("Welcome " + name)
                            if usertype == "Seller":
                                master.switch_frame(Page3_DashboardSeller)
                            elif usertype == "Buyer":
                                master.switch_frame(Page3_DashboardBuyer)
                            return
                    messagebox.showerror(
                        "Invalid credentials", "Invalid username/usertype or password!"
                    )
            else:
                messagebox.showwarning("Invalid User Type!", "Enter a valid User type")
        else:
            messagebox.showwarning(
                "Empty fields!", "Fill all the fields correctly to proceed."
            )

    def signup(self, master, showMsg=True):
        if showMsg:
            messagebox.showinfo("Console", "Switch to console to register user")
        print("\n\n\n\n==================SIGNUP HERE==================")
        print("\n1.) Buyer")
        print("2.) Seller")
        print("Press any Other Numeric Key to Exit")
        ch = int(input("\nEnter you choice : "))
        print("\n")
        suc = None
        if ch == 1:
            # Integer conversion will happen in the function itself
            name = input("Enter your Name : ")
            age = input("Enter your Age :")
            gender = input("Enter your Gender (Male/Female) : ")
            mobno = input("Enter your Mobile number : ")
            user = input("Enter your Username : ")
            pswd = input("Enter your Password : ")
            repass = input("Retype Password : ")
            pin = input("Enter PIN : ")
            DelAdd = input("Enter your Delivery Address : ")
            suc = self.RegisterBuyer(
                master, name, age, gender, mobno, user, pswd, repass, pin, DelAdd
            )
        elif ch == 2:
            name = input("Enter your Name : ")
            age = input("Enter your Age : ")
            gender = input("Enter your Gender (Male/Female): ")
            mobno = input("Enter your Mobile number : ")
            user = input("Enter your Username : ")
            pswd = input("Enter your Password : ")
            repass = input("Retype Password : ")
            pin = input("Enter PIN : ")
            OrgName = input("Enter your Organisation Name : ")
            OrgAdd = input("Enter your Organisation Address : ")
            suc = self.RegisterSeller(
                master,
                name,
                age,
                gender,
                mobno,
                user,
                pswd,
                repass,
                pin,
                OrgName,
                OrgAdd,
            )
        else:
            print("Invalid choice!")
            print("Ending Registration Process")

        if suc is None:
            print("\nRegistration Failed! :-(")
            y = input("\nWant to Restart the Registration (Yes/No) : ")
            if y.lower() == "yes" or y.lower() == "y":
                self.signup(master, showMsg=False)
            else:
                print("Ending Registration Process")
        print("Switch to App")

    def RegisterBuyer(
        self, master, name, age, gender, mobno, user, pswd, repass, pin, DelAdd
    ):
        if pswd == repass:
            rec = Apptools.defaultqueryrun(self, "logindatabuyer")
            query_2 = "select id from logindatabuyer where username = %s;"
            query_3 = "select id from logindatabuyer where mobno = %s;"

            if rec:
                out = Apptools.sql_run(self, [query_2, (user,)], [query_3, (mobno,)])
                cond1 = Apptools.in_limit(self, 10**9, 10**10 - 1, mobno)
                cond2 = Apptools.in_limit(self, 0, 150, age)
                cond3 = Apptools.check_digit(self, age, pin, mobno)
                cond4 = mobno.find(".") == -1 and mobno.find("-") == -1
                cond5 = Apptools.is_not_null(
                    self,
                    name,
                    age,
                    gender,
                    mobno,
                    user,
                    pswd,
                    repass,
                    pin,
                    mobno,
                    DelAdd,
                )
                cond6 = len(pin) >= 6

                if cond1 and cond2 and cond3 and cond4 and cond5:
                    gender = gender[0].upper()
                    if out == [[], []]:
                        if not (cond6):
                            print(
                                "Weak PIN", "PIN must be of atleast 6 digits.", sep="\n"
                            )
                            return
                        uid = str(Apptools.generate_id(self, "logindatabuyer"))
                        rec = Apptools.insertSQL(
                            self,
                            "logindatabuyer",
                            int(uid),
                            name,
                            float(age),
                            gender,
                            int(mobno),
                            DelAdd,
                            user,
                            pswd,
                            int(pin),
                            "N",
                        )
                        if rec is not None:
                            print(
                                "Registration done",
                                "Registered user successfully",
                                sep="\n",
                            )
                            return True
                    else:
                        if out[0] != []:
                            print(
                                "Sorry! Username already taken",
                                "Try a different username",
                                sep="\n",
                            )
                        elif out[1] != []:
                            print(
                                "Sorry! Mobile number is already taken",
                                "Try a different mobile number",
                                sep="\n",
                            )
                else:
                    if not (cond1):
                        print(
                            "Invalid entry",
                            "Enter Valid 10-digit Mobile Number",
                            sep="\n",
                        )
                    elif not (cond2):
                        print("Invalid entry", "Enter Valid Age (0~150 year)", sep="\n")
                    else:
                        print(
                            "Invalid entry",
                            "Fill all the entry correctly to proceed",
                            sep="\n",
                        )
        else:
            print("Password Mismatch", "Password Mismatch\nRe-enter Password", sep="\n")

    def RegisterSeller(
        self, master, name, age, gender, mobno, user, pswd, repass, pin, OrgName, OrgAdd
    ):
        if pswd == repass:
            rec = Apptools.defaultqueryrun(self, "logindataseller")
            query_2 = "select id from logindataseller where username = %s;"
            query_3 = "select id from logindataseller where mobno = %s;"

            if rec:
                out = Apptools.sql_run(self, [query_2, (user,)], [query_3, (mobno,)])
                cond1 = Apptools.in_limit(self, 10**9, 10**10 - 1, mobno)
                cond2 = Apptools.in_limit(self, 0, 150, age)
                cond3 = Apptools.check_digit(self, age, pin, mobno)
                cond4 = mobno.find(".") == -1 and mobno.find("-") == -1
                cond5 = Apptools.is_not_null(
                    self,
                    name,
                    age,
                    gender,
                    mobno,
                    user,
                    pswd,
                    repass,
                    pin,
                    mobno,
                    OrgName,
                    OrgAdd,
                )
                cond6 = len(pin) >= 6

                if cond1 and cond2 and cond3 and cond4 and cond5:
                    gender = gender[0].upper()
                    if out == [[], []]:
                        if not (cond6):
                            print("Weak PIN", "PIN must be of atleast 6 digits.")
                            return
                        uid = str(Apptools.generate_id(self, "logindataseller"))

                        rec = Apptools.insertSQL(
                            self,
                            "logindataseller",
                            int(uid),
                            name,
                            float(age),
                            gender,
                            int(mobno),
                            OrgName,
                            OrgAdd,
                            user,
                            pswd,
                            int(pin),
                        )
                        if rec is not None:
                            print("Registration done", "Registered user successfully")
                            return True
                    else:
                        if out[0] != []:
                            print(
                                "Sorry! Username already taken",
                                "Try a different username",
                            )
                        elif out[1] != []:
                            print(
                                "Sorry! Mobile number is already taken",
                                "Try a different mobile number",
                            )
                else:
                    if not (cond1):
                        print("Invalid entry", "Enter Valid 10-digit Mobile Number")
                    elif not (cond2):
                        print("Invalid entry", "Enter Valid Age (0~150 year)")
                    else:
                        print(
                            "Invalid entry", "Fill all the entry correctly to proceed"
                        )
        else:
            print("Password Mismatch", "Password Mismatch\nRe-enter Password")


class Page3_DashboardSeller(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.tkLabel(
            self, "Kans:Your Shopping Partner", 0, 0, 15, "Segoe UI", 20, 10
        )

        Apptools.tkLabel(self, "Seller's Console", 1, 0, 15, "Segoe UI", 0, 0)

        Apptools.tkLabel(self, G_NAME.get(), 2, 0, 20, "Segoe Print", 0, 20)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 0, 300, 200)

        btn = tk.Button(
            self,
            text="Profile",
            command=lambda: master.switch_frame(Page4_SellerShowProfile),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Add Items",
            command=lambda: master.switch_frame(Page4_SellerAddItems),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Edit Items",
            command=lambda: master.switch_frame(Page4_SellerModifyItems),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Search items",
            command=lambda: master.switch_frame(Page4_SellerSearchItem),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Remove items",
            command=lambda: master.switch_frame(Page4_SellerRemoveItem),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=8, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Recent Transactions",
            command=lambda: master.switch_frame(Page4_SellerRecentTransactions),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=9, column=0, pady=3)

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=10, column=0, pady=3)


class Page3_DashboardBuyer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        Apptools.tkLabel(
            self, "Kans:Your Shopping Partner", 0, 0, 15, "Segoe UI", 20, 10
        )

        Apptools.tkLabel(self, "Buyer's Dashboard", 1, 0, 15, "Segoe UI", 0, 0)

        Apptools.tkLabel(self, G_NAME.get(), 2, 0, 20, "Segoe Print", 0, 20)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 0, 300, 200)

        btn = tk.Button(
            self,
            text="Show Profile",
            command=lambda: master.switch_frame(Page4_BuyerShowProfile),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Premium Membership",
            command=lambda: master.switch_frame(Page3_BuyerPremium),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn = tk.Button(
            self,
            text="Start Shopping",
            command=lambda: master.switch_frame(Page3_BuyerShoppe),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)


class Page3_BuyerPremium(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardBuyer),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        Apptools.tkLabel(
            self, "Kans:Your Shopping Partner", 1, 1, 15, "Segoe UI", 20, 10
        )

        Apptools.tkLabel(self, "Premium Membership", 2, 1, 15, "Segoe UI", 0, 0)

        txt = """Get Enjoying Benefits like
        Free Delivery
        Exclusive Bargains and a lot more."""
        Apptools.tkLabel(self, txt, 3, 1, 10, "Segoe UI", 0, 10)

        if self.CheckIsPremium():
            Apptools.tkLabel(
                self,
                "You already have our Premium Membership\nStart Shopping",
                4,
                1,
                15,
                "Segoe Print",
                0,
                10,
            )
        else:
            txt = """You are going to be charged Rs 100 for
            activating Lifetime Premium membership\nPay Rs 100 to Company."""
            Apptools.tkLabel(self, txt, 4, 1, 8, "Segoe UI", 0, 10)

            btn = tk.Button(
                self, text="Go Premium", command=lambda: self.getmembership(master)
            )
            btn.config(
                bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9"
            )
            btn.grid(row=5, column=1, pady=3)

    def CheckIsPremium(self):
        rec = Apptools.defaultqueryrun(self, "logindatabuyer")
        query_2 = "select ispremium from logindatabuyer where username = %s;"
        if rec:
            out = Apptools.sql_run(self, [query_2, (G_USERNAME.get(),)])[0][0][0]
            if out.lower() == "y":
                return True
        return False

    def getmembership(self, master):
        rec = Apptools.defaultqueryrun(self, "logindatabuyer")
        query_3 = "Update logindatabuyer set isPremium='Y' where username = %s;"
        if rec:
            rec3 = Apptools.sql_run(self, [query_3, (G_USERNAME.get(),)])
            if rec3 is not None:
                messagebox.showinfo(
                    "You are now a premium member",
                    "Get exclusive discount and benefits.\nStart Shooping",
                )
                master.switch_frame(Page3_DashboardBuyer)


class Page3_BuyerShoppe(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardBuyer),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        Apptools.tkLabel(
            self, "Kans:Your Shopping Partner", 1, 1, 15, "Segoe UI", 20, 10
        )

        Apptools.tkLabel(self, "Start Shopping!", 2, 1, 15, "Segoe UI", 0, 0)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(
            self,
            text="Start Shopping",
            command=lambda: master.switch_frame(Page4_BuyerShopping),
        )
        btn.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(
            self,
            text="Cart",
            command=lambda: master.switch_frame(Page7_BuyerPaymentProceed),
        )
        btn.config(
            bg="#1F8EE7", padx=29, fg="#E8E8E8", bd=0, activebackground="#3297E9"
        )
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(
            self,
            text="Recently brought",
            command=lambda: master.switch_frame(Page4_BuyerRecentlyBrought),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


class Page4_SellerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        Apptools.tkLabel(self, "Profile", 1, 1, 20, "Segoe UI", 60, 10, cs=2)

        Fieldname = [
            "Name",
            "Age",
            "Gender",
            "Mobile No.",
            "Name of Organisation",
            "Address of Organisation",
        ]
        query = "select Name,age,Gender,MobNo,orgName,AddOrg from logindataseller where username=%s;"
        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])
        if out:
            out = list(out[0][0])
            if out[2] == "M":
                out[2] = "Male"
            elif out[2] == "F":
                out[2] = "Female"
            else:
                out[2] = "Not specified"

            for i in range(len(Fieldname)):
                Apptools.tkLabel(
                    self, Fieldname[i] + ":", i + 2, 1, 15, "Segoe Print", 5, 0
                )
                Apptools.tkLabel(self, out[i], i + 2, 2, 15, "Segoe Print", 5, 0)


class Page4_SellerAddItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        Apptools.tkLabel(self, "Add Items", 1, 1, 20, "Segoe UI", 30, 10, cs=3)

        arr = ["Item Name", "Wholesale Price", "Retail Price", "No. of Stocks"]
        Entry = []
        rowR = 2
        for i in range(len(arr)):
            Apptools.tkLabel(self, arr[i], rowR, 1, 10, "Segoe UI", 5, 10)
            Entry.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry[i].grid(row=rowR, column=2)
            rowR += 1

        Apptools.tkLabel(self, "Description", 6, 1, 10, "Segoe UI", 5, 10)

        IDesc = tk.Text(self, fg="#E8E8E8", bg="#333333", height=5)
        IDesc.config(width=15)
        IDesc.grid(row=6, column=2)

        Apptools.tkLabel(self, "Category", 7, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1)

        Category = [
            "Stationary",
            "Electronics",
            "Clothing",
            "Beauty",
            "Softwares",
            "Sports",
            "Daily Use",
            "Grocery",
            "Health",
            "Others",
        ]

        CategoryVar = StringVar(self, "Stationary")
        Menu = tk.OptionMenu(self, CategoryVar, *Category)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=7, column=2)

        Apptools.tkLabel(self, "Add Image", 8, 1, 10, "Segoe UI", 5, 10)

        globals()["savlocimgbtn"] = DEFAULTIMAGEDir
        Apptools.imgsavebtn(self, DEFAULTIMAGEDir, 100, 100, 8, 2)

        btn = tk.Button(self, text="Add Item")
        btn.config(
            command=lambda: self.additem(
                master,
                Entry[0].get(),
                Entry[1].get(),
                Entry[2].get(),
                Entry[3].get(),
                IDesc.get("1.0", "end-1c"),
                CategoryVar.get(),
                savlocimgbtn,
            )
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=9, column=3, pady=10)

    def additem(self, master, iname, iwp, irp, istock, idesc, icat, filedir):
        cond1 = Apptools.is_not_null(
            self, iname, iwp, irp, istock, idesc, icat, filedir
        )
        cond2 = Apptools.check_digit(self, iwp, irp, istock)
        cond3 = cond1 and float(irp) >= float(iwp)
        if cond1 and cond2 and cond3:
            rec = Apptools.defaultqueryrun(self, "items")

            if rec:
                if float(istock) >= 0 and round(float(istock)) == float(istock):
                    ino = Apptools.generate_id(self, "items", "itemno")
                    rec2 = Apptools.insertSQL(
                        self,
                        "items",
                        int(ino),
                        iname,
                        float(iwp),
                        float(irp),
                        idesc,
                        icat,
                        int(istock),
                        filedir,
                        G_USERNAME.get(),
                    )

                    if rec2 is not None:
                        messagebox.showinfo("Success!", "Item added successfully")
                        master.switch_frame(Page3_DashboardSeller)
                else:
                    messagebox.showwarning(
                        "Invalid Input", "Enter a valid no. of Stock (>=0)"
                    )

        else:
            if cond1 and not (cond3):
                messagebox.showwarning(
                    "Invalid Input",
                    "Wholesale must be less than or equal to retail price",
                )
            else:
                messagebox.showwarning(
                    "Invalid Input", "Fill all the forms correctly to continue"
                )


class Page4_SellerModifyItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        Apptools.tkLabel(
            self, "Modify Item Details", 1, 1, 20, "Segoe UI", 30, 10, rs=1, cs=3
        )

        Apptools.tkLabel(self, "Item Code", 2, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1)

        itemno = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn = tk.Button(self, text="Get Details")
        btn.config(command=lambda: self.modify(master, itemno.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        Apptools.tkLabel(
            self,
            "Item Code can be found in\nSearch Items Section.",
            6,
            1,
            10,
            "Segoe UI",
            5,
            10,
            rs=1,
            cs=3,
        )

    def modify(self, master, itemno):
        frame = ScrollableFrame(self, ch=350, cw=385)
        sframe = frame.scrollable_frame
        cond1 = Apptools.check_digit(self, itemno)
        if cond1:
            rec = Apptools.defaultqueryrun(self, "items")
            query = "select iname,iwhp,irp,idesc,imgdir,icat,istock from items where itemno=%s and SellerUsername=%s;"
            out = Apptools.sql_run(self, [query, (itemno, G_USERNAME.get())])

            data = ["" for i in range(4)]
            if out and rec:
                data = out[0]
                if data != []:
                    sep = ttk.Separator(self, orient="horizontal")
                    sep.grid(row=4, column=0, columnspan=5, sticky="ews")
                    data = data[0]
                    Entry_Obj = []
                    Fieldname = [
                        "Item Name",
                        "Wholesale Price",
                        "Retail Price",
                        "Description",
                    ]

                    for i in range(3):
                        Apptools.tkLabel(
                            sframe,
                            Fieldname[i],
                            i,
                            1,
                            10,
                            "Segoe UI",
                            20,
                            5,
                            rs=1,
                            cs=1,
                        )

                        Entry_Obj.append(tk.Entry(sframe, fg="#E8E8E8", bg="#333333"))
                        Entry_Obj[i].grid(row=i, column=2)
                        Entry_Obj[i].insert(0, data[i])

                    Apptools.tkLabel(
                        sframe, Fieldname[3], 3, 1, 10, "Segoe UI", 20, 5, rs=1, cs=1
                    )

                    Entry_Obj.append(
                        tk.Text(sframe, fg="#E8E8E8", bg="#333333", height=5)
                    )
                    Entry_Obj[3].config(width=15)
                    Entry_Obj[3].grid(row=3, column=2)
                    Entry_Obj[3].insert(tk.INSERT, data[3])

                    Apptools.tkLabel(
                        sframe, "Category", 4, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1
                    )

                    Category = [
                        "Stationary",
                        "Electronics",
                        "Clothing",
                        "Beauty",
                        "Softwares",
                        "Sports",
                        "Daily Use",
                        "Grocery",
                        "Health",
                        "Others",
                    ]

                    CategoryVar = StringVar(self, data[5].title())
                    Menu = tk.OptionMenu(sframe, CategoryVar, *Category)
                    Menu.config(
                        bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333"
                    )
                    Menu["menu"].config(
                        bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7"
                    )
                    Menu.grid(row=4, column=2)

                    Apptools.tkLabel(
                        sframe, "No. of Stocks", 5, 1, 10, "Segoe UI", 20, 5, rs=1, cs=1
                    )

                    Stock = tk.Entry(sframe, fg="#E8E8E8", bg="#333333")
                    Stock.grid(row=5, column=2)
                    Stock.insert(0, data[6])

                    Apptools.tkLabel(
                        sframe, "Add Image", 6, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1
                    )

                    globals()["savlocimgbtn"] = data[4]
                    Apptools.imgsavebtn(sframe, savlocimgbtn, 100, 100, 6, 2, data[4])

                    btn = tk.Button(sframe, text="Modify Details")
                    btn.config(
                        command=lambda: self.modifyDetails(
                            master,
                            itemno,
                            Entry_Obj[0].get(),
                            Entry_Obj[1].get(),
                            Entry_Obj[2].get(),
                            Entry_Obj[3].get("1.0", "end-1c"),
                            CategoryVar.get(),
                            savlocimgbtn,
                            Stock.get(),
                        )
                    )
                    btn.config(
                        bg="#1F8EE7",
                        padx=3,
                        fg="#E8E8E8",
                        bd=0,
                        activebackground="#3297E9",
                    )
                    btn.grid(row=7, column=3, pady=10)

                    frame.grid(row=5, column=0, columnspan=5)

                else:
                    messagebox.showwarning(
                        "Invalid Item Code", "Item Code is incorrect"
                    )
                    master.switch_frame(Page3_DashboardSeller)
        else:
            messagebox.showwarning(
                "Invalid Field", "Fill all the forms correctly to continue"
            )

    def modifyDetails(
        self, master, itemno, iname, iwhp, irp, idesc, icat, filedir, istock
    ):
        cond1 = Apptools.is_not_null(
            self, iname, iwhp, irp, idesc, icat, filedir, istock
        )
        cond2 = Apptools.check_digit(self, iwhp, irp, istock)
        cond4 = cond1 and float(irp) >= float(iwhp)
        cond5 = float(istock) >= 0 and round(float(istock)) == float(istock)
        Category = [
            "Stationary",
            "Electronics",
            "Clothing",
            "Beauty",
            "Softwares",
            "Sports",
            "Daily Use",
            "Grocery",
            "Health",
            "Others",
        ]
        cond3 = icat.title() in Category
        if cond1 and cond2 and cond3 and cond4 and cond5:
            rec = Apptools.defaultqueryrun(self, "items")
            if rec:
                query_2 = "Update items Set iname=%s,iwhp=%s,irp=%s,idesc=%s,imgdir=%s,icat=%s,istock=%s where itemno=%s;"
                rec2 = Apptools.sql_run(
                    self,
                    [query_2, (iname, iwhp, irp, idesc, filedir, icat, istock, itemno)],
                )

                if rec2 is not None:
                    messagebox.showinfo(
                        "Success!", "Item's details updated successfully"
                    )
                    master.switch_frame(Page3_DashboardSeller)

        else:
            if cond1 and not (cond4):
                messagebox.showwarning(
                    "Invalid Input",
                    "Wholesale must be less than or equal to retail price",
                )
            elif not (cond5):
                messagebox.showwarning(
                    "Invalid Input", "Enter a valid no. of Stock (>=0)"
                )
            else:
                messagebox.showwarning(
                    "Invalid Input", "Fill all the forms correctly to continue"
                )


class Page4_SellerSearchItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=5, sticky="e")

        Apptools.tkLabel(self, "Search Items", 1, 1, 20, "Segoe UI", 30, 10, rs=1, cs=4)

        Apptools.tkLabel(
            self, "Search Criteria", 2, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1
        )

        Searchcr = [
            "Item Name",
            "Wholesale Price",
            "Retail Price",
            "Description",
            "Category",
        ]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        Apptools.tkLabel(self, "Enter Value", 3, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1)

        val = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn = tk.Button(self, text="Search")
        btn.config(command=lambda: self.search(val.get(), SearchcrVar.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        btn = tk.Button(self, text="Show All")
        btn.config(command=self.showAll)
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)

        btn = tk.Button(self, text="Out of Stock")
        btn.config(command=self.outofstock)
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=4, padx=5)

    def search(self, text, criteria):
        Apptools.defaultqueryrun(self, "items")

        if Apptools.is_not_null(self, text):
            if criteria not in ("Wholesale Price", "Retail Price"):
                text = "%" + text + "%"
                query = (
                    "Select * from items where "
                    + self.dbeqv(criteria)
                    + " like %s and SellerUsername=%s;"
                )
                record = Apptools.sql_run(self, [query, (text, G_USERNAME.get())])
            else:
                if Apptools.check_digit(self, text):
                    query = (
                        "Select * from items where "
                        + self.dbeqv(criteria)
                        + " = %s and SellerUsername=%s;"
                    )
                    record = Apptools.sql_run(self, [query, ((text, G_USERNAME.get()))])
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

    def dbeqv(self, colname):
        txt = ""
        data = [
            "Item Name",
            "Wholesale Price",
            "Retail Price",
            "Description",
            "Category",
        ]
        if colname == data[0]:
            txt = "iname"
        elif colname == data[1]:
            txt = "iwhp"
        elif colname == data[2]:
            txt = "irp"
        elif colname == data[3]:
            txt = "idesc"
        elif colname == data[4]:
            txt = "icat"
        return txt

    def showAll(self):
        Apptools.defaultqueryrun(self, "items")
        sql_query = "Select * from items where SellerUsername=%s;"
        record = Apptools.sql_run(self, [sql_query, (G_USERNAME.get(),)])
        if record is not None:
            out = record[0]
            if out != []:
                self.output(out)
        if out == []:
            messagebox.showinfo("No data", "No records found")

    def outofstock(self):
        Apptools.defaultqueryrun(self, "items")

        sql_query = "Select * from items where SellerUsername=%s and istock=0;"
        record = Apptools.sql_run(self, [sql_query, (G_USERNAME.get(),)])
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

        Apptools.tkLabel(
            screen, "Search Items", 0, 0, 20, "Segoe UI", 30, 10, rs=1, cs=1
        )

        column = (
            "Item no.",
            "Item Name",
            "Wholesale Price",
            "Retail Price",
            "Description",
            "Category",
            "Stock",
        )
        listBox = ttk.Treeview(screen)

        verscrlbar = ttk.Scrollbar(screen, orient="vertical", command=listBox.yview)
        verscrlbar.grid(row=1, column=1, sticky="nsw", rowspan=2)

        listBox.config(selectmode="extended", columns=column, show="headings")
        listBox.configure(yscrollcommand=verscrlbar.set)

        for i in range(0, len(column)):
            listBox.heading(column[i], text=column[i])
            listBox.column(column[i], minwidth=0)

        for col in column:
            listBox.heading(col, text=col)
            listBox.column(col, width=tkFont.Font().measure(col.title()))
        listBox.grid(row=1, column=0)

        for i in out:
            i = self.singleline(i)
            listBox.insert("", "end", values=i[: len(column)])

            for indx, val in enumerate(i[: len(column)]):
                ilen = tkFont.Font().measure(val)
                if listBox.column(column[indx], width=None) < ilen:
                    listBox.column(column[indx], width=ilen)

    def singleline(self, txtlines):
        l = []
        for i in txtlines:
            if isinstance(i, str):
                l.append(i.replace("\n", " "))
            else:
                l.append(i)
        return l


class Page4_SellerRemoveItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        Apptools.tkLabel(self, "Remove Item", 1, 1, 20, "Segoe UI", 30, 10, rs=1, cs=3)

        Apptools.tkLabel(self, "Item Code", 2, 1, 10, "Segoe UI", 5, 10, rs=1, cs=1)

        itemno = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn = tk.Button(self, text="Delete Item")
        btn.config(command=lambda: self.deleteitem(master, itemno.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        Apptools.tkLabel(
            self,
            "Item Code can be found in\nSearch Items Section.",
            6,
            1,
            10,
            "Segoe UI",
            5,
            10,
            rs=1,
            cs=3,
        )

    def deleteitem(self, master, itemno):
        cond1 = Apptools.check_digit(self, itemno)
        if cond1:
            rec = Apptools.defaultqueryrun(self, "items")
            query = "select iname,irp,idesc from items where itemno=%s and SellerUsername=%s;"
            out = Apptools.sql_run(self, [query, (itemno, G_USERNAME.get())])
            if rec and out:
                data = out[0]
                if data != []:
                    data = data[0]
                    txt = (
                        "Name = "
                        + data[0]
                        + "\nPrice = "
                        + str(data[1])
                        + "\nDescription = "
                        + data[2]
                    )
                    choice = messagebox.askyesno(
                        "Alert", "Are you sure want to remove the item?\n" + txt
                    )
                    if choice:
                        del_query = "Delete from items where itemno = %s;"
                        rec = Apptools.sql_run(self, [del_query, (itemno,)])
                        if rec is not None:
                            messagebox.showinfo("Success", "Item Removed Successfully")
                            Apptools.clearImgCache(self)
                            master.switch_frame(Page3_DashboardSeller)
                else:
                    messagebox.showwarning(
                        "Invalid Item Code", "Item Code is incorrect"
                    )
        else:
            messagebox.showwarning(
                "Invalid Field", "Fill all the forms correctly to continue"
            )


class Page4_SellerRecentTransactions(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        frame = ScrollableFrame(self, ch=300, cw=585)
        sframe = frame.scrollable_frame

        btn = tk.Button(
            sframe,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardSeller),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            sframe, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        Apptools.tkLabel(
            sframe, "Transaction Log", 1, 0, 20, "Segoe UI", 30, 10, rs=1, cs=4
        )

        self.recentlybrought(sframe)

        frame.grid(row=0, column=0)

    def recentlybrought(self, sframe):
        rec = Apptools.defaultqueryrun(self, "trecord")
        query = "Select * from trecord where SellerUsername=%s;"
        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])

        if out is not None and rec:
            out = out[0]
            if out != []:
                self.output(out, sframe)
            else:
                messagebox.showinfo("No records found", "No recent transactions")

    def output(self, out, sframe):
        column = (
            "Transaction Unique Id",
            "Transaction Id",
            "Date and Time",
            "Item name",
            "Quantity",
            "Amount Paid",
            "Buyer Name",
            "Seller Organisation",
        )

        listBox = ttk.Treeview(
            sframe, selectmode="extended", columns=column, show="headings"
        )

        for i in range(len(column)):
            listBox.heading(column[i], text=column[i])
            listBox.column(column[i], minwidth=0)
        for col in column:
            listBox.heading(col, text=col)
            listBox.column(col, width=tkFont.Font().measure(col.title()))
        listBox.grid(row=2, column=1, sticky="we")

        for i in out:
            i = i[:-3]
            listBox.insert("", "end", values=i)

            for indx, val in enumerate(i):
                ilen = tkFont.Font().measure(val)
                if listBox.column(column[indx], width=None) < ilen:
                    listBox.column(column[indx], width=ilen)


class Page4_BuyerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_DashboardBuyer),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        Apptools.tkLabel(self, "Profile", 1, 1, 20, "Segoe UI", 30, 10, rs=1, cs=2)

        Fieldname = [
            "Name",
            "Age",
            "Gender",
            "Mobile No.",
            "Premium Member",
            "Delivery Address",
        ]
        query = "select Name,age,Gender,MobNo,ispremium,deladd from logindatabuyer where username=%s;"
        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])
        if out:
            out = list(out[0][0])
            if out[2] == "M":
                out[2] = "Male"
            elif out[2] == "F":
                out[2] = "Female"
            else:
                out[2] = "Not specified"

            if out[4].upper() == "Y":
                out[4] = "Yes"
            else:
                out[4] = "No"
            for i in range(len(Fieldname)):
                Apptools.tkLabel(
                    self,
                    Fieldname[i] + ":",
                    i + 2,
                    1,
                    15,
                    "Segoe Print",
                    5,
                    0,
                    rs=1,
                    cs=1,
                )

                Apptools.tkLabel(
                    self, out[i], i + 2, 2, 15, "Segoe Print", 5, 0, rs=1, cs=1
                )


class Page4_BuyerRecentlyBrought(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        frame = ScrollableFrame(self, ch=300, cw=585)

        btn = tk.Button(
            frame.scrollable_frame,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_BuyerShoppe),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            frame.scrollable_frame,
            text="Logout",
            command=lambda: Apptools.logout(self, master),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        Apptools.tkLabel(
            frame.scrollable_frame,
            "Recently Brought",
            1,
            0,
            20,
            "Segoe UI",
            30,
            10,
            rs=1,
            cs=4,
        )

        self.recentlybrought(frame.scrollable_frame)

        frame.grid(row=0, column=0)

    def recentlybrought(self, sframe):
        rec = Apptools.defaultqueryrun(self, "trecord")
        query = "Select * from trecord where BuyerUsername=%s;"
        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])

        if out is not None and rec:
            out = out[0]
            if out != []:
                self.output(out, sframe)
            else:
                messagebox.showinfo(
                    "No records found", "No Items Brought Recently\nStart Shopping"
                )

                Apptools.tkLabel(
                    sframe, "Start Shopping", 2, 1, 15, "Segoe UI", 30, 10, rs=1, cs=1
                )

    def output(self, out, sframe):
        column = (
            "Transaction Unique Id",
            "Transaction Id",
            "Date and Time",
            "Item name",
            "Quantity",
            "Amount Paid",
            "Buyer Name",
            "Seller Organisation",
        )

        listBox = ttk.Treeview(
            sframe, selectmode="extended", columns=column, show="headings"
        )

        for i in range(len(column)):
            listBox.heading(column[i], text=column[i])
            listBox.column(column[i], minwidth=0)
        for col in column:
            listBox.heading(col, text=col)
            listBox.column(col, width=tkFont.Font().measure(col.title()))
        listBox.grid(row=2, column=1, sticky="we")

        for i in out:
            i = i[:-3]
            listBox.insert("", "end", values=i)

            for indx, val in enumerate(i):
                ilen = tkFont.Font().measure(val)
                if listBox.column(column[indx], width=None) < ilen:
                    listBox.column(column[indx], width=ilen)


class Page4_BuyerShopping(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        frame = ScrollableFrame(self)

        btn = tk.Button(
            frame.scrollable_frame,
            text="Go Back",
            command=lambda: master.switch_frame(Page3_BuyerShoppe),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            frame.scrollable_frame,
            text="Logout",
            command=lambda: Apptools.logout(self, master),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        Apptools.tkLabel(
            frame.scrollable_frame,
            "Kans\nStart Shopping",
            1,
            1,
            20,
            "Segoe UI",
            0,
            10,
            rs=1,
            cs=3,
        )

        Apptools.image_Show(
            frame.scrollable_frame, DASHBOARDImgDir, 2, 0, 700, 110, cspan=5
        )

        Dir = CATEGORYCARDImgDir
        r, c = 3, 1
        for i in range(len(Dir)):
            diry = CATEGORYCARDFOLDERNAME + "//" + Dir[i]
            try:
                Photo = Image.open(diry)
                Photo = Photo.resize((200, 200))
                render = ImageTk.PhotoImage(Photo)

            except Exception as e:
                Photo = Image.open(DEFAULTIMAGEDir)
                Photo = Photo.resize((200, 200))
                render = ImageTk.PhotoImage(Photo)
                print(e)
            imgbtnfs = tk.Button(frame.scrollable_frame, image=render)
            imgbtnfs.image = render
            imgbtnfs.grid(row=r, column=c, padx=10, pady=10)
            imgbtnfs.config(command=lambda x=i: self.framechange(master, x))

            if c == 3:
                r += 1
                c = 1
            else:
                c += 1

        frame.grid(row=0, column=0)

    def framechange(self, master, x):
        globals()["itemtype"] = x
        master.switch_frame(Page5_BuyerItemPicker)


class Page5_BuyerItemPicker(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Go Back",
            command=lambda: master.switch_frame(Page4_BuyerShopping),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            self, text="Logout", command=lambda: Apptools.logout(self, master)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        Apptools.tkLabel(
            self, "Kans\nStart Shopping", 1, 0, 20, "Segoe UI", 0, 10, rs=1, cs=3
        )

        cat = self.itemcategory(itemtype)

        Apptools.tkLabel(self, cat.title(), 2, 0, 20, "Segoe UI", 0, 10, rs=1, cs=3)

        self.search(master, cat)

    def search(self, master, category):
        Apptools.defaultqueryrun(self, "items")

        if Apptools.is_not_null(self, category):
            category = "%" + category + "%"
            query = "Select * from items where icat like %s and istock>0;"
            record = Apptools.sql_run(self, [query, (category,)])

            if record is not None:
                out = record[0]
                self.output(master, out)
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def output(self, master, out):
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=3, sticky="ew")
        frame = ScrollableFrame(self, cw=500, ch=300)

        if out != []:
            r = 0
            for ino, iname, iwp, irp, idesc, icat, istock, imgdir, selluser in out:
                orgname = self.sellerorgname(selluser)

                txt = "Item name : " + iname.title() + "\nSeller : " + orgname
                txt += (
                    "\nDescription : " + idesc.title() + "\nCategory : " + icat.title()
                )
                txt += "\nPrice : ₹" + str(irp)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    print(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((250, 150))
                    render = ImageTk.PhotoImage(Photo)

                imgbtnfs = tk.Button(
                    frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT
                )
                imgbtnfs.image = render
                imgbtnfs.config(
                    bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT
                )
                imgbtnfs.config(activebackground="#3297E9", font=("Segoe Print", 15))
                imgbtnfs.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                idata = [
                    ino,
                    iname,
                    iwp,
                    irp,
                    idesc,
                    icat,
                    istock,
                    imgdir,
                    selluser,
                    orgname,
                ]
                imgbtnfs.config(command=lambda x=idata: self.imgitemclick(master, x))

                r += 1

        else:
            Apptools.tkLabel(
                frame.scrollable_frame,
                "No Items Found :-(",
                0,
                2,
                30,
                "Segoe Print",
                100,
                100,
                rs=1,
                cs=4,
            )

        frame.grid(row=6, column=0, columnspan=3)

    def sellerorgname(self, suser):
        rec = Apptools.defaultqueryrun(self, "logindataseller")
        if rec:
            query = "select OrgName from logindataseller where username=%s;"
            out = Apptools.sql_run(self, [query, (suser,)])
            if out:
                if out[0]:
                    return out[0][0][0]

    def addtocart(self, ino, iqty, istock, showMsg=True):
        cond1 = Apptools.check_digit(self, iqty)
        cond2 = Apptools.in_limit(self, 1, istock, iqty)
        cond3 = iqty.find(".") == -1 and iqty.find("-") == -1

        if cond1 and cond2 and cond3:
            cartuc = Apptools.generateuniquecode(self, "cart", "cartuc")
            Apptools.defaultqueryrun(self, "cart")
            query11 = "Select cartuc,iquantity from cart where itemno=%s and BuyerUsername = %s;"
            query12 = "Select istock from items where itemno=%s;"
            out = Apptools.sql_run(
                self, [query11, (ino, G_USERNAME.get())], [query12, (ino,)]
            )

            if out is not None and out[0] != [] and out[1] != []:
                istockn = out[1][0][0]
                if out[0][0][1] + int(iqty) <= istockn:
                    query2 = "Update cart set iquantity=iquantity+%s where cartuc=%s;"
                    rec0 = Apptools.sql_run(self, [query2, (iqty, out[0][0][0])])
                    if rec0 is not None:
                        if showMsg:
                            messagebox.showinfo(
                                "Success!", "Added to Cart Successfully!"
                            )
                        return True
                else:
                    maxst = istockn - out[0][0][1]
                    if maxst == 0 and istock > 0:
                        messagebox.showwarning(
                            "Out of Stock",
                            "Item is out of stock check your cart if you have pre-booked that.",
                        )
                    else:
                        messagebox.showwarning(
                            "Invalid Input!",
                            "Enter Valid Input for Quantity\nMin Value=0\nMax Value="
                            + str(maxst),
                        )
            elif out[0] == []:
                rec = Apptools.insertSQL(
                    self, "cart", cartuc, ino, iqty, G_USERNAME.get()
                )
                if rec is not None:
                    if showMsg:
                        messagebox.showinfo("Success!", "Added to Cart Successfully!")
                    return True
        elif istock == 0:
            messagebox.showwarning("Out of Stock", "Item is out of stock.")
        else:
            messagebox.showwarning(
                "Invalid Input!",
                "Enter Valid Input for Quantity\nMin Value=0\nMax Value=" + str(istock),
            )

    def imgitemclick(self, master, x):
        globals()["chooseditemdetails"] = x
        ino, iname, iwp, irp, idesc, icat, istock, imgdir, selluser, orgname = x
        qty = simpledialog.askinteger("Input", "Enter Quantity", parent=self)
        if qty is not None:
            x = self.addtocart(ino, str(qty), istock)
            if x:
                choice = messagebox.askyesno("Proceed to Pay?", "Proceed to payment?")
                if choice:
                    master.switch_frame(Page7_BuyerPaymentProceed)

    def itemcategory(self, i):
        Category = [
            "Stationary",
            "Electronics",
            "Clothing",
            "Beauty",
            "Softwares",
            "Sports",
            "Daily Use",
            "Grocery",
            "Health",
            "Others",
        ]
        if i <= 9:
            return Category[i]


class Page7_BuyerPaymentProceed(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        sframe = ScrollableFrame(self, cw=750, ch=600)

        btn = tk.Button(
            sframe.scrollable_frame,
            text="Buyer's Home",
            command=lambda: master.switch_frame(Page3_BuyerShoppe),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(
            sframe.scrollable_frame,
            text="Logout",
            command=lambda: Apptools.logout(self, master),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        Apptools.tkLabel(
            sframe.scrollable_frame,
            "Payment Confirmation",
            1,
            0,
            20,
            "Segoe UI",
            30,
            10,
            rs=1,
            cs=3,
        )

        lbl = tk.Label(sframe.scrollable_frame, text="Cart")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="w")

        sep = ttk.Separator(sframe.scrollable_frame, orient="horizontal")
        sep.grid(row=3, column=0, sticky="ew", columnspan=2)

        frame = ScrollableFrame(sframe.scrollable_frame, cw=550, ch=300)

        out = self.retrievedata()

        totalprice = 0

        if out != []:
            r = 0
            for (
                ino,
                iname,
                iwp,
                irp,
                idesc,
                icat,
                istock,
                imgdir,
                selluser,
                iqty,
            ) in out:
                orgname = self.sellerorgname(selluser)

                txt = "Item name : " + iname.title() + "\nSeller : " + orgname
                txt += (
                    "\nDescription : " + idesc.title() + "\nCategory : " + icat.title()
                )
                txt += "\nPrice : ₹" + str(irp) + "\nQuantity : " + str(iqty)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    print(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                lbl = tk.Label(
                    frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT
                )
                lbl.image = render
                lbl.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT)
                lbl.config(activebackground="#3297E9", font=("Segoe Print", 15))
                lbl.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                btn = tk.Button(
                    frame.scrollable_frame,
                    text="Remove Item",
                    command=lambda x=ino: self.deleteitemcart(master, x),
                )
                btn.config(
                    bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9"
                )
                btn.grid(row=r, column=1)
                r += 1
                totalprice += irp * iqty

        else:
            Apptools.tkLabel(
                frame.scrollable_frame,
                "No Items Found :-(",
                0,
                2,
                30,
                "Segoe Print",
                100,
                100,
                rs=1,
                cs=4,
            )

        frame.grid(row=4, column=0, columnspan=2, sticky="nw")

        userd = self.userdata()
        netb = 0
        if userd is not None:
            lbl = tk.Label(
                sframe.scrollable_frame,
                text="Deliever to\n" + userd[0] + "\n" + userd[1],
            )
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=3, column=2, padx=10, pady=5, rowspan=2, sticky="ns")

            netb = self.bargain(out, userd[2])
            lbl1 = tk.Label(sframe.scrollable_frame, text="Net Bargain : ₹" + str(netb))
            lbl1.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl1.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsw")

            lbl = tk.Label(
                sframe.scrollable_frame,
                text="Amount to be Paid : ₹"
                + str(round(totalprice - netb + 5, 2))
                + "\nInclusive of PG Charge(₹5)",
            )
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="nsw")

        lbl = tk.Label(
            sframe.scrollable_frame, text="Total Price : ₹" + str(totalprice)
        )
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsw")

        price = round(totalprice - netb, 2)
        btn = tk.Button(
            sframe.scrollable_frame,
            text="Proceed to Pay",
            command=lambda: self.payportal(master, out, price, sframe),
        )
        btn.config(
            bg="#1F8EE7", padx=7, pady=4, fg="#E8E8E8", bd=0, activebackground="#3297E9"
        )
        btn.grid(row=6, column=2, rowspan=3)

        sframe.grid(row=0, column=0)

    def retrievedata(self):
        Apptools.defaultqueryrun(self, "cart")
        Apptools.defaultqueryrun(self, "items")
        query = "Select itemno,iquantity from cart where buyerusername =%s;"
        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])

        data = []
        if out is not None:
            if out[0] != []:
                out = out[0]
                for ino, iqty in out:
                    query2 = "Select * from items where itemno=%s;"
                    out2 = Apptools.sql_run(self, [query2, (ino,)])

                    if out2 is not None and out2[0] != []:
                        out2 = out2[0][0]
                        data.append(list(out2) + [iqty])
        return data

    def userdata(self):
        query = "select Name,DelAdd,IsPremium from logindatabuyer where username=%s;"

        out = Apptools.sql_run(self, [query, (G_USERNAME.get(),)])
        if out:
            if out[0]:
                return out[0][0]

    def deleteitemcart(self, master, ino):
        query = "delete from cart where itemno=%s and BuyerUsername=%s;"
        rec = Apptools.sql_run(self, [query, (ino, G_USERNAME.get())])
        if rec is not None:
            messagebox.showinfo("Success", "Item Deleted Successfully")
            master.switch_frame(Page7_BuyerPaymentProceed)

    def bargain(self, out, ispremium):
        netbargain = 0

        if out != [] and ispremium.upper() == "Y":
            for (
                ino,
                iname,
                iwp,
                irp,
                idesc,
                icat,
                istock,
                imgdir,
                selluser,
                iqty,
            ) in out:
                r = (irp / iwp) * 100
                if r > 120:
                    netbargain += max(0, iqty * (irp - (iwp * 120 / 100)))
                    # Ensuring at least 20% Profit(approx) for seller
        # To ensure bargain is never greater than the limit due to approximation
        return round(netbargain, 2)

    def payportal(self, master, out, price, sframe):
        items = []
        if out != []:
            for (
                ino,
                iname,
                iwp,
                irp,
                idesc,
                icat,
                istock,
                imgdir,
                selluser,
                iqty,
            ) in out:
                if istock >= iqty:
                    items.append(
                        [
                            ino,
                            iname,
                            iwp,
                            irp,
                            idesc,
                            icat,
                            istock,
                            imgdir,
                            selluser,
                            iqty,
                        ]
                    )

                else:
                    txtmsg = (
                        "Only a Few stocks are left as item is getting out of stock."
                    )
                    txtmsg += "\nStocks available for " + iname + " is " + str(istock)
                    txtmsg += (
                        "\nCan't Buy this item. :-(\nTry Checking with fewer stocks"
                    )

                    messagebox.showwarning("Item is out of Stock", txtmsg)
            if items != []:
                self.paymentpage(master, price, items, sframe)

        else:
            messagebox.showwarning(
                "Empty Cart", "Your Cart is Empty Start Shopping Now."
            )

    def paymentpage(self, master, price, out, sframe):
        screen = tk.Toplevel(self, bg="#333333")
        screen.iconphoto(False, Icon)
        screen.title("Payment Portal @Kans")
        screen.resizable(0, 0)

        Apptools.tkLabel(
            screen, "Payment Portal", 0, 1, 20, "Segoe UI", 30, 10, rs=1, cs=3
        )

        Apptools.tkLabel(
            screen,
            "Total Transaction Amount : ₹" + str(price) + "+₹5 (PG Charges)",
            1,
            1,
            8,
            "Segoe UI",
            20,
            10,
            rs=1,
            cs=1,
        )

        Apptools.tkLabel(screen, "Enter PIN", 2, 1, 8, "Segoe UI", 20, 10, rs=1, cs=1)

        pin = tk.Entry(screen, fg="#E8E8E8", bg="#333333", show="*")
        pin.grid(row=2, column=2)

        btn = tk.Button(screen, text="Proceed")
        btn.config(
            command=lambda: self.checktrans(master, pin.get(), price, out, sframe)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

    def checktrans(self, master, pin, price, out, sframe):
        if pin == G_PIN.get():
            txt = (
                "Transaction Amount : "
                + str(price + 5)
                + "\nIncluding PG Charges\nAre you sure want to proceed?"
            )
            choice = messagebox.askyesno("Transaction Confirmation", txt)
            if choice:
                tid = Apptools.generateuniquecode(self, "trecord", "tid")
                for i in range(len(out)):
                    ino = out[i][0]
                    irp = out[i][3]
                    iqty = out[i][9]
                    selleruser = out[i][8]
                    iname = out[i][1]

                    ispremium = self.userdata()[2]
                    netbargain = self.bargain([out[i]], ispremium)

                    bname = self.buyername(G_USERNAME.get())
                    sorg = self.sellerorgname(selleruser)

                    query3 = "delete from cart where itemno=%s and BuyerUsername=%s;"
                    query4 = "Update items set istock=istock-%s where itemno=%s;"

                    tuid = Apptools.generateuniquecode(self, "trecord", "tuid")
                    tdate = self.timeformat()
                    rec4 = Apptools.insertSQL(
                        self,
                        "trecord",
                        tuid,
                        tid,
                        tdate,
                        iname,
                        iqty,
                        (irp * iqty - netbargain),
                        bname,
                        sorg,
                        ino,
                        G_USERNAME.get(),
                        selleruser,
                    )

                    rec3 = Apptools.sql_run(
                        self, [query3, (ino, G_USERNAME.get())], [query4, (iqty, ino)]
                    )

                if rec4 is not None and rec3 is not None:
                    messagebox.showinfo(
                        "Success!", "Transaction completed successfully!"
                    )
                    lbl = tk.Label(
                        sframe.scrollable_frame,
                        text="Transaction Done\nItem Delivered\nPay Cash on Delivery",
                    )
                    lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=6, column=2, rowspan=3, sticky="ns")
        else:
            messagebox.showwarning(
                "Invalid PIN", "Invalid PIN\nTry entering correct PIN"
            )

    def timeformat(self):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date

    def sellerorgname(self, user):
        Apptools.defaultqueryrun(self, "logindataseller")
        query = "Select OrgName from logindataseller where username=%s;"
        out = Apptools.sql_run(self, [query, (user,)])
        if out and out[0]:
            return out[0][0][0]
        else:
            return "SellerUsername.:-" + user

    def buyername(self, user):
        Apptools.defaultqueryrun(self, "logindatabuyer")
        query = "Select Name from logindatabuyer where username=%s;"
        out = Apptools.sql_run(self, [query, (user,)])
        if out and out[0]:
            return out[0][0][0]
        else:
            return "Buyer Username:-" + user


# Main Program
if __name__ == "__main__":
    app = App()
    app.title("Kans:Your shopping partner")
    app.resizable(0, 0)
    try:
        Icon = PhotoImage(file=LOGOImgDir)
        app.iconphoto(False, Icon)
    except Exception as e:
        print(e)
        Icon = PhotoImage(file=DEFAULTIMAGEDir)
        app.iconphoto(False, Icon)
    app.mainloop()
