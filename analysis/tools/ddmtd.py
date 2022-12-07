import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy.fftpack import fft
import tools.base as base
import pandas as pd


class ddmtd():
    #################################
    # Constants
    #################################
    N=100000
    INPUT_FREQ = 160*10**6
    # INPUT_FREQ = 40*10**6
    # INPUT_FREQ = 640*10**6
    FREQ = (1.0*N)/(N+1)*INPUT_FREQ


    MEASURE_FREQ = FREQ
    MEASURE_PERIOD = 1.*10**9/MEASURE_FREQ# ns

    PERIOD =  1.0*10**9/FREQ # ns

    BEAT_FREQ = 1.*INPUT_FREQ/(N+1)
    BEAT_PERIOD = 1./BEAT_FREQ


    MULT_FACT = MEASURE_PERIOD*10**(-9)/(N+1)*10**9 #give output in ns

    ERR = PERIOD/N
    #################################
    # END of Constants
    #################################
    
    save_name_folder = ""
    quiet=0
    def __init__(self,data_frame_input,q=0,channel=(1,3)):
        self.quiet = q
        self.data_frame_input = data_frame_input
        if type(data_frame_input) == pd.core.frame.DataFrame:
            self.df = pd.DataFrame()

            edge1   = data_frame_input[f"edge{channel[0]}"].values
            ddmtd1  = data_frame_input[f"ddmtd{channel[0]}"].values
            edge2   = data_frame_input[f"edge{channel[1]}"].values
            ddmtd2  = data_frame_input[f"ddmtd{channel[1]}"].values
            


            # # make the first transistion ==1
            # if edge1[0] == 0:
            #     edge1 = edge1[1:]
            #     ddmtd1 = ddmtd1[1:]
            #     edge2 = edge2[:-1]
            #     ddmtd2 = ddmtd2[:-1]
            #     print("deleted first transition of ddmtd1")

            # if edge2[0] == 0:
            #     edge2 = edge2[1:]
            #     ddmtd2 = ddmtd2[1:]
            #     edge1 = edge1[:-1]
            #     ddmtd1 = ddmtd1[:-1]
            #     print("deleted first transition of ddmtd2")
            # make data the same size # if there are the first missing edge....
            # if (edge1.size != edge2.size):
            #     if (edge1.size > edge2.size):
            #         edge1  = edge1 [1:]
            #         ddmtd1 = ddmtd1[1:]
            #     else:
            #         edge2  = edge2 [1:]
            #         ddmtd2 = ddmtd2[1:]

            


            # Save it into dataFrame
            self.df['edge1']    = edge1
            self.df['ddmtd1']   = ddmtd1
            self.df['edge2']    = edge2
            self.df['ddmtd2']   = ddmtd2


            # self.df = self.df[self.df.ddmtd1 != 2147483647].reset_index(drop=1) #remove memory that is not used
            # self.df = self.df[self.df.ddmtd1 != 0].reset_index(drop=1) #remove memory that is not used



            #Determining fall or rise edges, and removing metastate edges
            self.MetaRemoveContEdged()#.iloc[5:-5,:].reset_index(drop =1)


            

            self.values1_rise = self.dff.val1[self.dff.par1==1].values
            self.values1_fall = self.dff.val1[self.dff.par1==-1].values
            self.values2_rise = self.dff.val2[self.dff.par2==1].values
            self.values2_fall = self.dff.val2[self.dff.par2==-1].values




            # trim everything to the lowest sized array
            min_len = np.min((self.values1_fall.size,self.values1_rise.size,self.values2_fall.size,self.values2_rise.size))
            # print(min_len)
            self.values1_rise =self.values1_rise[:min_len]
            self.values1_fall =self.values1_fall[:min_len]
            self.values2_rise =self.values2_rise[:min_len]
            self.values2_fall =self.values2_fall[:min_len]
            



            self.TIE_fall = self.values1_fall - self.values2_fall
            self.fall_edge_times = self.values1_fall
            self.TIE_rise = self.values1_rise- self.values2_rise
            self.rise_edge_times = self.values1_rise

            # making the size of Rise and Fall the same
            if self.TIE_rise.size > self.TIE_fall.size:
                self.TIE_rise=self.TIE_rise[:-1]
                self.rise_edge_times = self.rise_edge_times[:-1]
            elif self.TIE_fall.size > self.TIE_rise.size:
                self.TIE_fall=self.TIE_fall[:-1]
                self.fall_edge_times = self.fall_edge_times[:-1]


                
            
        else:
            self.myprint ("Didn't load a pandas dataFrame")



    def pTrigger(self,par1,val1,par2,val2):

        #delete until val1 is > val2
        # index=0
        # while(1):
        #     if (val1[index] < val2[index]) or (par2[index] != par1[index]):
        #         par1 = np.delete(par1,index,axis=0)
        #         val1 = np.delete(val1,index,axis=0)
        #     elif (val1[index] > val2[index]) and (par2[index] == par1[index]):
        #         break


        #Set Postive trigger
        index = 0
        while(1):
            if par1[index] != 1:
                par1 = np.delete(par1,index,axis=0)
                val1 = np.delete(val1,index,axis=0)
            elif par1[index] == 1:
                break


        index = 0
        while(1):
            if par2[index] != 1:
                par2 = np.delete(par2,index,axis=0)
                val2 = np.delete(val2,index,axis=0)
            elif par2[index] == 1:
                break




                
        return par1,val1,par2,val2
            





    def MetaRemoveContEdged(self):
            df = self.df
            par1,val1 = self.edgeCleanEdged(df.edge1,df.ddmtd1)
            par2,val2 = self.edgeCleanEdged(df.edge2,df.ddmtd2)
            #Making the firt entry for both dataset to be a positive edge
            par1,val1,par2,val2 = self.pTrigger(par1,val1,par2,val2)
            
            #make both arrays same length
            if val1.size > val2.size:
                val1 = val1[:val2.size]
                par1 = par1[:val2.size]
            else:
                val2 = val2[:val1.size]
                par2 = par2[:val1.size]


            #Keep startings similar...
            # par1,val1,par2,val2=self.correct_Firstpoints(par1,val1,par2,val2)
            self.dff =  pd.DataFrame()
            self.dff["par1"] = par1
            self.dff["val1"] = val1        
                
            self.dff["par2"] = par2
            self.dff["val2"] = val2






    
    def Recalc(self):
        self.MEASURE_FREQ = (1.0*self.N)/(self.N+1)*self.INPUT_FREQ

        # self.MEASURE_FREQ = self.FREQ #Hz
        self.MEASURE_PERIOD = 1.*10**9/self.MEASURE_FREQ# ns

        self.PERIOD =  1.0*10**9/self.INPUT_FREQ # ns

        self.BEAT_FREQ = 1.*self.INPUT_FREQ/(self.N+1) #Hz
        self.BEAT_PERIOD = 1./self.BEAT_FREQ #s

        self.ERR = self.PERIOD/self.N

        self.MULT_FACT = self.MEASURE_PERIOD*10**(-9)/(self.N+1)*10**9 #ns
        self.myprint("Recalculations Done.")
        self.myprint(f"N = {self.N}")
        self.myprint(f"Input Freq = {self.INPUT_FREQ/10**6} MHz")
        self.myprint(f"PLL Freq = {self.MEASURE_FREQ/10**6} MHz")
        self.myprint(f"BEAT Freq = {self.BEAT_FREQ/10**3} kHz")
        self.myprint(f"Err = {self.ERR * 10**3} ps")


        self.myprint(f"$$$$$$$$$$$$ Recovered Beat Freq $$$$$$$$$$$$")
        try:
            self.myprint(f"BEAT Freq DDMTD1 = {1/(np.average(self.deltaEdge(self.dff.val1))*2*self.MEASURE_PERIOD*10**-6)} kHz")
            self.myprint(f"BEAT Freq DDMTD2 = {1/(np.average(self.deltaEdge(self.dff.val2))*2*self.MEASURE_PERIOD*10**-6)} kHz")

            self.myprint(f"Recovered N of DDMTD1 = {np.average(self.deltaEdge(self.dff.val1))*2}")
            self.myprint(f"Recovered N of DDMTD2 = {np.average(self.deltaEdge(self.dff.val2))*2}")

        except:
            self.myprint("Not able to find the deltaEdges")



    def deltaEdge(self,edges):
        edges = np.array(edges)
        pre_edges = np.insert(edges,0,0)[:-1]
        diff = edges - pre_edges
        out = np.array(diff)
        return out

    
    # def FFT(self,ylim=(None,None),xlim=(None,None),save_name="",disp=0,sep=""):
    #     if sep == "TIE1":
    #         TIE = self.TIE1
    #     elif sep == "TIE2":
    #         TIE = self.TIE2
    #     else:
    #         TIE = self.val1-self.val2


    #     y,x = base.FFT(self.val1,TIE,ylim=ylim,xlim=xlim,save_name=save_name,MEASURE_PERIOD=self.MEASURE_PERIOD,MULT_FACT=self.MULT_FACT,NN=self.N,disp=disp)
    #     return y,x

    def drawTIE(self,save_name='',bns=None,fit=False, sep="",draw=False):
        if sep == "TIE_FALL":
            TIE = self.TIE_fall
        elif sep == "TIE_RISE":
            TIE = self.TIE_rise
        else:
            TIE = (self.TIE_fall + self.TIE_rise)/2

            
        # bins = 100
        bins = np.arange(np.min(TIE),np.max(TIE),1)*self.MULT_FACT
        popt,pcov = base.drawTIE(TIE,save_name=save_name,bns=bins,MULT_FACT=self.MULT_FACT,fit=fit,figName=sep,draw=draw)
        return popt,np.sqrt(np.diag(pcov)),TIE.size,


    def myprint(self,stuff):
        if not self.quiet:
            print (stuff)

    

    def edgeCleanEdged(self,parity,edges): #Cleans up the edges and identifies whether it is a rising or falling edge
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
                    # print(int(parity[i-1]-parity[i]),parity[i],edges[i],parity[i-1],edges[i-1]) 
                    
                    # print(i,i-1)
                    # print(parity.size,edges.size)
                    # print(meta)
                    out.append(np.average((np.min(meta),np.max(meta)))) #Average of last and first state
                    # out.append(np.average(meta)) #Average of Metastability
                    # out.append(np.min(meta)) #first state
                    # out.append(np.max(meta)) #last state
                else: #removes the last edge
                    break

        return np.array(out_parity),np.array(out)


