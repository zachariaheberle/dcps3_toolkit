import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
import time
import pandas as pd
import os

from tools.base import *
from tools.ddmtd import ddmtd
from time import sleep

import matplotlib
matplotlib.style.available
# import scienceplots
# matplotlib.style.use(['seaborn-v0_8-darkgrid', 'science'])
# plt.rcParams['figure.figsize'] = [4, 3]
plt.rcParams['figure.dpi'] = 300

# Setting all the variables...
N=100000  #Setting the DDMTD N
freq="160"#in MHz #Setting the input clock frequency
pll_config_folder="../rpi_side/PLL_Conf/"
fig_save_folder = f"./dcps3Test/figures/N{N}/"
data_save_folder = f"./dcps3Test/data/N{N}/"
run_number = 1
coarse_control = 0
fine_control = 0
stage4_tune = 2
stage5_tune = 2
channel = 2
run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}"

dat = []
for coarse_control in range(0,32,1):
    try:
    # for coarse_control in [0,1,2,4,8,16]:
        # run_name = f"f_{fine_control}"
        run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}"
        print(f"{data_save_folder+run_name}_ddmtd1.txt")
        df1 = pd.read_csv(f"{data_save_folder+run_name}_ddmtd1.txt",names=['edge1','ddmtd1'])
        df2 = pd.read_csv(f"{data_save_folder+run_name}_ddmtd2.txt",names=['edge2','ddmtd2'])
        df = pd.concat((df1,df2),axis=1)
        # df

        # df.ddmtd2.diff().iloc[:].plot()
        # df.ddmtd1.diff().iloc[:].plot()


        # Create a DDMTD Object for analysis of the data
        data = ddmtd(df.iloc[:,:],channel=(1,2)) #creates a ddmtd object
        #Setting the correct N can recalculating all the scalings
        data.N = N  
        # data.N = 1000000 
        data.INPUT_FREQ = 160*10**6 #In Hz 
        data.Recalc()
        mean_val = np.mean(np.concatenate((data.TIE_rise,data.TIE_fall)))*data.MULT_FACT*1000
        # print(
        # # np.mean(data.TIE_fall)*data.MULT_FACT*1000,
        # # np.mean(data.TIE_rise)*data.MULT_FACT*1000,
        # np.mean(np.concatenate((data.TIE_rise,data.TIE_fall)))*data.MULT_FACT*1000
        # )

        dat.append((coarse_control,mean_val))
    except FileNotFoundError:
        print(f"Could not find {data_save_folder+run_name}_ddmtd1.txt")
        continue

dat = np.asarray(dat)
x = dat.T[0]
y = -1*(dat.T[1]+200)%3125

y = y-y[0]

# x = x[:(len(x) - 1)]
# y = y[:(len(y) - 1)]

f,ax = plt.subplots()
# fit
popt,pcov = np.polyfit(x,y,1,cov=True)
p_e = np.sqrt(np.diag(pcov))
# ax.plot(x,popt[0]*x+popt[1],color="r",linestyle='--',label=f"Channel {channel} \n{popt[0]:4.3}+/- {p_e[0]:4.2} [ps/step]")

plt.scatter(x,y,s=6)

ax.set_ylim([0, 248])
ax.set_ylabel("Delay [ps]")
# ax.set_xlabel("Coarse Step")
ax.legend(loc="upper left",fontsize=10)
ax.set_title(f"Coarse Delay Channel {channel}: {stage4_tune} {stage5_tune}")