# Centrophone, Fall 2016
# Duncan MacConnell
#
# Based on Example 12 - Graphical User Interfaces
# Author: Steven Yi <stevenyi@gmail.com>
# 2013.10.28
#

from Tkinter import *
import csnd6
import os
import numpy as np
import librosa
import random

def_orc = """

sr        =         44100
kr        =         4410
ksmps     =         10
nchnls    =         1
0dbfs 	  = 		1

massign 1,1
prealloc 1,10
gacmb	init	0
garvb	init	0
gaech	init 	0


; CENTROPHONE SAMPLER
instr 1

    ktrig 	init 1				; calculate centroid
    i1 		notnum 				; get midi note number
    inotendx = i1 % 12			; keys 0 - 12, A = 0
            ; print inotendx

    ispeed = (2*floor((i1 -21) / 12) / 7 ) + 0.1
            ; print ispeed

    kcont 	init 1
    krevb 	init 0
    kecho	init 0
            midicontrolchange 15, kcont, 0, 1	; use controller 7 for speed
            midicontrolchange 14, krevb, 0, 1	; controller 8 for reverb
            ; printk2 krevb
            ; printk2 kcont

    iamp	ampmidi 1	; scale amplitude between 0 and 1


    if(inotendx==0) then
        Sfile = "./audio/{0}"
    elseif(inotendx==1) then
        Sfile = "./audio/{1}"
    elseif(inotendx==2) then
        Sfile = "./audio/{2}"
    elseif(inotendx==3) then
        Sfile = "./audio/{3}"
    elseif(inotendx==4) then
        Sfile = "./audio/{4}"
    elseif(inotendx==5) then
        Sfile = "./audio/{5}"
    elseif(inotendx==6) then
        Sfile = "./audio/{6}"
    elseif(inotendx==7) then
        Sfile = "./audio/{7}"
    elseif(inotendx==8) then
        Sfile = "./audio/{8}"
    elseif(inotendx==9) then
        Sfile = "./audio/{9}"
    elseif(inotendx==10) then
        Sfile = "./audio/{10}"
    elseif(inotendx==11) then
        Sfile = "./audio/{11}"
    else
        Sfile = "./audio/{12}"
    endif

    ichn filenchnls Sfile

    if ichn == 1 then
        awav   		diskin2 Sfile, ispeed+kcont, 0, 1, 0, 32		;mono signal
                    out iamp*awav
    else
        awav, awav2 diskin2 Sfile, ispeed+kcont, 0, 1, 0, 32		;mono signal
                    outs iamp*awav, iamp*awav2
    endif

    gacpy	= 		awav
    garvb	=		garvb+(awav*krevb)
    gaech	=		gaech+(awav*kecho)

endin

; REVERB SEND from controller 8
instr 	199
    idur    =       p3
    irvbtim	=		p4
    ihiatn	=		p5
    arvb	nreverb	garvb, irvbtim, ihiatn
            outs	arvb, arvb
    garvb	=		0
endin
"""

the_order = ["1.aif","2.aif","3.aif","4.aiff","5.wav","6.wav","7.aiff","8.aiff","9.wav","10.wav","11.wav","12.wav","12.wav"]
orc = def_orc.format(*the_order)

# create an instance of Csound, set options, compile orchestra, start csound
c = csnd6.Csound()
c.SetOption("-odac")
c.SetOption("-+rtmidi=portmidi")
c.SetOption("-Ma")
c.CompileOrc(orc)
c.Start()
perfThread = csnd6.CsoundPerformanceThread(c)
perfThread.Play()


def start_csound(new_orc):
    print "Restarting CSound"
    print new_orc
    c.CompileOrc(new_orc)                               # Compile Orchestra from String
    c.Start()                                           # When compiling from strings, this call is
                                                        # necessary before doing any performing
    perfThread.InputMessage("i 199 0 3600 5.6 .8");     # reverb instrument keeps score going

def determine_centroid(directory):
    cent = []
    filtered_files = []

    # filter out config files
    files = os.listdir(directory)
    for f in files:
        if not f.startswith('.'):
            filtered_files.append(f)

    # randomly pick 13 samples
    filtered_files = random.sample(files, 13)
    print "selected files:", filtered_files

    for f in filtered_files:
            thisfile = os.getcwd() + "/audio/" + f
            # determine the spectral centroid
            y, sr = librosa.load(thisfile)
            cents = librosa.feature.spectral_centroid(y=y, sr=sr, S=None, n_fft=32768, hop_length=16384, freq=None)
            cent.append([f, np.sum(cents)])
            print "Analyzing " + f + " ..." + str(np.sum(cents))
    return cent

def format_orc(the_files):

    the_files = sorted(the_files, key=get_key)
    file_order = []
    for eachFile in the_files:
        file_order.append(eachFile[0])
        print eachFile[0]
    print file_order
    orc = def_orc.format(*file_order)
    return orc


def get_key(item):
    return item[1]


class Centrophone(Frame):

    def __init__(self,master=None):
        master.title("Csound API GUI Example")
        self.items = []
        self.notes = []
        Frame.__init__(self,master)

        dc = determine_centroid("audio")
        fc = format_orc(dc)
        # print fc          # to see generated orchestra
        self.pack()
        start_csound(fc)

        self.master.protocol("WM_DELETE_WINDOW", self.quit)

    def create_ui(self):
        self.size = 600
        self.canvas = Canvas(self,height=self.size,width=self.size)
        self.canvas.pack()
        # self.button = Button(self.canvas, text='Play Note', command=self.playNote)
        # self.button.pack()

    def quit(self):
        self.master.destroy()
        perfThread.Stop()
        perfThread.Join()


app = Centrophone(Tk())
app.mainloop()

