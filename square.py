import numpy as np
from numpy import square

class Leastsq:
    def __init__(self,xlist,ylist,var=0.01):
        self.xlist=xlist
        self.ylist=ylist
        self.delta_var=var
        self.n=1
    
    def setDeltaVar(self,var):
        self.delta_var=var
        

    def resolveLeastsq(self,n):
        m=len(self.xlist)
        x_square_list=[m+1]
        for i in range(0,2*n):
            sum_n=0
            x_n=i+1
            for x in self.xlist:
                sum_n+=x**x_n
            x_square_list.append(sum_n)
        #print x_square_list
        a_list=[]
        #split square to form a
        for i in range(0,n+1):
            split=x_square_list[i:(i+n+1)]
            a_list.append(split)
        a=np.array(a_list)
        b_list=[]
        for i in range(0,n+1):
            sum_xy=0
            for j in range(0,m):
                sum_xy+=self.xlist[j]**i*self.ylist[j]
            b_list.append(sum_xy)
        #print b_list
        b=np.array(b_list)
        p=np.linalg.solve(a, b)
        #print 'P2:', p
        return p
    
    def Leastsq(self,p,x):
        n=len(p)
        x_list=[]
        for i in range(0,n):
            x_n=x**i
            x_list.append(x_n)
        x_array=np.array(x_list)
        #print x_array
        y=x_array.dot(p)
        return y
    
    def LeastsqPredict(self,n,x):
        return  self.Leastsq(self.resolveLeastsq(n), x)
    
    def squareVar(self,n):
        y_Leastsq=[]
        for j in range(0,len(self.xlist)):
            y=self.LeastsqPredict(n, self.xlist[j])
            y_Leastsq.append(round(y,2))
        square_sum=0
        print y_Leastsq
        for i in range(0,len(self.xlist)):
            #print y_Leastsq[i],self.ylist[i]
            square_sum+=(y_Leastsq[i]-self.ylist[i])**2
        return square_sum
    
    def getOptimizeN(self):
        n=1
        square_sum0=10**10
        """
        
        print 'n:',n
        print '0:%s,1%s' % (square_sum0,square_sum1)
        """
        while True: # and square_sum0>square_sum1:
            square_sum1=self.squareVar(n)
            delta=abs(square_sum0-square_sum1)
            print 'n:',n
            print '0:%s,1%s' % (square_sum0,square_sum1)
            if delta<0.01:
                break
            square_sum0=square_sum1
            n+=1
            
    
        self.n=n
        return n
    
    def getNextPredict(self):
        n=self.n
        next_x=len(self.xlist)+1
        next_y=self.LeastsqPredict(n, next_x)
        return next_y

def test():
    #xlist=[1,2,3,4,5,6,7,8,9,10]
    #ylist=[8.10,8.63,8.52,8.62,8.39,8.39,8.30,8.34,8.49,8.46]
    ylist=[19434.27, 23742.1, 14847.23, 16600.12, 18202.63, 35925.95, 19939.21, 8370.59, 18680.25, 13541.48, 14636.29, 13748.87, 9562.08, 13986.38, 8604.73, 18162.43, 14143.54, 24275.75, 20525.22, 21822.84, 30919.35, 33744.51, 55045.94, 25894.2, 42896.96, 46771.34, 30587.45, 18053.81, 41796.5, 41019.47, 50870.09, 29796.87, 80051.99, 54867.51, 101183.75, 53081.94, 40806.93, 52807.5, 58459.54, 55078.86, 31217.31, 39876.87, 53659.65, 28753.01, 42426.06, 43935.92, 124358.08, 76730.36]
    ylist=[57.32, 57.53, 56.69, 55.53, 55.28, 54.42, 53.7, 54.99, 54.67, 54.63, 54.84, 54.39, 53.69, 53.5, 51.98, 51.35, 50.07, 50.48, 50.36, 50.55, 51.6, 52.2, 51.59, 51.14, 51.69, 51.3, 51.41, 51.07, 48.9, 47.99]
    last=ylist.pop()
    xlist=[]
    for i in range(0,len(ylist)):
        xlist.append(i+1)
    
    #xlist=[0.02,0.02,0.06,0.06,0.11,0.11,0.22,0.22,0.56,0.56,1.10,1.10]
    #ylist=[76,47,97,107,123,139,159,152,191,201,207,200]
    #resolveLeastsq(xlist, ylist,3)
    minisq=Leastsq(xlist,ylist,0.01)
    minisq.getOptimizeN()
    #y=minisq.getNextPredict()
    print minisq.n
    minisq.squareVar(minisq.n)
    y=minisq.LeastsqPredict(1,11)
    print y
test()
