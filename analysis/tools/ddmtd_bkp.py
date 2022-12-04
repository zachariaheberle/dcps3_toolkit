# Written by Rohith Saradhy
# Email -> rohithsaradhy@gmail.com

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
import tools.base as base




class ddmtd():
    #################################
    # Constants
    #################################
    N=100000
    INPUT_FREQ = 160*10**6 #U1 Hz
    # INPUT_FREQ = 40*10**6
    # INPUT_FREQ = 640*10**6
    MEASURE_FREQ = (1.0*N)/(N+1)*INPUT_FREQ #Uddmtd Hz

    MEASURE_PERIOD = 1.*10**9/MEASURE_FREQ# ns

    PERIOD =  1.0*10**9/INPUT_FREQ # ns

    BEAT_FREQ = 1.*INPUT_FREQ/(N+1) #Hz
    BEAT_PERIOD = 1./BEAT_FREQ  #s


    MULT_FACT = MEASURE_PERIOD*10**(-9)/(N+1)*10**9 #give output in ns

    ERR = PERIOD/N
    #################################
    # END of Constants
    #################################
    
    save_name_folder = ""
    quiet=0
    def __init__(self,save_name_folder,q=0):
        self.quiet = q
        self.save_name_folder = save_name_folder
        if save_name_folder != "":
            df1 = pd.read_csv(f"{save_name_folder}_ddmtd1.txt",sep=",",header=0,skiprows=1,names=["edge1","ddmtd1"])
            df2 = pd.read_csv(f"{save_name_folder}_ddmtd2.txt",sep=",",header=0,skiprows=1,names=["edge2","ddmtd2"])
            self.df  = pd.concat((df1,df2),axis=1)
            self.df  = self.df.dropna()

            

            self.values1 = self.df.ddmtd1
            self.values2 = self.df.ddmtd2
            #Separating Odd and Even Edges

            self.dff = self.MetaRemoveContEdged().dropna().iloc[5:-5,:].reset_index(drop =1)
            self.values1_fall = self.dff.val1[self.dff.par1==1].values
            self.values1_rise = self.dff.val1[self.dff.par1==-1].values
            self.values2_fall = self.dff.val2[self.dff.par2==1].values
            self.values2_rise = self.dff.val2[self.dff.par2==-1].values


            if (self.values1_fall.size > self.values2_fall.size ):
                size_fall =  self.values2_fall.size
            else:
                size_fall =  self.values1_fall.size

            if (self.values1_rise.size > self.values2_rise.size ):
                size_rise =  self.values2_rise.size
            else:
                size_rise =  self.values1_rise.size


            self.TIE_fall = self.values1_fall[:size_fall] - self.values2_fall[:size_fall]
            self.fall_edge_times = self.values1_fall[:size_fall]
            self.TIE_rise = self.values1_rise[:size_rise] - self.values2_rise[:size_rise]
            self.rise_edge_times = self.values1_rise[:size_rise]
            

            #Shifting the edges if they do not match
            if self.dff.par1[0] == self.dff.par2[0]:
                self.TIE = self.dff.val1.values - self.dff.val2.values
            else:
                self.TIE = self.dff.val1[1:].values - self.dff.val2[:-1].values

            

            ## Legacy Code  #Check to see if it works with this...  
            # self.val1,self.val2 = base.MetaRemoveCont(self.values1,self.values2)
            # self.TIE1,self.TIE2,(self.VAL) = base.SeparatePosNegCont(self.val1,self.val2)
            # (VAL1_EVN,VAL1_ODD,VAL2_EVN,VAL2_ODD)
        else:
            self.myprint ("Loaded empty, Specify Load file")


    def MetaRemoveContEdged(self):
        df = self.df
        par1,val1 = base.edgeCleanEdged(df.edge1,df.ddmtd1)
        par2,val2 = base.edgeCleanEdged(df.edge2,df.ddmtd2)
        dff =  pd.DataFrame()

        if val1.size > val2.size:
            val1 = val1[:val2.size]
            par1 = par1[:val2.size]
        else:
            val2 = val2[:val1.size]
            par2 = par2[:val1.size]


        dff["par1"] = par1
        dff["val1"] = val1        
            
        dff["par2"] = par2
        dff["val2"] = val2

        return dff

    # def save(self):
    #     if self.save_name_folder != "":
    #         temp_datafile = self.save_name_folder+"_data.txt"
    #         f = open(temp_datafile,'w')
    #         for i in range(0,self.val1.size):
    #             f.write("%15.4f,%15.4f,%15.4f \n"%(self.val1[i],self.val2[i],self.val1[i]-self.val2[i]))
    #         f.close()
    #         self.myprint(f"Saved to {temp_datafile}")
    #     else:
    #         self.myprint ("Please set save_name_folder var")
    

    # def load(self,computeAll=False):
    #     VAL1,VAL2 = [],[]
    #     if self.save_name_folder != "":
    #         temp_datafile = self.save_name_folder+"_data.txt"
    #         data_file = open(temp_datafile)
    #         for lines in data_file:
    #             val1,val2,_ = lines.split(",")
    #             VAL1.append(float(val1))
    #             VAL2.append(float(val2))   
    #         self.val1  = np.array(VAL1)
    #         self.val2  = np.array(VAL2)
    #         if computeAll:
    #             self.TIE1,self.TIE2,(self.VAL) = base.SeparatePosNegCont(self.val1,self.val2)
    #             self.myprint("Loaded by computing all")
    #         else:
    #             self.myprint("Fast Loaded")
                
    #         # self.myprint("Done Loading")
    #     else:
    #         self.myprint ("Please set save_name_folder var")


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
            self.myprint(f"BEAT Freq DDMTD1 Fall = {1/(np.average(self.deltaEdge(self.values1_fall))*self.MEASURE_PERIOD*10**-6)} kHz")
            self.myprint(f"BEAT Freq DDMTD2 Fall = {1/(np.average(self.deltaEdge(self.values2_fall))*self.MEASURE_PERIOD*10**-6)} kHz")
            self.myprint(f"BEAT Freq DDMTD1 Rise = {1/(np.average(self.deltaEdge(self.values1_rise))*self.MEASURE_PERIOD*10**-6)} kHz")
            self.myprint(f"BEAT Freq DDMTD2 Rise = {1/(np.average(self.deltaEdge(self.values2_rise))*self.MEASURE_PERIOD*10**-6)} kHz")
            
            


            self.myprint(f"Recovered N DDMTD1 Fall = {(np.average(self.deltaEdge(self.values1_fall)))}")
            self.myprint(f"Recovered N DDMTD2 Fall = {(np.average(self.deltaEdge(self.values2_fall)))}")


            self.myprint(f"Recovered N DDMTD1 Rise = {(np.average(self.deltaEdge(self.values1_rise)))}")
            self.myprint(f"Recovered N DDMTD2 Rise = {(np.average(self.deltaEdge(self.values2_rise)))}")

        except:
            self.myprint("Not able to find the deltaEdges")




    def deltaEdge(self,edges):
        edges = np.array(edges)
        pre_edges = np.insert(edges,0,0)[:-1]
        diff = edges - pre_edges
        out = np.array(diff)
        return out

    
    def FFT(self,ylim=(None,None),xlim=(None,None),save_name="",disp=0,sep=""):
        y,x = base.FFT(self.dff.val1,self.TIE,ylim=ylim,xlim=xlim,save_name=save_name,MEASURE_PERIOD=self.MEASURE_PERIOD,MULT_FACT=self.MULT_FACT,NN=self.N,disp=disp)
        return y,x

    def drawTIE(self,save_name='',bns=None,fit=False, sep=""):
        if sep == "fall":
            TIE = self.TIE_fall
        elif sep == "rise":
            TIE = self.TIE_rise
        else:
            TIE = self.TIE


        if bns==None:
            bns=(np.arange(np.min(TIE),np.max(TIE),50))*self.MULT_FACT


        base.drawTIE(TIE,save_name=save_name,bns=bns,MULT_FACT=self.MULT_FACT,fit=fit,NN=self.N)



    def myprint(self,stuff):
        if not self.quiet:
            print (stuff)

            