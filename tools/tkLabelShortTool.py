# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 17:20:24 2021

@author: compaq
"""
x='0'
while x!='end' and x!='':
    x=input("Enter label:\n")

    a=x.find("tk.Label(")+len("tk.Label(")
    b=min(x.find(",",a), x.find(")",a))

    frame=x[a:b]

    a=x.find("text=")+len("text=")
    b=min(x.find(",",a),x.find(")",a))

    text=x[a:b].replace('"','')

    a=x.find("font=(")+len("font=(")
    b=x.find(")",a)

    font=x[a:b]
    fsize=font[font.find(",")+1:]
    fname=font[:font.find(",")].replace('"','')

    a=x.find("row=")+len("row=")
    b=min(x.find(",",a), x.find(")",a))
    ro=x[a:b]

    a=x.find("column=")+len("column=")
    b=min(x.find(",",a), x.find(")",a))
    col=x[a:b]

    if x.find("padx=")>=0:
        a=x.find("padx=")+len("padx=")
        b=min(x.find(",",a), x.find(")",a))
        px=x[a:b]
    else:
        px='0'

    if x.find("pady=")>=0:
        a=x.find("pady=")+len("pady=")
        b=min(x.find(",",a), x.find(")",a))
        py=x[a:b]
    else:
        py='0'

    if x.find("columnspan=")>=0:
        a=x.find("columnspan=")+len("columnspan=")
        b=min(x.find(",",a), x.find(")",a))
        cs=x[a:b]
    else:
        cs='1'

    if x.find("rowspan=")>=0:
        a=x.find("rowspan=")+len("rowspan=")
        b=min(x.find(",",a), x.find(")",a))
        rs=x[a:b]
    else:
        rs='1'


    comm="Apptools.tkLabel({0},'{1}',{2},{3},{4},'{5}',{6},{7},rs={8},cs={9})".format(frame,text,ro,col,fsize,fname,px,py,rs,cs)
    print(comm)