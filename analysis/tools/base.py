import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# import astropy.stats as astro
from scipy.stats import norm
from scipy.fftpack import fft, rfft
# from pyfftw.interfaces.scipy_fftpack import fft
from scipy.signal import blackman,gaussian,tukey




# #################################
# # Constants
# #################################
# N=100000
# INPUT_FREQ = 160*10**6
# # INPUT_FREQ = 40*10**6
# # INPUT_FREQ = 640*10**6
# FREQ = (1.0*N)/(N+1)*INPUT_FREQ


# MEASURE_FREQ = FREQ
# MEASURE_PERIOD = 1.*10**9/MEASURE_FREQ# ns

# PERIOD =  1.0*10**9/FREQ # ns

# BEAT_FREQ = 1.*INPUT_FREQ/(N+1)
# BEAT_PERIOD = 1./BEAT_FREQ


# MULT_FACT = MEASURE_PERIOD*10**(-9)/(N+1)*10**9
# #################################
# # END of Constants
# #################################





def getData(dataFile1,skip=False):
    OUT1 = []
    values1 = []
    data_file = open(dataFile1)
    j = 0
    for lines in data_file:
        if(str(lines) == "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"):
            OUT1.append(np.array(values1))
            values1 = []
        else:
            if(j>=1):
                val1 = int(lines.split(",")[0])
                values1.append(val1)
            j=j+1
    return OUT1

    #make square wave with edges
def deltaEdge(cycles):
    out = []
    for edges in cycles:
        edges = np.array(edges)
        pre_edges = np.insert(edges,0,0)[:-1]
        diff = edges - pre_edges
        out.append(np.array(diff))
    return np.concatenate(out)


def clean640(cycles):
    threshold = 500000
    out = []
    for edges in cycles:
        edges = np.array(edges)
        pre_edges = np.insert(edges,0,0)[:-1]
        diff = edges - pre_edges
        dels = np.where(np.abs(diff) > threshold)
        edges = np.delete(edges,dels)
        out.append(np.array(edges))
    return out

def edgeCleanEdged(parity,edges): #Cleans up the edges and identifies whether it is a rising or falling edge
    N=2000 # number of cycle difference in metastability
    # N=5500 # number of cycle difference in metastability
    # N=15000 # number of cycle difference in metastability continuous

    look_ahead=10000 # number of counter entries to look ahead
    edges = np.array(edges)
    out = []
    out_parity = []
    i=1
    while (i<edges.size):
            meta = []
            meta.append(edges[i])

            ignore = 0

            for look in range(1,look_ahead):
                ignore = look -1
                if i+look >= edges.size:
                    break
                elif edges[i+look]-edges[i] > N:
                    break
                else:
                    meta.append(edges[i+look])
            

            i=i+1+ignore
            if (i < edges.size):
                out_parity.append(int(parity[i-1]-parity[i])) # 1 if pos edge,   -1 if neg edge
                # print(parity[i],edges[i],parity[i-1],edges[i-1]) 
                # print(i,i-1)
                # print(meta)
                out.append(np.average((np.min(meta),np.max(meta)))) #Average of last and first state
                # out.append(np.average(meta)) #Average of Metastability
                # out.append(np.min(meta)) #first state
                # out.append(np.max(meta)) #last state
            else: #removes the last edge
                break

            
    return np.array(out_parity),np.array(out)


def edgeClean(edges): #We are using averages
    # N=1000 # number of cycle difference in metastability
    N=5500 # number of cycle difference in metastability
    # N=15000 # number of cycle difference in metastability continuous

    look_ahead=1000 # number of counter entries to look ahead
    edges = np.array(edges)
    out = []
    i=0
    while (i<edges.size):
            meta = []
            meta.append(edges[i])
            ignore = 0
            for look in range(1,look_ahead):
                ignore = look -1
                if i+look >= edges.size:
                    break
                elif edges[i+look]-edges[i] > N:
                    break
                else:
                    meta.append(edges[i+look])
            i=i+1+ignore
            # out.append(np.average(meta)) #Average of Metastability
            out.append(np.average((np.min(meta),np.max(meta)))) #Average of last and first state
            # out.append(np.min(meta)) #first state
            # out.append(np.max(meta)) #last state
    return np.array(out)


def MetaRemove(values1,values2):
    out1,out2 = [],[]
    if len(values1) == len(values2):
        for i in range(0,len(values1)):
            val1 = edgeClean(values1[i])
            val2 = edgeClean(values2[i])
            if val1.size > val2.size:
                val1 = val1[:val2.size]
            else:
                val2 = val2[:val1.size]
            out1.append(np.array(val1))
            out2.append(np.array(val2))
        return np.array(out1),np.array(out2)
            
    else:
        print("input arrays have different sizes")


def MetaRemoveCont(values1,values2):
    val1 = edgeClean(values1)
    val2 = edgeClean(values2)
    if val1.size > val2.size:
        val1 = val1[:val2.size]
    else:
        val2 = val2[:val1.size]
    return val1,val2




def SeparatePosNeg(data1,data2):
    OUT1,OUT2 = np.array([]),np.array([])
    VAL1_EVN,VAL2_EVN,VAL1_ODD,VAL2_ODD = np.array([]),np.array([]),np.array([]),np.array([])
    for i in range(0,len(data1)):
        IGNORE = 10000000000000     
        out1,out2 = [],[]
        val1_evn,val2_evn,val1_odd,val2_odd = [],[],[],[]
        for k in range(0,data1[i].size):
            if np.abs(np.average(data1[i][k]-data2[i][k])) > IGNORE:
                continue
            if k%2 == 0:
                out1.append(data1[i][k]-data2[i][k])
                val1_evn.append(data1[i][k])
                val2_evn.append(data2[i][k])

            else:
                out2.append(data1[i][k]-data2[i][k])
                val1_odd.append(data1[i][k])
                val2_odd.append(data2[i][k])

        out1,out2 = np.array(out1),np.array(out2)
        if OUT1.size == 0:
            OUT1 = np.concatenate((OUT1,out1))
            OUT2 = np.concatenate((OUT2,out2))
            VAL1_EVN = np.concatenate((VAL1_EVN,val1_evn))
            VAL1_ODD = np.concatenate((VAL1_ODD,val1_odd))
            VAL2_EVN = np.concatenate((VAL2_EVN,val2_evn))
            VAL2_ODD = np.concatenate((VAL2_ODD,val2_odd))
        else:
            # if np.abs(OUT1[-1] - out1[0]) < np.abs(OUT1[-1] - out2[0]):
            if np.abs(np.average(OUT1) - np.average(out1)) < np.abs(np.average(OUT1) - np.average(out2)):
                OUT1 = np.concatenate((OUT1,out1))
                OUT2 = np.concatenate((OUT2,out2))
                VAL1_EVN = np.concatenate((VAL1_EVN,val1_evn))
                VAL1_ODD = np.concatenate((VAL1_ODD,val1_odd))
                VAL2_EVN = np.concatenate((VAL2_EVN,val2_evn))
                VAL2_ODD = np.concatenate((VAL2_ODD,val2_odd))
            else:
                OUT1 = np.concatenate((OUT1,out2))
                OUT2 = np.concatenate((OUT2,out1))
                VAL1_EVN = np.concatenate((VAL1_EVN,val1_odd))
                VAL1_ODD = np.concatenate((VAL1_ODD,val1_evn))
                VAL2_EVN = np.concatenate((VAL2_EVN,val2_odd))
                VAL2_ODD = np.concatenate((VAL2_ODD,val2_evn))
        # print np.average(out1),np.average(out2)
        # print np.average(OUT1),np.average(OUT2)
    return  OUT1,OUT2,(VAL1_EVN,VAL1_ODD,VAL2_EVN,VAL2_ODD)




def SeparatePosNegCont(data1,data2):
    OUT1,OUT2 = np.array([]),np.array([])
    VAL1_EVN,VAL2_EVN,VAL1_ODD,VAL2_ODD = np.array([]),np.array([]),np.array([]),np.array([])
    IGNORE = 1000000000     
    out1,out2 = [],[]
    val1_evn,val2_evn,val1_odd,val2_odd = [],[],[],[]
    for k in range(0,data1.size):
        if np.abs(np.average(data1[k]-data2[k])) > IGNORE:
            continue
        if k%2 == 0:
            out1.append(data1[k]-data2[k])
            val1_evn.append(data1[k])
            val2_evn.append(data2[k])

        else:
            out2.append(data1[k]-data2[k])
            val1_odd.append(data1[k])
            val2_odd.append(data2[k])

    out1,out2 = np.array(out1),np.array(out2)
    if OUT1.size == 0:
        OUT1 = np.concatenate((OUT1,out1))
        OUT2 = np.concatenate((OUT2,out2))
        VAL1_EVN = np.concatenate((VAL1_EVN,val1_evn))
        VAL1_ODD = np.concatenate((VAL1_ODD,val1_odd))
        VAL2_EVN = np.concatenate((VAL2_EVN,val2_evn))
        VAL2_ODD = np.concatenate((VAL2_ODD,val2_odd))
    else:
        # if np.abs(OUT1[-1] - out1[0]) < np.abs(OUT1[-1] - out2[0]):
        if np.abs(np.average(OUT1) - np.average(out1)) < np.abs(np.average(OUT1) - np.average(out2)):
            OUT1 = np.concatenate((OUT1,out1))
            OUT2 = np.concatenate((OUT2,out2))
            VAL1_EVN = np.concatenate((VAL1_EVN,val1_evn))
            VAL1_ODD = np.concatenate((VAL1_ODD,val1_odd))
            VAL2_EVN = np.concatenate((VAL2_EVN,val2_evn))
            VAL2_ODD = np.concatenate((VAL2_ODD,val2_odd))
        else:
            OUT1 = np.concatenate((OUT1,out2))
            OUT2 = np.concatenate((OUT2,out1))
            VAL1_EVN = np.concatenate((VAL1_EVN,val1_odd))
            VAL1_ODD = np.concatenate((VAL1_ODD,val1_evn))
            VAL2_EVN = np.concatenate((VAL2_EVN,val2_odd))
            VAL2_ODD = np.concatenate((VAL2_ODD,val2_evn))
        # print np.average(out1),np.average(out2)
        # print np.average(OUT1),np.average(OUT2)
    return  OUT1,OUT2,(VAL1_EVN,VAL1_ODD,VAL2_EVN,VAL2_ODD)
        


def applyFormatting(ax,fig,NN=100000):
    ##Formatting
    ax.text(.01, 1.07, r"$\bf{DDMTD}$ Preliminary",
        #  transform=fig.transFigure,
         transform=ax.transAxes,
         fontsize=18,
         verticalalignment='top',
         multialignment='center',
         # bbox=props,
         # zorder=15,
         label="cms")

    textDisp = "N="+str(NN)
    ax.grid()
    ax.minorticks_on()
    # ax.tick_params(axis='both', left='True', top='False', right='True',
    #                 bottom='True', labelleft='True', labeltop='False',
    #                 labelright='False', labelbottom='True')
    _ = ax.text(
        
    #   0.73, .93,
      .81, 1.07,
      textDisp,
    #   transform=fig.transFigure,
      transform=ax.transAxes,
      fontsize=14,
      verticalalignment='top',
      multialignment='center',
      # bbox=props,
      # zorder=15,
      label="lumi")


def drawTIE(TIE1,save_name="",bns=100,cutoff=0,MULT_FACT=1,fit=False,figName="",draw=False):

    if bns.size > 10000:
        print ("bin size to  high, aborting")
        return 0,0
        
    N = TIE1.size
    Y,bins=np.histogram(TIE1*MULT_FACT,bins=bns)

    bin_mid = (bins+(bins[1]-bins[0])/2)[:-1]
    bns2Consider = np.where(Y > 1)
    average_TIE  = np.average(bin_mid[bns2Consider])

    try:
        popt, pcov = curve_fit(gauss_function, bin_mid[bns2Consider], Y[bns2Consider],p0=[1,average_TIE,.001])
    except:
        print("Not able to fit")
        fit = False


    if (fit==False):
        pass
    else:
        print(draw)
        if (draw):
            
            fig,ax = plt.subplots(figsize=(8,6))
            _=ax.hist(TIE1*MULT_FACT,bins=bns)
            plt.plot(np.linspace(bins[0],bins[-1],100), gauss_function(np.linspace(bins[0],bins[-1],100), *popt),
                    label=' fit '
                    ,linestyle='dashed',linewidth=5)

            textstr = f'$\sigma$ =   {np.abs(round(popt[2]*10**3,3))} ps'
            textstr += f'\n$\mu$ =  {round(popt[1]*10**3,3)} ps'
            textstr += f'\n N = {N} '


            props = dict(boxstyle='round', facecolor='white', alpha=0.9)
            ax.text(0.1, 0.95,textstr,
                    transform=ax.transAxes,
                    fontsize=10,
                    verticalalignment='top',
                    multialignment='left',
                    bbox=props,
                    label="Cuts")
            ax.legend(loc="upper right")
            applyFormatting(ax,fig)

            ax.set_xlabel("TIE (ns)")
            ax.set_ylabel("Events")
            plt.savefig(save_name)
    return popt,pcov





# def gauss_function(x, x0, sigma):
def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

    # return a*np.exp(-((x-x0)/sigma)**2 /2)
    # return 1/(sigma*np.sqrt(2*np.pi))*np.exp((-((x-x0)/(sigma))**2)/2)


def sine(x,A,f,phi,D):
    return A*np.sin(2*np.pi*f*x+phi)+D


    
# Simple test to see if values were skipped!
def quickTest(val1):
    test = (val1 -np.insert(val1,0,0)[:-1])[1:]
    if (np.where((test >51000)|(test < 48000))[0].size == 0): print ("Awesome, this works")
    print (f"Max: {np.max(test)}\nMin: {np.min(test)}")
    # return test

    



#Quick Fourier Transform
def FFT(x,y,ylim=(0,1),xlim=(0,1600),save_name=None,MEASURE_PERIOD=1,MULT_FACT=1,NN=100000,disp=0):



    if (x.size <= 1000 or y.size <= 1000):
        print ("Arrays are very small; discontinuing FFT ")
        return 0,0
    

    
    #low_freq_thres = 50 #Depends on lowest frequency you want to see; the lower you go, high processing time
    #numOfItems = 10 # check cleanFFTdata Method IV
    #thres_sec = numOfItems/low_freq_thres  #seconds  
    #thres =  int(thres_sec / ((x[1]-x[0])* MEASURE_PERIOD*10**-9))
    ## print(thres)

    #Select Window of the injected noise faster...
    # N1 = cleanFFTdata(x[:thres],y[:thres],NN)
    # N2 = cleanFFTdata(x[-thres:],y[-thres:],NN)
    # N = (N1[0],x.size - N2[1])
    # print(N)

    #Select Window over the entire length...
    # N = cleanFFTdata(x,y,NN)
    N = (0,-1)

    # return N 




    
    
    



    # return N

    
    x = x[N[0]:N[1]]*MEASURE_PERIOD*10**(-9)
    y = y[N[0]:N[1]]*MULT_FACT*10**3    #*(gauss_function(X,20,0,.1)*np.sin(2*np.pi*50*X)+0.5*np.sin(2*np.pi*100*X))
    # x=  x*MEASURE_PERIOD*10**(-9)
    # y = y*MULT_FACT*10**3 


   


    N = x.size
    # freq_low = x[-1]
    # print(f"Time Window \t:: {freq_low} s")
    # print(f"freq low lime \t:: {1/x[-1]} Hz")
    T = abs(x[1]-x[2])
    # print (f"No: of data points {N}, \nInterval \t:: {T} s")
    yf = fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    fig,ax = plt.subplots(figsize=(8,6))
    applyFormatting(ax,fig,NN)
    Y =  2.0/N * np.abs(yf[0:N//2])
    X = xf
    ax.plot(X, Y,color="red")
    ax.set_xlabel("Freq(Hz)")
    ax.set_ylim(ylim[0],ylim[1])
    ax.set_xlim(xlim[0],xlim[1])

    
    ax.set_ylabel("Time(ps)")
    
    if save_name!=None:
        plt.savefig(save_name)


    ymax,ypos  =np.max(Y[10:-10]), np.where(Y == np.max(Y[10:-10]))[0]
    xmax = X[ypos]
    print(f" The peak: {ymax},{xmax}")
    if disp==0:
        plt.close()
    return ymax,xmax[0]
                


def cleanFFTdata(X,Y,NN): # run this only on 

    # #Method I
    # center = np.average(Y)
    # # print(center)
    # #find begining
    # lookAhead = int(50 *100000/NN) # Works > 50Hz
    # tune = int(5 *100000/NN) 


    # i=0

    # # tune = 25
    
    # while(True):
    #     start =i*lookAhead + find_nearest_indx(Y[i*lookAhead:(i+1)*lookAhead],center)
    #     if(start < tune):
    #         i=i+1
    #         continue
    #     elif (i>100): break;
    #     else:
    #         after =  np.average(Y[start+1:start+tune])
    #         before  =  np.average(Y[start-tune:start])
    #         # print (f"{Y[start]} \t {before} \t {after}")

    #         if ((Y[start] < after) and (before < Y[start])):
    #             break
    #         else:
    #             i=i+1

    # i=0
    # while(True):
    #     end =Y.size - (i+1)*lookAhead + find_nearest_indx(Y[-(i+1)*lookAhead:-(i)*lookAhead-1],center)
    #     # print (f"{end} \t {Y[end]} \t {Y[end -1]}")
    #     if(end > Y.size -tune-1):
    #         i=i+1
    #         continue
    #     elif (i>100): break;
    #     else:        
    #         if ((Y[end] > np.average(Y[end-tune:end])) and (np.average(Y[end:end+tune]) > Y[end])):
    #             break
    #         else:
    #             i=i+1
            




    # Method II
    # start=0
    # period = 1/freq
    # measure_period = measure_period*10**(-9) #Covert to s

    # near_whole  = measure_period*(X[-1]-X[start])/period
    # end = find_nearest_indx(X*measure_period,   period*int(near_whole) + X[start]*measure_period)
    # # print (f"{near_whole} \t {end} \t {X[end]*measure_period} \t {near_whole*period}  ")
 

            


    # # Method III


    # maxi = 30
    # skip = 5
    # dat = []
    # for i in range(0,maxi,skip):
    #     for j in range(-1,-1*maxi,-1*skip):
    #         out = scanFFT(X,Y,N=(i,j))        
    #         dat.append((out,int(i),int(j)))
            
    # peaks = np.array(dat).T[0]    
    # peak_max_index = np.where(peaks == np.max(peaks))[0][0]            
    # start,end =  (int(np.array(dat).T[1][peak_max_index]),int(np.array(dat).T[2][peak_max_index]))    





    # Method IV
    center = np.average(Y)
    prev_i = 0
    numOfItems = 10
    #lookAhead= int(Y.size/(numOfItems*2))
    lookAhead= int(50*100000/NN)

    # I = []
    # for i in range(lookAhead,Y.size,int(lookAhead)):
    #     temp = Y[prev_i:i]
    #     value = find_nearest_indx(temp, center) +prev_i
    #     prev_i = i
    #     I.append(value)

        
    # # I = np.array(I)

    # J = I[-numOfItems+1:]
    # I = I[:numOfItems]
    


    prev_i = 0
    I ,J= [],[]
    for i in range(lookAhead,numOfItems*lookAhead+1,int(lookAhead)):
        temp = Y[prev_i:i]
        value = find_nearest_indx(temp, center) +prev_i
        prev_i = i
        I.append(value)
        
    prev_i = Y.size-numOfItems*lookAhead
    for i in range(Y.size-(numOfItems-1)*lookAhead,Y.size+1,int(lookAhead)):
        temp = Y[prev_i:i]
        value = find_nearest_indx(temp, center) +prev_i
        prev_i = i
        J.append(value)
    
    
    

    
    # print(I)
    # print (J)


    
    
    
    dat = []
    for i in I:
        for j in J:
            if(j-i > 100):
                out = scanFFT(X,Y,N=(i,j))        
                dat.append((out,int(i),int(j)))
            
    peaks = np.array(dat).T[0]    
    peak_max_index = np.where(peaks == np.max(peaks))[0][0]
    start,end  =  (int(np.array(dat).T[1][peak_max_index]),int(np.array(dat).T[2][peak_max_index]))

    






    
    return start,end


def scanFFT(x,y,N=(0,-1)):
    x = x[N[0]:N[1]]
    y = y[N[0]:N[1]]    
    N = x.size
    T = abs(x[1]-x[2])
    # print (f"No: of data points {N}, \nInterval \t:: {T} s")
    yf = fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    Y =  2.0/N * np.abs(yf[0:N//2])
    X = xf
    ymax=np.max(Y[10:-10])
    return ymax


def find_nearest_indx(array, value):
    if (array.size > 0):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx
    else:
        print ("Edge fix algo failed")





        
        
        

import pickle
def save_obj(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)





# use 14 cycles for 160MHz, and 3 cycles for 40MHz
import subprocess
def runBash(cmd,show=False):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if show:
        if output != None:
            print (output.decode("utf-8"))
        if error != None:
            print (error.decode("utf-8"))



def DataAq(cycles=2,ser="DDMTD",data_save_folder="./data",save_name="test",compiles=0):
    cmd = f"../RPi_Side/runAtNex.sh ddmtd_mem.exe {compiles} {cycles} {ser}"
    runBash(cmd)
    cmd = f'scp {ser}:Flash_Firmware/ddmtd_mem_dump1.txt   {data_save_folder+save_name+"_1.txt"}'
    runBash(cmd)
    cmd = f'scp {ser}:Flash_Firmware/ddmtd_mem_dump2.txt   {data_save_folder+save_name+"_2.txt"}'
    runBash(cmd)








import os.path

def pll_copyConf(conf='160MHz_100k.h'):
    direc = f"../RPi_Side/Flash_Firmware/PLL_Conf/{conf}"
    if os.path.isfile(direc):
        print(f" copying {conf} as Si5344_REG in Flash_Firmware Folder")
        cmd = f"cp {direc}  ../RPi_Side/Flash_Firmware/Si5344_REG.h"
        runBash(cmd,0)
    else:
        print("Config not found!!!")
