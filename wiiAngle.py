#!/usr/bin/python

# Program to encourage kids to hold a wiimote still. Wiimote is attached to their head
# so that they hold still in mock fMRI scanner for training.
#
# Home button == Exit the program
# "A" == Take current pointing vector as axis
# "+" == Enable rumble if angular tolerance is exceeded
# "-" == Disable rumble (program starts in this state)
#
# Need to have python and python cwiid library installed, on ubuntu do :
# sudo apt-get install libcwiimote-dev python-cwiid python-tk
# It is written in C and can be accessed via python (like this) or via C
# directly (yet to do that).
#
# A lot of this was taken from
# http://www.benjiegillam.com/2008/09/mythpywii-a-wiimote-interface-to-mythtv-using-python/
# which also lists a lot more buttons that can be accessed.
#
# Niles Oien nilesOien@gmail.com August 2012
#

###############################################
# Import libraries.
import cwiid
import time
import math
import sys
import os

from Tkinter import *
import datetime

subjectName=None
subjectAge=None
logFilename=None

def exitButtonCallback():
	global dataEntryRoot
	dataEntryRoot.destroy()
	quit()

def proceedButtonCallback():
	global dataEntryRoot
	global nameEntry
	global ageEntry
	global subjectName
	global subjectAge
	subjectName=nameEntry.get()
	subjectAge=ageEntry.get()
	dataEntryRoot.destroy()

def failDone():
	global fail
	fail.destroy()	
	
def tickTock():
	global connectWin
	connectWin.after(250, tickTock)
	print "tickTock"

# Make sure the "./wiiData" directory exists.
# Create it if it does not.
if (not (os.path.isdir("./wiiData"))):
	os.makedirs("./wiiData")
	
if (not (os.path.isdir("./wiiData"))):
	print "Failed to create directory ./wiiData, exiting"
	sys.exit(0)

print
print "wii data acquisition system starting"
print
print "Enter subject information into GUI window"
print

go=True
while (go) :

	dataEntryRoot = Tk()
	dataEntryRoot.wm_title('Motion tracking')

	w1 = Label(dataEntryRoot, text="Motion tracking by Niles Oien nilesOien@gmail.com")
	w1.pack()

	w2 = Label(dataEntryRoot, text="Enter subject name and age and click Proceed")
	w2.pack()

	nameEntry=Frame(dataEntryRoot)
	nameEntry.pack()
	w3 = Label(nameEntry, text="Subject ID :")
	w3.pack( side = LEFT )

	subjName = StringVar()
	nameEntry = Entry(nameEntry, textvariable=subjName)
	nameEntry.pack( side = RIGHT )

	ageEntry=Frame(dataEntryRoot)
	ageEntry.pack()

	w4 = Label(ageEntry, text="Subject age :")
	w4.pack( side = LEFT )

	subjAge = StringVar()
	ageEntry = Entry(ageEntry, textvariable=subjAge)
	ageEntry.pack( side = RIGHT )

	buttonFrame=Frame(dataEntryRoot)
	buttonFrame.pack()

	exitButton = Button(buttonFrame, text="Exit", command=exitButtonCallback)
	exitButton.pack( side = LEFT )

	proceedButton = Button(buttonFrame, text="Proceed", command=proceedButtonCallback)
	proceedButton.pack( side = RIGHT)

	dataEntryRoot.bind("<Return>", lambda event: proceedButton.invoke())

	w5 = Label(dataEntryRoot, text="After clicking Proceed, press 1 and 2 on the Wii remote")
	w5.pack()

	dataEntryRoot.mainloop()

	if ((len(subjectName) > 0) and (len(subjectAge) > 0)):
		ok=True
		try :
			age = int(subjectAge)
		except :
			ok=False

		if (ok) :
			if (age < 0):
				ok=False

		if not ok :	
			fail=Tk()
			fail.wm_title('Enter integer age')
			f1=Label(fail, text="Please enter a positive integer for age")
			f1.pack()
			failButton=Button(fail, text="OK", command=failDone)
			failButton.pack()
			fail.bind("<Return>", lambda event: failButton.invoke())
			fail.mainloop()
		else :
			nm=list(subjectName)
			for i in range(len(nm)):
				if (nm[i] == ' '):
					nm[i]='_'
			now = datetime.datetime.now()
			logFilename = "./wiiData/" + now.strftime("%Y%m%d_%H%M%S") + '_' + ''.join(nm) + '_' + str(age) + '_motion.csv'
			go=False

print subjectName + ' is of age ' + subjectAge + ', the log file name is ' + logFilename



#################################################
#
#
# Main program starts
#
#
#
###############################################

# Set global variables.

# Cal data from wiimote - set to None for now
wii_calibration = None

# Mean of X,Y,Z from wiimote
Xm=0.0
Ym=0.0
Zm=1.0


# Boolean determining if we need a header on the data file. Set to false
# once the header is written.
needFileHeader=True

# X,Y,Z to measure angle relative to (initially set to horizontal plane)
X0=0.0
Y0=0.0
Z0=1.0

# Arrays to write X,Y,Z from wiimote to.
Xa=list()
Ya=list()
Za=list()

# Number of values from wiimote to average over.
nAvg=12

# Default angular tolerance (can be overridden by command line)
angleTol = 10.0

# If we are rumbling when angular tol exceeded
rumbleMode=False

# If we are writing to the log file
logMode=False

# Structure to hold wiimote interface
wiimote=None

# Window containers that need to be global so I can get at them in callbacks
wfail=None

numRumbles=0

##################################################
#
# Function definitions

# Process wii pointing data into X,Y or Z values with calibration data.
def wii_rel(v, axis):
	return float(v - wii_calibration[0][axis]) / (
	wii_calibration[1][axis] - wii_calibration[0][axis])

# Get the average of a list and clear the list
def get_mean(a):
	retVal=float(sum(a))/float(len(a))
	del a[:]
	return retVal

# Accept the current vector as being where to measure angles from
def acceptCurrent():
	global Xm
	global Ym
	global Zm
	global X0
	global Y0
	global Z0
	X0=Xm
	Y0=Ym
	Z0=Zm

# Calculate angle relative to axis, rumble if in rumble mode
def doProc():
	global Xm
	global Ym
	global Zm
	global logMode
	global rumbleMode
	global logFilename
	global numRumbles
	global needFileHeader
	global startTime

	Xm=get_mean(Xa)
	Ym=get_mean(Ya)
	Zm=get_mean(Za)
	dot = Xm*X0 + Ym*Y0 + Zm*Z0
	modA=math.sqrt(Xm*Xm + Ym*Ym + Zm*Zm)
	modB=math.sqrt(X0*X0 + Y0*Y0 + Z0*Z0)
	cosAlpha=dot/(modA*modB)
	if (cosAlpha > 1.0) : cosAlpha=1.0
	if (cosAlpha < -1.0) : cosAlpha=-1.0
	alpha=math.acos(cosAlpha)
	alphaDeg=180.0*alpha/math.pi

	now = datetime.datetime.now()
	logStr="   Logging : OFF"
	if (logMode):
		logStr="   Logging :  ON"
	rumStr="   Rumbling : OFF"
	if (rumbleMode):
		rumStr="   Rumbling :  ON"

	print now.strftime("%H:%M:%S.%f") + "  Tolerance : " + str(angleTol) + logStr + rumStr + "  Angle : " + str(alphaDeg)

# Are we in logging mode? If so, open the output file and append to it.
# I use windows-style line terminations.
	if (logMode):
		fh=open(logFilename,"a")
		if (fh):
			dataTime=time.time()
			if (needFileHeader):
				startTime=dataTime

			elapsedTime=dataTime-startTime
			outStr=str(elapsedTime) + ", "
			outStr=outStr + str(X0) + ", " + str(Y0) + ", " + str(Z0) + ", "
			outStr=outStr + str(Xm) + ", " + str(Ym) + ", " + str(Zm) + ", "
			outStr=outStr + str(angleTol) + ", " + str(alphaDeg) + ", " + str(numRumbles) + "\r\n"
			if (needFileHeader):
				needFileHeader=False
				fh.write("timeSec, refX, refY, refZ, dataX, dataY, dataZ, angularTolDegrees, refToDataAngleDegrees, numRumbles\r\n")
			fh.write(outStr)
			fh.close()

	if (rumbleMode and (alphaDeg > angleTol)):
		Rumble()
	

def rwDestroy():
	global rw
	print "In rwDestroy()"
	rw.destroy()
	wiimote.rumble=0
	wiimote.led=0
	time.sleep(0.2)
	acceptCurrent()
	wiimote.enable(cwiid.FLAG_MESG_IFC)
	return

# Rumble the wiimote and turn leds on. Accept current angle as pointing angle.
def Rumble():
	global mainLabelString
	global numRumbles
	numRumbles = numRumbles + 1
	print
	print "RUMBLE NUMBER " + str(numRumbles) + "!"
	print
	wiimote.disable(cwiid.FLAG_MESG_IFC)
	wiimote.rumble=1
	wiimote.led=15
	time.sleep(0.5)
	wiimote.rumble=0
	wiimote.led=0
	time.sleep(0.2)
	acceptCurrent()
	mainLabelString.set("Angular tol : " + str(angleTol) + ", Rumbles : " + str(numRumbles))
	wiimote.enable(cwiid.FLAG_MESG_IFC)


def wfailDone():
	global wfail
	wfail.destroy()
	sys.exit(-1)

def wiiConnect():
	global wiimote
	global wcWin
	global wfail

	wiiOk=True
	try :
		wiimote = cwiid.Wiimote()
	except :
		print "Did not connect to wiimote"
		wiiOk=False

	wcWin.destroy()

	if not wiiOk :
		wfail=Tk()
		wfail.wm_title('Connect')
		wf1=Label(wfail, text="Failed to connect to Wii, exiting")
		wf1.pack()
		wfailButton=Button(wfail, text="OK", command=wfailDone)
		wfailButton.pack()
		wfail.mainloop()




######################################################################
#
#
# Get the angular tolerance from the command line, if specified (otherwise use default).
numArgs=len(sys.argv)
if (numArgs > 1) :
	angleTol=float(sys.argv[1])

# Tell the user what to do to get the bluetooth connection to the wiiMote started.
# You need a bluetooth device - I use a Rocketfish USB bluetooth adapter on Ubuntu.
print ""
print "Wii motion detection running with angle tolerance " + str(angleTol) + " degrees"
print ""
print "Once we are running :"
print " The A button on the wiimote will accept the current wiimote position as base"
print " The + button will activate motion detection"
print " The - button will deactivate motion detection"
print " The HOME button will exit the program"
print ""
print " Niles Oien nilesOien@gmail.com September 2012"
print ""
print 'Now place wiimote in discoverable mode by pressing 1 and 2 simultaneously...'

cs = "   Press 1 and 2 on the Wii remote   \n\n"
cs = cs + "On Wii :\n+ == enable rumbling\n"
cs = cs + "- == disable rumbling\n"
cs = cs + "Home == Done\n\n"
cs = cs + "   Press 1 and 2 on the Wii remote   \n"

wcWin=Tk()
wcwl=Label(wcWin, text=cs)
wcwl.pack()
wcWin.after(100, wiiConnect)
wcWin.wm_title("wiiMote")
wcWin.mainloop()


# Get the calibration data which will be used in the wii_rel() function
wii_calibration = wiimote.get_acc_cal(cwiid.EXT_NONE)
wiimote.enable(cwiid.FLAG_MESG_IFC)
print "Wiimote connected."

# Tell the wiimote what message types we want.
# Acceleration and buttons.
wiimote.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_BTN

def wiiGo() :
	global rumbleMode
	global toggleRumbleButton
	messages = wiimote.get_mesg()
	for mesg in messages: # Process the various message types.

		# Errors
		if mesg[0] == cwiid.MESG_ERROR:
			print "Error - did Wii disconnect?"
			bye()

		# Accelerometer data (the bulk of the data)
		if mesg[0] == cwiid.MESG_ACC:
			# Get X,Y,Z from accelerometer.
			X=wii_rel(mesg[1][cwiid.X], cwiid.X)
			Y=wii_rel(mesg[1][cwiid.Y], cwiid.Y)
			Z=wii_rel(mesg[1][cwiid.Z], cwiid.Z)
			# Add data to global arrays.
			Xa.append(X)
			Ya.append(Y)
			Za.append(Z)
			# If we have enough data in the arrays, do processing to get angle.
			if (len(Za) == nAvg):
				doProc()

		# Button press data
		if mesg[0] == cwiid.MESG_BTN:
			if mesg[1] & cwiid.BTN_HOME:
				print "Home button - exit"
				bye()
			if mesg[1] & cwiid.BTN_A:
				print "Current vector taken as base"
				acceptCurrent()
			if mesg[1] & cwiid.BTN_MINUS:
				print "Rumble deactivated"
				toggleRumbleButton["text"]="Turn rumble on"
				rumbleMode=False
			if mesg[1] & cwiid.BTN_PLUS:
				print "Rumble activated"
				rumbleMode=True
				toggleRumbleButton["text"]="Turn rumble off"

	mainGui.after(10, wiiGo)


def decAngle():
	global angleTol
	global mainLabelString
	if (angleTol > 2):
		angleTol=angleTol-1
		mainLabelString.set("Angular tol : " + str(angleTol) + ", Rumbles : " + str(numRumbles))

def incAngle():
	global angleTol
	global mainLabelString
	if (angleTol < 20):
		angleTol=angleTol+1
		mainLabelString.set("Angular tol : " + str(angleTol) + ", Rumbles : " + str(numRumbles))


def toggleRumble():
	global rumbleMode
	global toggleRumbleButton
	if (rumbleMode):
		rumbleMode=False
		toggleRumbleButton["text"]="Turn rumble on"
	else :
		acceptCurrent()
		rumbleMode=True
		toggleRumbleButton["text"]="Turn rumble off"

def toggleLog():
	global logMode
	global toggleLogButton
	if (logMode):
		logMode=False
		toggleLogButton["text"]="Turn logging on"
	else :
		logMode=True
		toggleLogButton["text"]="Turn logging off"



def bye():
	global mainGui
	mainGui.destroy()
	sys.exit(0)


mainGui=Tk()

mainLabelString=StringVar()
mainLabelString.set("Angular tol : " + str(angleTol) + ", Rumbles : " + str(numRumbles))
mainLabel=Label(mainGui, textvariable=mainLabelString)
mainLabel.pack()

fTop=Frame(mainGui)
fTop.pack()

incButton=Button(fTop, text="Increment Angle", command=incAngle)
incButton.pack(side=LEFT, anchor=W, padx=5)

toggleRumbleButton=Button(fTop, text="Turn rumble on", command=toggleRumble)
toggleRumbleButton.pack(side=LEFT, anchor=CENTER, padx=5)

acceptButton=Button(fTop, text="Accept current angle", command=acceptCurrent)
acceptButton.pack(side=LEFT, anchor=E, padx=5)

fBottom=Frame(mainGui)
fBottom.pack(side=BOTTOM, pady=5)

decButton=Button(fBottom, text="Decrement Angle", command=decAngle)
decButton.pack(side=LEFT, anchor=W, padx=5)

toggleLogButton=Button(fBottom, text="Turn logging on", command=toggleLog)
toggleLogButton.pack(side=LEFT, anchor=CENTER, padx=5)

byeButton=Button(fBottom, text="Exit", command=bye)
byeButton.pack(side=LEFT, anchor=E, padx=60)



mainGui.after(500, wiiGo)
mainGui.wm_title("Motion tracking")
mainGui.mainloop()



# If we got here, the 'go' variable was set to false to exit the loop, and we exit the program.
print "Normal termination"
sys.exit(0)

