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

# Setting default variables...
N=100000  #Setting the DDMTD N
freq="160"#in MHz #Setting the input clock frequency
fig_save_folder = f"./dcps3Test/figures/N{N}/"
data_save_folder = f"./dcps3Test/data/N{N}/"
coarse_control = 0
fine_control = 0
stage4_tune = 2
stage5_tune = 3
channel = 2
run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}"

def weighted_std_dev(mean, values, weights):
    total = 0
    for value, weight in zip(values, weights):
        total += weight*(mean - value)**2
    return np.sqrt(total / (((len(values)-1)/len(values)) * sum(weights)))

def get_data(data_save_folder, run_name, fit=True, draw=False):
    df1 = pd.read_csv(f"{data_save_folder+run_name}_ddmtd1.txt",names=['edge1','ddmtd1'])
    df2 = pd.read_csv(f"{data_save_folder+run_name}_ddmtd2.txt",names=['edge2','ddmtd2'])
    df = pd.concat((df1,df2),axis=1)
    # Create a DDMTD Object for analysis of the data
    data = ddmtd(df.iloc[2:],channel=(1,2), q=1) #creates a ddmtd object (fix 2: later)
    data.N = N
    data.INPUT_FREQ = 160*10**6 #In Hz 
    data.Recalc()
    if fit:
        gauss_fit, _, count = data.drawTIE(sep='',fit=True,draw=draw)
        mean_val, std_dev = gauss_fit[1]*1000, abs(gauss_fit[2])*1000
        return mean_val, std_dev / np.sqrt(count)
    else:
        mean_val = np.mean(np.concatenate((data.TIE_rise,data.TIE_fall)))*data.MULT_FACT*1000
        return mean_val

def adjust_offsets(y, offset_8, offset_16, offset_24):
        new_vals = []
        for i, val in enumerate(y):
            if i < 8:
                new_vals.append(val)
            elif 8 <= i < 16:
                new_vals.append(val - offset_8)
            elif 16 <= i < 24:
                new_vals.append(val - offset_16)
            elif 24 <= i:
                new_vals.append(val - offset_24)
        return np.asarray(new_vals)

def find_offsets(x, y, yerr):

    offset_8, offset_16, offset_24 = (0, 0, 0)
    ideal = False
    power = 0
    max_power = 5

    def get_slope_error(x, y, yerr):
        popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
        return np.sqrt(np.diag(pcov))[0]


    def check_offset(y, offset_8, offset_16, offset_24, min_err):
        y = adjust_offsets(y, offset_8, offset_16, offset_24)
        slope_err = get_slope_error(x, y, yerr)
        if slope_err < min_err:
            return True, slope_err
        else:
            return False, min_err

    step = 0
    min_err = get_slope_error(x, y, yerr)
    while ideal == False:
        # print(f"Power: {power}, Step: {step}")
        # print(f"Offset 8: {offset_8}, Offset 16: {offset_16}, Offset 24: {offset_24}")
        # print(f"Min Error: {min_err}\n")
        if step == 0:
            if check_offset(y, offset_8 - 10**(-power), offset_16, offset_24, min_err)[0] == True:
                min_err = check_offset(y, offset_8 - 10**(-power), offset_16, offset_24, min_err)[1]
                offset_8 = offset_8 - 10**(-power)
            elif check_offset(y, offset_8 + 10**(-power), offset_16, offset_24, min_err)[0] == True:
                min_err = check_offset(y, offset_8 + 10**(-power), offset_16, offset_24, min_err)[1]
                offset_8 = offset_8 + 10**(-power)
            else:
                if power < max_power:
                    power += 1
                else:
                    power = 0
                    step += 1
        elif step == 1:
            if check_offset(y, offset_8, offset_16 - 10**(-power), offset_24, min_err)[0] == True:
                min_err = check_offset(y, offset_8, offset_16 - 10**(-power), offset_24, min_err)[1]
                offset_16 = offset_16 - 10**(-power)
            elif check_offset(y, offset_8, offset_16 + 10**(-power), offset_24, min_err)[0] == True:
                min_err = check_offset(y, offset_8, offset_16 + 10**(-power), offset_24, min_err)[1]
                offset_16 = offset_16 + 10**(-power)
            else:
                if power < max_power:
                    power += 1
                else:
                    power = 0
                    step += 1 
        elif step == 2:
            if check_offset(y, offset_8, offset_16, offset_24 - 10**(-power), min_err)[0] == True:
                min_err = check_offset(y, offset_8, offset_16, offset_24 - 10**(-power), min_err)[1]
                offset_24 = offset_24 - 10**(-power)
            elif check_offset(y, offset_8, offset_16, offset_24 + 10**(-power), min_err)[0] == True:
                min_err = check_offset(y, offset_8, offset_16, offset_24 + 10**(-power), min_err)[1]
                offset_24 = offset_24 + 10**(-power)
            else:
                if power < max_power:
                    power += 1
                else:
                    power = 0
                    step += 1
        else:
            ideal = True
            return offset_8, offset_16, offset_24 


        



def plot_coarse_consistency(data_save_folder):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    for channel in range(2, 4, 1):
        channel_data = []
        for run in range(10):
            run_data = []
            for coarse_control in range(32):
                print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((coarse_control, mean_val, std_err))
            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]
            y = y-y[0]

            # ax = f.add_subplot(121)

            # popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            # p_e = np.sqrt(np.diag(pcov))

            # ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{popt[0]:4.3}+/- {p_e[0]:4.2} [ps/step]")
            # ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")
            # ax.set_title("Before Y adjustment")
            # ax.legend()

            offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)
            y = adjust_offsets(y, offset_8, offset_16, offset_24)

            #ax = f.add_subplot(122)

            popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            # ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{popt[0]:4.3}+/- {p_e[0]:4.2} [ps/step]")
            # ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")
            # ax.set_title("After Y adjustment")
            # ax.legend()
            # plt.show()

            channel_data.append((run, popt[0], p_e[0] / np.sqrt(len(y))))
    
        channel_data = np.asarray(channel_data)
        x = channel_data.T[0]
        y = channel_data.T[1]
        yerr = channel_data.T[2]

        weighted_mean = np.average(y, weights=1/yerr**2)
        err = weighted_std_dev(weighted_mean, y, 1/yerr**2) / np.sqrt(len(y))

        # popt,pcov = np.polyfit(x,y,0,cov="unscaled",w=1/yerr**2)
        # p_e = np.sqrt(np.diag(pcov))

        # weighted_mean = popt[0]
        # _sig = p_e[0]


        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps/step]")
        ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
        ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

        ax.set_ylim([7.11, 7.18])

        ax.set_ylabel("Delay per Coarse Step [ps/step]")
        ax.set_xlabel("Run Number")
        ax.set_xticks(range(10))
        ax.set_xticklabels(range(10))
        ax.legend(loc="upper left",fontsize=8)
        ax.set_title(f"Coarse Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    plt.savefig("dcps3Test/figures/dcps3_coarse_consistency_test2.png", dpi=300, facecolor="#FFFFFF")
    plt.close()


def plot_coarse_cell_consistency(data_save_folder):
    f = plt.figure(figsize=(10,24))
    f.subplots_adjust(top=0.96, bottom=0.04, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    for channel in range(2, 4, 1):
        channel_data = []
        for i, coarse_control in enumerate([0, 1, 2, 4, 8, 16]):
            run_data = []
            for run in range(10):
                #print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_err))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]

            weighted_mean = np.average(y, weights=1/yerr**2)
            err = weighted_std_dev(weighted_mean, y, 1/yerr**2) / np.sqrt(len(y))

            if coarse_control == 0:
                offset = weighted_mean
                weighted_mean = 0.0
                y = y - offset
            else:
                weighted_mean -= offset
                y = y - offset
        
            ax = f.add_subplot(6, 2, channel-1 + 2*i)
            ax.grid(True, alpha=0.5)
            if coarse_control == 16:
                ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{weighted_mean:4.4}+/-{err:4.2} [ps]")
            else:
                ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps]")
            ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            if coarse_control == 0:
                ax.set_ylim([-0.2, 0.2])
            elif coarse_control == 1:
                ax.set_ylim([8.65, 9.05])
            elif coarse_control == 2:
                ax.set_ylim([17.1, 17.5])
            elif coarse_control == 4:
                ax.set_ylim([32.65, 33.05])
            elif coarse_control == 8:
                ax.set_ylim([59.2, 59.6])
            else:
                ax.set_ylim([122.34, 122.74])
        
            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Coarse Delay Cell Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}\nCell {coarse_control}")
    plt.savefig("dcps3Test/figures/dcps3_coarse_cell_consistency_test.png", dpi=300, facecolor="#FFFFFF")



def plot_fine_consistency(data_save_folder):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    for channel in range(2, 4, 1):
        channel_data = []
        for run in range(10):
            run_data = []
            for fine_control in range(66):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((fine_control, mean_val, std_err))
            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]
            y = y-y[0]

            popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            channel_data.append((run, popt[0], p_e[0] / np.sqrt(len(y))))
    
        channel_data = np.asarray(channel_data)
        x = channel_data.T[0]
        y = channel_data.T[1]
        yerr = channel_data.T[2]

        weighted_mean = np.average(y, weights=1/yerr**2)
        err = weighted_std_dev(weighted_mean, y, 1/yerr**2) / np.sqrt(len(y))

        # popt,pcov = np.polyfit(x,y,0,cov="unscaled",w=1/yerr**2)
        # p_e = np.sqrt(np.diag(pcov))

        # weighted_mean = popt[0]
        # _sig = p_e[0]

        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps/step]")
        ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
        ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

        ax.set_ylim([0.269, 0.277])
        
        ax.set_ylabel("Delay per Fine Step [ps/step]")
        ax.set_xlabel("Run Number")
        ax.set_xticks(range(10))
        ax.set_xticklabels(range(10))
        ax.legend(loc="upper left",fontsize=8)
        ax.set_title(f"Fine Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    plt.savefig("dcps3Test/figures/dcps3_fine_consistency_test2.png", dpi=300, facecolor="#FFFFFF")
    plt.close()

def plot_fine_cell_consistency(data_save_folder):
    f = plt.figure(figsize=(10,264))
    f.subplots_adjust(top=0.96, bottom=0.04, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    for channel in range(2, 4, 1):
        for i, fine_control in range(66):
            run_data = []
            for run in range(10):
                #print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"chan{channel}_fcell{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_err))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]

            weighted_mean = np.average(y, weights=1/yerr**2)
            err = weighted_std_dev(weighted_mean, y, 1/yerr**2) / np.sqrt(len(y))

            if fine_control == 0:
                offset = weighted_mean
                weighted_mean = 0.0
                y = y - offset
            else:
                weighted_mean -= offset
                y = y - offset
        
            ax = f.add_subplot(66, 2, channel-1 + 2*i)
            ax.grid(True, alpha=0.5)
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps]")
            ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            if fine_control == 0:
                ax.set_ylim([-0.1, 0.1])
            else:
                #ax.set_ylim([.2, .3])
                pass
        
            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Cell Consistency Check\nChannel {channel}: Fine Cell {fine_control}")
    plt.savefig("dcps3Test/figures/dcps3_fine_cell_consistency_test.pdf", dpi=300, facecolor="#FFFFFF")

#plot_coarse_consistency(f"./dcps3Test/data/N{N}_coarse/")
plot_fine_consistency(f"./dcps3Test/data/N{N}_fine/")
#plot_coarse_cell_consistency(f"./dcps3Test/data/N{N}_coarse/")
plot_fine_cell_consistency(f"./dcps3Test/data/N{N}_fine_cell/")