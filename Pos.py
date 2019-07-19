import math
"""
Track position
"""
class Pos():
    def __init__(self):
        self.nsamp = 12 # number of samples in each measure

        # timeseries
        self.x = []
        self.y = []
        self.z = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.means = [None]x6

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
        """
        self.a1.append(rot[0])
        self.a2.append(rot[1])
        self.a3.append(rot[2])
        if(len(self.a1) >= self.nsamp):
            return(self.angle())
        else:
            return(None)

    def dist(self):
        """
        euclidian distance: end-point from sample mean
        clears timeseries
        """
        x1 = self.x[-1]
        y1 = self.y[-1]
        z1 = self.z[-1]
        x2 = get_mean(self.x)
        y2 = get_mean(self.y)
        z2 = get_mean(self.z)
        self.mean[0:3] = [x2, y2, z2]
        self.etrans = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        return self.etrans

    def angle(self):
        """
        angle: end-point from sample mean
        clears timeseries
        """
        X0=self.a1[-1]
        Y0=self.a2[-1]
        Z0=self.a3[-1]

        Xm=get_mean(self.a1)
        Ym=get_mean(self.a2)
        Zm=get_mean(self.a3)

        self.mean[3:6] = [Xm, Ym, Zm]

        dot = Xm*X0 + Ym*Y0 + Zm*Z0
        modA=math.sqrt(Xm*Xm + Ym*Ym + Zm*Zm)
        modB=math.sqrt(X0*X0 + Y0*Y0 + Z0*Z0)
        cosAlpha=dot/(modA*modB)

        if (cosAlpha > 1.0) : cosAlpha=1.0
        if (cosAlpha < -1.0) : cosAlpha=-1.0
        alpha=math.acos(cosAlpha)
        self.alphaDeg=180.0*alpha/math.pi
        return(self.alphaDeg)

   def current_enorm(self):
       pass 
    
   def fd(self):
       pass

def get_mean(a):
    """get mean and remove all elements"""
    retVal=float(sum(a))/float(len(a))
    del a[:]
    return retVal

