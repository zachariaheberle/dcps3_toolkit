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
    data = ddmtd(df.iloc[:,:],channel=(1,2), q=1) #creates a ddmtd object (fix 2: later)
    data.N = N
    data.INPUT_FREQ = 160*10**6 #In Hz 
    data.Recalc()
    if fit:
        gauss_fit, _, count = data.drawTIE(sep='',fit=True,draw=False)
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
            new_vals.append(val + offset_8)
        elif 16 <= i < 24:
            new_vals.append(val + offset_16)
        elif 24 <= i:
            new_vals.append(val + offset_24)
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
        #print(f"Min Error: {min_err}\n")
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
            #print(f"y is {y}")
            #print(f"Error should be {min_err:.3f}, Offsets are {offset_8:.3f}, {offset_16:.3f}, {offset_24:.3f}")
            return offset_8, offset_16, offset_24 


        



def plot_coarse_consistency(data_save_folder, figure_save_folder, plot_all_runs=False):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/coarse_consistency_plots")
        except FileExistsError:
            pass

    for channel in range(2, 4, 1):
        channel_data = []
        offset_data = []
        for run in range(10):
            run_data = []
            for coarse_control in range(32):
                print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((coarse_control, mean_val, std_err))

            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]
            y = y-y[0]

            offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)

            channel_data.append((x, y, yerr, run))
            offset_data.append((offset_8, offset_16, offset_24))

        offset_data = np.asarray(offset_data)

        offset_8 = np.mean(offset_data.T[0])
        offset_16 = np.mean(offset_data.T[1])
        offset_24 = np.mean(offset_data.T[2])

        # figg, ax = plt.subplots()
        # ax.axhline(offset_8, color='black',linewidth=1, linestyle='-.')
        # ax.axhline(offset_16, color='black',linewidth=1, linestyle='-.')
        # ax.axhline(offset_24, color='black',linewidth=1, linestyle='-.')
        # ax.fill_between(x, offset_8+offset_8_err, offset_8-offset_8_err, color='orange', alpha=.5)
        # ax.fill_between(x, offset_16+offset_16_err, offset_16-offset_16_err, color='orange', alpha=.5)
        # ax.fill_between(x, offset_24+offset_24_err, offset_24-offset_24_err, color='orange', alpha=.5)
        # ax.scatter(range(10), offset_data.T[0], c="red", label=f"Offset 8")
        # ax.scatter(range(10), offset_data.T[1], c="green", label=f"Offset 16")
        # ax.scatter(range(10), offset_data.T[2], c="blue", label=f"Offset 24")
        # ax.set_xlim(-1, 11)
        # ax.legend(loc="best")
        # plt.savefig(f"{figure_save_folder}/test.png", dpi=300, facecolor="#FFFFFF")
        # plt.close(figg)
        # return

        slope_data = []
        for x, y, yerr, run in channel_data:
            #offset_8, offset_16, offset_24 = offset_data[run]

            y = adjust_offsets(y, offset_8, offset_16, offset_24)

            popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            if plot_all_runs:
                fig, ax = plt.subplots()

                ax.grid(True, alpha=0.5)
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{popt[0]:4.3}+/- {p_e[0]:4.2} [ps/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")
                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax.set_xlabel("Coarse Step")
                ax.set_ylabel("Delay [ps]")
                ax.legend()
                ax.set_ylim([-5, 250])

                plt.savefig(f"{figure_save_folder}/coarse_consistency_plots/coarse_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)
            
            slope_data.append((run, popt[0], p_e[0]))
    
        slope_data = np.asarray(slope_data)
        x = slope_data.T[0]
        y = slope_data.T[1]
        yerr = slope_data.T[2]

        # weighted_mean = np.average(y, weights=1/yerr**2)
        # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

        popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        weighted_mean = popt[0]
        err = p_e[0]


        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps/step]")
        ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
        ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

        ax.set_ylim([weighted_mean-0.2, weighted_mean+0.2])

        ax.set_ylabel("Delay per Coarse Step [ps/step]")
        ax.set_xlabel("Run Number")
        ax.set_xticks(range(10))
        ax.set_xticklabels(range(10))
        ax.legend(loc="upper left",fontsize=8)
        ax.set_title(f"Coarse Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    plt.savefig(f"{figure_save_folder}/dcps3_coarse_consistency.png", dpi=300, facecolor="#FFFFFF")
    plt.close()

def plot_coarse_cell_consistency(data_save_folder, figure_save_folder):
    f = plt.figure(figsize=(10,24))
    f.subplots_adjust(top=0.96, bottom=0.04, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 4, 1):
        channel_data = []
        for i, coarse_control in enumerate([0, 1, 2, 4, 8, 16]):
            run_data = []
            for run in range(10):
                #print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_err))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]

            # weighted_mean = np.average(y, weights=1/yerr**2)
            # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

            popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            err = p_e[0]

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

            ax.set_ylim([weighted_mean-0.4, weighted_mean+0.4])
        
            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Coarse Delay Cell Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}\nCell {coarse_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_coarse_cell_consistency_test.png", dpi=300, facecolor="#FFFFFF")

def plot_fine_consistency(data_save_folder, figure_save_folder, plot_all_runs=False):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/fine_consistency_plots")
        except FileExistsError:
            pass

    for channel in range(2, 4, 1):
        channel_data = []
        for run in range(10):
            run_data = []
            for fine_control in range(66):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((fine_control, mean_val, std_err))
            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]
            y = y-y[0]

            channel_data.append((x, y, yerr, run))

            # channel_data.append((run, popt[0], p_e[0]))
    
        slope_data = []
        for x, y, yerr, run in channel_data:

            popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            if plot_all_runs:
                fig, ax = plt.subplots()

                ax.grid(True, alpha=0.5)
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{popt[0]:4.3}+/- {p_e[0]:4.2} [ps/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")
                ax.set_title(f"Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax.set_xlabel("Fine Step")
                ax.set_ylabel("Delay [ps]")
                ax.legend()
                ax.set_ylim([-0.5, 20])

                plt.savefig(f"{figure_save_folder}/fine_consistency_plots/coarse_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)
            
            slope_data.append((run, popt[0], p_e[0]))
    
        slope_data = np.asarray(slope_data)
        x = slope_data.T[0]
        y = slope_data.T[1]
        yerr = slope_data.T[2]

        # weighted_mean = np.average(y, weights=1/yerr**2)
        # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

        popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        weighted_mean = popt[0]
        err = p_e[0]

        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps/step]")
        ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
        ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

        ax.set_ylim([weighted_mean-0.005, weighted_mean+0.005])
        
        ax.set_ylabel("Delay per Fine Step [ps/step]")
        ax.set_xlabel("Run Number")
        ax.set_xticks(range(10))
        ax.set_xticklabels(range(10))
        ax.legend(loc="upper left",fontsize=8)
        ax.set_title(f"Fine Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    plt.savefig(f"{figure_save_folder}/dcps3_fine_consistency_test.png", dpi=300, facecolor="#FFFFFF")
    plt.close()

def plot_fine_cell_consistency(data_save_folder, figure_save_folder):
    f = plt.figure(figsize=(10,264), dpi=100)
    f.subplots_adjust(top=0.997, bottom=0.003, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 4, 1):
        for i, fine_control in enumerate(range(66)):
            run_data = []
            for run in range(10):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_err))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = -1*(run_data.T[1]+200)%3125
            yerr = run_data.T[2]

            # weighted_mean = np.average(y, weights=1/yerr**2)
            # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

            popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            err = p_e[0]

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

            ax.set_ylim([weighted_mean-0.4, weighted_mean+0.4])

            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Cell Consistency Check\nChannel {channel}: Fine Cell {fine_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_fine_cell_consistency_test.pdf", dpi=100, facecolor="#FFFFFF")

def plot_fine_cell_relative_consistency(data_save_folder, figure_save_folder, plot_all_runs=False):
    f = plt.figure(figsize=(10,264), dpi=100)
    f.subplots_adjust(top=0.997, bottom=0.003, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    run = 0

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/fine_delay_relative_consistency_plots")
        except FileExistsError:
            pass

    for channel in range(2, 4, 1):
        channel_data = []
        for i, fine_control in enumerate(range(66)):
            run_data = []
            for run in range(10):
                print(f"Calculating fine control: {fine_control} channel: {channel} run: {run}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                if fine_control == 0:
                    prev_run_name = run_name
                else:
                    prev_run_name = f"chan{channel}_f{fine_control-1}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_err = get_data(data_save_folder, run_name)
                prev_mean_val, prev_std_err = get_data(data_save_folder, prev_run_name)
                mean_val = ((-1*(mean_val+200)%3125)-200) - ((-1*(prev_mean_val+200)%3125)-200)
                if fine_control != 0:
                    std_err = std_err + prev_std_err
                run_data.append((run, mean_val, std_err))

            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = run_data.T[1]
            yerr = run_data.T[2]

            if plot_all_runs:
                channel_data.append((fine_control, y, yerr, x))

            popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            err = p_e[0]

            ax = f.add_subplot(66, 2, channel-1 + 2*i)
            ax.grid(True, alpha=0.5)
            ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{weighted_mean:4.3}+/-{err:4.2} [ps]")
            ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Runs")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Delay")

            if fine_control == 0:
                ax.set_ylim([-0.1, 0.1])
            else:
                ax.set_ylim([0, 0.65])

            ax.set_ylabel("Relative Delay [ps]")
            ax.set_xlabel("Fine Delay Cell")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Cell Relative Consistency Check\nChannel {channel} | Fine Cell {fine_control}")
        
        if plot_all_runs:
            
            for run in range(10):
                x = []
                y = []
                yerr = []
                for fine_control, y_run, y_run_err, runs in channel_data:
                    x.append(fine_control)
                    y.append(y_run[run])
                    yerr.append(y_run_err[run])
                
                x = np.asarray(x)
                y = np.asarray(y)
                yerr = np.asarray(yerr)
                
                fig, ax = plt.subplots()

                popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                p_e = np.sqrt(np.diag(pcov))

                weighted_mean = popt[0]
                err = p_e[0]

                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Cells\n{weighted_mean:4.3}+/-{err:4.2} [ps]")
                ax.fill_between(x, weighted_mean+err, weighted_mean-err, color='orange', alpha=.5, label="Standard Error All Cells")
                ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Delay")
                ax.set_title(f"Fine Delay Cell Relative Consistency Check\nChannel {channel} | Run {run}")
                ax.set_ylim([-0.05, 0.6])
                ax.set_xlabel("Coarse Delay Step")
                ax.set_ylabel("Delay [ps]")
                ax.legend(loc="lower right")

                fig.savefig(f"{figure_save_folder}/fine_delay_relative_consistency_plots/relative_fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)


                

    f.savefig(f"{figure_save_folder}/dcps3_fine_cell_relative_consistency.pdf", dpi=100, facecolor="#FFFFFF")
    plt.close()


#plot_coarse_consistency(f"./dcps3Test/data/board1/N{N}_coarse", f"./dcps3Test/figures/board1", True)
#plot_fine_consistency(f"./dcps3Test/data/board1/N{N}_fine", f"./dcps3Test/figures/board1", True)
#plot_coarse_cell_consistency(f"./dcps3Test/data/board1/N{N}_coarse", f"./dcps3Test/figures/board1")
#plot_fine_cell_consistency(f"./dcps3Test/data/board1/N{N}_fine_cell", f"./dcps3Test/figures/board1")
plot_fine_cell_relative_consistency(f"./dcps3Test/data/board1/N{N}_fine/", f"./dcps3Test/figures/board1", True)