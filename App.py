# -*- coding: utf-8 -*-
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
    print("Import Error", e, sep="\n")
    print("Part/Complete of Program may malfunction severely.")
    print("Strongly Recommended to install module before starting")

"""
Database and File saving Directories
"""
HOST = "localhost"
USERNAME = "root"
PASSWORD = "password"
DATABASE = "Kans2"
savedir = "C:\\Kans\\App\\ItemImage\\"


"""
Some Custom Variable(Not to be modified)
"""
savlocimgbtn = ""
chooseditemdetails = []

"""
Image Files Directories
"""
LOGOImgDir = "logo.png"
DEFAULTIMAGEDir = "Additem.png"
HOMEPAGEImgDir = "logo.png"


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
        >>> print(sql_run(None,['Select * from base;']))
        [[(1, 'a'), (2, 'B'), (3, 'C'), (4, 'D'), (5, 'D')]]
        >>> print(sql_run(None,['Insert into base values(%s,%s);',(6,"d")]))
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
                pswd = simpledialog.askstring(
                    "Input", "Enter Database Password", parent=self
                )
                if user is not None and pswd is not None:
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
        if table == "items":
            def_query = """Create table IF NOT EXISTS items(
            itemno int PRIMARY KEY,
            iname varchar(64) NOT NULL,
            iwhp int NOT NULL,
            irp int NOT NULL,
            idesc varchar(250) NOT NULL,
            icat varchar(32) NOT NULL,
            istock int NOT NULL,
            imgdir varchar(255) NOT NULL);
            """
        elif table == "cart":
            def_query = """Create table IF NOT EXISTS cart(
            cartuc varchar(8) PRIMARY KEY,
            itemno int,
            iquantity int NOT NULL);"""

        elif table == "trecord":
            def_query = """Create table IF NOT EXISTS trecord(
            tuid varchar(8) PRIMARY KEY,
            tid varchar(8) ,
            tdate datetime NOT NULL,
            iname varchar(64) NOT NULL,
            tqty int NOT NULL,
            tpaidamt DECIMAL(20,2) NOT NULL,
            titemno int NOT NULL);"""
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
        Apptools.image_Show(self, HOMEPAGEImgDir, 0, 0, 300, 450, rspan=5)

        lbl = tk.Label(self, text="Welcome to\nKans")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        btn = tk.Button(
            self,
            text="Add Items",
            command=lambda: master.switch_frame(Page4_SellerAddItems),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=2, column=2, padx=5)

        btn = tk.Button(
            self,
            text="Buy Item",
            command=lambda: master.switch_frame(Page4_BuyerSearchItems),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=2, padx=5)


class Page4_SellerAddItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self, text="Go Back", command=lambda: master.switch_frame(Homepage)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        lbl = tk.Label(self, text="Add Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Item Name")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        Iname = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iname.grid(row=2, column=2)

        lbl = tk.Label(self, text="Wholesale Price")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        Iwhp = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iwhp.grid(row=3, column=2)

        lbl = tk.Label(self, text="Retail Price")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, pady=10)

        Irp = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Irp.grid(row=4, column=2)

        lbl = tk.Label(self, text="No. of Stocks")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, padx=5, pady=10)

        Istock = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Istock.grid(row=5, column=2)

        lbl = tk.Label(self, text="Description")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5, pady=10)

        IDesc = tk.Text(self, fg="#E8E8E8", bg="#333333", height=5)
        IDesc.config(width=15)
        IDesc.grid(row=6, column=2)

        lbl = tk.Label(self, text="Category")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5, pady=10)

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

        lbl = tk.Label(self, text="Add Image")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5, pady=10)

        globals()["savlocimgbtn"] = DEFAULTIMAGEDir
        Apptools.imgsavebtn(self, DEFAULTIMAGEDir, 100, 100, 8, 2)

        btn = tk.Button(self, text="Add Item")
        btn.config(
            command=lambda: self.additem(
                master,
                Iname.get(),
                Iwhp.get(),
                Irp.get(),
                Istock.get(),
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
                    )

                    if rec2 is not None:
                        messagebox.showinfo("Success!", "Item added successfully")
                        master.switch_frame(Homepage)
                        Apptools.clearImgCache(self)
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


class Page4_BuyerSearchItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self, text="Go Back", command=lambda: master.switch_frame(Homepage)
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        lbl = tk.Label(self, text="Search Items")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=4, padx=30, pady=10)

        lbl = tk.Label(self, text="Search Criteria")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        Searchcr = ["Item Name", "Description", "Category"]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Value")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        val = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn = tk.Button(self, text="Search")
        btn.config(command=lambda: self.search(master, val.get(), SearchcrVar.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        self.showAll(master)

    def search(self, master, text, criteria):
        Apptools.defaultqueryrun(self, "items")

        if Apptools.is_not_null(self, text):
            text = "%" + text + "%"
            query = "Select * from items where " + self.dbeqv(criteria) + " like %s;"
            record = Apptools.sql_run(self, [query, (text,)])

            if record is not None:
                out = record[0]
                self.output(master, out)
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def showAll(self, master):
        Apptools.defaultqueryrun(self, "items")
        sql_query = "Select * from items where istock>0;"
        record = Apptools.sql_run(self, [sql_query, ()])
        if record is not None:
            out = record[0]
            if out != []:
                self.output(master, out)
            if out == []:
                messagebox.showinfo("No data", "No records found")

    def dbeqv(self, colname):
        txt = ""
        data = ["Item Name", "Description", "Category"]
        if colname == data[0]:
            txt = "iname"
        elif colname == data[1]:
            txt = "idesc"
        elif colname == data[2]:
            txt = "icat"
        return txt

    def output(self, master, out):
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=5, column=0, columnspan=5, sticky="ew")
        frame = ScrollableFrame(self, cw=500, ch=300)

        if out != []:
            r = 0
            for ino, iname, iwp, irp, idesc, icat, istock, imgdir in out:
                txt = "Item name : " + iname.title()
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

                idata = [ino, iname, iwp, irp, idesc, icat, istock, imgdir]
                imgbtnfs.config(command=lambda x=idata: self.framechange(master, x))
                r += 1

        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)

        frame.grid(row=6, column=0, columnspan=5)

    def framechange(self, master, x):
        globals()["chooseditemdetails"] = x
        master.switch_frame(Page6_BuyerProductView)


class Page6_BuyerProductView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Back",
            command=lambda: master.switch_frame(Page4_BuyerSearchItems),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        lbl = tk.Label(self, text="Kans : Your Shopping Partner")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=4, padx=30, pady=10)

        itemdetails = chooseditemdetails

        ino, iname, iwp, irp, idesc, icat, istock, imgdir = itemdetails

        txt = "Item name : " + iname.title()
        txt += "\nDescription : " + idesc.title() + "\nCategory : " + icat.title()
        txt += "\nPrice : ₹" + str(irp)

        try:
            Photo = Image.open(imgdir)
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        except Exception as e:
            print(e)

            Photo = Image.open(DEFAULTIMAGEDir)
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        lbl = tk.Label(self, text=txt, image=render, compound=tk.LEFT)
        lbl.image = render
        lbl.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0)
        lbl.config(activebackground="#3297E9", font=("Segoe Print", 15))
        lbl.grid(row=2, column=1, columnspan=2, rowspan=2, padx=10, pady=10)

        btn = tk.Button(
            self,
            text="Add to Cart",
            command=lambda: self.addtocart(ino, qty.get(), istock),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=2, column=3, pady=10)

        lbl = tk.Label(self, text="Enter Quantity")
        lbl.config(font=("Chiller", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, pady=10)

        qty = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        qty.grid(row=4, column=2)
        qty.insert(0, 1)

        btn = tk.Button(
            self,
            text="Add to Cart &\nProceed to Pay",
            command=lambda: self.paypage(master, ino, qty.get(), istock),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=2, padx=10, pady=10)

    def addtocart(self, ino, iqty, istock, showMsg=True):
        cond1 = Apptools.check_digit(self, iqty)
        cond2 = Apptools.in_limit(self, 1, istock, iqty)
        cond3 = iqty.find(".") == -1 and iqty.find("-") == -1

        if cond1 and cond2 and cond3:
            cartuc = Apptools.generateuniquecode(self, "cart", "cartuc")
            Apptools.defaultqueryrun(self, "cart")
            query11 = "Select cartuc,iquantity from cart where itemno=%s;"
            query12 = "Select istock from items where itemno=%s;"
            out = Apptools.sql_run(self, [query11, (ino,)], [query12, (ino,)])

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
                rec = Apptools.insertSQL(self, "cart", cartuc, ino, iqty)
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

    def paypage(self, master, ino, qty, istock):
        cond = self.addtocart(ino, qty, istock, showMsg=False)
        if cond:
            master.switch_frame(Page7_BuyerPaymentProceed)


class Page7_BuyerPaymentProceed(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(
            self,
            text="Back",
            command=lambda: master.switch_frame(Page6_BuyerProductView),
        )
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        lbl = tk.Label(self, text="Payment Confirmation")
        lbl.config(font=("Chiller", 40), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Cart")
        lbl.config(font=("Chiller", 30), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="w")

        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=3, column=0, sticky="ew", columnspan=2)

        frame = ScrollableFrame(self, cw=550, ch=300)

        out = self.retrievedata()

        totalprice = 0

        if out != []:
            r = 0
            for ino, iname, iwp, irp, idesc, icat, istock, imgdir, iqty in out:
                txt = "Item name : " + iname.title()
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
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)

        frame.grid(row=4, column=0, columnspan=2, sticky="nw")

        netb = 0

        netb = self.bargain(out)
        lbl1 = tk.Label(self, text="Net Bargain : ₹" + str(netb))
        lbl1.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl1.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsw")

        lbl = tk.Label(
            self,
            text="Amount to be Paid : ₹"
            + str(round(totalprice - netb + 5, 2))
            + "\nInclusive of PG Charge(₹5)",
        )
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="nsw")

        lbl = tk.Label(self, text="Total Price : ₹" + str(totalprice))
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsw")

        price = round(totalprice - netb, 2)
        btn = tk.Button(
            self,
            text="Proceed to Pay",
            command=lambda: self.payportal(master, out, price),
        )
        btn.config(
            bg="#1F8EE7", padx=7, pady=4, fg="#E8E8E8", bd=0, activebackground="#3297E9"
        )
        btn.grid(row=6, column=2, rowspan=3)

    def retrievedata(self):
        Apptools.defaultqueryrun(self, "cart")
        Apptools.defaultqueryrun(self, "items")
        query = "Select itemno,iquantity from cart;"
        out = Apptools.sql_run(self, [query, ()])

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

    def deleteitemcart(self, master, ino):
        query = "delete from cart where itemno=%s;"
        rec = Apptools.sql_run(self, [query, (ino,)])
        if rec is not None:
            messagebox.showinfo("Success", "Item Deleted Successfully")
            master.switch_frame(Page7_BuyerPaymentProceed)

    def bargain(self, out, ispremium="y"):
        netbargain = 0

        if out != [] and ispremium.upper() == "Y":
            for ino, iname, iwp, irp, idesc, icat, istock, imgdir, iqty in out:
                r = (irp / iwp) * 100
                if r > 120:
                    netbargain += max(0, iqty * (irp - (iwp * 120 / 100)))
                    # Ensuring at least 20% Profit(approx) for seller and admin combined
                    # 14% for seller
        # To ensure bargain is never greater than the limit due to approximation
        return round(netbargain, 2)

    def payportal(self, master, out, price):
        items = []
        if out != []:
            for ino, iname, iwp, irp, idesc, icat, istock, imgdir, iqty in out:
                if istock >= iqty:
                    items.append(
                        [ino, iname, iwp, irp, idesc, icat, istock, imgdir, iqty]
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
                self.paymentpage(master, price, items)

        else:
            messagebox.showwarning(
                "Empty Cart", "Your Cart is Empty Start Shopping Now"
            )

    def checktrans(self, master, price, out):
        tid = Apptools.generateuniquecode(self, "trecord", "tid")
        for i in range(len(out)):
            ino = out[i][0]
            irp = out[i][3]
            iqty = out[i][8]
            iname = out[i][1]

            netbargain = self.bargain([out[i]], "Y")

            query3 = "delete from cart where itemno=%s;"
            query4 = "Update items set istock=istock-%s where itemno=%s;"

            rec2 = Apptools.sql_run(self, [query3, (ino,)], [query4, (iqty, ino)])
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
                ino,
            )

            if rec2 is not None and rec4 is not None:
                c = rec2 + rec4  # adds two list
            else:
                messagebox.showerror("Transaction Failed!", "Ask Admin for refund")
                c = None
                break

        if c is not None:
            messagebox.showinfo("Success!", "Transaction completed successfully!")
            lbl = tk.Label(
                self, text="Transaction Done\nItem Delivered\nCash on Delivery"
            )
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=6, column=2, rowspan=3, sticky="ns")

    def timeformat(self):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date

    def addtocart(self, ino, istock):
        iqty = simpledialog.askinteger(
            "Input", "Enter Quantity?", parent=self, minvalue=1, maxvalue=istock
        )

        if iqty is not None:
            iqty = str(iqty)
            cond1 = Apptools.check_digit(self, iqty)
            cond2 = Apptools.in_limit(self, 1, istock, iqty)
            cond3 = iqty.find(".") == -1 and iqty.find("-") == -1

            if cond1 and cond2 and cond3:
                cartuc = Apptools.generateuniquecode(self, "cart", "cartuc")
                Apptools.defaultqueryrun(self, "cart")
                query11 = "Select cartuc,iquantity from cart where itemno=%s;"
                query12 = "Select istock from items where itemno=%s;"
                out = Apptools.sql_run(self, [query11, (ino,)], [query12, (ino,)])

                if out is not None and out[0] != [] and out[1] != []:
                    istockn = out[1][0][0]
                    if out[0][0][1] + int(iqty) <= istockn:
                        query2 = (
                            "Update cart set iquantity=iquantity+%s where cartuc=%s;"
                        )
                        rec0 = Apptools.sql_run(self, [query2, (iqty, out[0][0][0])])
                        if rec0 is not None:
                            messagebox.showinfo(
                                "Success!", "Added to Cart Successfully!"
                            )
                            return True
                    else:
                        maxst = istockn - out[0][0][1]
                        if maxst == 0 and istockn > 0:
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
                    rec = Apptools.insertSQL(self, "cart", cartuc, ino, iqty)
                    if rec is not None:
                        messagebox.showinfo("Success!", "Added to Cart Successfully!")
                        return True
            elif istock == 0:
                messagebox.showwarning("Out of Stock", "Item is out of stock.")
            else:
                messagebox.showwarning(
                    "Invalid Input!",
                    "Enter Valid Input for Quantity\nMin Value=0\nMax Value="
                    + str(istock),
                )


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
