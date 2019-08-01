import math
import datetime
import os.path
"""
Track position
"""
class Pos():
    def __init__(self, max_dot):
        self.nsamp = 12 # number of samples in each measure
        self.max_dot = max_dot # max angle dot product, othewrise inc n_over

        # timeseries
        self.x = []
        self.y = []
        self.z = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.rel_rot = [0] * 3
        self.rel_trans = [0] * 3
        self.means = [None] * 6
        self.n_over = 0

        # alos used to determine if logging has started
        self.log_handle = None
        # track so we can spit it out at the end
        self.logFilename = None

    def reset(self):
        self.rel_rot   = [0]*3
        self.rel_trans = [0]*3

    def add_trans(self, trans):
        """
        add trans values (motion event)
        """
        self.x.append(trans[0])
        self.y.append(trans[1])
        self.z.append(trans[2])
        if(len(self.x) >= self.nsamp):
            return(self.dist())
        else:
            return(None)

    def add_rot(self, rot):
        """
        add rotation values (accel event)
        return magnitude and sign if have enough samples
        sideffect: eventaul get_mean() clears self.a{1,2,3}
        """
        self.a1.append(rot[0])
        self.a2.append(rot[1])
        self.a3.append(rot[2])
        if(len(self.a1) >= self.nsamp):
            return self.angle()
        else:
            return None

    def dist(self):
        """
        euclidian distance: end-point from sample mean
        clears timeseries
        """
        X0 = self.x[-1]
        Y0 = self.y[-1]
        Z0 = self.z[-1]
        # mean and clear
        Xm = get_mean(self.x)
        Ym = get_mean(self.y)
        Zm = get_mean(self.z)


        # update postion used for (used for gl display)
        self.rel_trans[0] += Xm - X0 
        self.rel_trans[1] += Ym - Y0 
        self.rel_trans[2] += Zm - Z0 

        # for logging
        self.means[0:3] = [Xm, Ym, Ym]
        self.nots[0:3] = [X0, Y0, Z0]

        self.etrans = math.sqrt((Xm-X0)**2 + (Ym-Y0)**2 + (Zm-Z0)**2)
        return self.etrans

    def angle(self):
        """
        angle: end-point from sample mean
        side effects:
          * clears timeseries via get_mean
          * write to log if start_log has been called
          * check max_dot and inc n_over
        """
        X0=self.a1[-1]
        Y0=self.a2[-1]
        Z0=self.a3[-1]

        Xm=get_mean(self.a1)
        Ym=get_mean(self.a2)
        Zm=get_mean(self.a3)

        self.means[3:6] = [Xm, Ym, Zm]
        self.nots[3:6] = [X0, Y0, Z0]

        # update relative rotation (used for gl display)
        self.rel_rot[0] += Xm - X0 
        self.rel_rot[1] += Ym - Y0 
        self.rel_rot[2] += Zm - Z0 

        dot = Xm*X0 + Ym*Y0 + Zm*Z0
        modA=math.sqrt(Xm*Xm + Ym*Ym + Zm*Zm)
        modB=math.sqrt(X0*X0 + Y0*Y0 + Z0*Z0)
        div=modA*modB
        if div == 0:
            div = .00001
        cosAlpha=dot/div

        if (cosAlpha > 1.0) : cosAlpha=1.0
        if (cosAlpha < -1.0) : cosAlpha=-1.0
        alpha=math.acos(cosAlpha)
        self.alphaDeg=180.0*alpha/math.pi

        if self.alphaDeg > self.max_dot:
            self.n_over += 1

        # run log here
        if self.log_handle:
            log_handle.write(pos.log_str())

        return self.alphaDeg
    
    def log_str(printheader=False):
        """ what to log
        header an option here so changes are easy to track
        N.B. b/c trans and deg are collected independently,
             the [XYZ]t[0m] [XYZ]r[0m] iteams in each row might not be in sync
        file likely written on rotation record
        """
        if header:
            out = "time, alpha, n_over, Xtm, Ytm, Ztm, Xrm, Yrm, Zrm, Xt0, Yt0, Zt0, Xr0, Yr0, Zr0"
            return out
        now = datetime.datetime.now().strftime("%s")
        data = [now, self.alphaDeg, self.n_over] + self.means + self.nots
        out = ", ".join([str(x) for x in data])
        return out


    def start_log(self):
        """
        define log_handler to start logging
        """
        start = datetime.datetime.now()
        name = "_".join(start.strftime("%Y%m%d_%H%M%S"),
                        sid.replace('[^A-Za-z0-9]','-'),
                        age)
        self.logFilename = "./wiiData/%s_motion.csv" % name
        writeheader = not os.path.exists(self.logFilename)
        print('starting log @ ', self.logFilename)
        self.log_handle=open(self.logFilename,"a")
        if writeheader:
            self.log_handle.write(log_str(printheader=True))
     
    def current_enorm(self):
        pass 

    def fd(self):
       pass

def get_mean(a):
    """get mean and remove all elements"""
    retVal=float(sum(a))/float(len(a))
    del a[:]
    return retVal

