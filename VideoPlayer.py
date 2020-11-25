import os 
import vlc
import sys
import time
import pathlib
import platform
import tkinter as Tk
import tkinter.messagebox as msgbox
from tkinter            import ttk
from tkinter.filedialog import askopenfilename
from threading          import Timer, Thread, Event


class tkkTimer(Thread):
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = Event()
        self.tick     = tick
        self.iters    = 0
    
    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()
            # print('TkkTimer Start')
        
    def stop(self):
        self.stopFlag.set()
    
    def get(self):
        return self.iters


class Player(Tk.Frame):
    def __init__(self, parent, title=None):
        Tk.Frame.__init__(self, parent)
        self.parent = parent

        if title == None:
            title  = "Tk_Vlc"
            self.parent.title(title)
        
        menubar  = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        fileMenu = Tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Open", underline = 0, command=self.OnOpen)# command
        fileMenu.add_command(label="Exit", underline = 1, command=self.parent.destroy)
        menubar.add_cascade(label='File', menu=fileMenu)
        
        # Secound Panel Holds Controls
        self.Instance = vlc.Instance()
        self.player   = self.Instance.media_player_new()
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel,bg='black')
        self.canvas.pack(fill=Tk.BOTH,expand=1)
        self.videopanel.pack(fill=Tk.BOTH, expand=1)
        # Control Panels
        ctrlpanel = ttk.Frame(self.parent)
        pause     = ttk.Button(ctrlpanel, text="Pause", command=self.OnPause) # Command 
        play      = ttk.Button(ctrlpanel, text="Play", command=self.OnPlay) # Command
        stop      = ttk.Button(ctrlpanel, text="Stop", command=self.OnStop) # Wait For COmmand
        pause.pack(side=Tk.LEFT)
        play.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        self.volume_var = Tk.IntVar()
        self.volsider   = Tk.Scale(ctrlpanel, fg='red',variable=self.volume_var, from_=0, to=100, orient=Tk.HORIZONTAL, length=100, command=self.volume_sel)  # Wati For Command
        self.volsider.pack(side=Tk.LEFT,)
        ctrlpanel.pack(side=Tk.BOTTOM)
        # Control Pnael2
        ctrlpanel2     = ttk.Frame(self.parent)
        self.scale_var = Tk.DoubleVar()
        self.timeslider_last_val = "" 
        self.timeslider = Tk.Scale(ctrlpanel2, variable=self.scale_var,fg='red',from_=0,to=1000,orient=Tk.HORIZONTAL, length=500, command=self.scale_sel)
        self.timeslider.pack(side=Tk.BOTTOM, fill=Tk.X)
        self.timeslider_last_update = time.time()
        ctrlpanel2.pack(side=Tk.BOTTOM,fill=Tk.X)
        # Vlc Player Controls
        self.timer    = tkkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()

    def OnOpen(self):
        self.OnStop()
        # p = pathlib.Path(os.path.expanduser('~'))
        fullname = askopenfilename()
        if os.path.exists(fullname):
            print(fullname)
            # dirname  = os.path.dirname(fullname)
            # filename = os.path.basename(fullname)
            # Creation
            self.Media = self.Instance.media_new(fullname)
            self.player.set_media(self.Media) 
            # set The Windows id Where To render Vlc Videos
            if platform.system() == 'Windows':
                self.player.set_hwnd(self.GetHandle())
            else:
                self.player.set_xwindow(self.GetHandle())
            self.OnPlay()
            self.volsider.set(self.player.audio_get_volume())
    
    def OnPlay(self):
        if not self.player.get_media():
            self.OnOpen()
        else:
            if self.player.play() == -1:
                self.errorDialog('Unable To Play')

    def GetHandle(self):
        return self.videopanel.winfo_id()
    
    def OnPause(self):
        self.player.pause()
    
    def OnStop(self):
        self.player.stop()
    
    def OnTimer(self):
        if self.player == None:
            return
        try:
            length = self.player.get_length()
            dbl    = length * 0.001
            self.timeslider.config(to=dbl)
            tyme   = self.player.get_time()
            if tyme == -1:
                tyme = 0
            dbl = tyme * 0.001
            self.timeslider_last_val = ("%.0f"%dbl) + '.0'
            if time.time() > (self.timeslider_last_update + 2.0):
                self.timeslider.set(dbl)
            if not self.player.is_playing():
            	self.player.stop()
            	
        except:
            self.player.stop()
            os._exit(0)

    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval))

    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 200:
            volume = 200
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("FailEd To Set Volume")
    
    def OnToggleVolume(self, evt):
        is_mute = self.player.audio_get_mute()
        self.player.audio_get_mute(not is_mute)
        self.volume_var.set(self.player.audio_get_volume())

    
    def errorDialog(self, error):
        msgbox.showerror("Vlc Error",error)



if __name__ == "__main__":
    root   = Tk.Tk()
    player = Player(root,'tkinter_Vlc') 
    root.mainloop()