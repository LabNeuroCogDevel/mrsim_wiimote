from tkinter import *
class InfoDialog():
    """display window to get subject info"""
    def __init__(self):
        self.sid = None
        self.age = None
        self.dataEntryRoot = Tk()
        self.dataEntryRoot.wm_title('Motion tracking')

        w1 = Label(self.dataEntryRoot, text="Motion tracking by Niles Oien nilesOien@gmail.com")
        w1.pack()

        w2 = Label(self.dataEntryRoot, text="Enter subject name and age and click Proceed")
        w2.pack()

        nameEntry=Frame(self.dataEntryRoot)
        nameEntry.pack()
        w3 = Label(nameEntry, text="Subject ID :")
        w3.pack( side = LEFT )

        self.subjName = StringVar()
        nameEntry = Entry(nameEntry, textvariable=self.subjName)
        nameEntry.pack( side = RIGHT )

        ageEntry=Frame(self.dataEntryRoot)
        ageEntry.pack()

        w4 = Label(ageEntry, text="Subject age :")
        w4.pack( side = LEFT )

        self.subjAge = StringVar()
        ageEntry = Entry(ageEntry, textvariable=self.subjAge)
        ageEntry.pack( side = RIGHT )

        buttonFrame=Frame(self.dataEntryRoot)
        buttonFrame.pack()

        exitButton = Button(buttonFrame, text="Exit", command=lambda: exit(1))
        exitButton.pack( side = LEFT )

        proceedButton = Button(buttonFrame, text="OK", command=lambda: self.check() )
        proceedButton.pack( side = RIGHT)

        self.dataEntryRoot.bind("<Return>", lambda event: proceedButton.invoke())

        w5 = Label(self.dataEntryRoot, text="Make sure Wiimote is paired!")
        w5.pack()

    def check(self):
        """ do we have a workable age and subject id?"""
        sid = self.subjName.get()
        try:
            age=int(self.subjAge.get())
        except:
            age=None

        if len(sid) <= 0 or age is None:
            errorMsg("Please enter a positive integer for age")
            print(sid, age)
            return False
        else:
            self.sid = sid
            self.age = age
            self.dataEntryRoot.destroy()
            return True
        

    def run(self):
        """run until acceptable inputs, return sid and age"""
        self.dataEntryRoot.mainloop()
        return (self.sid, self.age)

def errorMsg(msg):
    """use Tk to display an error message"""
    fail=Tk()
    fail.wm_title(msg)
    f1=Label(fail, text=msg)
    f1.pack()
    failButton=Button(fail, text="OK", command=lambda: fail.destroy())
    failButton.pack()
    fail.bind("<Return>", lambda event: failButton.invoke())
    fail.mainloop()


if __name__ == "__main__":
    app = InfoDialog()
    (sid, age) = app.run()
    print(sid, age)
