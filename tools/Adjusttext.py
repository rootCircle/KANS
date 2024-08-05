# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 02:28:56 2021

@author: compaq
"""


def adjusttxt(txt, lim, maxlimadj=6):
    reqtxt = ""
    i = 0
    words = txt.split()
    prolist = ["" for i in range(len(words))]

    while words:
        if len(prolist[i]) > lim:
            prolist[i], pos, txt = adjustlengthycontinuedletter(
                prolist[i], lim, maxlimadj
            )
            if txt != "":
                words.insert(0, txt)

            reqtxt += prolist[i].strip() + "\n"
            i += 1
        else:
            prolist[i] += words[0] + " "
            del words[0]
    else:
        if txt:
            prolist[i], pos, txt = adjustlengthycontinuedletter(
                prolist[i], lim, maxlimadj
            )
            if txt != "":
                words.insert(0, txt)

            reqtxt += prolist[i].strip() + "\n"
    try:
        return reqtxt + adjusttxt(words[0], lim, maxlimadj)
    except:
        return ""


def adjustlengthycontinuedletter(txt, lim, maxlimadj):
    instxt = ""
    if len(txt) > lim + maxlimadj:
        temp = txt.split()
        if len(temp) > 1:
            txt = ""
            for k in range(len(temp) - 1):
                txt += temp[k] + " "
            instxt = temp[-1]
        else:
            txt = temp[0][: lim + maxlimadj] + "-"
            instxt = temp[0][lim + maxlimadj :]

    return txt, 0, instxt


txt = """sabhjdaskjsdjkj b bjlkdsms jkffjn ffjnjfjf jfdj njfdnkdjfjkn jn jkfd
df jfjd njdnj fnjnfjnfjfn onfl ndjkdodsnklsjj ksnk nsnlsnosnnkjnkj nn fiofjasksmafklmsfklmfdffffffffffffffffff"""

t = adjusttxt(txt, 8)
print(t)
