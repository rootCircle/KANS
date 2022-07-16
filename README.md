# KANS
eCommerce App for buyer,seller,admin all in one under python using firebase

# Installation
User Need a Firebase Account to host data

He/She has to modify service-accounts.json file located in res directory as well as Python Code containing details of Firebase account. Instruction through comment are given in source code itself.

# Thanks
Happy Coding

# DevSpeaks
Online Marketing Software is software used to ease the daily life of consumers by decreasing the gap between consumer and buyer and increasing convenience.
KANS here implies to as KINDLE AND NEO SHOPPING. The software's main motive is to provide a simple and interactive GUI to the user especially buyers. For this Tkinter and PIL libraries are used. The software support Profile Management,Item Management for all types of user viz. Seller, Buyers.
The project has been set on a dark theme to make it look appealing to the user. This project has ample use of Frames to avoid annoying pop-up window for each page change. This project also displays Images to provide a user-friendly environment. The software uses MySQL to store data which provide the user with smooth and limitless working.
The code is required to be configured very less to run, so it provides extreme portability and minimal setup.
The source code was initially written and run in Spyder (Python 3.6). But it has been run on IDLE (Python 3.9) also.
The code was been run and debugged multiple times to make sure that it is free of all error, but it can't be claimed to be error-free.

Created on Tue Jan 12 18:17:14 2021
Released on Mon Aug 23 06:54:23 2021

Requirements:
    libraries,
    local image files,
    service-account-file

### @author: Microsoftlabs
Scrolling through mousewheel is supported for Windows,Linux only
https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar

Email must always be in lower case

____________________________________________________

## Found Bugs,Feature request(to be entertained later)

TODO : Add support for '#.$[]\' in firebase
https://stackoverflow.com/questions/19132867/adding-firebase-data-dots-and-forward-slashes

TODO : Local Session Expiry Support by threading

TODO : Login Waiting Sync -Bugs

TODO : Page4_SellerRecentTransactions,Page4_BuyerRecentlyBrought

TODO : Transaction log every cash/wallet cash transaction made through Kans->Nested Treeview https://stackoverflow.com/questions/57036493/create-tkinter-nested-treeview-from-nested-dictionary

TODO : Check for http connection instead of https to decrease false positives in network tests

TODO : Multi-threading to increase server response time and decrease waiting time(also by optimisng queries)

TODO : GIF Transaprency

TODO : Add new encoding tech to avoid key duplication in tempbank using timestamp

TODO : LoadingPage bug removal for time syncronisation

TODO : In case an item is deleted remove it from carts,wishlist for all buyers

TODO : Tiny descrption on cart,wishlist,search product page based on some standard limit and later to be replaced by "..."

TODO : On waitlist clickling on item will jump it to product view of that item

TODO : Fix high floating values of amount and other numerical values

BUG FIX : invalid command name ".!page4_buyershopping2.!scrollableframe.!canvas" while scrolling in y direction on start shopping page

TODO : Edit Quantity in Carts Page

TODO : Seller's FAQ(Discount Slab,Wallet,Premium buyers etc)

TODO : Change default folder open location to Desktop

BUG FIX : Fix Loading GIF

TODO : Decrease opeartional time in processing and fix wishlist abnormal loading time

TODO : If Resource files are missing then download it from internet. Encrypt service files and regularly change encryption keys,so no server hacks!

SECURITY FIX : Fix firebase rules.

TODO : Requires owner to verify admin sign-up(s) before allowing them. Preventing system from compromise.

______________________________________________________

## Updates 

v1.1 @05/09/2021

1) Make file directory access cross compatible with linux

2) Error handling updates

v1.2 @07/09/2021

3) Optimised Imports and Bug Fixes

v1.3 @07/11/2021

4) Silenced bug at Line number @1079 invalid command name ".!page4_buyershopping2.!scrollableframe.!canvas"

______________________________________________________

## Walkthrough video
[![KANS on Firebase](https://img.youtube.com/vi/tx7vCw3fhNg/0.jpg)](https://www.youtube.com/watch?v=tx7vCw3fhNg "KANS on Firebase")

______________________________________________________

## Visit Website here
URL : https://microsoftlabs.github.io/KANS/
