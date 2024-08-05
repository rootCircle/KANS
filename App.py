# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:17:14 2021
Requirements:
    libraries,
    local image files,
    service-account-file + see line @114
pyrebase:login
firebase_admin:db,registration
firebase storage:All Images are saved and retrieved as .png file
@author: rootCircle
Scrolling through mousewheel is supported for Windows,Linux only
Email must always be in lower case
"""

"""
TODO : Add support for '#.$[]\' in firebase
TODO : Local Session Expiry Support by threading
TODO : Login Waiting Sync -Bugs
TODO : Page4_SellerRecentTransactions,Page4_BuyerRecentlyBrought
TODO : Transaction log every cash/wallet cash transaction made through Kans
TODO : Check for http connection instead of https to decrease false positives
TODO : Multi-threading to increase server response time and decrease waiting time(also by optimising queries)
TODO : GIF Transparency
TODO : Add new encoding tech to avoid key duplication in temp bank using timestamp
TODO : LoadingPage bug removal for time synchronisation
"""

LOG_FILE_FOLDER = "res"
LOG_FILE = ""
try:
    from datetime import datetime, timedelta
    import os
    import errno

    try:
        os.makedirs(LOG_FILE_FOLDER)
    except OSError as er:
        if er.errno != errno.EEXIST:
            print(er)

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

    LOG_FILE = os.path.join(LOG_FILE_FOLDER, "log.log")  # Log File init

    print(formatted_date, "============PROGRAM STARTS============", file=open(LOG_FILE, 'a'))
except Exception as e:
    print("ERROR", e)
    import sys

    sys.exit()

try:
    import tkinter as tk
    from tkinter import messagebox, Radiobutton, PhotoImage, StringVar, filedialog, ttk, simpledialog
    import tkinter.font as tkFont
    from PIL import Image, ImageTk
    import random
    import time
    import pyrebase
    import urllib.request
    import json
    import pickle
    import requests.exceptions
    import re
    import threading
    import firebase_admin as firebaseadmin
    import firebase_admin._auth_utils
    from firebase_admin import auth, db, storage
    from firebase_admin import exceptions as fireexception
    from dotenv import load_dotenv

except Exception as ex:
    try:
        os.makedirs(LOG_FILE_FOLDER)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(e)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    print(formatted_date, "Import Error\t", ex, file=open(LOG_FILE, 'a'))
    import sys

    sys.exit()

load_dotenv()  # take environment variables from .env.

"""
Some Custom Variable(Not to be modified)
"""
ITEMTYPE = -1
CHOOSEDITEMDETAILS = []

"""
Image Files Directories
"""
LOGOImgDir = os.path.join("data", "logonew.png")
DEFAULTIMAGEDir = os.path.join("data", "Additem.png")
HOMEPAGEImgDir = os.path.join("data", "logo.png")
SIGNUPPAGEImgDir = [os.path.join("data", "Part1.png"), os.path.join("data", "Part2.png")]
DASHBOARDImgDir = os.path.join("data", "Lighthouse.jpg")
# Files in Directory CATEGORYCARDFOLDERNAME Var
CATEGORYCARDFOLDERNAME = os.path.join("data", "CardsShop")
CATEGORYCARDImgDir = ["Img1.jpg", "Img2.jpg", "Img3.jpg", "Img4.jpg", "Img5.jpg", "Img6.jpg"]
CATEGORYCARDImgDir += ["Img7.jpg", "Img8.jpg", "Img9.jpg", "Img10.jpg"]

"""
Firebase Credentials
Dev need to enable login via EMAIL and PASSWORD in authentication section.
Put DB URL from RealTime Database section dashboard
FOR firebaseConfig variable : copy details from creating a web-app section in that firebase database
SERVICEACCOUNTFILE can be downloaded from setting section of Realtime database

in firebase variable:storage-bucket can be fetched from Storage section in Firebase
"""

SERVICEACCOUNTFILE = os.path.join("res", "service-account-file.json")
dbURL = os.getenv("FIREBASE_DB_URL")

firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    'databaseURL': dbURL,
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "serviceAccount": SERVICEACCOUNTFILE
}
pfirebase = pyrebase.initialize_app(firebaseConfig)
pauth = pfirebase.auth()

cred = firebaseadmin.credentials.Certificate(SERVICEACCOUNTFILE)
firebase = firebaseadmin.initialize_app(cred, {
    'databaseURL': dbURL,
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

WALLETTABLE = "Wallet"
CASHRECORDTABLE = "Cash Record Admin"
SESSION_USER = None
SESSION_FILE_FOLDER = "res"
SESSION_CACHE_FILE = os.path.join(SESSION_FILE_FOLDER, "sessioncache.dat")
CACHE_FOLDER = "cache"

LOADING_SCREENS = []
LOADING_GIF = os.path.join("data", "Loading.gif")

LeastWaitTime = 0.5  # in second(min time for loading)


# Application assume gif size to be 300*300

class LoadingPage(tk.Label):
    """
    Doesn't support non-void function as its return is not synchronised
    """

    def __init__(self, master, filename):
        try:
            im = Image.open(filename)
            seq = []
            try:
                while 1:
                    seq.append(im.copy())
                    im.seek(len(seq))  # skip to next frame
            except EOFError:
                pass  # we're done

            try:
                self.delay = im.info['duration']
            except KeyError:
                self.delay = 100

            first = seq[0].convert('RGBA')
            self.frames = [ImageTk.PhotoImage(first)]

            tk.Label.__init__(self, master, image=self.frames[0])

            temp = seq[0]
            for image in seq[1:]:
                temp.paste(image)
                frame = temp.convert('RGBA')
                self.frames.append(ImageTk.PhotoImage(frame))

            self.idx = 0

            self.cancel = self.after(self.delay, self.play)
        except FileNotFoundError as e:
            Apptools.writeLog("File not found\nQuit Module Use" + str(e))
            os._exit(0)

    def play(self):
        try:
            self.config(image=self.frames[self.idx])
            self.idx += 1
            if self.idx == len(self.frames):
                self.idx = 0
            self.cancel = self.after(self.delay, self.play)
        except Exception as e:
            Apptools.writeLog(e)

    def start(self, grab=True):
        """
        grab will set toplevel active and root window inactive
        """
        try:
            if not LOADING_SCREENS:
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                gifhalfdimension = [50, 50]
                LOADING_SCREENS.append(tk.Toplevel(self))
                screen = LOADING_SCREENS[-1]
                try:
                    screen.wm_overrideredirect(True)
                except:
                    screen.overrideredirect(True)

                # Eval is threading Unsafe
                # self.eval(f'tk::PlaceWindow {str(screen)} center')

                # x = self.winfo_x()
                # y = self.winfo_y()

                screen.geometry(
                    "+%d+%d" % (screen_width // 2 - gifhalfdimension[0], screen_height - 3 * gifhalfdimension[1]))
                screen.lift()
                screen.resizable(0, 0)
                if grab:
                    screen.grab_set()
                LoadingPage.anim = LoadingPage(screen, LOADING_GIF)
                LoadingPage.anim.pack()
            else:
                time.sleep(0.1)
                LoadingPage.start(self, grab)
        except RecursionError as e:
            Apptools.writeLog(e)

    def stop_it(self):
        try:
            if LOADING_SCREENS:
                try:
                    screen = LOADING_SCREENS[-1]
                    LoadingPage.anim.after_cancel(LoadingPage.anim.cancel)
                    screen.destroy()
                    del LOADING_SCREENS[-1]
                except IndexError as er:
                    Apptools.writeLog(er)
                    globals()['LOADING_SCREENS'] = []
            else:
                time.sleep(0.1)  # To avoid collission with other function calls
                LoadingPage.stop_it(self)
        except RecursionError as e:
            Apptools.writeLog(e)

    def perform(self, args):
        """
        args should include destination function
        order of args(root ,function,arguments)
        """
        t1 = threading.Thread(target=LoadingPage.start, args=(self,))
        t1.start()
        t2 = threading.Thread(target=LoadingPage.fxn, args=args)
        t2.start()

    def fxn(self, *args):
        t1 = time.time()
        function = args[0]
        arguments = args[1:]
        function(*arguments)
        t2 = time.time()

        diff = round(t2 - t1, 1)
        if diff < LeastWaitTime:
            time.sleep(LeastWaitTime - diff)
        LoadingPage.stop_it(self)


class Apptools:

    def check_mail(email):
        if email and isinstance(email, str):
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.fullmatch(regex, email):
                return True
        return False

    def image_Show(self, Dir, xrow, ycolumn, width, height, mode="grid", rspan=1, cspan=1, px=0, py=0):
        try:
            Photo = Image.open(Dir)
        except Exception as e:
            Apptools.writeLog(e)
            Photo = Image.open(DEFAULTIMAGEDir)
        Photo = Photo.resize((width, height))
        render = ImageTk.PhotoImage(Photo)
        img = tk.Label(self, image=render)
        img.image = render
        if mode == 'grid':
            img.grid(row=xrow, column=ycolumn, rowspan=rspan, columnspan=cspan, padx=px, pady=py, sticky="ns")
        else:
            img.place(x=xrow, y=ycolumn, relx=0, rely=0)

    @staticmethod
    def openfilename():
        filetype = [('Image files', '*.jpg;*.jpeg;*.png;*.bmp'), ('All files', '*')]
        filename = filedialog.askopenfilename(title='Open', initialdir=os.getcwd(), filetypes=filetype)
        if filename:
            return filename

    @staticmethod
    def open_img():
        filename = Apptools.openfilename()
        if filename:
            try:
                img = Image.open(filename)
                img = img.resize((300, 300), Image.ANTIALIAS)
                render = ImageTk.PhotoImage(img)
                img2 = img.resize((100, 100), Image.ANTIALIAS)
                renderCompressed = ImageTk.PhotoImage(img2)
                return render, renderCompressed, filename
            except Exception as e:
                Apptools.writeLog(e)

    def imgbutton(self, diry, width, height, irow, icolumn):
        try:
            Photo = Image.open(diry)
            Photo = Photo.resize((width, height))
            render = ImageTk.PhotoImage(Photo)

            imgbtn = tk.Button(self, image=render)
            imgbtn.config(command=lambda: Apptools.imgbutton_event(self, imgbtn))
            imgbtn.image = render
            imgbtn.grid(row=irow, column=icolumn, padx=10, pady=10)
        except Exception as e:
            Apptools.writeLog(e)
            self.imgbutton(DEFAULTIMAGEDir, width, height, irow, icolumn)

    def imgbutton_event(self, imgbtn):
        x = Apptools.open_img()
        if x:
            img, compImg, self.imageAddress = x
            imgbtn.config(image=compImg)
            imgbtn.image = compImg

    def is_not_null(*text):
        if len(text) != 0:
            for msg in text:
                if msg == "" or (isinstance(msg, str) and msg.strip() == ""):
                    return False
            return True
        else:
            return False

    def check_digit(*text):
        try:
            for i in text:
                x = float(i)
            return True
        except Exception as e:
            return False

    def in_limit(lower, upper, *text):
        if len(text) != 0:
            for msg in text:
                if Apptools.check_digit(msg):
                    val = float(msg)
                    if val > upper or val < lower:
                        return False
                else:
                    return False
            return True
        else:
            return False

    def generate_id(child, sp="id"):
        ref = FirebaseDB.getdataOrder(child, sp)
        if ref:
            out = list(ref.values())
            k = 1
            list_id = []
            for i in range(len(out)):
                list_id.append(out[i][sp])
            while k in list_id:
                k += 1
            return k
        elif ref is not None:
            return 1

    def randomtxt(length):
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

    def generateuniquecode(child, idty):
        """"
        User need to precheck for internet connection.
        """
        out = FirebaseDB.getdataOrder(child, idty)
        if out is not None:
            list_wal = []
            for i in out:
                list_wal.append(out[i][idty])

            txt = Apptools.randomtxt(8)

            while txt in list_wal:
                txt = Apptools.randomtxt(8)

            return txt

    def checkBalance(walno, pin):
        ref = FirebaseDB.getdataOrderEqual("Wallet", "WalletNo", walno)
        bal = 0
        if ref:
            data = list(ref.values())[0]
            if data['PIN'] == pin:
                bal = data['Balance']
            else:
                Apptools.writeLog("Error retrieving balance")
        # It return integer not string
        return bal

    def keyencoder(walno, bal):

        bal = str(bal)

        if len(bal) < len(walno):
            bal = "0" * (len(walno) - len(bal)) + bal
        elif len(bal) > len(walno):
            walno = "$" * (len(bal) - len(walno)) + walno

        encbal = ""
        for i in bal:
            encbal += chr(65 + int(i))

        data = list(encbal) + list(walno)
        l = len(data)
        key = ""
        seq = 0
        for i in range(l):
            rnd = random.randint(0, min(9, len(data) - 1))
            key += data[rnd]
            seq = seq * 10 + rnd
            del data[rnd]
        return key, seq

    def keydecoder(key, seq):
        l = []
        seq = str(seq)
        seq = "0" * (len(key) - len(seq)) + seq

        seq = Apptools.rev(seq)
        key = Apptools.rev(key)

        for i in range(len(key)):
            n = int(seq[i])
            l.insert(n, key[i])

        data = ""

        for i in range(len(key)):
            data += l[i]

        walno = data[len(key) // 2:]

        bal = 0

        for i in data[:len(key) // 2]:
            bal = bal * 10 + (ord(i) - 65)

        return walno, bal

    def rev(txt):
        rev = ""
        for i in txt:
            rev = i + rev
        return rev

    def CashoutRequest(walno, amt, pin):
        """Generate Key to initiate a cashout"""
        amt = int(amt)
        if amt <= 10000000:
            key, seq = Apptools.keyencoder(walno, amt)
            ref = FirebaseDB.getdataOrderEqual("Wallet", "WalletNo", walno)
            if ref:
                bal = list(ref.values())[0]['Balance']
                if pin == str(list(ref.values())[0]['PIN']):
                    details = {"Key": key, "SecretCode": int(seq)}
                    ref2 = FirebaseDB.pushData("TempBank", details)
                    if ref2:
                        ref3 = FirebaseDB.updateData("Wallet", {"Balance": bal - amt})
                        if ref3:
                            return key
        else:
            messagebox.showwarning("Amount exceed limit",
                                   "As per a guideline we only accept cashout request of only amount upto 1 Crore Rupees")

    @staticmethod
    def clearImgCache():
        try:
            os.makedirs(CACHE_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                Apptools.writeLog(e)

        onlyfiles = [os.path.join(CACHE_FOLDER, f) for f in os.listdir(CACHE_FOLDER) if
                     os.path.isfile(os.path.join(CACHE_FOLDER, f))]
        for l in onlyfiles:
            if os.path.exists(l):
                os.remove(l)

    def logout(master):
        Apptools.clearImgCache()
        pauth.current_user = None
        Apptools.clearSession()
        globals()['SESSION_USER'] = None
        master.switch_frame(Homepage)

    @staticmethod
    def writeSession():
        if pauth.current_user:
            try:
                os.makedirs(SESSION_FILE_FOLDER)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    Apptools.writeLog(e)
            with open(SESSION_CACHE_FILE, 'wb') as f:
                pickle.dump(pauth.current_user, f)

    @staticmethod
    def readSession():
        file_contents = ""
        try:
            try:
                os.makedirs(SESSION_FILE_FOLDER)
            except OSError as er:
                if er.errno != errno.EEXIST:
                    Apptools.writeLog(er)
            with open(SESSION_CACHE_FILE, "rb") as f:
                file_contents = pickle.load(f)
                if file_contents and FirebaseDB.connect():
                    pauth.current_user = ses = file_contents
                    globals()['SESSION_USER'] = auth.get_user(ses['localId'])
        except IOError as e:
            pass
            # Do nothing
        except EOFError as e:
            pass
        except firebase_admin._auth_utils.UserNotFoundError as e:
            pauth.current_user = None
            Apptools.clearSession()
            globals()['SESSION_USER'] = None
            Apptools.writeLog(e)
        except fireexception.UnavailableError as e:
            Apptools.writeLog(e)
        except Exception as e:
            Apptools.writeLog(e)

    @staticmethod
    def clearSession():
        try:
            os.makedirs(SESSION_FILE_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                Apptools.writeLog(e)
        with open(SESSION_CACHE_FILE, "wb") as f:
            pass

    def writeLog(msg):
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        try:
            os.makedirs(LOG_FILE_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                Apptools.writeLog(e)
        f = open(LOG_FILE, 'a')
        print(formatted_date, msg, file=f)
        f.flush()
        f.close()


class FirebaseDB:
    @staticmethod
    def signout():
        """
        Flushes pauth.current_user variable

        Returns True :after process is completed
                None :if some error occurs
        """
        try:
            pauth.current_user = None
            return True
        except Exception as e:
            Apptools.writeLog(e)

    def create_account(email, password, username, details, table):
        """
        Provide subscrption to authentication as well as creates another table for storing other details in
        Realtime databse simultaneously.
        :param email : Email
        :param password: Password
        :param username: Username(Used to associate email with username without creating separate table)
        :param details: Used to fetch Name to put it in Firebase authentication, Also to put all other data plus email
                        and username in separate RealTime Database
        :param table: Name of the table in which the details would be put in.
        :return: True : If everything is Ok
        None : If some error arises, it is often accompanied by a prompt displaying common errors like Duplicate Email,
                Invalid mail format, Weak Password etc. It also returns None if it can't connect to FirebaseDB
        """
        if FirebaseDB.connect():
            try:
                user = auth.create_user(email=email, password=password, display_name=details['Name'])
                data = {"Username": username, "Email": email}
                data.update(details)
                results = db.reference(table).push(data)
                return True
            except (ValueError, fireexception.FirebaseError, fireexception.UnavailableError) as e:
                e = str(e)
                Apptools.writeLog(e)
                if e.find("EMAIL_EXISTS") != -1:
                    messagebox.showinfo("Account with this email already created",
                                        "Account with this email already created.\nTry Another Email Address")
                elif e.find("Invalid password") != -1:
                    messagebox.showwarning("Weak Password", "Password must be of atleast 6 characters.")
                elif e.find("Malformed email address") != -1:
                    messagebox.showwarning("Invalid Email Address", "Email Address must be of Valid format!")
                else:
                    messagebox.showwarning("Error", e)
        else:
            Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")

    def login(email, password):
        """
        Provides SESSION details and service for authentication.
        Login using username is not supported and hence should be applied using
        another table pointing to email to username as defined in function create_account(...)

        :param email: Email for authentication
        :param password: Password
        :return: User credentials(Data Type: Dictionary) after login if everything is OK!
                    Contains Keys
                    kind , localId, email, displayName, idToken, registered, expiresIn, refreshToken

                None: If any error occurred like malformed email,invalid password, no internet etc
        """
        if FirebaseDB.connect():
            try:
                user = pauth.sign_in_with_email_and_password(email, password)
                return user
            except requests.exceptions.HTTPError as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "INVALID_PASSWORD":
                    messagebox.showwarning("Invalid credentials", "Enter correct Password!")
                elif error == "EMAIL_NOT_FOUND":
                    messagebox.showwarning("User not registered", "There is no user registered with this Email-Id.")
                else:
                    messagebox.showwarning("Error",
                                           "Some Error Occured while Logging-in\nPlease Retry!\n" + str(
                                               error))
                Apptools.writeLog(error)
                return False
        else:
            Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")

    def pushData(child, details, showWarning=True):
        """
        Writes data to FirebaseDB
        :param child: The address to the node on which data has to be written
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being, at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries. Each keys point of its own location
                    in database.
        :param details: Data-Type-Dictionary All the details in form of dictionary, one want to push
        :param showWarning: Shows messageBox for errors if True else not.
        :return: True : If data is successfully written
                 None : If some error arises
                 messageBox is shown if showWarning is True
        """
        if FirebaseDB.connect():
            try:
                results = db.reference(child).push(details)
                return True
            except (ValueError, fireexception.FirebaseError, fireexception.UnavailableError) as e:
                Apptools.writeLog(e)
                return
        elif showWarning:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
        Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")

    def getdataOrder(child, ordervar, showWarning=True):
        """
        Gets data from FirebaseDB ordered by ordervar
        :param child: The address to the node on which data has to be fetched from
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being ,at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                    Each keys point of its own location in database.
        :param ordervar: The name of attribute according to which data has to be sorted
        :param showWarning: Shows messageBox for error if True else not.
        :return: out : If data is successfully fetched
                       Data Type-Dictionary
                        {key:values pair}
                        each key:values pair correspond to a single a result found
                            This key is same as random set of character allocated on data creation.
                            and can be useful for accessing sub-child for that table.

                            The values is again a nested dictionary containing info about
                            fetched data in key:values pair where key is attribute and values is
                            the data in that attribute

                        In order to get data, say Name is the attribute and we need it
                        list(FirebaseDB.getdataOrder(...).values()) -> Contains all sets of N results found

                        To get first one:
                        list(FirebaseDB.getdataOrder(...).values())[0]['Name']

                 None : If some error arises
                 messageBox is shown if showWarning is True
        """
        if FirebaseDB.connect():
            try:
                out = db.reference(child).order_by_child(ordervar).get()
                print(out)
                if out is None:
                    out = {}  # To differentiate data from errors
                return out
            except Exception as e:
                Apptools.writeLog(e)
                return
        elif showWarning:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
        Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")

    def getdataOrderEqual(child, ordervar, equalvar, showWarning=True):
        """
        Gets data from FirebaseDB ordered by ordervar
        :param child: The address to the node on which data has to be fetched from
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being ,at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                    Each keys point of its own location in database.
        :param ordervar: The name of attribute for which equality has to be checked
        :param equalvar: The corresponding value to which equality is to be checked
        :param showWarning: Shows messageBox for error if True else not.
        :return: out : If data is successfully fetched
                       Data Type-Dictionary
                        {key:values pair}
                        each key:values pair correspond to a single a result found
                            This key is same as random set of character allocated on data creation.
                            and can be useful for accessing sub-child for that table.

                            The values is again a nested dictionary containing info about
                            fetched data in key:values pair where key is attribute and values is
                            the data in that attribute

                        In order to get data, say Name is the attribute and we need it
                        list(FirebaseDB.getdataOrderEqual(...).values()) -> Contains all sets of N results found

                        To get first one:
                        list(FirebaseDB.getdataOrder(...).values())[0]['Name']


                 None : If some error arises
                 messageBox is shown if showWarning is True
        """
        if FirebaseDB.connect():
            try:
                out = db.reference(child).order_by_child(ordervar).equal_to(equalvar).get()
                if out is None:
                    out = {}  # To differentiate data from errors
                return out
            except Exception as e:
                Apptools.writeLog(e)
                return
        elif showWarning:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
        Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")

    def updateData(child, data, identifier="Email", identifierval="", showWarning=True):
        """
        Updates data in RealTime Database with help of identifier.
        It will update all instances of data in case of multiple values found.

        In case of no identifier,function will update values for
        current user(using email by SESSION_USER.email)

        :param child: The address to the node on which data has to be fetched from
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being ,at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                    Each keys point of its own location in database.
        :param data: Data-Type-Dictionary Data to be updated on that node/child (Overwrite in case of data difference,
                        non-called attributes are still safe in database! Like if need to just update name ,
                        one only need to put name in data only not every other attribute.
                        Works more or less like <DICT1>.update(<DICT2>))
        :param identifier: Attribute according to which data has to be found and updated.
                            (It is recommended to use primary key type things here,
                            where there is no data duplicacy)
        :param identifierval: Value of the identifier attribute against which tuple(data) has to be found
        :param showWarning: Shows messageBox for error if True else not.

        :return: True : If data is successfully over-written
                 False : If some error arises
                 messageBox is shown if showWarning is True
        """
        try:
            if FirebaseDB.connect():
                if not identifierval:
                    identifierval = SESSION_USER.email
                if identifierval:
                    ref = db.reference(child).order_by_child(identifier).equal_to(identifierval).get()
                    if ref:
                        for key in list(ref.keys()):
                            result = db.reference(child).child(str(key)).update(data)
                        return True

            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
        except Exception as e:
            Apptools.writeLog(e)
        return False

    def deleteData(child, identifier="email", value="", key="", showWarning=True):
        """
        Deletes all instances of data satisfying a certain condition.

        In case identifier, value and key all three are given, then key is overridden by default.
        Then, Identifier, value is ignored.

        :param child: The address to the node on which data has to be fetched from
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being ,at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                    Each keys point of its own location in database.
        :param identifier: Attribute according to which data has to be deleted.
                            (It is recommended to use primary key type things here,
                            where there is no data duplicacy)
        :param value: Value of the identifier attribute against which tuple(data) has to be deleted
        :param key: In case identifier or value is not provided, key acts as last child node to that tuple/data.
        :param showWarning: Shows messageBox for error if True else not.

        :return: True : If data is successfully deleted/is not present
                 False : If some error arises
                 messageBox is shown if showWarning is True
        """
        try:
            if FirebaseDB.connect():
                if not key:
                    ref = FirebaseDB.getdataOrderEqual(child, identifier, value, showWarning=showWarning)
                    if ref:
                        key = list(ref.keys())
                if key:
                    if isinstance(key, (list, tuple)):
                        for ke in key:
                            db.reference(child).child(key).delete()
                    else:
                        db.reference(child).child(key).delete()
                    return True
                elif ref is not None:
                    return True  # Since data is not present it is pseudo-deleted

            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
        except Exception as e:
            Apptools.writeLog(e)
        return False

    def deleteAuthData(uid, showWarning=True):
        """
        Deletes Authentication data from Firebase Authentication Database.
        :param uid: An User ID String (fetched by SESSION_USER.uid)
            session = pauth.current_user
            SESSION_USER = auth.get_user(session['localId'])
        :param showWarning: Shows messageBox for error if True else not.

        :return: True : If authentication Data is successfully deleted. It doesn't removes secondary
                        database created at user sign-up.
                 False : If some error arises
                 messageBox is shown if showWarning is True
        """

        try:
            if FirebaseDB.connect():
                auth.delete_user(uid)
                return True
            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
        except Exception as e:
            Apptools.writeLog(e)
        return False

    def sendDataStorage(fileLocation, saveAsName, showWarning=True):
        """
        Stores the IMAGE into Google Cloud/ Firebase DB from a choosen local image location and return
        its database address
        Images will be stored as png file but can be modified to be used as any one.

        :param saveAsName: The name with which image would be saved on the server.(Excludes the extension)
        :param showWarning: Shows messageBox for error if True else not.

        :return:savefilename The (expected) location of image on the server. (If all goes OK!)
                False If some error occurs which is accompanied by a messageBox if allowed.
        """
        try:
            if FirebaseDB.connect():
                bucket = storage.bucket()
                if fileLocation and saveAsName:
                    extension = ".png"
                    savefilename = saveAsName + extension
                    blob = bucket.blob(savefilename)
                    blob.upload_from_filename(fileLocation)
                    return savefilename
            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            return False
        except Exception as e:
            Apptools.writeLog(e)
            return False

    def getDataStorage(imgURL, showWarning=True):
        """
        Get the IMAGE from Google Cloud/ Firebase DB and store it in cached directory and
        return the path to cached directory
        Cached image is in format of "YYYYMMDDHHMMSS"+{Random single,double and triple digit number}.png
                {Where Y is Year, M is Month and so on}
                eg: 202211181811452.png means it is created on 18:11:45 on 18/11/2022 where 2 is just a random successor.
        In case of dealing with programs fetching multiple images at same time, user must increase randint limit from 1000
        to an appreciable level. The purpose of random number is remove chances of duplicate datas will avoiding
        overhead of checking names of data.

        :param imgURL: The URL of the image stored at the DB. Generally it is just ImageName.extension
                        but it could be <Folder-Name>/ImageName.extension or anything else in other cases
        :param showWarning: Shows messageBox for error if True else not.

        :return:imgLocation The location of cached image fetched from server. (If all goes OK!)
                            The location by default doesn't contains the prefix i.e. the directory of os.path etc(parent working directory)
                            eg:- cache/127617262231111.png
                False If some error occurs which is accompanied by a messageBox if allowed.
        """
        try:
            if FirebaseDB.connect():
                bucket = storage.bucket(app=firebase)
                blob = bucket.blob(imgURL)
                now = datetime.now()
                formatted_date = now.strftime('%Y%m%d%H%M%S')

                try:
                    os.makedirs(CACHE_FOLDER)
                except OSError as er:
                    if er.errno != errno.EEXIST:
                        Apptools.writeLog(er)

                imgLocation = os.path.join(CACHE_FOLDER,
                                           "{0}.png".format(formatted_date + str(random.randint(0, 1000))))
                urllib.request.urlretrieve(
                    blob.generate_signed_url(timedelta(seconds=300), method='GET'), imgLocation)
                return imgLocation
            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            return False
        except Exception as e:
            Apptools.writeLog(e)
            return False

    def deleteDataStorage(imgURL, showWarning=True):
        """
        Deletes the Images from Firebase server based on its location.
        It in no ways delete the cache file generated during the deletion, which can
        be deleted using Apptools.clearImgCache(...) function or the data pointing to this URL
        stored in Real Time Database.

        :param imgURL: The URL of the image stored at the DB. Generally it is just ImageName.extension
                        but it could be <Folder-Name>/ImageName.extension or anything else in other cases
        :param showWarning: Shows messageBox for error if True else not.

        :return:True If all goes OK!
                False If some error occurs which is accompanied by a messageBox if allowed.
        """
        try:
            if FirebaseDB.connect():
                bucket = storage.bucket(app=firebase)
                blob = bucket.blob(imgURL)
                blob.delete()
                return True
            elif showWarning:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            else:
                Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")
            return False
        except Exception as e:
            Apptools.writeLog(e)
            return False

    def optimiseSearchVal(searchVal):
        """
        This function isn't needed by devs. It just is used to optimise user entered queries
        and create various standard iterations of it.

        Standard Iteration is : Title Case, All Upper, All Lower, first word lower rest all title
                                and the searchVal itself(Cam be modified every added iteration takes extra time to complete.)
        :param searchVal: Data-Type-String The variable to contain the search query
        :return List of standard iteration of values if string is not empty
                else it just returs the string itself in list form to reduce inconsistency
        """
        if searchVal and isinstance(searchVal, str):
            x1 = searchVal.title()
            x2 = searchVal.lower()
            x3 = x1[0].lower() + x1[1:]
            x4 = searchVal.upper()

            return searchVal, x1, x2, x3, x4
        return [searchVal]

    def deepSearchData(child, identifier, searchVal, filtervar=None, filterval=None, showWarning=True):
        """
       A more abstracted API is provided in Apptoolsv2.itemSearch(....) which searches for data in
       relation named 'Items'

       deepSearchData function tries to search a value from database. Its main purpose is to overcome
       the limits sets by Firebase APIs as explained in FirebaseDB.searchData(...)
       Data need not to be in standard state in database for this function.

       :Functioning: It first tries normal standard Firebase searching based on Firebase API.(Lenient than
                        searchData(.....) which uses various iterations, while this doesn't).Function could be modiied
                        to give local search method also. But has not been implemented due to
                        my personal coding requirements
                    If that fails i.e. no data could be found then it forces local searching as given below:
                        It fetches all data from child table and searches them locally.(More strong and flexible)

                        This is especially not recommended if database has some sensitive information that
                        should not be in public hands and/or if the size of child node is very large(in MBs) then
                        the function would be very slow.

       For example: If one searches for "Zoo" in ["Zoo","Zooras","aZoo",""zoo","ZOO","ZoO"]
                   All the results are shown if using deepSearchData(...)

       :param child:The address to the node on which data has to be fetched from
                   If one has created a table named Institute and another sub-table inside
                   the table say named Students.Idea being ,at a time all students of same
                   branch name is to be put at one branch.
                   So every new entry is defined by a random set of character allocated on data creation.
                   This key(random set of character) can be fetched using getdataOrderEqual function and
                   getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                   Each keys point of its own location in database.
       :param identifier: The attribute against which data has to be searched.
       :param searchVal: Value of the attribute against which data has to be searched.
       :param filtervar: Acts as a seondary but optional identifier to fetched results.(Case insensitive)
                           So,it can sort and show only that data which passes a EQUALITY condition..
                           This is just a EQUALITY checker(not like search) and is done locally, not on server. Hence,
                            Firebase API's limits doesn't affect these.
                           filtervar is the name of attribute against which secondary filtering is to be done.
       :param filterval: filterval is the value of the secondary attribute against which local filtering is to be done.
       :param showWarning: Shows messageBox for error if True else not.

       :return: searchResult: Type(List nested with Dictionary of found data(no key-index just values))
                              eg.- [{'Name':Value,'Name2':Value},{.....}]
               None: If some error occured, could by followed by messageBox if allowed.
               []: If no data is found

       """
        if FirebaseDB.connect():
            try:
                searchResult = []
                if filterval and filtervar:
                    ref = db.reference(child).order_by_child(filtervar).equal_to(filterval).get()
                else:
                    ref = db.reference(child).order_by_child(identifier).get()
                if ref:
                    data = list(ref.values())
                    for i in data:
                        if isinstance(i[identifier], (int, float)):
                            if searchVal == i[identifier]:
                                searchResult.append(i)
                        else:
                            if isinstance(i[identifier], str) and isinstance(searchVal, str):
                                if searchVal.lower() in i[identifier].lower():
                                    searchResult.append(i)
                            else:
                                if searchVal in i[identifier]:
                                    searchResult.append(i)
                return searchResult
            except Exception as e:
                Apptools.writeLog(e)
                return
        elif showWarning:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
        Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")

    def searchData(child, identifier, searchVal, filtervar=None, filterval=None, showWarning=True):
        """
        A more abstracted API is provided in Apptoolsv2.itemSearch(....) which searches for data in
        relation named 'Items'

        searchData function tries to search various standard iterations of a value from database.
        All data stored are assumed to be stored in standard state for this function.

        Firebase limit the capabilities for devs to search for data efficiently unless you pay them a
        price. The API currently allows devs to search for the values that start with parameter mandatorily.
        The given values can end with anything by the way.
        For example: If one searches for "Zoo" in ["Zoo","Zooras","aZoo",""zoo","ZOO","ZoO"]
                    Only ["Zoo","Zooras","zoo","ZOO"] is the result (ZoO is the reported due to insconsistent
                     formatting of upper and lower case)  If someone wants all of the results use
                     deepSearchData(....) function. More info is given in function docs.

        :param child:The address to the node on which data has to be fetched from
                    If one has created a table named Institute and another sub-table inside
                    the table say named Students.Idea being ,at a time all students of same
                    branch name is to be put at one branch.
                    So every new entry is defined by a random set of character allocated on data creation.
                    This key(random set of character) can be fetched using getdataOrderEqual function and
                    getting the keys of returned dictionaries using getdataOrderEqual(...).keys().
                    Each keys point of its own location in database.
        :param identifier: The attribute against which data has to be searched.
        :param searchVal: Value of the attribute against which data has to be searched.
        :param filtervar: Acts as a seondary but optional identifier to fetched results.(Case insensitive)
                            So,it can sort and show only that data which passes a EQUALITY condition..
                            This is just a EQUALITY checker(not like search) and is done locally, not on server. Hence,
                             Firebase API's limits doesn't affect these.
                            filtervar is the name of attribute against which secondary filtering is to be done.
        :param filterval: filterval is the value of the secondary attribute against which local filtering is to be done.
        :param showWarning: Shows messageBox for error if True else not.

        :return: searchResult: Type(List nested with Dictionary of found data(no key-index just values))
                               eg.- [{'Name':Value,'Name2':Value},{.....}]
                None: If some error occured, could by followed by messageBox if allowed.
                []: If no data is found

        """
        if FirebaseDB.connect():
            try:
                searchResult = []
                optimisedsearchval = FirebaseDB.optimiseSearchVal(searchVal)
                for i in optimisedsearchval:
                    ref = db.reference(child).order_by_child(identifier).start_at(i).end_at(i + "\uf8ff").get()
                    if ref:
                        searchResult.extend(list(ref.values()))

                if searchResult is None:
                    searchResult = []  # To differentiate data from errors
                if searchResult:
                    res = []
                    # Removing duplicate values due to using various iterations
                    [res.append(x) for x in searchResult if x not in res]
                    searchResult = res
                if filterval and filtervar:
                    res = []
                    for x in searchResult:
                        if isinstance(x[filtervar],str) and isinstance(filterval, str):
                            if x[filtervar].lower() == filterval.lower():
                                res.append(x)
                        elif isinstance(x[filtervar],(int,float)) and isinstance(filterval, (int,float)):
                            if x[filtervar] == filterval:
                                res.append(x)
                        else:
                            if filterval in x[filterval]:
                                res.append(x)

                    searchResult = res

                return searchResult

            except Exception as e:
                Apptools.writeLog(e)
                return
        elif showWarning:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
        Apptools.writeLog("Failed to Connect to Server\tNo Internet Connection or Server Unreachable")

    def sendPasswordResetEmail(email):
        """
        Send Password Reset Email for authenticated users(User authenticated using firebase authentication service
        with email and password (access Firebase console for more info))

        :param email: Email of the user with which he is authenticated with.

        :return: True If all goes as planned

                 False If some error occurred
                messageBox is generally showed for common errors
                like if INVALID EMAIL/EMAIL NOT FOUND etc
        """
        if FirebaseDB.connect():
            if Apptools.check_mail(email):
                try:
                    pauth.send_password_reset_email(email)
                    return True
                except requests.exceptions.HTTPError as e:
                    error_json = e.args[1]
                    error = json.loads(error_json)['error']['message']
                    if error == "INVALID_EMAIL":
                        messagebox.showwarning("Invalid Email", "Invalid Email\nPlease enter a valid email address")
                    elif error == "EMAIL_NOT_FOUND":
                        messagebox.showwarning("Incorrect Credentials!",
                                               "Incorrect Email!\nEnter correct Email address")
                    else:
                        messagebox.showerror("Error", "Some unknown error occurred.Please try later\nError:" + e)
                        Apptools.writeLog(e)
            else:
                messagebox.showwarning("Invalid Email", "Invalid Email\nPlease enter a valid email address")
        return False

    def connect(hosts=['http://google.com', dbURL]):
        """
        Tries to connect to various hosts (By default Google and Firebase Server)
        and check if user has valid internet connection or not.
        It is recommended to include dbURL to check if server is down or not with
        a recommended popular website like wikipedia, google etc.

        :param hosts: (DataType-List/Tuple/String) A list of hosts against which connection has
                                                to be checked.

        return: True if successfully connects to server
                False if failed to connect to server
        """
        try:
            if isinstance(hosts, (list,tuple)):
                for host in hosts:
                    urllib.request.urlopen(host)
                return True
            elif isinstance(hosts, str):
                urllib.request.urlopen(hosts)
                return True
            else:
                Apptools.writeLog("Invalid data type 'hosts'-expected string/tuple/list\nFirebaseDB.connect")
                return False
        except:
            return False


class Apptoolsv2:

    def itemSearch(self, text, criteria, filtervar=None, filterval=None, showWarning=True, deepSearch=False):
        if Apptools.is_not_null(text):
            if criteria not in ("Wholesale Price", "Retail Price"):
                if deepSearch:
                    record = FirebaseDB.deepSearchData("Items", criteria, text, filtervar=filtervar,
                                                       filterval=filterval, showWarning=showWarning)
                else:
                    record = FirebaseDB.searchData("Items", criteria, text, filtervar=filtervar, filterval=filterval,
                                                   showWarning=showWarning)
            else:
                if Apptools.check_digit(text):
                    ref = FirebaseDB.getdataOrderEqual("Items", criteria, float(text), showWarning=showWarning)
                    if ref is not None:
                        record = list(ref.values())
                else:
                    if showWarning:
                        messagebox.showwarning("Error", "Incorrect input!")
                    record = None
            if record is not None:
                if record:
                    return record
                elif showWarning:
                    messagebox.showinfo("No data", "No records found")
        elif showWarning:
            messagebox.showwarning("Error", "Incomplete input!")

    def Treeoutput(self, column, out, label=None, srow=0, scolumn=0, scolumnspan=1, singleLineFilter=True,
                   InScrollableframe=True, lbrow=1, lbcolumn=0, fheight=250, fwidth=750):
        """
        out must be in form of list
        srow,scolumn,scolumnspan if InScrollableframe is true for scrollable frame
        lbrow,lbcolumn if InScrollableframe is False
        give one extra space for lbrow if label has some Value
        """
        if InScrollableframe:
            frame = ScrollableFrame(self, ch=fheight, cw=fwidth, showscrlbar=False)
            sframe = frame.scrollable_frame
        else:
            sframe = self
        if label:
            lbl = tk.Label(sframe, text=label)
            lbl.config(font=('Segoe UI', 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=lbrow - 1, column=lbcolumn, padx=30, pady=10)

        Apptoolsv2.listBox = ttk.Treeview(sframe)

        verscrlbar = ttk.Scrollbar(sframe, orient="vertical", command=Apptoolsv2.listBox.yview)
        verscrlbar.grid(row=lbrow, column=lbcolumn + 1, sticky="nsw", rowspan=2)

        hscrollbar = ttk.Scrollbar(sframe, orient="horizontal", command=Apptoolsv2.listBox.xview)
        hscrollbar.grid(row=lbrow + 1, column=lbcolumn, sticky="new")
        Apptoolsv2.listBox.configure(yscrollcommand=verscrlbar.set)
        Apptoolsv2.listBox.configure(xscrollcommand=hscrollbar.set)

        Apptoolsv2.listBox.config(selectmode="extended", columns=column, show="headings")

        for i in range(0, len(column)):
            Apptoolsv2.listBox.heading(column[i], text=column[i],
                                       command=lambda c=column[i]: Apptoolsv2.sortby(self, Apptoolsv2.listBox, c, 0))
            Apptoolsv2.listBox.column(column[i], minwidth=0)

        for col in column:
            Apptoolsv2.listBox.heading(col, text=col)
            Apptoolsv2.listBox.column(col, width=tkFont.Font().measure(col.title()))
        Apptoolsv2.listBox.grid(row=lbrow, column=lbcolumn, sticky="nsew")

        for i in out:
            if singleLineFilter:
                i = Apptoolsv2.singleline(self, i)
            Apptoolsv2.listBox.insert("", "end", values=i[:len(column)])

            for indx, val in enumerate(i[:len(column)]):
                ilen = tkFont.Font().measure(val)
                if Apptoolsv2.listBox.column(column[indx], width=None) < ilen:
                    Apptoolsv2.listBox.column(column[indx], width=ilen)
        if InScrollableframe:
            frame.grid(row=srow, column=scolumn, columnspan=scolumnspan)

        Apptoolsv2.listBox.bind('<Enter>', Apptoolsv2._bound_to_mousewheel)
        Apptoolsv2.listBox.bind('<Leave>', Apptoolsv2._unbound_to_mousewheel)

    def _bound_to_mousewheel(event):
        Apptoolsv2.listBox.bind_all("<MouseWheel>", Apptoolsv2._on_mousewheel)

    def _unbound_to_mousewheel(event):
        Apptoolsv2.listBox.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
        Apptoolsv2.listBox.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def singleline(self, txtlines):
        l = []
        if isinstance(txtlines, (list, tuple)):
            for i in txtlines:
                if isinstance(i, str):
                    l.append(i.replace("\n", " "))
                else:
                    l.append(i)
            return l
        else:
            return txtlines

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        x = True

        for a, b in data:
            x = x and Apptools.check_digit(a)
        if x:
            for i in range(len(data)):
                data[i] = list(data[i])
                data[i][0] = float(data[i][0])
        data.sort(reverse=descending)

        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        tree.heading(col, command=lambda col=col: Apptoolsv2.sortby(self, tree, col, int(not descending)))

    def bargain(self, irp, iwp, iqty, isPremium="no"):
        netbargain = 0
        if isPremium.lower() == "yes":
            if irp and iwp and iqty:
                r = (irp / iwp) * 100
                if r > 120:
                    netbargain = max(0, iqty * (irp - (iwp * 120 / 100)))
                    # Ensuring at least 20% Profit(approx) for seller and admin combined
                    # 14% for seller
        return round(netbargain, 2)  # To ensure bargain is never greater than the limit due to approximation


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
    def __init__(self, container, cw=775, ch=500, showscrlbar=True, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg="#333333", highlightthickness=0)
        self.canvas.config(scrollregion=(0, 0, 900, 1000))
        if showscrlbar:
            vscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            hscrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        s = ttk.Style()
        s.configure('TFrame', background='#333333')

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self._canvasWidth = cw
        self._canvasHeight = ch
        self.canvas.config(width=self._canvasWidth, height=self._canvasHeight,
                           scrollregion=(0, 0, self._canvasWidth, self._canvasHeight))
        if showscrlbar:
            self.canvas.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

        self.canvas.grid(row=0, column=0)
        if showscrlbar:
            vscrollbar.grid(row=0, column=1, rowspan=2, sticky='nse')
            hscrollbar.grid(row=1, column=0, sticky='wse')

            self.canvas.bind('<Enter>', self._bound_to_mousewheel)
            self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        return None

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception as e:
            Apptools.writeLog(e)


class Homepage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        Apptools.image_Show(self, HOMEPAGEImgDir, 0, 0, 300, 450, rspan=10)

        lbl = tk.Label(self, text="Welcome to Kans")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3)

        lbl = tk.Label(self, text="Login")
        lbl.config(font=("Segoe UI", 18), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, columnspan=3, pady=20)

        lbl = tk.Label(self, text="Username/Email")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5)

        username = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        username.grid(row=3, column=2)

        lbl = tk.Label(self, text="Password")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5)

        password = tk.Entry(self, show="●", fg="#E8E8E8", bg="#333333")
        password.grid(row=4, column=2)

        btn = tk.Button(self, text="Login", command=lambda: self.Processing(master, username.get(), password.get()))
        btn.config(bg="#1F8EE7", padx=7, pady=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, padx=5)

        lbl = tk.Label(self, text="Not Registered? Signup Here")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Page2_Signup))
        lbl.grid(row=6, column=1, columnspan=3)

        btnres = tk.Button(self, text="Restore Previous Session")
        btnres.config(bg="#1F8EE7", padx=7, pady=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btnres.grid(row=7, column=1, columnspan=3, padx=5)
        btnres.config(command=lambda: self.Processing(master))

        lbl = tk.Label(self, text="Forgot Password?")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Page2_ForgotPassword))
        lbl.grid(row=8, column=1, columnspan=3)

        lbl = tk.Label(self, text="Usertype will be automatically selected as per the credentials.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1, columnspan=3, sticky="esw")

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.checkSession, *args))
        else:
            LoadingPage.perform(self, (self, self.login_check, *args))

    def login_check(self, master, user, pswd):
        if Apptools.is_not_null(user, pswd):
            email = ""
            if FirebaseDB.connect():
                if Apptools.check_mail(user.strip()):
                    email = user.strip().lower()
                else:
                    pre_user1 = pre_user2 = pre_user3 = None
                    pre_user1 = FirebaseDB.getdataOrderEqual("AdminUsers", "Username", user)
                    if not pre_user1 and pre_user1 is not None:
                        pre_user2 = FirebaseDB.getdataOrderEqual("BuyerUsers", "Username", user)
                        if not pre_user2 and pre_user2 is not None:
                            pre_user3 = FirebaseDB.getdataOrderEqual("SellerUsers", "Username", user)

                    pre_user = pre_user1 or pre_user2 or pre_user3
                    if pre_user:
                        val = list(pre_user.values())[0]
                        email = val['Email']

                if email:
                    result = FirebaseDB.login(email, pswd)
                    if result:
                        globals()['SESSION_USER'] = auth.get_user(result['localId'])
                        Apptools.writeSession()
                        self.loginbysession(master, SESSION_USER)
                        return
                else:
                    messagebox.showwarning("Invalid credentials", "Incorrect Username!")
            else:
                messagebox.showwarning(title="Warning!",
                                       message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                return
        else:
            messagebox.showwarning("Empty fields!", "Fill all the fields correctly to proceed.")

    def checkSession(self, master):
        if FirebaseDB.connect():
            # Somewhat Insecure
            session = pauth.current_user
            if not session:
                Apptools.readSession()
            session = pauth.current_user
            if session:
                try:
                    session = auth.get_user(session['localId'])
                    choice = messagebox.askyesno("Alert",
                                                 "Detected a previous session!\nWant to Continue Previous Session?")

                    if choice:
                        globals()['SESSION_USER'] = session
                        self.loginbysession(master, session)
                        return
                    elif not choice:
                        pauth.current_user = None
                        Apptools.clearSession()
                except firebase_admin._auth_utils.UserNotFoundError as e:
                    Apptools.clearSession()
                except fireexception.UnavailableError as e:
                    messagebox.showwarning(title="Warning!",
                                           message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                    return
            else:
                messagebox.showinfo("Info", "No Session Detected!")
        else:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")

    def loginbysession(self, master, sessiondetails):
        usertype = ""
        if sessiondetails:
            email = sessiondetails.email
            if email:
                pre_user1 = FirebaseDB.getdataOrderEqual("AdminUsers", "Email", email)
                if pre_user1:
                    usertype = "Admin"
                elif pre_user1 is not None:
                    pre_user2 = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", email)
                    if pre_user2:
                        usertype = "Buyer"
                    elif pre_user2 is not None:
                        pre_user3 = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", email)
                        if pre_user3:
                            usertype = "Seller"
        if usertype == "Admin":
            master.switch_frame(Page3_DashboardAdmin)
        elif usertype == "Seller":
            master.switch_frame(Page3_DashboardSeller)
        elif usertype == "Buyer":
            master.switch_frame(Page3_DashboardBuyer)
        return


class Page2_ForgotPassword(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Homepage))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=4, padx=20, pady=10)

        lbl = tk.Label(self, text="Retrieve Password")
        lbl.config(font=("Segoe UI", 17), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, columnspan=4, pady=20)

        lbl = tk.Label(self, text="Email")
        lbl.config(font=("Segoe UI", 13), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, pady=20)

        email = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        email.grid(row=3, column=2)

        btn = tk.Button(self, text="Send Reset Link", command=lambda: self.Processing(email.get()))
        btn.config(bg="#1F8EE7", padx=7, pady=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, padx=10, pady=10)

        lbl = tk.Label(self, text="Reset password link will be send to your registered email address")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=0, columnspan=4, sticky="esw")

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.sendEmail, *args))

    def sendEmail(self, email):
        status = FirebaseDB.sendPasswordResetEmail(email)
        if status:
            messagebox.showinfo("Success", "Send Email Successfully.\nCheck your email account\nCheck Spambox too.")
        elif not FirebaseDB.connect():
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")


class Page2_Signup(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans: You shopping partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0, padx=10)

        lbl = tk.Label(self, text="Signup as")
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, pady=10)

        user_type = StringVar(self, "Admin")
        user = {"Admin": "Admin", "Buyer": "Buyer", "Seller": "Seller"}
        i = 2
        for (text, value) in user.items():
            rbtn = Radiobutton(self, text=text, variable=user_type, value=value)
            rbtn.config(activebackground="#333333", bg="#333333", fg="#E8E8E8")
            rbtn.config(selectcolor="#333333")
            rbtn.grid(row=i, column=0)
            i += 1

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.chooseUserSignup(master, user_type.get()))
        btn.config(bg="#1F8EE7", padx=5, pady=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, padx=5, pady=10)

        lbl = tk.Label(self, text="Already Registered?\nLogin Here")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Homepage))
        lbl.grid(row=7, column=0)

    def chooseUserSignup(self, master, usertype):
        if usertype == "Admin":
            master.switch_frame(Page2_SignupAdmin)
        elif usertype == "Seller":
            master.switch_frame(Page2_SignupSeller)
        elif usertype == "Buyer":
            master.switch_frame(Page2_SignupBuyer)
        else:
            messagebox.showwarning("Invalid User Type!", "Enter a valid User type")


class Page2_SignupAdmin(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        frame = ScrollableFrame(self, ch=550, cw=585)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[0], 0, 0, 100, 550, rspan=11)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[1], 0, 4, 100, 550, rspan=11)

        lbl = tk.Label(frame.scrollable_frame, text="Kans")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Admin Signup")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Name")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5)

        name = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Email Id")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5)

        Email = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        Email.grid(row=4, column=2, padx=5)

        lbl = tk.Label(frame.scrollable_frame, text="PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, padx=5)

        Pin = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=5, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Username")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5)

        username = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        username.grid(row=6, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5)

        Password = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Password.grid(row=7, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Retype Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5)

        Repassword = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=8, column=2)

        button = tk.Button(frame.scrollable_frame, text="Register")
        button.config(
            command=lambda: self.Processing(master, frame.scrollable_frame, name.get(), Email.get(), username.get(),
                                            Password.get(), Repassword.get(), Pin.get()))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5, pady=3)
        button.grid(row=9, column=3, pady=10, padx=20)

        lbl = tk.Label(frame.scrollable_frame, text="Already Registered?\nLogin Here")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Homepage))
        lbl.grid(row=10, column=2)

        frame.grid(row=0, column=0)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.RegisterAdmin, *args))

    def RegisterAdmin(self, master, sframe, name, email, user, pswd, repass, pin):

        table = "AdminUsers"
        if pswd == repass:
            cond1 = pin.isdigit()
            cond2 = Apptools.check_mail(email)
            cond3 = Apptools.is_not_null(name, email, user, pswd, repass, pin)
            cond4 = len(pin) >= 6
            cond5 = len(pswd) >= 5
            if cond1 and cond2 and cond3:
                email = email.lower()
                if not cond4:
                    messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                    return
                if not cond5:
                    messagebox.showwarning("Weak Password", "Password must be of atleast 6 characters.")
                    return
                if FirebaseDB.connect():
                    pre_user1 = pre_user2 = pre_user3 = None
                    pre_user1 = FirebaseDB.getdataOrderEqual(table, "Username", user)
                    if not pre_user1 and pre_user1 is not None:
                        pre_user2 = FirebaseDB.getdataOrderEqual("BuyerUsers", "Username", user)
                        if not pre_user2 and pre_user2 is not None:
                            pre_user3 = FirebaseDB.getdataOrderEqual("SellerUsers", "Username", user)

                    if not (pre_user1 or pre_user2 or pre_user3):
                        walno = Apptools.generateuniquecode(WALLETTABLE, "WalletNo")
                        if walno:
                            details = {"Name": name, "PIN": pin, "WalletNo": walno}
                            status = statusPush1 = statusPush2 = False
                            status = FirebaseDB.create_account(email, pswd, user, details, table)

                            if status == True:
                                data = {"WalletNo": walno, "Email": email, "UserType": "Admin", "Balance": 0,
                                        "PIN": pin}
                                statusPush = FirebaseDB.pushData(WALLETTABLE, data)
                                if statusPush == True:
                                    data2 = {"Balance": 0, "Email": email}
                                    statusPush2 = FirebaseDB.pushData(CASHRECORDTABLE, data2)

                            FirebaseDB.signout()
                            if status == True and statusPush == True and statusPush2 == True:
                                messagebox.showinfo("Success", "Account Created Successfully")
                                Apptools.logout(master)
                            else:
                                if status:
                                    errmsg = "Authentication:" + str(status) + \
                                             "\nWallet Creation:" + str(statusPush) \
                                             + "\nCash Record" + str(statusPush2)

                                    messagebox.showwarning("Error",
                                                           "Some Error Occured while Signing-up\nPlease Retry!\nLog:\n" + errmsg)
                    else:
                        messagebox.showinfo("Account with this Username already exist",
                                            "Account with this Username already exist.\nTry Another Username")
                    del pre_user1
                    del pre_user2
                    del pre_user3
                else:
                    messagebox.showwarning(title="Warning!",
                                           message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                    return
            else:

                if not cond2:
                    messagebox.showinfo("Invalid entry", "Enter Valid E-mail address")
                elif not cond1:
                    messagebox.showinfo("Invalid entry", "Enter Valid PIN")
                else:
                    messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Password Mismatch\nRe-enter Password")


class Page2_SignupBuyer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        frame = ScrollableFrame(self, ch=600, cw=585)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[0], 0, 0, 100, 600, rspan=12)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[1], 0, 4, 100, 600, rspan=12)

        lbl = tk.Label(frame.scrollable_frame, text="Kans")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Buyer's Signup")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Name")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5)

        name = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Email Id")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5)

        emailid = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        emailid.grid(row=4, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, padx=5)

        Pin = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=5, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Username")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5)

        username = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        username.grid(row=6, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5)

        Password = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Password.grid(row=7, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Retype Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5)

        Repassword = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=8, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Delivery Address")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1, padx=5)

        DelAdd = tk.Text(frame.scrollable_frame, fg="#E8E8E8", bg="#333333", height=5)
        DelAdd.config(width=15)
        DelAdd.grid(row=9, column=2)

        button = tk.Button(frame.scrollable_frame, text="Register")
        button.config(command=lambda: self.Processing(master, name.get(), emailid.get(), username.get(), Password.get(),
                                                      Repassword.get(), Pin.get(), DelAdd.get("1.0", "end-1c")))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5, pady=3)
        button.grid(row=10, column=3, pady=10, padx=20)

        lbl = tk.Label(frame.scrollable_frame, text="Already Registered?\nLogin Here")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Homepage))
        lbl.grid(row=11, column=2)

        frame.grid(row=0, column=0)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.RegisterBuyer, *args))

    def RegisterBuyer(self, master, name, email, user, pswd, repass, pin, DelAdd):
        table = "BuyerUsers"
        if pswd == repass:
            cond1 = pin.isdigit()
            cond2 = Apptools.check_mail(email)
            cond3 = Apptools.is_not_null(name, user, pswd, repass, pin, email, DelAdd)
            cond4 = len(pin) >= 6
            cond5 = len(pswd) >= 6

            if cond1 and cond2 and cond3:
                email = email.lower()
                if not cond4:
                    messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                    return
                if not cond5:
                    messagebox.showwarning("Weak Password", "Password must be of atleast 6 characters.")
                    return
                if FirebaseDB.connect():
                    pre_user1 = pre_user2 = pre_user3 = None

                    pre_user1 = FirebaseDB.getdataOrderEqual(table, "Username", user)
                    if not pre_user1 and pre_user1 is not None:
                        pre_user2 = FirebaseDB.getdataOrderEqual("AdminUsers", "Username", user)
                        if not pre_user2 and pre_user2 is not None:
                            pre_user3 = FirebaseDB.getdataOrderEqual("SellerUsers", "Username", user)

                    if not (pre_user1 or pre_user2 or pre_user3):
                        walno = Apptools.generateuniquecode(WALLETTABLE, "WalletNo")
                        if walno:
                            details = {"Name": name, "Email": email, "Username": user, "PIN": pin,
                                       "Delivery Address": DelAdd.strip(),
                                       "Premium Account": "No", "WalletNo": walno}
                            status = statusPush = False
                            status = FirebaseDB.create_account(email, pswd, user, details, table)

                            if status == True:
                                data = {"WalletNo": walno, "Email": email, "UserType": "Buyer", "Balance": 0,
                                        "PIN": pin}
                                statusPush = FirebaseDB.pushData(WALLETTABLE, data)

                            FirebaseDB.signout()
                            if status == True and statusPush == True:
                                messagebox.showinfo("Success", "Account Created Successfully")
                                Apptools.logout(master)
                            else:
                                if status:
                                    errmsg = "Authentication:" + str(status) + \
                                             "\nWallet Creation:" + str(statusPush)
                                    messagebox.showwarning("Error",
                                                           "Some Error Occured while Signing-up\nPlease Retry!\nLog :\n" + errmsg)

                    else:
                        messagebox.showinfo("Account with this Username already exist",
                                            "Account with this Username already exist.\nTry Another Username")
                    del pre_user1
                    del pre_user2
                    del pre_user3
                else:
                    messagebox.showwarning(title="Warning!",
                                           message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                    return
            else:
                if not cond2:
                    messagebox.showinfo("Invalid entry", "Enter Valid E-mail address")
                elif not cond1:
                    messagebox.showinfo("Invalid entry", "Enter Valid PIN")
                else:
                    messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Password Mismatch\nRe-enter Password")


class Page2_SignupSeller(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        frame = ScrollableFrame(self, ch=600, cw=585)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[0], 0, 0, 100, 600, rspan=13)

        Apptools.image_Show(frame.scrollable_frame, SIGNUPPAGEImgDir[1], 0, 4, 100, 600, rspan=13)

        lbl = tk.Label(frame.scrollable_frame, text="Kans")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Seller's Signup")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Name")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5)

        name = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        name.grid(row=3, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Email Id")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5)

        email = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        email.grid(row=4, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, padx=5)

        Pin = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Pin.grid(row=5, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Username")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5)

        username = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        username.grid(row=6, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5)

        Password = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Password.grid(row=7, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Retype Password")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5)

        Repassword = tk.Entry(frame.scrollable_frame, show="●", fg="#E8E8E8", bg="#333333")
        Repassword.grid(row=8, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Name of Organisation")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1, padx=5)

        orgname = tk.Entry(frame.scrollable_frame, fg="#E8E8E8", bg="#333333")
        orgname.grid(row=9, column=2)

        lbl = tk.Label(frame.scrollable_frame, text="Address of Organisation")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=10, column=1, padx=5)

        OrgAdd = tk.Text(frame.scrollable_frame, fg="#E8E8E8", bg="#333333", height=5)
        OrgAdd.config(width=15)
        OrgAdd.grid(row=10, column=2)

        button = tk.Button(frame.scrollable_frame, text="Register")
        button.config(command=lambda: self.Processing(master, name.get(), email.get(), username.get(), Password.get(),
                                                      Repassword.get(), Pin.get(), orgname.get(),
                                                      OrgAdd.get("1.0", "end-1c")))
        button.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        button.config(padx=5, pady=3)
        button.grid(row=11, column=3, pady=10, padx=20)

        lbl = tk.Label(frame.scrollable_frame, text="Already Registered?\nLogin Here")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.config(cursor="hand2")
        lbl.bind("<Button-1>", lambda e: master.switch_frame(Homepage))
        lbl.grid(row=12, column=2)

        frame.grid(row=0, column=0)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.RegisterSeller, *args))

    def RegisterSeller(self, master, name, email, user, pswd, repass, pin, OrgName, OrgAdd):

        table = "SellerUsers"
        if pswd == repass:

            cond1 = pin.isdigit()
            cond2 = Apptools.check_mail(email)
            cond3 = Apptools.is_not_null(name, user, pswd, repass, pin, email, OrgAdd, OrgName)
            cond4 = len(pin) >= 6
            cond5 = len(pswd) >= 6

            if cond1 and cond2 and cond3:
                email = email.lower()
                if not cond4:
                    messagebox.showwarning("Weak PIN", "PIN must be of atleast 6 digits.")
                    return
                if not cond5:
                    messagebox.showwarning("Weak Password", "Password must be of atleast 6 characters.")
                    return
                if FirebaseDB.connect():

                    pre_user1 = pre_user2 = pre_user3 = None
                    pre_user1 = FirebaseDB.getdataOrderEqual(table, "Username", user)
                    if not pre_user1 and pre_user1 is not None:
                        pre_user2 = FirebaseDB.getdataOrderEqual("BuyerUsers", "Username", user)
                        if not pre_user2 and pre_user2 is not None:
                            pre_user3 = FirebaseDB.getdataOrderEqual("AdminUsers", "Username", user)

                    if not (pre_user1 or pre_user2 or pre_user3):
                        walno = Apptools.generateuniquecode(WALLETTABLE, "WalletNo")
                        if walno:
                            details = {"Name": name, "Email": email, "Username": user, "PIN": pin,
                                       "Organisation Name": OrgName, "Organisation Address": OrgAdd.strip(),
                                       "WalletNo": walno}
                            status = statusPush = False
                            status = FirebaseDB.create_account(email, pswd, user, details, table)
                            if status == True:
                                data = {"WalletNo": walno, "Email": email, "UserType": "Buyer", "Balance": 0,
                                        "PIN": pin}
                                statusPush = FirebaseDB.pushData(WALLETTABLE, data)

                            FirebaseDB.signout()
                            if status == True and statusPush == True:
                                messagebox.showinfo("Success", "Account Created Successfully")
                                Apptools.logout(master)
                            else:
                                if status:
                                    errmsg = "Authentication:" + str(status) + \
                                             "\nWallet Creation:" + str(statusPush)
                                    messagebox.showwarning("Error",
                                                           "Some Error Occured while Signing-up\nPlease Retry!\nLog :\n" + errmsg)
                    else:
                        messagebox.showinfo("Account with this Username already exist",
                                            "Account with this Username already exist.\nTry Another Username")
                    del pre_user1
                    del pre_user2
                    del pre_user3
                else:
                    messagebox.showwarning(title="Warning!",
                                           message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")
                    return
            else:

                if not cond2:
                    messagebox.showinfo("Invalid entry", "Enter Valid E-mail address")
                elif not cond1:
                    messagebox.showinfo("Invalid entry", "Enter Valid PIN")
                else:
                    messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
        else:
            messagebox.showwarning("Password Mismatch", "Password Mismatch\nRe-enter Password")


class Page3_DashboardAdmin(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0, padx=20, pady=10)

        lbl = tk.Label(self, text="Admin Console")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        dispname = SESSION_USER.display_name or "Buddy"
        lbl = tk.Label(self, text="Welcome " + dispname)
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, pady=20)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 0, 300, 200)

        btn = tk.Button(self, text="Profile", command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn = tk.Button(self, text="Wallet Mangament", command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)


class Page3_DashboardSeller(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0, padx=20, pady=10)

        lbl = tk.Label(self, text="Seller's Console")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        dispname = SESSION_USER.display_name or "Buddy"
        lbl = tk.Label(self, text="Welcome " + dispname)
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, pady=20)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 0, 300, 200)

        btn = tk.Button(self, text="Profile", command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn = tk.Button(self, text="Wallet Mangament",
                        command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn = tk.Button(self, text="Items Management", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)


class Page3_DashboardBuyer(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0, padx=20, pady=10)

        lbl = tk.Label(self, text="Buyer's Dashboard")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0)

        dispname = SESSION_USER.display_name or "Buddy"
        lbl = tk.Label(self, text="Welcome " + dispname)
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, pady=20)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 0, 300, 200)

        btn = tk.Button(self, text="Profile Management",
                        command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=0, pady=3)

        btn = tk.Button(self, text="Wallet Management", command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=0, pady=3)

        btn = tk.Button(self, text="Premium Membership", command=lambda: master.switch_frame(Page3_BuyerPremium))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=0, pady=3)

        btn = tk.Button(self, text="Start Shopping", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=0, pady=3)

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=8, column=0, pady=3)


class Page3_AdminProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardAdmin))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Show Profile", command=lambda: master.switch_frame(Page4_AdminShowProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=5)

        btn = tk.Button(self, text="Edit Profile", command=lambda: master.switch_frame(Page4_AdminEditProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Check Balance", command=lambda: master.switch_frame(Page4_AdminCheckBalance))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn = tk.Button(self, text="Delete Account", command=lambda: master.switch_frame(Page4_AdminDeleteAccount))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_AdminWalletManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardAdmin))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Cashout Money", command=lambda: master.switch_frame(Page4_AdminCashoutMoney))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Self Cashout Request",
                        command=lambda: master.switch_frame(Page4_AdminSelfCashoutRequest))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Top-up Wallet", command=lambda: master.switch_frame(Page4_AdminTopupWallet))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn = tk.Button(self, text="Pending Cashouts", command=lambda: master.switch_frame(Page4_AdminPendingCashout))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_SellerProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Show Profile", command=lambda: master.switch_frame(Page4_SellerShowProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Edit Profile", command=lambda: master.switch_frame(Page4_SellerEditProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Delete Account", command=lambda: master.switch_frame(Page4_SellerDeleteAccount))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


class Page3_SellerWalletManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Check Balance", command=lambda: master.switch_frame(Page4_SellerCheckBalance))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Cashout Request", command=lambda: master.switch_frame(Page4_SellerCashoutRequest))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Recharge Wallet Info",
                        command=lambda: master.switch_frame(Page4_SellerWalletRecharge))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


class Page3_SellerItemManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardSeller))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Item Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Add Items", command=lambda: master.switch_frame(Page4_SellerAddItems))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Edit Items", command=lambda: master.switch_frame(Page4_SellerModifyItems))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Add stocks", command=lambda: master.switch_frame(Page4_SellerAddStocks))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn = tk.Button(self, text="Search items", command=lambda: master.switch_frame(Page4_SellerSearchItem))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)

        btn = tk.Button(self, text="Remove items", command=lambda: master.switch_frame(Page4_SellerRemoveItem))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=8, column=1, pady=3)

        btn = tk.Button(self, text="Recent Transactions",
                        command=lambda: master.switch_frame(Page4_SellerRecentTransactions))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=9, column=1, pady=3)


class Page3_BuyerProfileManagement(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Profile Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Show Profile", command=lambda: master.switch_frame(Page4_BuyerShowProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Edit Profile", command=lambda: master.switch_frame(Page4_BuyerEditProfile))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Recently brought", command=lambda: master.switch_frame(Page4_BuyerRecentlyBrought))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn = tk.Button(self, text="Delete Account", command=lambda: master.switch_frame(Page4_BuyerDeleteAccount))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_BuyerPremium(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Premium Membership")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        txt = 'Get Enjoying Benefits like\n' \
              'Free Delivery\nExclusive Bargains and a lot more.'
        lbl = tk.Label(self, text=txt)
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, pady=10)

        self.Processing(master, None)

    def Processing(self, *args):
        if len(args) + 1 == 3:
            LoadingPage.perform(self, (self, self.CheckIsPremium, *args[:-1]))
        else:
            LoadingPage.perform(self, (self, self.getmembership, *args))

    def CheckIsPremium(self, master):
        lbl = tk.Label(self, text="Checking for your Premium status\nPlease be patient.....")
        lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, pady=10)
        ispremium = False
        result = FirebaseDB.getdataOrderEqual("BuyerUsers", "Premium Account", "Yes")
        if result:
            for i in result:
                key = i
                val = result[i]
                if val['Email'] == SESSION_USER.email:
                    ispremium = True

        if ispremium:
            lbl.config(text="You already have our Premium Membership\nStart Shopping")
        elif FirebaseDB.connect():
            txt = 'You are going to be charged Rs 100 from your wallet for \n' \
                  'activating Lifetime Premium membership'
            lbl.config(font=("Segoe UI", 12), text=txt)

            btn = tk.Button(self, text="Go Premium", command=lambda: self.Processing(master))
            btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
            btn.grid(row=5, column=1, pady=3)
        else:
            lbl.config(text="No Internet Connection\nFailed to connect to Server :-(")

    def getmembership(self, master):

        result = self.findsuperadmin()
        result2 = self.findWalletNo()
        if result is not None and result2 is not None:
            SAdminWal, SAdminBal = result
            UserWal, UserBal = result2

            if UserBal >= 100:
                step1 = FirebaseDB.updateData("Wallet", {"Balance": UserBal - 100}, "WalletNo", UserWal)
                if step1:
                    step2 = FirebaseDB.updateData("Wallet", {"Balance": SAdminBal + 100}, "WalletNo", SAdminWal)
                    if step2:
                        step3 = FirebaseDB.updateData("BuyerUsers", {"Premium Account": "Yes"})
                        if step3:
                            messagebox.showinfo("Success", "You are now our premium member\n"
                                                           "Get exclusive discount and benefits.\nStart Shooping")
                            master.switch_frame(Page3_DashboardBuyer)

            elif UserBal < 100:
                messagebox.showwarning("Insufficient fund in wallet", "Please recharge your wallet to continue.")
        else:
            messagebox.showinfo("No admin on system", "Can't proceed transaction.\nNo admin on system")

    def findsuperadmin(self):
        result = FirebaseDB.getdataOrderEqual("Wallet", "UserType", "Admin")
        if result:
            for i in result:
                walletno = result[i]["WalletNo"]
                balance = result[i]["Balance"]
                return walletno, balance

    def findWalletNo(self):
        result = FirebaseDB.getdataOrderEqual("Wallet", "UserType", "Buyer")
        if result:
            for i in result:
                if result[i]["Email"] == SESSION_USER.email:
                    walletno = result[i]["WalletNo"]
                    balance = result[i]["Balance"]
                    return walletno, balance
        return None, None


class Page3_BuyerShoppe(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Start Shopping!")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Start Shopping", command=lambda: master.switch_frame(Page4_BuyerShopping))
        btn.config(bg="#1F8EE7", fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Search items", command=lambda: master.switch_frame(Page4_BuyerSearchItems))
        btn.config(bg="#1F8EE7", padx=6, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Wishlist", command=lambda: master.switch_frame(Page4_BuyerWishlist))
        btn.config(bg="#1F8EE7", padx=19, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)

        btn = tk.Button(self, text="Cart", command=lambda: master.switch_frame(Page7_BuyerPaymentProceed))
        btn.config(bg="#1F8EE7", padx=29, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=7, column=1, pady=3)


class Page3_BuyerWallet(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_DashboardBuyer))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans:Your Shopping Partner")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(self, text="Wallet Management")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1)

        Apptools.image_Show(self, DASHBOARDImgDir, 3, 1, 200, 150)

        btn = tk.Button(self, text="Check Balance", command=lambda: master.switch_frame(Page4_BuyerCheckBalance))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=1, pady=3)

        btn = tk.Button(self, text="Cashout Request", command=lambda: master.switch_frame(Page4_BuyerCashout))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=3)

        btn = tk.Button(self, text="Recharge Wallet", command=lambda: master.switch_frame(Page4_BuyerWalletRecharge))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=1, pady=3)


class Page4_AdminShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10, columnspan=2)

        Loadinglbl = tk.Label(self, text="Loading\nPlease be patient....")
        Loadinglbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        Loadinglbl.grid(row=2, column=1, padx=20, pady=10, columnspan=2)

        self.Processing(Loadinglbl)

    def check(self, Loadinglbl):
        if FirebaseDB.connect():
            Fieldname = ["Name", "Email Address", "Username", "Wallet No"]
            for i in range(len(Fieldname)):
                lbl = tk.Label(self, text=Fieldname[i] + ":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=1, padx=5)

            self.Processing()
        else:
            lbl = tk.Label(self, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=2, column=0, columnspan=4, padx=30, pady=100)
        Loadinglbl.destroy()

    def Processing(self, *args):
        if len(args) + 1 == 1:
            LoadingPage.perform(self, (self, self.showprofile, *args))
        else:
            LoadingPage.perform(self, (self, self.check, *args))

    def showprofile(self):
        FieldId = ["Name", "Email", "Username", "WalletNo"]
        result = FirebaseDB.getdataOrderEqual("AdminUsers", "Email", SESSION_USER.email)
        if result:
            out = []
            data = list(result.values())[0]
            for i in FieldId:
                out.append(data[i])
            for i in range(len(FieldId)):
                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=2, padx=5)


class Page4_AdminEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=20, pady=10)

        Entry_Obj = []
        Fieldname = ["Name"]
        for i in range(1):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i + 2, column=1, padx=20, pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i + 2, column=2)
            # Entry_Obj[i].insert(0, data[i])

        btn = tk.Button(self, text="Modify Profile")
        btn.config(command=lambda: self.Processing(master, Entry_Obj[0].get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=8, column=3, pady=10)

        self.Processing(Entry_Obj)

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.getprofile, *args))
        else:
            LoadingPage.perform(self, (self, self.modifyProfile, *args))

    def getprofile(self, Entry_Obj):
        result = FirebaseDB.getdataOrderEqual("AdminUsers", "Email", SESSION_USER.email)

        data = ["" for i in range(1)]
        if result:
            data[0] = list(result.values())[0]['Name']
        Entry_Obj[0].insert(0, data[0])

    def modifyProfile(self, master, name):
        cond1 = Apptools.is_not_null(name)
        if cond1:
            rec = FirebaseDB.updateData("AdminUsers", {"Name": name})
            if rec:
                user = auth.update_user(SESSION_USER.uid, display_name=name)
                if user:
                    globals()['SESSION_USER'] = auth.get_user(SESSION_USER.uid)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardAdmin)
        else:
            messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")


class Page4_AdminCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Check Balance")
        btn.config(command=lambda: self.Processing(pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkBal, *args))

    def checkBal(self, pin):
        ref = FirebaseDB.getdataOrderEqual("AdminUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)

                sep = ttk.Separator(self, orient='horizontal')
                sep.grid(row=4, column=0, columnspan=5, sticky="ew")

                lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ " + str(bal))
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=5, column=1, columnspan=3, padx=20, pady=20)

            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_AdminDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        msg = "Make sure you settle your account before deleting your account\n" \
              "Failing to do so may cause a fraud case be filed against you\n" \
              "as per Company's Terms of Service\n\nMake sure you redeem all your cashout before account deletion\n" \
              "Post deletion cashout redemption is not possible."
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, columnspan=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkDel, *args))

    def checkDel(self, master, pin):
        ref = FirebaseDB.getdataOrderEqual("AdminUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)
                ref2 = FirebaseDB.getdataOrder("AdminUsers", "Email")
                if ref2:
                    noofadmin = len(list(ref2.values()))
                    if noofadmin > 1:
                        if bal == 0:
                            ref3 = FirebaseDB.getdataOrderEqual("Cash Record Admin", "Email", SESSION_USER.email)
                            if ref3:
                                cash = list(ref3.values())[0]['Balance']
                                if cash != 0:
                                    msg2 = "Show this message to company before deleting your account for settling\nCash to be taken by company : " + str(
                                        cash) + "\nNegative value means cash to be given by company."
                                    messagebox.showwarning("Cash settlement", msg2)
                                else:
                                    choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                                    if choice:
                                        step1 = FirebaseDB.deleteAuthData(SESSION_USER.uid)
                                        if step1:
                                            step2 = FirebaseDB.deleteData("Wallet", identifier="Email",
                                                                          value=SESSION_USER.email)
                                            if step2:
                                                step3 = FirebaseDB.deleteData("Cash Record Admin",
                                                                              key=list(ref3.keys())[0])
                                                if step3:
                                                    step4 = FirebaseDB.deleteData("AdminUsers", key=list(ref.keys())[0])
                                                    if step4:
                                                        messagebox.showinfo("Success", "Account Deleted Successfully")
                                                        Apptools.logout(master)

                        else:
                            if bal > 0:
                                msg = "You have with us the precious money in your account,proceed for a self cashout request before deleting account.\nInconvenience regretted"
                                messagebox.showwarning("Money is Precious", msg)
                            else:
                                msg = "You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from another admin before deleting account.\nInconvenience regretted"
                                messagebox.showwarning("Money is Precious", msg)
                    else:
                        msg = "As you are the only admin on our system hence we can't lose you\nIf you want to leave us contact System administrator or wait for another admin to Sign in (for a cashout request to happen)\nInconvenience regretted"
                        messagebox.showerror("Access denied", msg)
            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_AdminCashoutMoney(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Cash withdrawl")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, pady=10)

        lbl = tk.Label(self, text="Enter Email")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        email = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        email.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Withdrawl amount")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        amt = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=3, column=2)

        lbl = tk.Label(self, text="Enter KEY")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, pady=10)

        key = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        key.grid(row=4, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(email.get(), amt.get(), key.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.cashout, *args))

    def cashout(self, email, amt, key):
        cond1 = Apptools.is_not_null(email, key)
        cond2 = amt.isdigit() and Apptools.in_limit(5, 10 ** 7, amt)
        cond3 = len(key) == 16
        cond4 = Apptools.check_mail(email)
        if cond1 and cond2 and cond3 and cond4:
            ref = FirebaseDB.getdataOrderEqual("Wallet", "Email", email)
            if ref:
                data = list(ref.values())[0]
                walno = data['WalletNo']
                ref2 = FirebaseDB.getdataOrderEqual("TempBank", "Key", key)
                if ref2:
                    data2 = list(ref2.values())[0]
                    SecretCode = data2['SecretCode']
                    kwal, kbal = Apptools.keydecoder(key, SecretCode)
                    if kwal == walno and amt == str(kbal):
                        ref3 = FirebaseDB.getdataOrderEqual("Wallet", "Email", SESSION_USER.email)
                        if ref3:
                            data3 = list(ref3.values())[0]
                            adminWalNo = data3['WalletNo']
                            ref4 = FirebaseDB.getdataOrderEqual("Cash Record Admin", "Email", SESSION_USER.email)
                            if ref4:
                                cashRecordBal = list(ref4.values())[0]['Balance']
                                if adminWalNo != walno:
                                    res1 = FirebaseDB.updateData("Wallet", {"Balance": data3['Balance'] + 5})
                                    res2 = FirebaseDB.updateData("Cash Record Admin",
                                                                 {"Balance": cashRecordBal - (kbal - 5)})
                                    if res1 and res2:
                                        res3 = FirebaseDB.deleteData("TempBank", key=list(ref2.keys())[0])
                                        if res3:
                                            messagebox.showinfo("Success!", "Cashout Successful")

                                            sep = ttk.Separator(self, orient='horizontal')
                                            sep.grid(row=6, column=0, columnspan=5, sticky="ew")

                                            lbl = tk.Label(self,
                                                           text="Withdrawl Amount : " + amt + "\nAmount to be Paid : " + str(
                                                               kbal - 5) + "\nPG & Service Charges : 5")
                                            lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
                                            lbl.grid(row=7, column=1, columnspan=3, padx=5, pady=10)
                                else:
                                    messagebox.showerror("Cashout not possible!",
                                                         "You can't take cashout of your own personal account")

                    else:
                        messagebox.showwarning("Invalid Credentials",
                                               "Either Email Address or Withdrawl amount is incorrect.")
                elif ref2 is not None:
                    messagebox.showwarning("Invalid Key",
                                           "Key is not found in our servers\nMaybe already used or invalid")
            elif ref is not None:
                messagebox.showerror("No such user exists!",
                                     "No such user exists!\nTry entering correct username/details")
        else:
            if not (cond1 or cond4):
                messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")
            elif not cond4:
                messagebox.showinfo("Invalid entry", "Enter Valid E-mail address")
            elif not cond2:
                messagebox.showinfo("Invalid entry", "Enter Valid Amount (5~10 million)")
            elif not cond3:
                messagebox.showinfo("Invalid entry", "Enter Valid Key of length = 16")
            else:
                messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")


class Page4_AdminSelfCashoutRequest(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Self Cashout Request")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        msg = "This service is availed for a full cashout.\n" \
              "No custom amount can't be put"
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, columnspan=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.AdmSelfcashout, *args))

    def AdmSelfcashout(self, master, pin):
        ref = FirebaseDB.getdataOrderEqual("Wallet", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            walno = data['WalletNo']
            if str(data['PIN']) == pin:
                bal = Apptools.checkBalance(walno, pin)
                ref2 = FirebaseDB.getdataOrder("AdminUsers", "Email")
                if ref2:
                    noofadmin = len(list(ref2.values()))
                    if noofadmin > 1:
                        if bal > 0:
                            key = Apptools.CashoutRequest(walno, bal, pin)
                            if key is not None:
                                messagebox.showinfo("Action Initiated",
                                                    "Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                                sep = ttk.Separator(self, orient='horizontal')
                                sep.grid(row=5, column=0, columnspan=5, sticky="ew")

                                lbl = tk.Label(self, text="Successful\nAmount : " + str(
                                    bal) + "\nKey : " + key + "\nNote it down(Not recoverable)")
                                lbl.config(font=("Sans Serif", 15), fg="#E8E8E8", bg="#333333")
                                lbl.grid(row=6, column=1, pady=10, columnspan=3)
                        else:
                            messagebox.showwarning("Insufficient fund", "There is insufficient money in your wallet.")
                    else:
                        msg = "As there are the only one admin on our system hence we can't do this transcation (for a cashout request to happen)\nInconvenience regretted"
                        messagebox.showerror("Access denied", msg)
            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_AdminTopupWallet(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Top-Up Account")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter Email")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        email = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        email.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Topup Amount")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        amt = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=3, column=2)

        lbl = tk.Label(self, text="Enter your PIN")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=4, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(email.get(), amt.get(), pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.topup, *args))

    def topup(self, email, amt, pin):
        cond1 = Apptools.is_not_null(email, amt, pin)
        cond2 = Apptools.in_limit(5, 10 ** 7, amt)
        cond3 = amt.isdigit()
        cond4 = Apptools.check_mail(email)
        if cond1 and cond3 and cond2 and cond4:
            ref = FirebaseDB.getdataOrderEqual("Wallet", "Email", SESSION_USER.email)
            if ref:
                data = list(ref.values())[0]
                adminWalNo = data['WalletNo']
                if str(data['PIN']) == pin:
                    netamt = str(int(amt) - 5)

                    ref2 = FirebaseDB.getdataOrderEqual("Wallet", "Email", email)
                    if ref2:
                        data2 = list(ref2.values())[0]
                        walno = data2['WalletNo']

                        ref3 = FirebaseDB.getdataOrderEqual("Cash Record Admin", "Email", SESSION_USER.email)
                        if ref3:
                            cashRecordBal = list(ref3.values())[0]['Balance']
                            if adminWalNo != walno:
                                choice = messagebox.askyesno("Sure",
                                                             "Are you sure want to recharge the wallet of user with "
                                                             "email address '" + email + "' with Rs. " + netamt +
                                                             "?\nPG & Other Charge = Rs. 5")
                                if choice:
                                    res1 = FirebaseDB.updateData("Wallet", {"Balance": data2['Balance'] + int(netamt)},
                                                                 identifierval=email)

                                    if res1:
                                        res2 = FirebaseDB.updateData("Cash Record Admin", {"Balance":
                                                                                               cashRecordBal + int(
                                                                                                   amt)})
                                        if res2:
                                            res3 = FirebaseDB.updateData("Wallet", {"Balance": data['Balance'] + 5})
                                            if res3:
                                                messagebox.showinfo("Transaction successful!",
                                                                    "Transferred Rs. " + netamt + " to user Successfully\nAsk user to check his account")
                                                msg = "Transaction Receipt\nEmail : {0}\nNet Amount Recharged : {1}\nPG & Other Charge : 5\nCash Given by user : {2}".format(
                                                    email, netamt, amt).strip()
                                                sep = ttk.Separator(self, orient='horizontal')
                                                sep.grid(row=6, column=0, columnspan=5, sticky="ew")

                                                lbl = tk.Label(self, text=msg)
                                                lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                                                lbl.grid(row=7, column=1, columnspan=3, pady=10, padx=5)
                            else:
                                messagebox.showerror("TopUp not possible!",
                                                     "You can take topup your own personal account")

                    elif ref2 is not None:
                        messagebox.showerror("No such user exists!", "No such user exists!\n"
                                                                     "Try entering correct email address")
                else:
                    messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")
        else:
            if not cond4:
                messagebox.showinfo("Invalid entry", "Enter Valid E-mail address")
            elif not cond2:
                messagebox.showinfo("Invalid entry", "Enter Valid Amount (5~10^7)")
            else:
                messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")


class Page4_AdminPendingCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_AdminWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Pending Cashout")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=30, pady=10)

        self.Processing()

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.pendingcashout, *args))

    def pendingcashout(self):
        lbl = tk.Label(self, text="Loading! Please be patient....")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=30, pady=10)
        ref = FirebaseDB.getdataOrder("TempBank", "Key", showWarning=False)
        if ref:
            data = list(ref.values())
            for i in range(len(data)):
                data[i] = Apptools.keydecoder(data[i]['Key'], data[i]['SecretCode'])
            lbl.destroy()
            self.output(data)

        elif not FirebaseDB.connect():
            lbl.config(text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")

        elif ref is not None:
            messagebox.showinfo("No pending cashout(s)", "No records found")
            lbl.config(font=("Segoe UI", 15), text="No pending cashout(s)")
        else:
            lbl.config(font=("Segoe UI", 15), text="Unknown Error Occured!\nPlease try later")

    def output(self, out):
        column = ("Wallet Number", "Amount")
        Apptoolsv2.Treeoutput(self, column, out, srow=2, scolumn=1, singleLineFilter=False, InScrollableframe=False,
                              lbrow=2, lbcolumn=1)


class Page4_SellerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=2, padx=60, pady=10)

        Loadinglbl = tk.Label(self, text="Loading\nPlease be patient....")
        Loadinglbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        Loadinglbl.grid(row=2, column=1, padx=20, pady=10, columnspan=2)
        self.Processing(Loadinglbl)

    def check(self, Loadinglbl):
        if FirebaseDB.connect():
            Fieldname = ["Name", "Username", "Email", "Name of Organisation", "Address of Organisation",
                         "Wallet Number"]
            for i in range(len(Fieldname)):
                lbl = tk.Label(self, text=Fieldname[i] + ":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=1, padx=5)

            self.Processing()
        else:
            lbl = tk.Label(self, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=2, column=0, columnspan=4, padx=30, pady=100)
        Loadinglbl.destroy()

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.check, *args))
        else:
            LoadingPage.perform(self, (self, self.showprofile, *args))

    def showprofile(self):
        FieldId = ["Name", "Username", "Email", "Organisation Name", "Organisation Address", "WalletNo"]
        result = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", SESSION_USER.email)
        if result:
            out = []
            data = list(result.values())[0]
            for i in FieldId:
                out.append(data[i])
            for i in range(len(FieldId)):
                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=2, padx=5)


class Page4_SellerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=20, pady=10)

        Fieldname = ["Name", "Name of Organisation", "Address of Organisation"]
        Entry_Obj = []
        for i in range(len(Fieldname) - 1):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i + 2, column=1, padx=20, pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i + 2, column=2)

        lbl = tk.Label(self, text=Fieldname[2])
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=20, pady=5)

        Entry_Obj.append(tk.Text(self, fg="#E8E8E8", bg="#333333", height=5))
        Entry_Obj[2].config(width=15)
        Entry_Obj[2].grid(row=4, column=2)

        btn = tk.Button(self, text="Modify Profile")
        btn.config(command=lambda: self.Processing(master, Entry_Obj[0].get(), Entry_Obj[1].get(),
                                                   Entry_Obj[2].get("1.0", "end-1c")))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)
        self.Processing(Entry_Obj)

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.getProfile, *args))
        else:
            LoadingPage.perform(self, (self, self.modifyProfile, *args))

    def getProfile(self, Entry_Obj):
        Fieldname = ["Name", "Name of Organisation", "Address of Organisation"]
        FieldId = ["Name", "Organisation Name", "Organisation Address"]
        result = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", SESSION_USER.email)

        data = ["" for i in range(len(Fieldname))]
        if result:
            i = 0
            for key in FieldId:
                data[i] = list(result.values())[0][key]
                i += 1

        for i in range(len(Fieldname) - 1):
            Entry_Obj[i].insert(0, data[i])
        Entry_Obj[2].insert(tk.INSERT, data[2])

    def modifyProfile(self, master, name, orgname, addorg):
        cond1 = Apptools.is_not_null(name, orgname, addorg)
        if cond1:
            rec = FirebaseDB.updateData("SellerUsers",
                                        {"Organisation Name": orgname, "Organisation Address": addorg.strip(),
                                         "Name": name})
            if rec:
                userup1 = auth.update_user(SESSION_USER.uid, display_name=name)
                if userup1:
                    globals()['SESSION_USER'] = auth.get_user(SESSION_USER.uid)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardSeller)
        else:
            messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")


class Page4_SellerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        lbl = tk.Label(self, text="Make sure you redeem all your Cashout before Account Deletion.\n"
                                  "Post Deletion Cashout redemption is not possible.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, columnspan=3, padx=20, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkDel, *args))

    def checkDel(self, master, pin):

        ref = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)
                if bal == 0:
                    choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                    if choice:
                        step1 = FirebaseDB.deleteAuthData(SESSION_USER.uid)
                        if step1:
                            step2 = FirebaseDB.deleteData("Wallet", identifier="Email",
                                                          value=SESSION_USER.email)
                            if step2:
                                step3 = FirebaseDB.getdataOrderEqual("Items", "Seller Email", SESSION_USER.email)
                                if step3 is not None:
                                    val = list(step3.values())
                                    chk = True
                                    for data in val:
                                        chk = chk and FirebaseDB.deleteDataStorage(data['Image Location'])
                                    if chk:
                                        step4 = FirebaseDB.deleteData("Items",
                                                                      identifier="Seller Email",
                                                                      value=SESSION_USER.email)
                                        if step4:
                                            step5 = FirebaseDB.deleteData("SellerUsers", key=list(ref.keys())[0])
                                            if step5:
                                                messagebox.showinfo("Success", "Account Deleted Successfully")
                                                Apptools.logout(master)

                else:
                    if bal > 0:
                        msg = "You have with us the precious money in your account,proceed for a cashout request before deleting account.\nInconvenience regretted"
                        messagebox.showwarning("Money is Precious", msg)
                    else:
                        msg = "You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from admin before deleting account.\nInconvenience regretted"
                        messagebox.showwarning("Money is Precious", msg)

            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_SellerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Check Balance")
        btn.config(command=lambda: self.Processing(pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkBal, *args))

    def checkBal(self, pin):
        ref = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)

                sep = ttk.Separator(self, orient='horizontal')
                sep.grid(row=4, column=0, columnspan=5, sticky="ew")

                lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ " + str(bal))
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=5, column=1, columnspan=3, padx=20, pady=20)
            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_SellerCashoutRequest(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Cashout Request")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter Balance")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        amt = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=3, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get(), amt.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        msg = "After generation of key write down key and amount safely\n" \
              "and show it to our nearest admin.\n" \
              "PG charges (Rs.5) is applicable."
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, columnspan=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.Sellercashout, *args))

    def Sellercashout(self, master, pin, amt):
        cond1 = amt.isdigit()
        cond2 = Apptools.in_limit(5, 10 ** 7, amt)
        if cond1 and cond2:
            ref = FirebaseDB.getdataOrderEqual("Wallet", "Email", SESSION_USER.email)
            if ref:
                data = list(ref.values())[0]
                walno = data['WalletNo']
                if str(data['PIN']) == pin:
                    bal = Apptools.checkBalance(walno, pin)
                    if bal >= int(amt):
                        key = Apptools.CashoutRequest(walno, amt, pin)
                        if key is not None:
                            messagebox.showinfo("Action Initiated",
                                                "Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                            sep = ttk.Separator(self, orient='horizontal')
                            sep.grid(row=6, column=0, columnspan=5, sticky="ew")

                            lbl = tk.Label(self,
                                           text="Status : Success\nAmount : " + amt + "\nKey : " + key + "\nNote it down(Not recoverable)")
                            lbl.config(font=("Sans Serif", 15), fg="#E8E8E8", bg="#333333")
                            lbl.grid(row=7, column=1, columnspan=3, pady=10)
                    else:
                        messagebox.showwarning("Insufficient fund",
                                               "There is insufficient money in your wallet.")
                else:
                    messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")
        else:
            messagebox.showwarning("Invalid entry", "Invalid amount.\nEnter a valid amount(5~Max 1 Crore).")


class Page4_SellerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerWalletManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Wallet Recharge Info")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=30, pady=10)

        msg = "To recharge your wallet you must go to our admin locations,\n" \
              "Admin will ask for your Email and Amount to be topup\n" \
              "PG Charges of Rs. 5 irrespective of topup amount is applicable.\n" \
              "Never share your personal details like your PIN,Password etc with admin."
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=30, pady=10)


class Page4_SellerAddItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
        self.imageAddress = DEFAULTIMAGEDir

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Add Items")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Item Name")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        Iname = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iname.grid(row=2, column=2)

        lbl = tk.Label(self, text="Wholesale Price")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        Iwhp = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Iwhp.grid(row=3, column=2)

        lbl = tk.Label(self, text="Retail Price")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, pady=10)

        Irp = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Irp.grid(row=4, column=2)

        lbl = tk.Label(self, text="No. of Stocks")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, padx=5, pady=10)

        Istock = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        Istock.grid(row=5, column=2)

        lbl = tk.Label(self, text="Description")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5, pady=10)

        IDesc = tk.Text(self, fg="#E8E8E8", bg="#333333", height=5)
        IDesc.config(width=15)
        IDesc.grid(row=6, column=2)

        lbl = tk.Label(self, text="Category")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5, pady=10)

        Category = ["Stationary", "Electronics", "Clothing", "Beauty",
                    "Softwares", "Sports", "Daily Use", "Grocery", "Health", "Others"]

        CategoryVar = StringVar(self, "Stationary")
        Menu = tk.OptionMenu(self, CategoryVar, *Category)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=7, column=2)

        lbl = tk.Label(self, text="Add Image")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5, pady=10)

        Apptools.imgbutton(self, DEFAULTIMAGEDir, 100, 100, 8, 2)

        btn = tk.Button(self, text="Add Item")
        btn.config(command=lambda: self.Processing(master, Iname.get(), Iwhp.get(), Irp.get(), Istock.get(),
                                                   IDesc.get("1.0", "end-1c"), CategoryVar.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=9, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.additem, *args))

    def additem(self, master, iname, iwp, irp, istock, idesc, icat):
        filedir = self.imageAddress
        cond1 = Apptools.is_not_null(iname, iwp, irp, istock, idesc, icat, filedir)
        cond2 = Apptools.check_digit(iwp, irp) and istock.isdigit()  # Auto check for -ve number and decimal
        cond3 = cond2 and float(irp) >= float(iwp) > 0
        if cond1 and cond2 and cond3:
            ref = FirebaseDB.getdataOrderEqual("SellerUsers", "Email", SESSION_USER.email)
            if ref:
                data = list(ref.values())[0]
                selorg = data['Organisation Name']
                savename = Apptools.generateuniquecode("Items", "Image Location")
                uploadImgurl = FirebaseDB.sendDataStorage(filedir, savename)
                if uploadImgurl:
                    icode = Apptools.generate_id("Items", "ItemCode")
                    if icode:
                        details = {"ItemCode": icode, "ItemName": iname, "Wholesale Price": float(iwp),
                                   "Retail Price": float(irp), "Category": icat,
                                   "Stock": int(istock), "Description": idesc.strip(), "Image Location": uploadImgurl,
                                   "Seller Organisation Name": selorg, "Seller Email": SESSION_USER.email}
                        result = FirebaseDB.pushData("Items", details)
                        if result:
                            messagebox.showinfo("Success!", "Item added successfully")
                            master.switch_frame(Page4_SellerAddItems)  # Refresh the Page

        else:
            if cond2 and not (cond3):
                messagebox.showwarning("Invalid Input",
                                       "Wholesale must be less than or equal to retail price and must be greater than zero.")
            else:
                messagebox.showwarning("Invalid Input", "Fill all the forms correctly to continue")


class Page4_SellerModifyItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Item Details")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        itemcode = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemcode.grid(row=2, column=2)

        btn = tk.Button(self, text="Get Details")
        btn.config(command=lambda: self.Processing(master, itemcode.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, columnspan=3, padx=5, pady=10)

    def Processing(self, *args):
        if len(args) + 1 == 3:
            LoadingPage.perform(self, (self, self.getDetails, *args))
        else:
            LoadingPage.perform(self, (self, self.modifyDetails, *args))

    def getDetails(self, master, itemcode):
        frame = ScrollableFrame(self, ch=350, cw=385)
        sframe = frame.scrollable_frame
        sframe.imageAddress = ""
        cond1 = itemcode.isdigit()
        if cond1:
            res = FirebaseDB.getdataOrderEqual("Items", "ItemCode", int(itemcode))
            if res:
                val = list(res.values())[0]
                if val['Seller Email'] == SESSION_USER.email:

                    data = ["" for i in range(4)]

                    sep = ttk.Separator(self, orient='horizontal')
                    sep.grid(row=4, column=0, columnspan=5, sticky="ews")

                    lbl = tk.Label(sframe, text="Modify Details")
                    lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=0, column=0, columnspan=4, pady=5)

                    Entry_Obj = []
                    Fieldname = ["Item Name", "Wholesale Price", "Retail Price", "Description"]
                    FieldID = ["ItemName", "Wholesale Price", "Retail Price", "Description"]
                    i = 0
                    for key in FieldID:
                        data[i] = val[key]
                        i += 1
                    for i in range(3):
                        lbl = tk.Label(sframe, text=Fieldname[i])
                        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                        lbl.grid(row=i + 1, column=1, padx=20, pady=5)

                        Entry_Obj.append(tk.Entry(sframe, fg="#E8E8E8", bg="#333333"))
                        Entry_Obj[i].grid(row=i + 1, column=2)
                        Entry_Obj[i].insert(0, data[i])

                    lbl = tk.Label(sframe, text=Fieldname[3])
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=4, column=1, padx=20, pady=5)

                    Entry_Obj.append(tk.Text(sframe, fg="#E8E8E8", bg="#333333", height=5))
                    Entry_Obj[3].config(width=15)
                    Entry_Obj[3].grid(row=4, column=2)
                    Entry_Obj[3].insert(tk.INSERT, data[3])

                    lbl = tk.Label(sframe, text="Category")
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=5, column=1, padx=5, pady=10)

                    Category = ["Stationary", "Electronics", "Clothing", "Beauty",
                                "Softwares", "Sports", "Daily Use", "Grocery", "Health", "Others"]

                    CategoryVar = StringVar(self, val['Category'].title())
                    Menu = tk.OptionMenu(sframe, CategoryVar, *Category)
                    Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
                    Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
                    Menu.grid(row=5, column=2)

                    lbl = tk.Label(sframe, text="Add Image")
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=6, column=1, padx=5, pady=10)

                    imgloc = FirebaseDB.getDataStorage(val['Image Location'])
                    if imgloc:
                        sframe.imageAddress = imgloc
                    else:
                        sframe.imageAddress = DEFAULTIMAGEDir
                    Apptools.imgbutton(sframe, sframe.imageAddress, 100, 100, 6, 2)
                    sframe.address = "1"

                    btn = tk.Button(sframe, text="Modify Details")
                    btn.config(command=lambda: self.Processing(sframe, master, itemcode, Entry_Obj[0].get(),
                                                               Entry_Obj[1].get(), Entry_Obj[2].get(),
                                                               Entry_Obj[3].get("1.0", "end-1c"), CategoryVar.get()))
                    btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
                    btn.grid(row=7, column=3, pady=10)

                    frame.grid(row=5, column=0, columnspan=5)

                else:
                    messagebox.showwarning("Invalid Item Code", "Item Code is incorrect")
                    master.switch_frame(Page4_SellerModifyItems)
            elif res is not None:
                messagebox.showwarning("Invalid Item Code", "Item Code is incorrect")
                master.switch_frame(Page4_SellerModifyItems)
        else:
            messagebox.showwarning("Invalid Field", "Fill all the forms correctly to continue")

    def modifyDetails(self, sframe, master, itemcode, iname, iwhp, irp, idesc, icat):
        filedir = sframe.imageAddress
        cond1 = Apptools.is_not_null(iname, iwhp, irp, idesc, icat, filedir)
        cond2 = Apptools.check_digit(iwhp, irp)
        cond4 = cond1 and cond2 and float(irp) >= float(iwhp) > 0
        Category = ["Stationary", "Electronics", "Clothing", "Beauty",
                    "Softwares", "Sports", "Daily Use", "Grocery", "Health", "Others"]
        cond3 = icat.title() in Category
        if cond1 and cond2 and cond3 and cond4:
            ref = FirebaseDB.getdataOrderEqual("Items", "ItemCode", int(itemcode))
            if ref:
                data = list(ref.values())[0]
                x = data['Image Location'][::-1]
                savename = x[x.find(".") + 1:][::-1]
                uploadImgurl = FirebaseDB.sendDataStorage(filedir, savename)
                if uploadImgurl:
                    details = {"ItemName": iname, "Wholesale Price": float(iwhp),
                               "Retail Price": float(irp), "Category": icat,
                               "Description": idesc.strip(), "Image Location": uploadImgurl}
                    result = FirebaseDB.updateData("Items", details, identifier="ItemCode", identifierval=int(itemcode))
                    if result:
                        messagebox.showinfo("Success!", "Item's details updated successfully")
                        master.switch_frame(Page4_SellerModifyItems)

        else:
            if cond2 and not (cond4):
                messagebox.showwarning("Invalid Input",
                                       "Wholesale must be less than or equal to retail price and must be greater than zero.")
            else:
                messagebox.showwarning("Invalid Input", "Fill all the forms correctly to continue")


class Page4_SellerAddStocks(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Add Stocks")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        itemno = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn = tk.Button(self, text="Get Details")
        btn.config(command=lambda: self.Processing(master, itemno.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10, padx=15)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=1, columnspan=3, padx=5, pady=10)

    def Processing(self, *args):
        if len(args) + 1 == 3:
            LoadingPage.perform(self, (self, self.getDetails, *args))
        else:
            LoadingPage.perform(self, (self, self.modifyDetails, *args))

    def getDetails(self, master, itemcode):
        cond1 = itemcode.isdigit()
        if cond1:
            ref = FirebaseDB.getdataOrderEqual("Items", "ItemCode", int(itemcode))
            if ref:
                data = list(ref.values())[0]
                if data['Seller Email'] == SESSION_USER.email:
                    sep = ttk.Separator(self, orient='horizontal')
                    sep.grid(row=4, column=0, columnspan=5, sticky="ews")

                    lbl = tk.Label(self, text="Modify Details")
                    lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=5, column=0, columnspan=5, pady=5)

                    lbl = tk.Label(self, text="Item Name")
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=6, column=1, padx=20, pady=5)

                    lbl = tk.Label(self, text=data["ItemName"])
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=6, column=2, pady=5, sticky="wns")

                    lbl = tk.Label(self, text="No. of Stocks")
                    lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
                    lbl.grid(row=7, column=1, padx=20, pady=10)

                    Stock = tk.Entry(self, fg="#E8E8E8", bg="#333333")
                    Stock.grid(row=7, column=2)
                    Stock.insert(0, data['Stock'])

                    btn = tk.Button(self, text="Modify Details")
                    btn.config(command=lambda: self.Processing(master, itemcode, Stock.get()))
                    btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
                    btn.grid(row=8, column=3, pady=10, padx=15)

                else:
                    messagebox.showwarning("Invalid Item Code", "Item Code is incorrect")
                    master.switch_frame(Page4_SellerAddStocks)
            elif ref is not None:
                messagebox.showwarning("Invalid Item Code", "Item Code is incorrect")
                master.switch_frame(Page4_SellerAddStocks)
        else:
            messagebox.showwarning("Invalid Input", "Fill all the forms correctly to continue")

    def modifyDetails(self, master, itemcode, istock):
        cond1 = itemcode.isdigit() and istock.isdigit()
        if cond1:
            details = {"Stock": int(istock)}
            result = FirebaseDB.updateData("Items", details, identifier="ItemCode", identifierval=int(itemcode))
            if result:
                messagebox.showinfo("Success!", "Stocks Updated successfully")
                master.switch_frame(Page4_SellerAddStocks)
        else:
            messagebox.showwarning("Invalid Input", "Fill all the forms correctly to continue")


class Page4_SellerSearchItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=5, sticky="e")

        lbl = tk.Label(self, text="Search Items")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=4, padx=30, pady=10)

        lbl = tk.Label(self, text="Search Criteria")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        Searchcr = ["Item Name", "Wholesale Price", "Retail Price", "Description", "Category"]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Value")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        val = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn = tk.Button(self, text="Search")
        btn.config(command=lambda: self.Processing(val.get(), SearchcrVar.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        btn = tk.Button(self, text="Deep Search")
        btn.config(command=lambda: self.Processing(val.get(), SearchcrVar.get(), True))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=4, pady=10)

        btn = tk.Button(self, text="Show All")
        # Adding extra parameter to differentiate it from outofstock
        btn.config(command=lambda: self.Processing(None))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)

        btn = tk.Button(self, text="Out of Stock")
        btn.config(command=self.Processing)
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=4, padx=5)

        msg = "Search Result provided are case-sensitive.\n" \
              "Searched item must start with given value for getting result.\nElse try deep search(may take longer time)"

        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=0, padx=5, pady=10, columnspan=6)

    def Processing(self, *args):
        if len(args) + 1 == 3 or len(args) + 1 == 4:
            LoadingPage.perform(self, (self, self.search, *args))
        elif len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.showAll, *args[:-1]))
        else:
            LoadingPage.perform(self, (self, self.outofstock, *args))

    def search(self, text, criteria, deepSearch=False):
        dbeqv = criteria if criteria != "Item Name" else "ItemName"
        rec = Apptoolsv2.itemSearch(self, text, dbeqv, filtervar="Seller Email", filterval=SESSION_USER.email,
                                    deepSearch=deepSearch)
        if rec:
            if deepSearch:
                self.output(rec, "Deepsearch Results for {0} in {1}".format(str(text), str(criteria)))
            else:
                self.output(rec, "Search Results for {0} in {1}".format(str(text), str(criteria)))

    def showAll(self):
        record = FirebaseDB.getdataOrderEqual("Items", "Seller Email", SESSION_USER.email)
        if record:
            out = list(record.values())
            self.output(out, "Full Inventory")
        elif record is not None:
            messagebox.showinfo("No data", "No records found")

    def outofstock(self):
        record = FirebaseDB.getdataOrderEqual("Items", "Seller Email", SESSION_USER.email)
        if record:
            out = list(record.values())
            res = []
            [res.append(i) for i in out if i['Stock'] == 0]
            out = res
            if out:
                self.output(out, "Out of Stock Items")
            else:
                messagebox.showinfo("No data", "No records found")
        elif record is not None:
            messagebox.showinfo("No data", "No records found")

    def output(self, out, title="Search Results"):
        screen = tk.Toplevel(self, bg="#333333")
        screen.iconphoto(False, Icon)
        screen.title(title)
        screen.resizable(0, 0)

        column = ("Item Code", "Item Name", "Wholesale Price", "Retail Price", "Description", "Category", "Stock")
        Apptoolsv2.Treeoutput(screen, column, self.getValue(out), InScrollableframe=False, label="Search Results")

    def getValue(self, data):
        if data:
            columnId = ("ItemCode", "ItemName", "Wholesale Price", "Retail Price", "Description", "Category", "Stock")
            out = []
            for row in data:
                r = []
                for key in columnId:
                    r.append(row[key])
                out.append(r)
            return out


class Page4_SellerRemoveItem(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Remove Item")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Item Code")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        itemno = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        itemno.grid(row=2, column=2)

        btn = tk.Button(self, text="Delete Item")
        btn.config(command=lambda: self.Processing(master, itemno.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        lbl = tk.Label(self, text="Item Code can be found in\nSearch Items Section.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, columnspan=3, padx=5, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.deleteitem, *args))

    def deleteitem(self, master, itemcode):
        cond1 = itemcode.isdigit()
        if cond1:
            res = FirebaseDB.getdataOrderEqual("Items", "ItemCode", int(itemcode))
            if res:
                data = list(res.values())[0]
                if data['Seller Email'] == SESSION_USER.email:
                    txt = "Name = " + data['ItemName'] + "\nPrice = " + str(data['Retail Price']) + "\nDescription = " + \
                          data["Description"].strip()
                    choice = messagebox.askyesno("Alert", "Are you sure want to remove the item?\n" + txt)
                    if choice:
                        ref = FirebaseDB.deleteDataStorage(data['Image Location'])
                        if ref:
                            ref2 = FirebaseDB.deleteData("Items", key=list(res.keys())[0])
                            if ref2:
                                messagebox.showinfo("Success", "Item Removed Successfully")
                                master.switch_frame(Page3_SellerItemManagement)
            elif res is not None:
                messagebox.showwarning("Invalid Item Code", "Item Code is incorrect")
        else:
            messagebox.showwarning("Invalid Field", "Fill all the forms correctly to continue")


class Page4_SellerRecentTransactions(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_SellerItemManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Transaction Log")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=4, padx=30, pady=10)

        self.recentlytrans()

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.recentlytrans, *args))

    def recentlytrans(self):
        lbl = tk.Label(self, text="Page Under Construction!\nInconvenience never regretted")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, columnspan=4)
        """
        transaction = []
        res = FirebaseDB.getdataOrderEqual("Item Transaction Record","Seller Email",SESSION_USER.email)
        if res is not None:
            res2 = FirebaseDB.getdataOrderEqual("Cash Transaction Record","Source Email",SESSION_USER.email)
            if res2 is not None:
                res3 = FirebaseDB.getdataOrderEqual("Cash Transaction Record","Destiantion Email",SESSION_USER.email)
                if res3 is not None:
                    transaction = list(res.values()) + list(res2.values()) +list(res3.values())

                    sep = ttk.Separator(self,orient='horizontal')
                    sep.grid(row=2,column=0,columnspan=4,sticky="ews")
                    frame = ScrollableFrame(self,ch=228,cw=585)
                    sframe=frame.scrollable_frame
                    if transaction!=[]:
                        self.output(transaction,sframe)
                    else:
                        lbl = tk.Label(sframe, text="No recent transactions")
                        lbl.config(font=("Segoe UI",20), fg="#E8E8E8", bg="#333333")
                        lbl.grid(row=0, column=0,padx=180,pady=80)
                        messagebox.showinfo( "No records found","No recent transactions")

                    frame.grid(row=3,column=0,columnspan=4)
        """

    def output(self, out, sframe):

        column = ("Transaction ID", "Date and Time", "Description", "Debit/Credit", "Amount Paid", "Buyer Name")

        listBox = ttk.Treeview(sframe, selectmode="extended", columns=column, show="headings")

        verscrlbar = ttk.Scrollbar(sframe, orient="vertical", command=listBox.yview)
        verscrlbar.grid(row=2, column=2, sticky="nsw", rowspan=2)

        listBox.configure(yscrollcommand=verscrlbar.set)

        for i in range(len(column)):
            listBox.heading(column[i], text=column[i], command=lambda c=column[i]: self.sortby(listBox, c, 0))
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

    def arrangeItemTransData(self, out):
        res = []
        fieldID = ['Transaction ID', 'Datetime', '', '']
        if out:
            for i in range(10):
                res.append()

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        x = True

        for a, b in data:
            x = x and Apptools.check_digit(a)
        if x:
            for i in range(len(data)):
                data[i] = list(data[i])
                data[i][0] = int(data[i][0])
        data.sort(reverse=descending)

        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))


class Page4_BuyerShowProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=2, padx=30, pady=10)

        Loadinglbl = tk.Label(self, text="Loading\nPlease be patient....")
        Loadinglbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        Loadinglbl.grid(row=2, column=1, padx=20, pady=10, columnspan=2)
        self.Processing(Loadinglbl)

    def check(self, Loadinglbl):
        if FirebaseDB.connect():
            Fieldname = ["Name", "Username", "Email", "Premium Account", "Delivery Address", "Wallet Number"]
            for i in range(len(Fieldname)):
                lbl = tk.Label(self, text=Fieldname[i] + ":")
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=1, padx=5)

            self.Processing()
        else:
            lbl = tk.Label(self, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=2, column=0, columnspan=4, padx=30, pady=100)
        Loadinglbl.destroy()

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.check, *args))
        else:
            LoadingPage.perform(self, (self, self.showprofile, *args))

    def showprofile(self):
        FieldId = ["Name", "Username", "Email", "Premium Account", "Delivery Address", "WalletNo"]
        result = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        if result:
            out = []
            data = list(result.values())[0]
            for i in FieldId:
                out.append(data[i])
            for i in range(len(FieldId)):
                lbl = tk.Label(self, text=out[i])
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=i + 2, column=2, padx=5)


class Page4_BuyerEditProfile(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Modify Profile")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=20, pady=10)

        Fieldname = ["Name", "Delivery Address"]
        Entry_Obj = []
        for i in range(len(Fieldname) - 1):
            lbl = tk.Label(self, text=Fieldname[i])
            lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=i + 2, column=1, padx=20, pady=5)

            Entry_Obj.append(tk.Entry(self, fg="#E8E8E8", bg="#333333"))
            Entry_Obj[i].grid(row=i + 2, column=2)

        lbl = tk.Label(self, text=Fieldname[1])
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=20, pady=5)

        Entry_Obj.append(tk.Text(self, fg="#E8E8E8", bg="#333333", height=5))
        Entry_Obj[1].config(width=15)
        Entry_Obj[1].grid(row=4, column=2)

        btn = tk.Button(self, text="Modify Profile")
        btn.config(command=lambda: self.Processing(master, Entry_Obj[0].get(),
                                                   Entry_Obj[1].get("1.0", "end-1c")))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, pady=10)

        self.Processing(Entry_Obj)

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.getProfile, *args))
        else:
            LoadingPage.perform(self, (self, self.modifyProfile, *args))

    def getProfile(self, Entry_Obj):
        Fieldname = ["Name", "Delivery Address"]
        FieldId = ["Name", "Delivery Address"]
        result = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)

        data = ["" for i in range(len(Fieldname))]
        if result:
            i = 0
            for key in FieldId:
                data[i] = list(result.values())[0][key]
                i += 1

        for i in range(len(Fieldname) - 1):
            Entry_Obj[i].insert(0, data[i])

        Entry_Obj[1].insert(tk.INSERT, data[1])

    def modifyProfile(self, master, name, deladd):
        cond1 = Apptools.is_not_null(name, deladd)
        if cond1:
            rec = FirebaseDB.updateData("BuyerUsers",
                                        {"Delivery Address": deladd.strip(),
                                         "Name": name})
            if rec:
                userup1 = auth.update_user(SESSION_USER.uid, display_name=name)
                if userup1:
                    globals()['SESSION_USER'] = auth.get_user(SESSION_USER.uid)
                    messagebox.showinfo("Success!", "Profile updated successfully")
                    master.switch_frame(Page3_DashboardBuyer)
        else:
            messagebox.showinfo("Invalid entry", "Fill all the entry correctly to proceed")


class Page4_BuyerRecentlyBrought(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=3, sticky="e")

        lbl = tk.Label(self, text="Recently Brought")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=4, padx=30, pady=10)

        self.recentlybrought()

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.recentlybrought, *args))

    def recentlybrought(self):
        lbl = tk.Label(self, text="Page Under Construction!\nInconvenience NEVER Regretted")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, columnspan=4, padx=20, pady=80)
        """
        rec=Apptools.defaultqueryrun(self,"trecord")
        query="Select * from trecord where BuyerUsername=%s;"
        out=Apptools.sql_run(self,[query,(G_USERNAME.get(),)])

        if out is not None and rec:
            sep = ttk.Separator(self,orient='horizontal')
            sep.grid(row=2,column=0,columnspan=4,sticky="ews")
            frame = ScrollableFrame(self,ch=228,cw=585)
            sframe=frame.scrollable_frame
            out=out[0]
            if out!=[]:
                self.output(out,sframe)
            else:
                messagebox.showinfo( "No records found","No Items Brought Recently\nStart Shopping")

                lbl = tk.Label(sframe, text="Start Shopping")
                lbl.config(font=("Segoe UI",20), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=0, column=0,padx=220,pady=80)

            frame.grid(row=3,column=0,columnspan=4)
        """

    def output(self, out, sframe):
        column = ("Transaction Unique Id", "Transaction Id", "Date and Time", "Item name", "Quantity", "Amount Paid",
                  "Buyer Name", "Seller Organisation")

        listBox = ttk.Treeview(sframe, selectmode="extended", columns=column, show="headings")

        verscrlbar = ttk.Scrollbar(sframe, orient="vertical", command=listBox.yview)
        verscrlbar.grid(row=2, column=2, sticky="nsw")

        listBox.configure(yscrollcommand=verscrlbar.set)

        for i in range(len(column)):
            listBox.heading(column[i], text=column[i], command=lambda c=column[i]: self.sortby(listBox, c, 0))
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

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        x = True

        for a, b in data:
            x = x and Apptools.check_digit(a)
        if x:
            for i in range(len(data)):
                data[i] = list(data[i])
                data[i][0] = int(data[i][0])
        data.sort(reverse=descending)

        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))


class Page4_BuyerDeleteAccount(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerProfileManagement))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Delete Account")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

        lbl = tk.Label(self, text="Make sure you redeem all your Cashout before Account Deletion.\n"
                                  "Post Deletion Cashout redemption is not possible.")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, columnspan=3, padx=20, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkDel, *args))

    def checkDel(self, master, pin):

        ref = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)
                if bal == 0:
                    choice = messagebox.askyesno("Alert", "Are you sure want to delete your account?")
                    if choice:
                        step1 = FirebaseDB.deleteAuthData(SESSION_USER.uid)
                        if step1:
                            step2 = FirebaseDB.deleteData("Wallet", identifier="Email",
                                                          value=SESSION_USER.email)
                            if step2:
                                step3 = FirebaseDB.deleteData("BuyerUsers", key=list(ref.keys())[0])
                                if step3:
                                    messagebox.showinfo("Success", "Account Deleted Successfully")
                                    Apptools.logout(master)
                else:
                    if bal > 0:
                        msg = "You have with us the precious money in your account,proceed for a cashout request before deleting account.\nInconvenience regretted"
                        messagebox.showwarning("Money is Precious", msg)
                    else:
                        msg = "You have to settle your account,proceed for a wallet topup request (Equivalent to loan balance in wallet) from admin before deleting account.\nInconvenience regretted"
                        messagebox.showwarning("Money is Precious", msg)

            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_BuyerCheckBalance(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Check Balance")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(self, text="Check Balance")
        btn.config(command=lambda: self.Processing(pin.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.checkBal, *args))

    def checkBal(self, pin):
        ref = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        if ref:
            data = list(ref.values())[0]
            opin = data['PIN']
            if pin == opin:
                walno = data['WalletNo']
                bal = Apptools.checkBalance(walno, pin)

                sep = ttk.Separator(self, orient='horizontal')
                sep.grid(row=4, column=0, columnspan=5, sticky="ew")

                lbl = tk.Label(self, text="The Precious Money in your wallet is\n₹ " + str(bal))
                lbl.config(font=("Segoe Print", 15), fg="#E8E8E8", bg="#333333")
                lbl.grid(row=5, column=1, columnspan=3, padx=20, pady=20)
            else:
                messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")


class Page4_BuyerCashout(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Cashout Request")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(self, text="Enter Balance")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        amt = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        amt.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=20, pady=10)

        pin = tk.Entry(self, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=3, column=2)

        btn = tk.Button(self, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get(), amt.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        msg = "After generation of key write down key and amount safely\n" \
              "and show it to our nearest admin.\n" \
              "PG charges (Rs.5) is applicable."
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe Print", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=5, column=1, columnspan=3, pady=10)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.buyercashout, *args))

    def buyercashout(self, master, pin, amt):
        cond1 = amt.isdigit()
        cond2 = Apptools.in_limit(5, 10 ** 7, amt)
        if cond1 and cond2:
            ref = FirebaseDB.getdataOrderEqual("Wallet", "Email", SESSION_USER.email)
            if ref:
                data = list(ref.values())[0]
                walno = data['WalletNo']
                if str(data['PIN']) == pin:
                    bal = Apptools.checkBalance(walno, pin)
                    if bal >= int(amt):
                        key = Apptools.CashoutRequest(walno, amt, pin)
                        if key is not None:
                            messagebox.showinfo("Action Initiated",
                                                "Use the Key to get access to your wallet amount (in cash) to our nearest agent.")

                            sep = ttk.Separator(self, orient='horizontal')
                            sep.grid(row=6, column=0, columnspan=5, sticky="ew")

                            lbl = tk.Label(self,
                                           text="Status : Success\nAmount : " + amt + "\nKey : " + key + "\nNote it down(Not recoverable)")
                            lbl.config(font=("Sans Serif", 15), fg="#E8E8E8", bg="#333333")
                            lbl.grid(row=7, column=1, columnspan=3, pady=10)
                    else:
                        messagebox.showwarning("Insufficient fund",
                                               "There is insufficient money in your wallet.")
                else:
                    messagebox.showwarning("Incorrect PIN", "Try entering correct PIN")
        else:
            messagebox.showwarning("Invalid entry", "Invalid amount.\nEnter a valid amount(5~Max 1 Crore).")


class Page4_BuyerWalletRecharge(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerWallet))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Wallet Recharge Info")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=30, pady=10)

        msg = "To recharge your wallet you must go to our admin locations,\n" \
              "Admin will ask for your Email and Amount to be topup\n" \
              "PG Charges of Rs. 5 irrespective of topup amount is applicable.\n" \
              "Never share your personal details like your PIN,Password etc with admin."
        lbl = tk.Label(self, text=msg)
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=30, pady=10)


class Page4_BuyerShopping(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):

        frame = ScrollableFrame(self)

        btn = tk.Button(frame.scrollable_frame, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(frame.scrollable_frame, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(frame.scrollable_frame, text="Kans\nStart Shopping")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, pady=10, columnspan=3)

        frame.grid(row=0, column=0)

        self.show(master, frame)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.show, *args))

    def show(self, master, frame):
        Apptools.image_Show(frame.scrollable_frame, DASHBOARDImgDir, 2, 0, 700, 110, cspan=5)

        Dir = CATEGORYCARDImgDir
        r, c = 3, 1
        for i in range(len(Dir)):
            diry = os.path.join(CATEGORYCARDFOLDERNAME, Dir[i])
            try:
                Photo = Image.open(diry)
                Photo = Photo.resize((200, 200))
                render = ImageTk.PhotoImage(Photo)

            except Exception as e:
                Photo = Image.open(DEFAULTIMAGEDir)
                Photo = Photo.resize((200, 200))
                render = ImageTk.PhotoImage(Photo)
                Apptools.writeLog(e)
            imgbtnfs = tk.Button(frame.scrollable_frame, image=render)
            imgbtnfs.image = render
            imgbtnfs.grid(row=r, column=c, padx=10, pady=10)
            imgbtnfs.config(command=lambda x=i: self.framechange(master, x))

            if c == 3:
                r += 1
                c = 1
            else:
                c += 1

    def framechange(self, master, x):
        globals()['ITEMTYPE'] = x
        master.switch_frame(Page5_BuyerItemPicker)


class Page5_BuyerItemPicker(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='#333333')
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page4_BuyerShopping))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Kans\nStart Shopping")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=3, pady=10)

        self.Processing(master)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.findCat, *args))

    def findCat(self, master):
        cat = self.itemcategory(ITEMTYPE)

        lbl = tk.Label(self, text=cat.title())
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=0, pady=10, columnspan=3)

        lbl = tk.Label(self, text="Loading Items!\nPlease be patient")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=0, pady=100, padx=100, columnspan=3)

        self.search(master, cat)

        lbl.destroy()

    def search(self, master, category):
        if Apptools.is_not_null(category):
            res = Apptoolsv2.itemSearch(self, category, "Category", showWarning=False)
            out = []
            if res:
                [out.append(row) for row in res if row['Stock'] > 0]

            if out is not None:
                self.output(master, out)
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def output(self, master, out):
        sep = ttk.Separator(self, orient='horizontal')
        sep.grid(row=3, column=0, columnspan=3, sticky="ew")
        frame = ScrollableFrame(self, cw=500, ch=300)

        if out:
            r = 0
            for data in out:
                iname, orgname, idesc = data['ItemName'], data['Seller Organisation Name'], data['Description']
                icat, irp, imgDBdir = data['Category'], data['Retail Price'], data['Image Location']
                icode, iwp, istock = data['ItemCode'], data['Wholesale Price'], data['Stock']
                selluser = data["Seller Email"]

                imgdir = FirebaseDB.getDataStorage(imgDBdir, showWarning=False)
                if not imgdir:
                    imgdir = DEFAULTIMAGEDir

                txt = "Item name : " + iname.title().strip() + "\nSeller : " + orgname
                txt += "\nDescription : " + idesc.title().strip() + "\nCategory : " + icat.title()
                txt += "\nPrice : ₹" + str(irp)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    Apptools.writeLog(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((250, 150))
                    render = ImageTk.PhotoImage(Photo)

                imgbtnfs = tk.Button(frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT)
                imgbtnfs.image = render
                imgbtnfs.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT)
                imgbtnfs.config(activebackground="#3297E9", font=("Segoe Print", 15))
                imgbtnfs.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                idata = [icode, iname, iwp, irp, idesc, icat, istock, imgdir, selluser, orgname]
                imgbtnfs.config(command=lambda x=idata: self.framechange(master, x))
                r += 1

        elif FirebaseDB.connect():
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)

        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=30, pady=100)

        frame.grid(row=4, column=0, columnspan=3)

    def framechange(self, master, x):
        globals()['CHOOSEDITEMDETAILS'] = x
        master.switch_frame(Page6_BuyerProductView)

    def itemcategory(self, i):
        Category = ["Stationary", "Electronics", "Clothing", "Beauty",
                    "Softwares", "Sports", "Daily Use", "Grocery", "Health", "Others"]
        if i <= 9:
            return Category[i]


class Page4_BuyerSearchItems(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=5, sticky="e")

        lbl = tk.Label(self, text="Search Items")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, columnspan=4, padx=30, pady=10)

        lbl = tk.Label(self, text="Search Criteria")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, pady=10)

        Searchcr = ["Item Name", "Description", "Category", "Sold By"]

        SearchcrVar = StringVar(self, "Item Name")
        Menu = tk.OptionMenu(self, SearchcrVar, *Searchcr)
        Menu.config(bg="#333333", bd=0, fg="#E8E8E8", activebackground="#333333")
        Menu["menu"].config(bg="#333333", fg="#E8E8E8", activebackground="#1F8EE7")
        Menu.grid(row=2, column=2)

        lbl = tk.Label(self, text="Enter Value")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, pady=10)

        val = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        val.grid(row=3, column=2)

        btn = tk.Button(self, text="Search")
        btn.config(command=lambda: self.Processing(master, val.get(), SearchcrVar.get()))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=3, pady=10)

        btn = tk.Button(self, text="Advanced Search")
        btn.config(command=lambda: self.Processing(master, val.get(), SearchcrVar.get(), True))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=4, column=4, pady=10, padx=5)

    def Processing(self, *args):
        LoadingPage.perform(self, (self, self.search, *args))

    def search(self, master, text, criteria, deepSearch=False):
        Searchcr = ["Item Name", "Description", "Category", "Sold By"]
        dbcr = ["ItemName", "Description", "Category", "Seller Organisation Name"]

        if Apptools.is_not_null(text, criteria):
            dbeqv = [dbcr[i] for i in range(len(Searchcr)) if Searchcr[i] == criteria]
            if dbeqv:
                dbeqv = dbeqv[0]

            res = Apptoolsv2.itemSearch(self, text, dbeqv, showWarning=False, deepSearch=deepSearch)
            out = []
            if res:
                [out.append(row) for row in res if row['Stock'] > 0]

            if out is not None:
                self.output(master, out)
        else:
            messagebox.showwarning("Error", "Incomplete input!")

    def output(self, master, out):
        sep = ttk.Separator(self, orient='horizontal')
        sep.grid(row=5, column=0, columnspan=6, sticky="ew")
        frame = ScrollableFrame(self, cw=500, ch=300)

        if out:
            r = 0
            for data in out:
                iname, orgname, idesc = data['ItemName'], data['Seller Organisation Name'], data['Description']
                icat, irp, imgDBdir = data['Category'], data['Retail Price'], data['Image Location']
                icode, iwp, istock = data['ItemCode'], data['Wholesale Price'], data['Stock']
                selluser = data["Seller Email"]

                imgdir = FirebaseDB.getDataStorage(imgDBdir, showWarning=False)
                if not imgdir:
                    imgdir = DEFAULTIMAGEDir

                txt = "Item name : " + iname.title().strip() + "\nSeller : " + orgname
                txt += "\nDescription : " + idesc.title().strip() + "\nCategory : " + icat.title()
                txt += "\nPrice : ₹" + str(irp)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    Apptools.writeLog(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((250, 150))
                    render = ImageTk.PhotoImage(Photo)

                imgbtnfs = tk.Button(frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT)
                imgbtnfs.image = render
                imgbtnfs.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT)
                imgbtnfs.config(activebackground="#3297E9", font=("Segoe Print", 15))
                imgbtnfs.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                idata = [icode, iname, iwp, irp, idesc, icat, istock, imgdir, selluser, orgname]
                imgbtnfs.config(command=lambda x=idata: self.framechange(master, x))
                r += 1

        elif FirebaseDB.connect():
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)
        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=30, pady=100)

        frame.grid(row=6, column=0, columnspan=6)

    def framechange(self, master, x):
        globals()['CHOOSEDITEMDETAILS'] = x
        master.switch_frame(Page6_BuyerProductView)


class Page6_BuyerProductView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Buyer's Home", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=4, sticky="e")

        lbl = tk.Label(self, text="Kans : Your Shopping Partner")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=5, padx=30, pady=10)

        sep = ttk.Separator(self, orient='horizontal')
        sep.grid(row=2, column=0, columnspan=5, sticky="ew")

        frame = ScrollableFrame(self, cw=500, ch=300)
        sframe = frame.scrollable_frame

        itemdetails = CHOOSEDITEMDETAILS

        icode, iname, iwp, irp, idesc, icat, istock, imgdir, selluser, orgname = itemdetails

        try:
            Photo = Image.open(imgdir)
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        except Exception as e:
            Apptools.writeLog(e)

            Photo = Image.open(DEFAULTIMAGEDir)
            Photo = Photo.resize((200, 200))
            render = ImageTk.PhotoImage(Photo)

        img = tk.Label(sframe, image=render)
        img.image = render

        img.grid(row=0, column=0, rowspan=9, padx=25, pady=50, sticky="nsw")

        lbl = tk.Label(sframe, text=iname.title())
        lbl.config(font=("Segoe UI", 25), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        lbl = tk.Label(sframe, text="By " + orgname.title().strip())
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=10, sticky="w")

        lbl = tk.Label(sframe, text="M.R.P.: ₹" + str(round(irp)))
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=5, sticky="w")

        disc = Apptoolsv2.bargain(self, irp, iwp, 1, isPremium="Yes")  # To show max premium discounts
        discprice = irp - disc

        lbl = tk.Label(sframe, text="Price: ₹" + str(round(discprice, 2)) + " With Premium Account only")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=1, padx=5, sticky="w")

        lbl = tk.Label(sframe, text="You save: ₹" + str(round(disc, 2)))
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, sticky="w")

        lbl = tk.Label(sframe, text="Category : " + icat.title())
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=1, padx=5, pady=3, sticky="w")

        lbl = tk.Label(sframe, text="Description")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        lbl = tk.Label(sframe, text=idesc.title().strip())
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=1, padx=5, sticky="w")

        lbl = tk.Label(sframe, text="Contact Details")
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=0, columnspan=2, sticky="w", padx=5)

        lbl = tk.Label(sframe, text="Seller Email Address: " + selluser)
        lbl.config(font=("Segoe UI", 12), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=10, column=0, columnspan=2, sticky="w", padx=5)

        lbl = tk.Label(self, text="Enter Quantity")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=4, column=1, padx=5, pady=10)

        qty = tk.Entry(self, fg="#E8E8E8", bg="#333333")
        qty.grid(row=4, column=2)
        qty.insert(0, 1)

        btn = tk.Button(self, text="Add to Cart", command=lambda: self.Processing(icode, qty.get(), istock))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=1, pady=10)

        btn = tk.Button(self, text="Add to Wishlist", command=lambda: self.Processing(icode))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=2, padx=10)

        btn = tk.Button(self, text="Add to Cart &\nProceed to Pay",
                        command=lambda: self.Processing(master, icode, qty.get(), istock))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=5, column=3, padx=10, pady=10)

        frame.grid(row=3, column=0, columnspan=5)

    def Processing(self, *args):
        if len(args) + 1 == 5:
            LoadingPage.perform(self, (self, self.paypage, *args))
        elif len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.addtowishlist, *args))
        else:
            LoadingPage.perform(self, (self, self.addtocart, *args))

    def addtocart(self, icode, iqty, istock, showMsg=True):
        iqty = str(iqty)
        cond1 = iqty.isdigit()
        cond2 = Apptools.in_limit(1, istock, iqty)

        if cond1 and cond2:

            res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
            if res:
                key = list(res.keys())[0]
                details = {"ItemCode": icode, "Quantity": int(iqty)}
                if key:
                    res2 = FirebaseDB.getdataOrderEqual("BuyerUsers/" + key + "/Cart", "ItemCode", int(icode))
                    if res2:
                        res3 = FirebaseDB.getdataOrderEqual("Items", "ItemCode", int(icode))
                        if res3:
                            prestockuser = list(res2.values())[0]['Quantity'] if res2 else 0
                            itemstock = list(res3.values())[0]['Stock']
                            if prestockuser + int(iqty) <= itemstock:
                                data = {"Quantity": prestockuser + int(iqty)}
                                rec = FirebaseDB.updateData("BuyerUsers/" + key + "/Cart", data, identifier="ItemCode",
                                                            identifierval=int(icode))
                                if rec:
                                    if showMsg:
                                        messagebox.showinfo("Success!", "Added to Cart Successfully!")
                                    return True

                            else:
                                maxfreestock = itemstock - prestockuser
                                if maxfreestock == 0 and itemstock > 0:
                                    messagebox.showwarning("Out of Stock",
                                                           "Item is out of stock check your cart if you have pre-booked that.")
                                else:
                                    messagebox.showwarning("Invalid Input!",
                                                           "Enter Valid Input for Quantity\nMin Value=1\nMax Value=" + str(
                                                               maxfreestock))
                    elif res2 is not None:
                        rec2 = FirebaseDB.pushData("BuyerUsers/" + key + "/Cart", details)
                        if rec2:
                            if showMsg:
                                messagebox.showinfo("Success!", "Added to Cart Successfully!")
                            return True
        elif istock == 0:
            messagebox.showwarning("Out of Stock", "Item is out of stock.")
        else:
            messagebox.showwarning("Invalid Input!",
                                   "Enter Valid Input for Quantity\nMin Value=1\nMax Value=" + str(istock))

    def addtowishlist(self, icode):
        res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        res2 = None
        if res:
            key = list(res.keys())[0]
            if key:
                res2 = FirebaseDB.getdataOrderEqual("BuyerUsers/" + key + "/Wishlist", "ItemCode", int(icode))
        if not res2 and res2 is not None:
            rec = FirebaseDB.pushData("BuyerUsers/" + key + "/Wishlist", {"ItemCode": int(icode)})
            if rec:
                messagebox.showinfo("Success!", "Added to Wish List Successfully!")
        elif res2:
            messagebox.showinfo("Item Already Exist!", "Item Already Exist in your wishlist!")

    def paypage(self, master, icode, qty, istock):
        cond = self.addtocart(icode, qty, istock, showMsg=False)
        if cond:
            master.switch_frame(Page7_BuyerPaymentProceed)


class Page7_BuyerPaymentProceed(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
        self.buyerdetails = None
        self.userDBkey = None

    def makeWidgets(self, master):
        sframe = ScrollableFrame(self, cw=750, ch=500)

        btn = tk.Button(self, text="Buyer's Home", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Payment Confirmation")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=3, padx=30, pady=10)

        sep = ttk.Separator(self, orient='horizontal')
        sep.grid(row=2, column=0, sticky="ew", columnspan=3)

        lbl = tk.Label(sframe.scrollable_frame, text="Cart")
        lbl.config(font=("Segoe UI", 15), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=0, columnspan=2, padx=30, pady=10, sticky="w")

        self.Processing(master, sframe)

        sframe.grid(row=3, column=0, columnspan=3)

    def Processing(self, *args):
        if len(args) + 1 == 3:
            LoadingPage.perform(self, (self, self.initialisecart, *args))
        elif len(args) + 1 == 4:
            LoadingPage.perform(self, (self, self.deleteitemcart, *args[:-1]))
        else:
            LoadingPage.perform(self, (self, self.checktrans, *args))

    def initialisecart(self, master, sframe):

        WAITlbl = tk.Label(sframe.scrollable_frame, text="Loading Cart\nPlease be patient.....")
        WAITlbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        WAITlbl.grid(row=4, column=0, columnspan=2, padx=50, pady=20)

        sep = ttk.Separator(sframe.scrollable_frame, orient='horizontal')
        sep.grid(row=3, column=0, sticky="ew", columnspan=2)

        frame = ScrollableFrame(sframe.scrollable_frame, cw=550, ch=290)

        Item = self.retrievedata()

        totalPrice = 0
        maxNetBargain = 0
        if Item:
            r = 0
            for data in Item:
                iname, orgname, idesc = data['ItemName'], data['Seller Organisation Name'], data['Description']
                icat, irp, imgDBdir = data['Category'], data['Retail Price'], data['Image Location']
                icode, iwp, istock = data['ItemCode'], data['Wholesale Price'], data['Stock']
                selluser, iqty = data["Seller Email"], data['Quantity']

                imgdir = FirebaseDB.getDataStorage(imgDBdir, showWarning=False)
                if not imgdir:
                    imgdir = DEFAULTIMAGEDir

                txt = "Item name : " + iname.title().strip() + "\nSeller : " + orgname
                txt += "\nDescription : " + idesc.title().strip() + "\nCategory : " + icat.title()
                txt += "\nPrice : ₹" + str(irp) + "\nQuantity : " + str(iqty)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    Apptools.writeLog(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                lbl = tk.Label(frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT)
                lbl.image = render
                lbl.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT)
                lbl.config(activebackground="#3297E9", font=("Segoe Print", 15))
                lbl.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                btn = tk.Button(frame.scrollable_frame, text="Remove Item",
                                command=lambda x=icode: self.Processing(master, x, None))
                btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
                btn.grid(row=r, column=1)
                r += 1
                totalPrice += irp * iqty
                maxNetBargain += Apptoolsv2.bargain(self, irp, iwp, iqty, "Yes")

        elif FirebaseDB.connect():
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)

        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=30, pady=100)

        frame.grid(row=4, column=0, columnspan=2, sticky="nw")

        userd = self.userdata()

        netb = 0
        delnameandaddress = "\nYou\nAt Given Address"
        if userd:
            if userd['Premium Account'].lower() == 'yes':
                netb = round(maxNetBargain, 2)
                delnameandaddress = "\n" + userd["Name"] + "\n" + userd["Delivery Address"]

        lbl = tk.Label(sframe.scrollable_frame, text="Deliever to" + delnameandaddress)
        lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=3, column=2, padx=10, pady=5, rowspan=2, sticky="ns")

        lbl = tk.Label(sframe.scrollable_frame, text="Total Price : ₹" + str(round(totalPrice, 2)))
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=6, column=0, columnspan=2, padx=3, sticky="nsw")

        lbl1 = tk.Label(sframe.scrollable_frame, text="Net Bargain : ₹" + str(netb))
        lbl1.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl1.grid(row=7, column=0, columnspan=2, padx=3, sticky="nsw")

        lbl = tk.Label(sframe.scrollable_frame, text="Amount to be Paid : ₹" + str(round(totalPrice - netb + 5, 2)))
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=8, column=0, columnspan=2, padx=3, sticky="nsw")

        lbl = tk.Label(sframe.scrollable_frame, text="Inclusive of PG Charge(₹5)")
        lbl.config(font=("Segoe UI", 10), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=9, column=0, columnspan=2, padx=3, sticky="nsw")

        price = round(totalPrice - netb, 2)  # Exclusive of PG Charges
        btn = tk.Button(sframe.scrollable_frame, text="Proceed to Pay",
                        command=lambda: self.payportal(master, Item, price, sframe))
        btn.config(bg="#1F8EE7", padx=7, pady=4, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=6, column=2, rowspan=3)

        WAITlbl.destroy()

    def retrievedata(self):
        res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        if res:
            self.buyerdetails = list(res.values())[0]
            self.userDBkey = list(res.keys())[0]
            key = list(res.keys())[0]
            res2 = FirebaseDB.getdataOrder("BuyerUsers/" + key + "/Cart", ordervar="ItemCode")

            if res2:
                data = []
                val = list(res2.values())
                for d in val:
                    res3 = FirebaseDB.getdataOrderEqual("Items", "ItemCode", d['ItemCode'], showWarning=False)

                    if res3:
                        val2 = list(res3.values())[0]
                        val2.update(d)
                        data.append(val2)
                return data
            elif res2 is not None:
                return []

    def userdata(self):
        if not (self.buyerdetails and self.userDBkey):
            res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email, showWarning=False)
            if res:
                self.buyerdetails = list(res.values())[0]
                self.userDBkey = list(res.keys())[0]
        return self.buyerdetails

    def deleteitemcart(self, master, icode):
        if not self.userDBkey:
            self.userdata()
        key = self.userDBkey
        rec = FirebaseDB.deleteData("BuyerUsers/" + key + "/Cart", identifier="ItemCode", value=icode)
        if rec:
            messagebox.showinfo("Success", "Item Deleted Successfully")
            master.switch_frame(Page7_BuyerPaymentProceed)

    def payportal(self, master, out, price, sframe):
        items = []
        if out:
            for data in out:
                iname, orgname, idesc = data['ItemName'], data['Seller Organisation Name'], data['Description']
                icat, irp = data['Category'], data['Retail Price']
                icode, iwp, istock = data['ItemCode'], data['Wholesale Price'], data['Stock']
                selluser, iqty = data["Seller Email"], data['Quantity']
                if istock >= iqty:
                    items.append([icode, iname, iwp, irp, idesc, icat, istock, selluser, iqty, orgname])

                else:
                    txtmsg = "Only a Few stocks are left as item is getting out of stock."
                    txtmsg += "\nStocks available for " + iname + " is " + str(istock)
                    txtmsg += "\nCan't Buy this item. :-(\nTry Checking with fewer stocks"

                    messagebox.showwarning("Item is out of Stock", txtmsg)
            if items:
                self.paymentpage(master, price, items, sframe)

        else:
            messagebox.showwarning("Empty Cart", "Your Cart is Empty! Start Shopping Now.")

    def paymentpage(self, master, price, out, sframe):
        screen = tk.Toplevel(self, bg="#333333")
        screen.iconphoto(False, Icon)
        screen.title("Payment Portal @Kans")
        screen.resizable(0, 0)
        screen.lift()

        lbl = tk.Label(screen, text="Payment Portal")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=0, column=1, columnspan=3, padx=30, pady=10)

        lbl = tk.Label(screen, text="Total Transaction Amount : ₹" + str(price) + "+₹5 (PG Charges)")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=1, padx=20, pady=10)

        lbl = tk.Label(screen, text="Enter PIN")
        lbl.config(font=("Segoe UI", 8), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=2, column=1, padx=20, pady=10)

        pin = tk.Entry(screen, fg="#E8E8E8", bg="#333333", show="●")
        pin.grid(row=2, column=2)

        btn = tk.Button(screen, text="Proceed")
        btn.config(command=lambda: self.Processing(master, pin.get(), price, out, sframe, screen))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=3, column=3, pady=10)

    def checktrans(self, master, pin, price, out, sframe, screen):
        Buyerdetails = self.userdata()
        buyerKey = self.userDBkey
        opin = Buyerdetails['PIN']
        if pin == opin and FirebaseDB.connect():
            screen.destroy()
            Buyerwalno = Buyerdetails['WalletNo']
            BuyerbalanceInAC = round(float(Apptools.checkBalance(Buyerwalno, pin)), 2)
            Trec = False
            if BuyerbalanceInAC >= price + 5:
                txt = "Transaction Amount : " + str(
                    price + 5) + "\nIncluding PG Charges\nBalance after deduction : " + str(
                    round(BuyerbalanceInAC - (price + 5), 2)) + "\nAre you sure want to proceed?"
                choice = messagebox.askyesno("Transaction Confirmation", txt)
                if choice:
                    SUPERADMIN = self.findsuperadmin()
                    if SUPERADMIN:
                        admEmail, admwalno, admBalanceInAC = SUPERADMIN
                        rec = FirebaseDB.updateData("Wallet", {"Balance": BuyerbalanceInAC - (price + 5)})
                        if rec:
                            # tid= Apptools.generateuniquecode("trecord", "tid")
                            for i in range(len(out)):
                                icode = out[i][0]
                                irp = out[i][3]
                                iwp = out[i][2]
                                iqty = out[i][8]
                                istock = out[i][6]
                                sellerEmail = out[i][7]
                                iname = out[i][1]
                                sellerwalno, sbalanceinAC = self.walnofind("Wallet", sellerEmail)

                                ispremium = Buyerdetails["Premium Account"]
                                netbargain = Apptoolsv2.bargain(irp, iwp, iqty, ispremium)

                                bname = Buyerdetails["Name"]
                                sorg = out[i][9]

                                rec2 = FirebaseDB.updateData("Wallet", {
                                    "Balance": sbalanceinAC + round(((irp * iqty - netbargain) * 0.95), 2)},
                                                             identifierval=sellerEmail)
                                if rec2:
                                    rec3 = FirebaseDB.deleteData("BuyerUsers/" + buyerKey + "/Cart", "ItemCode", icode)
                                    if rec3:
                                        rec4 = FirebaseDB.updateData("Items", {"Stock": istock - iqty},
                                                                     identifier="ItemCode", identifierval=icode)
                                # tuid= Apptools.generateuniquecode("trecord", "tuid")
                                # tdate=self.timeformat()
                                # rec4=Apptools.insertSQL(self,"trecord", tuid, tid, tdate, iname, iqty, (irp*iqty-netbargain), bname, sorg, icode, G_USERNAME.get(), sellerEmail)

                                if rec2 and rec3 and rec4:
                                    Trec = True
                                else:
                                    messagebox.showerror("Transaction Failed!", "Ask Admin for refund")
                                    Trec = None
                                    break

                            rec5 = FirebaseDB.updateData("Wallet",
                                                         {"Balance": admBalanceInAC + 5 + round(price * 0.05, 2)},
                                                         identifierval=admEmail)
                            if rec5 is not None:
                                Trec = Trec and rec5
                            else:
                                messagebox.showerror("Transaction Failed!", "Contact Admin for details")
                                Trec = None

                            if Trec is not None:
                                messagebox.showinfo("Success!", "Transaction completed successfully!")
                                lbl = tk.Label(sframe.scrollable_frame, text="Transaction Done\nItem Delivered")
                                lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
                                lbl.grid(row=6, column=2, rowspan=3, sticky="ns")
                    elif FirebaseDB.connect():
                        messagebox.showinfo("Transaction Failed",
                                            "As there is no Admin on our system so your transaction cannot be processed.")

            elif FirebaseDB.connect():
                messagebox.showwarning("Insufficient fund",
                                       "There is insufficient fund in your wallet.\nTry Recharging Your Wallet")
        elif FirebaseDB.connect():
            messagebox.showwarning("Invalid PIN", "Invalid PIN\nTry entering correct PIN")
        else:
            messagebox.showwarning(title="Warning!",
                                   message="Failed to Connect to Server\nNo Internet Connection or Server Unreachable")

    def walnofind(self, child, email):
        res = FirebaseDB.getdataOrderEqual(child, "Email", email)
        if res:
            val = list(res.values())[0]
            return val['WalletNo'], val['Balance']

    def timeformat(self):
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date

    def findsuperadmin(self):
        result = FirebaseDB.getdataOrderEqual("Wallet", "UserType", "Admin")
        if result:
            for i in result:
                walletno = result[i]["WalletNo"]
                balance = result[i]["Balance"]
                email = result[i]['Email']
                return email, walletno, balance
                # Auto break out of loop


class Page4_BuyerWishlist(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#333333")
        self.makeWidgets(master)
        self.userDBkey = None

    def makeWidgets(self, master):
        btn = tk.Button(self, text="Go Back", command=lambda: master.switch_frame(Page3_BuyerShoppe))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=0, sticky="w")

        btn = tk.Button(self, text="Logout", command=lambda: Apptools.logout(master))
        btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
        btn.grid(row=0, column=2, sticky="e")

        lbl = tk.Label(self, text="Wishlist")
        lbl.config(font=("Segoe UI", 20), fg="#E8E8E8", bg="#333333")
        lbl.grid(row=1, column=0, columnspan=3, padx=30, pady=10)

        sep = ttk.Separator(self, orient='horizontal')
        sep.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.Processing(master)

    def Processing(self, *args):
        if len(args) + 1 == 2:
            LoadingPage.perform(self, (self, self.getData, *args))
        elif len(args) + 1 == 5:
            LoadingPage.perform(self, (self, self.cartcall, *args))
        else:
            LoadingPage.perform(self, (self, self.deletewishlist, *args))

    def getData(self, master):
        WAITlbl = tk.Label(self, text="Loading Wishlist\nPlease be patient.....")
        WAITlbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
        WAITlbl.grid(row=3, column=0, columnspan=3, padx=80, pady=70)

        frame = ScrollableFrame(self, cw=650, ch=300)

        Item = self.retrievedatafromDB()
        if Item:
            r = 0

            for data in Item:
                iname, orgname, idesc = data['ItemName'], data['Seller Organisation Name'], data['Description']
                icat, irp, imgDBdir = data['Category'], data['Retail Price'], data['Image Location']
                icode, iwp, istock = data['ItemCode'], data['Wholesale Price'], data['Stock']
                selluser = data["Seller Email"]

                imgdir = FirebaseDB.getDataStorage(imgDBdir, showWarning=False)
                if not imgdir:
                    imgdir = DEFAULTIMAGEDir

                txt = "Item name : " + iname.title().strip() + "\nSeller : " + orgname
                txt += "\nDescription : " + idesc.title().strip() + "\nCategory : " + icat.title()
                txt += "\nPrice : ₹" + str(irp)

                try:
                    Photo = Image.open(imgdir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                except Exception as e:
                    Apptools.writeLog(e)

                    Photo = Image.open(DEFAULTIMAGEDir)
                    Photo = Photo.resize((200, 200))
                    render = ImageTk.PhotoImage(Photo)

                lbl = tk.Label(frame.scrollable_frame, text=txt, image=render, compound=tk.LEFT)
                lbl.image = render
                lbl.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, justify=tk.LEFT)
                lbl.config(activebackground="#3297E9", font=("Segoe Print", 15))
                lbl.grid(row=r, column=0, padx=10, pady=10, sticky="w")

                btn = tk.Button(frame.scrollable_frame, text="Remove Item",
                                command=lambda x=icode: self.Processing(master, x))
                btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
                btn.grid(row=r, column=1, padx=3)

                btn = tk.Button(frame.scrollable_frame, text="Add to Cart",
                                command=lambda x=(icode, istock): self.addtocart(master, x[0], x[1]))
                btn.config(bg="#1F8EE7", padx=3, fg="#E8E8E8", bd=0, activebackground="#3297E9")
                btn.grid(row=r, column=2)
                r += 1

        elif FirebaseDB.connect():
            lbl = tk.Label(frame.scrollable_frame, text="No Items Found :-(")
            lbl.config(font=("Segoe Print", 30), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=100, pady=100)
        else:
            lbl = tk.Label(frame.scrollable_frame, text="No Internet Connection\nFailed to connect to Server :-(")
            lbl.config(font=("Segoe Print", 20), fg="#E8E8E8", bg="#333333")
            lbl.grid(row=0, column=2, columnspan=4, padx=30, pady=100)

        frame.grid(row=3, column=0, columnspan=3, sticky="nw")
        WAITlbl.destroy()

    def retrievedatafromDB(self):
        res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
        if res:
            self.buyerdetails = list(res.values())[0]
            self.userDBkey = list(res.keys())[0]
            key = list(res.keys())[0]
            res2 = FirebaseDB.getdataOrder("BuyerUsers/" + key + "/Wishlist", ordervar="ItemCode")
            if res2:
                data = []
                val = list(res2.values())
                for d in val:
                    res3 = FirebaseDB.getdataOrderEqual("Items", "ItemCode", d['ItemCode'], showWarning=False)

                    if res3:
                        val2 = list(res3.values())[0]
                        val2.update(d)
                        data.append(val2)
                return data
            elif res2 is not None:
                return []

    def userdata(self):
        if not self.userDBkey:
            res = FirebaseDB.getdataOrderEqual("BuyerUsers", "Email", SESSION_USER.email)
            if res:
                self.userDBkey = list(res.keys())[0]

    def deletewishlist(self, master, icode, showMsg=True):
        if not self.userDBkey:
            self.userdata()
        key = self.userDBkey
        rec = FirebaseDB.deleteData("BuyerUsers/" + key + "/Wishlist", identifier="ItemCode", value=icode)
        if rec:
            if showMsg:
                messagebox.showinfo("Success", "Item Deleted Successfully")
            master.switch_frame(Page4_BuyerWishlist)

    def addtocart(self, master, icode, istock):
        iqty = simpledialog.askinteger("Input", "Enter Quantity?", parent=self, minvalue=1, maxvalue=istock)

        if iqty is not None:
            iqty = str(iqty)
            self.Processing(master, icode, iqty, istock)

    def cartcall(self, master, icode, iqty, istock):
        Page6_BuyerProductView.addtocart(self, icode, iqty, istock)
        self.deletewishlist(master, icode, False)


# Main Program
if __name__ == "__main__":
    app = App()
    app.title("Kans:Your Shopping Partner")
    app.resizable(0, 0)
    app.update_idletasks()
    x_Left = int(app.winfo_screenwidth() / 4)
    app.geometry("+{}+{}".format(x_Left, 100))
    try:
        Icon = PhotoImage(file=LOGOImgDir)
        app.iconphoto(False, Icon)
    except Exception as e:
        Apptools.writeLog(e)
        Icon = PhotoImage(file=DEFAULTIMAGEDir)
        app.iconphoto(False, Icon)
    app.mainloop()
