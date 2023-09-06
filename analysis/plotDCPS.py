import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
import time
import pandas as pd
import os
from glob import glob
import sigfig

from tools.base import *
from tools.ddmtd import ddmtd
from time import sleep

import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
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
        return mean_val, std_dev, count
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

def reduced_chi2(residuals, std_devs):
    total = 0
    for residual, std_dev in zip(residuals, std_devs):
        total += residual**2 / std_dev**2
    return total / len(residuals) - 2 

def plot_coarse_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, plot_sim=False, plot_temp=False):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 2

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/coarse_consistency_plots")
        except FileExistsError:
            pass
    
    if plot_temp:
        T = pd.read_csv(f"{data_save_folder}/temp_info.txt", skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])
        output = []

    for channel in range(2, 4, 1):
        channel_data = []
        offset_data = []
        for run in range(10):
            run_data = []
            for coarse_control in range(32):
                print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((coarse_control, mean_val, std_dev/np.sqrt(count)))

            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+300)%3125
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

            adjusted_y = adjust_offsets(y, offset_8, offset_16, offset_24)

            popt,pcov = np.polyfit(x,adjusted_y,1,cov=True,w=1/yerr**2) # Get only error from adjusted slope
            p_e = np.sqrt(np.diag(pcov))
            popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2) # Get actual slope from raw data


            if plot_all_runs:
                fig, ax = plt.subplots() # Line plots

                if plot_sim:
                    data = pd.read_csv("./dcps3Test/data/simulation/DCSP3_sims_coarse.csv", 
                                        names = ["step", "00", "23", "13", "11", "12", "01"])
                    
                    y00 = np.asarray(data["00"][1:], dtype=np.float64)
                    y00 = y00 - y00[0]
                    y23 = np.asarray(data["23"][1:], dtype=np.float64)
                    y23 = y23 - y23[0]
                    y13 = np.asarray(data["13"][1:], dtype=np.float64)
                    y13 = y13 - y13[0]
                    y11 = np.asarray(data["11"][1:], dtype=np.float64)
                    y11 = y11 - y11[0]
                    y12 = np.asarray(data["12"][1:], dtype=np.float64)
                    y12 = y12 - y12[0]
                    y01 = np.asarray(data["01"][1:], dtype=np.float64)
                    y01 = y01 - y01[0]

                    #ax.plot(x, y00, color="orange",  marker="o", markersize=3, linestyle='--', label="Simulation | S4: 0, S5: 0")
                    ax.plot(x, y23, color="purple",  marker="v", markersize=3, linestyle='--', label="Simulation | S4: 2, S5: 3")
                    #ax.plot(x, y13, color="green",   marker="^", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 3")
                    #ax.plot(x, y11, color="purple",  marker="<", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 1")
                    #ax.plot(x, y12, color="magenta", marker=">", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 2")
                    #ax.plot(x, y01, color="pink",    marker="s", markersize=3, linestyle='--', label="Simulation | S4: 0, S5: 1")
                
                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                residuals = y - (popt[0]*x + popt[1])
                residuals_std_dev = weighted_std_dev(0, residuals, yerr)

                ax.grid(True, alpha=0.5)
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [ps/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")
                ax2.legend(loc="upper right", fontsize=5)
                ax2.set_ylim(-15, 15)

                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax2.set_xlabel("Coarse Step")
                ax.set_ylabel("Delay [ps]")
                ax2.set_ylabel("Residual [ps]")
                ax.set_ylim([-5, 300])

                if plot_temp:
                    target_temp = round(np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & (run=={run})").temp))
                    mean_temp = np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & (run=={run})").temp)
                    ylim = ax.get_ylim()
                    yrange = ylim[1] - ylim[0]
                    new_ylim = (target_temp-1, target_temp+1) # Use this to program new yaxis limits
                    new_yrange = new_ylim[1] - new_ylim[0]
                    
                    # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
                    # (and its inverse) for this to work correctly
                    temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
                    temp_ax.set_ylabel("Temperature [\u00b0C]")
                    temp_vals = T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & (run=={run})").temp
                    temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
                    ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")

                    offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)
                    adjusted_y = adjust_offsets(y, offset_8, offset_16, offset_24)
                    _, pcov = np.polyfit(x, adjusted_y, 1, cov=True, w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))


                    output.append((channel, stage4_tune, stage5_tune, popt[0], p_e[0], mean_temp))

                ax.legend()

                plt.savefig(f"{figure_save_folder}/coarse_consistency_plots/coarse_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)

                fig, ax = plt.subplots() # Histogram plots

                ax.hist(residuals, bins=np.arange(-15.5, 15.5, 1), label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")

                ax.grid(True, alpha=0.5)
                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune} Residuals")
                ax.set_xlabel("Delay Offset From Fit [ps]")
                ax.set_ylabel("Counts")
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_save_folder}/coarse_consistency_plots/coarse_delay_chan{channel}_run{run}_residuals.png", dpi=300, facecolor="#FFFFFF")
                plt.close()
            
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
        std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
        err = p_e[0]


        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{sigfig.round(weighted_mean, err)} [ps/step]")
        ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [ps/step]")
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

def plot_coarse_stage_test(data_save_folder, figure_save_folder, plot_temp=False):
    run = 0
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    figure_save_folder += "/coarse_stage_tests"
    no_file = False

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    if plot_temp:
        T = pd.read_csv(f"{data_save_folder}/temp_info.txt", skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])
        output = []

    for channel in range(2, 4, 1):
        for stage4_tune in [0, 2, 3]:
            for stage5_tune in [0, 2, 3]:
                plot_data = []
                for coarse_control in range(32):
                    print(f"Calculating coarse control: {coarse_control} channel: {channel} s4: {stage4_tune} s5: {stage5_tune}")
                    run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                    try:
                        mean_val, std_dev, count = get_data(data_save_folder, run_name)
                    except FileNotFoundError:
                        no_file = True
                        break
                    plot_data.append((coarse_control, mean_val, std_dev/np.sqrt(count), std_dev))
                
                if no_file:
                    no_file = False
                    continue
            
                fig, ax = plt.subplots() # Line plots

                plot_data = np.asarray(plot_data)

                x = plot_data.T[0]
                y = ((lambda channel: -1 if channel==2 else 1)(channel))*(plot_data.T[1]+300)%3125
                yerr = plot_data.T[2]
                ystd_dev = plot_data.T[3]
                y = y - y[0]

                popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
                p_e = np.sqrt(np.diag(pcov))

                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("bottom", size="30%", pad=0.1)
                residuals = y - (popt[0]*x + popt[1])
                residuals_std_dev = weighted_std_dev(0, residuals, yerr)

                ax.grid(True, alpha=0.5)
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [ps/step]\nReduced \u03c7\u00B2: {reduced_chi2(residuals, ystd_dev):.3f}")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")
                ax2.legend(loc="upper right", fontsize=5)
                if stage4_tune == 0 or stage5_tune == 0:
                    pass
                else:
                    ax2.set_ylim([-15, 15])

                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune}")
                ax2.set_xlabel("Coarse Step")
                ax.set_ylabel("Delay [ps]")
                if stage4_tune == 0 or stage5_tune == 0:
                    ax.set_ylim([-5, 200])
                else:
                    ax.set_ylim([-5, 260])

                if plot_temp:
                    target_temp = round(np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune})").temp))
                    mean_temp = np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune})").temp)
                    ylim = ax.get_ylim()
                    yrange = ylim[1] - ylim[0]
                    new_ylim = (target_temp-1, target_temp+1) # Use this to program new yaxis limits
                    new_yrange = new_ylim[1] - new_ylim[0]
                    
                    # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
                    # (and its inverse) for this to work correctly
                    temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
                    temp_ax.set_ylabel("Temperature [\u00b0C]")
                    temp_vals = T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune})").temp
                    temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
                    ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")

                    offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)
                    adjusted_y = adjust_offsets(y, offset_8, offset_16, offset_24)
                    _, pcov = np.polyfit(x, adjusted_y, 1, cov=True, w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))


                    output.append((channel, stage4_tune, stage5_tune, popt[0], p_e[0], mean_temp))
                    
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_save_folder}/coarse_plot_chan{channel}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                plt.close()

                fig, ax = plt.subplots() # Histogram plots

                if stage4_tune == 0 or stage5_tune == 0:
                    ax.hist(residuals, bins=np.arange(-50.5, 50.5, 5), label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")
                else:
                    ax.hist(residuals, bins=np.arange(-15.5, 15.5, 1), label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")

                ax.grid(True, alpha=0.5)
                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune} Residuals")
                ax.set_xlabel("Delay Offset From Fit [ps]")
                ax.set_ylabel("Counts")
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_save_folder}/coarse_plot_chan{channel}_s4{stage4_tune}_s5{stage5_tune}_residuals.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                plt.close()
    if plot_temp:
        return output            

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
                print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+300)%3125
            yerr = run_data.T[2]

            # weighted_mean = np.average(y, weights=1/yerr**2)
            # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

            popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
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
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{sigfig.round(weighted_mean, err)} [ps]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [ps]")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            ax.set_ylim([weighted_mean-0.4, weighted_mean+0.4])
        
            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Coarse Delay Cell Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}\nCell {coarse_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_coarse_cell_consistency_test.png", dpi=300, facecolor="#FFFFFF")

def plot_coarse_step_relative_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, num_runs=10, s4=[2, 3], s5=[2, 3], plot_temp=False):
    coarse_control = 0
    fine_control = 0

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/coarse_delay_relative_consistency_plots")
        except FileExistsError:
            pass
    
    if plot_temp:
        T = pd.read_csv(f"{data_save_folder}/temp_info.txt", skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])

    for stage4_tune in s4:
        for stage5_tune in s5:
            f = plt.figure(figsize=(10,128), dpi=100)
            f.subplots_adjust(top=0.994, bottom=0.006, hspace=0.5, wspace=0.3)
            for channel in range(2, 4, 1):
                channel_data = []
                for i, coarse_control in enumerate(range(32)):
                    run_data = []
                    for run in range(num_runs):
                        print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                        run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                        if coarse_control == 0:
                            prev_run_name = run_name
                        else:
                            prev_run_name = f"/chan{channel}_f{fine_control}_c{coarse_control-1}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                        try:
                            mean_val, std_dev, count = get_data(data_save_folder, run_name)
                            prev_mean_val, prev_std_dev, prev_count = get_data(data_save_folder, prev_run_name)
                        except FileNotFoundError:
                            continue
                        factor = ((lambda channel: -1 if channel==2 else 1)(channel))
                        mean_val = ((factor*(mean_val+300)%3125)-300) - ((factor*(prev_mean_val+300)%3125)-300)
                        if coarse_control != 0:
                            std_err = np.sqrt((std_dev/np.sqrt(count))**2 + (prev_std_dev/np.sqrt(prev_count))**2)
                        else:
                            std_err = std_dev/np.sqrt(count)
                        run_data.append((run, mean_val, std_err))
                
                    run_data = np.asarray(run_data)

                    x = run_data.T[0]
                    y = run_data.T[1]
                    yerr = run_data.T[2]

                    if plot_all_runs:
                        channel_data.append((coarse_control, y, yerr, x))

                    if num_runs > 1:
                        popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                        p_e = np.sqrt(np.diag(pcov))

                        weighted_mean = popt[0]
                        std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                        err = p_e[0]

                        ax = f.add_subplot(32, 2, channel-1 + 2*i)
                        ax.grid(True, alpha=0.5)
                        ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{sigfig.round(weighted_mean, err)} [ps]")
                        ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [ps]")
                        ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Coarse Delay")

                        ax.set_ylim([weighted_mean-0.6, weighted_mean+0.6])

                        ax.set_ylabel("Relative Delay [ps]")
                        ax.set_xlabel("Run Number")
                        ax.set_xticks(range(10))
                        ax.set_xticklabels(range(10))
                        ax.legend(loc="upper left",fontsize=8)
                        ax.set_title(f"Coarse Delay Relative Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune} | Coarse Step {coarse_control}")
        
                if plot_all_runs:
                    
                    for run in range(num_runs):
                        x = []
                        y = []
                        yerr = []
                        for coarse_control, y_run, y_run_err, runs in channel_data:
                            x.append(coarse_control)
                            y.append(y_run[run])
                            yerr.append(y_run_err[run])
                        
                        x = np.asarray(x)
                        y = np.asarray(y)
                        yerr = np.asarray(yerr)
                        
                        fig, ax = plt.subplots()

                        popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                        p_e = np.sqrt(np.diag(pcov))

                        weighted_mean = popt[0]
                        std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                        err = p_e[0]

                        ax.grid(True, alpha=0.5)
                        ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Steps\n{sigfig.round(weighted_mean, err)} [ps]")
                        ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Steps\n{sigfig.round(std_dev, err).split(' ')[0]} [ps]")
                        ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Coarse Step Delay")
                        ax.set_title(f"Coarse Delay Relative Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                        ax.set_ylim([-.1, 15])
                        ax.set_xlabel("Coarse Delay Step")
                        ax.set_ylabel("Delay [ps]")

                        if plot_temp:
                            target_temp = round(np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp))
                            ylim = ax.get_ylim()
                            yrange = ylim[1] - ylim[0]
                            new_ylim = (target_temp-1.5, target_temp+0.5) # Use this to program new yaxis limits
                            new_yrange = new_ylim[1] - new_ylim[0]
                            
                            # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
                            # (and its inverse) for this to work correctly
                            temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
                            temp_ax.set_ylabel("Temperature [\u00b0C]")
                            temp_vals = T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp
                            temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
                            ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")

                        ax.legend(loc="lower right")
                
                    fig.savefig(f"{figure_save_folder}/coarse_delay_relative_consistency_plots/relative_coarse_delay_chan{channel}_s4{stage4_tune}_s5{stage5_tune}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                    plt.close(fig)


                
            if num_runs > 1:
                f.savefig(f"{figure_save_folder}/dcps3_coarse_step_s4{stage4_tune}_s5{stage5_tune}_relative_consistency.pdf", dpi=100, facecolor="#FFFFFF")
            plt.close()

def plot_fine_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, plot_sim=False, num_runs=10, plot_temp=False):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 0
    stage5_tune = 0

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass
    if plot_all_runs:
        try:
            os.makedirs(f"{figure_save_folder}/fine_consistency_plots")
        except FileExistsError:
            pass
    
    if plot_temp:
        T = pd.read_csv(f"{data_save_folder}/temp_info.txt", skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])
        output = []

    for channel in range(2, 4, 1):
        channel_data = []
        for run in range(num_runs):
            run_data = []
            for fine_control in range(67):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((fine_control, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+300)%3125 
            yerr = run_data.T[2] * 1000 #-> convert to femtoseconds
            y = (y-y[0]) * 1000 # -> convert to femtoseconds

            channel_data.append((x, y, yerr, run))

            # channel_data.append((run, popt[0], p_e[0]))
    
        slope_data = []
        for x, y, yerr, run in channel_data:

            popt,pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            if plot_all_runs:
                fig, ax = plt.subplots()

                if plot_sim:
                    data = pd.read_csv("./dcps3Test/data/simulation/DCSP3_sims_fine.csv", 
                                        names = ["step", "0", "16", "31"])
                    
                    y0 = np.asarray(data["0"][1:], dtype=np.float64)
                    y0 = y0 - y0[0]
                    y16 = np.asarray(data["16"][1:], dtype=np.float64)
                    y16 = y16 - y16[0]
                    y31 = np.asarray(data["31"][1:], dtype=np.float64)
                    y31 = y31 - y31[0]

                    ax.plot(x, y0/1e3, color="magenta",   marker="o", markersize=3, linestyle='--', label="Simulation | Coarse Step: 0")
                    #ax.plot(x, y16, color="yellow",  marker="v", markersize=3, linestyle='--', label="Simulation | C Step: 16")
                    #ax.plot(x, y31, color="green",   marker="^", markersize=3, linestyle='--', label="Simulation | C Step: 31")
                
                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                residuals = y - (popt[0]*x + popt[1])
                residuals_std_dev = weighted_std_dev(0, residuals, yerr)

                ax.grid(True, alpha=0.5)
                ax.plot(x, (popt[0]*x+popt[1])/1e3,color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [fs/step]")
                ax.errorbar(x, y/1e3, yerr=yerr/1e3, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [fs]")
                ax2.legend(loc="upper right", fontsize=5)
                ax2.set_ylim(-300, 300)

                ax.set_title(f"Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax2.set_xlabel("Fine Step")
                ax.set_ylabel("Delay [ps]")
                ax2.set_ylabel("Residual [fs]")
                ax.set_ylim([-0.5, 25])

                if plot_temp:
                    target_temp = round(np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp))
                    ylim = ax.get_ylim()
                    yrange = ylim[1] - ylim[0]
                    new_ylim = (target_temp-1, target_temp+1) # Use this to program new yaxis limits
                    new_yrange = new_ylim[1] - new_ylim[0]
                    
                    # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
                    # (and its inverse) for this to work correctly
                    temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
                    temp_ax.set_ylabel("Temperature [\u00b0C]")
                    temp_vals = T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp
                    temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
                    ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")
                    output.append((channel, stage4_tune, stage5_tune, popt[0], p_e[0], target_temp))

                ax.legend()

                plt.savefig(f"{figure_save_folder}/fine_consistency_plots/fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                plt.close(fig)

                fig, ax = plt.subplots() # Histogram plots

                ax.hist(residuals, bins=np.arange(-310, 330, 20), label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [fs]")

                ax.grid(True, alpha=0.5)
                ax.set_title(f"Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} Residuals")
                ax.set_xlabel("Delay Offset From Fit [fs]")
                ax.set_ylabel("Counts")
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_save_folder}/fine_consistency_plots/fine_delay_chan{channel}_run{run}_residuals.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)
            
            slope_data.append((run, popt[0], p_e[0]))
    
        if num_runs > 1:

            slope_data = np.asarray(slope_data)
            x = slope_data.T[0]
            y = slope_data.T[1]
            yerr = slope_data.T[2]

            # weighted_mean = np.average(y, weights=1/yerr**2)
            # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

            popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
            err = p_e[0]

            ax = f.add_subplot(int(f"12{channel-1}"))
            ax.grid(True, alpha=0.5)
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{sigfig.round(weighted_mean, err)} [fs/step]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [fs/step]")
            ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

            ax.set_ylim([weighted_mean-5, weighted_mean+5])
            
            ax.set_ylabel("Delay per Fine Step [fs/step]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    if num_runs > 1:
        plt.savefig(f"{figure_save_folder}/dcps3_fine_consistency_test.png", dpi=300, facecolor="#FFFFFF")
    plt.close()

    if plot_temp:
        return output

def plot_fine_cell_consistency(data_save_folder, figure_save_folder):
    f = plt.figure(figsize=(10,268), dpi=100)
    f.subplots_adjust(top=0.997, bottom=0.003, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 0
    stage5_tune = 0

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 4, 1):
        for i, fine_control in enumerate(range(67)):
            run_data = []
            for run in range(10):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = (((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+300)%3125) * 1000 # convert to femtoseconds
            yerr = run_data.T[2] * 1000 # convert to femtoseconds

            # weighted_mean = np.average(y, weights=1/yerr**2)
            # err = weighted_std_dev(weighted_mean, y, 1/yerr**2)

            popt,pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
            err = p_e[0]

            if fine_control == 0:
                offset = weighted_mean
                weighted_mean = 0.0
                y = (y - offset)
            else:
                weighted_mean -= offset
                y = y - offset
        
            ax = f.add_subplot(67, 2, channel-1 + 2*i)
            ax.grid(True, alpha=0.5)
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{sigfig.round(weighted_mean, err)} [fs]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [fs]")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            ax.set_ylim([weighted_mean-400, weighted_mean+400])

            ax.set_ylabel("Delay [fs]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Cell Consistency Check\nChannel {channel}: Fine Cell {fine_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_fine_cell_consistency_test.pdf", dpi=100, facecolor="#FFFFFF")

def plot_fine_cell_relative_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, num_runs=10, plot_temp=False):
    f = plt.figure(figsize=(10,268), dpi=100)
    f.subplots_adjust(top=0.997, bottom=0.003, hspace=0.5, wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 0
    stage5_tune = 0
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
    
    if plot_temp:
        T = pd.read_csv(f"{data_save_folder}/temp_info.txt", skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])

    for channel in range(2, 4, 1):
        channel_data = []
        for i, fine_control in enumerate(range(67)):
            run_data = []
            for run in range(num_runs):
                print(f"Calculating fine control: {fine_control} channel: {channel} run: {run}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                if fine_control == 0:
                    prev_run_name = run_name
                else:
                    prev_run_name = f"chan{channel}_f{fine_control-1}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                prev_mean_val, prev_std_dev, prev_count = get_data(data_save_folder, prev_run_name)
                factor = ((lambda channel: -1 if channel==2 else 1)(channel))
                mean_val = ((factor*(mean_val+300)%3125)-300) - ((factor*(prev_mean_val+300)%3125)-300)
                if fine_control != 0:
                    std_err = np.sqrt((std_dev/np.sqrt(count))**2 + (prev_std_dev/np.sqrt(prev_count))**2)
                else:
                    std_err = std_dev/np.sqrt(count)
                run_data.append((run, mean_val, std_err))

            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = run_data.T[1] * 1000 # convert to femtoseconds
            yerr = run_data.T[2] * 1000 # convert to femtoseconds

            if plot_all_runs:
                channel_data.append((fine_control, y, yerr, x))

            if num_runs > 1:
                popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                p_e = np.sqrt(np.diag(pcov))

                weighted_mean = popt[0]
                std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                err = p_e[0]

                ax = f.add_subplot(67, 2, channel-1 + 2*i)
                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{sigfig.round(weighted_mean, err)} [fs]")
                ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [fs]")
                ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Delay")

                if fine_control == 0:
                    ax.set_ylim([-100, 100])
                else:
                    ax.set_ylim([0, 650])

                ax.set_ylabel("Relative Delay [fs]")
                ax.set_xlabel("Run Number")
                ax.set_xticks(range(10))
                ax.set_xticklabels(range(10))
                ax.legend(loc="upper left",fontsize=8)
                ax.set_title(f"Fine Delay Cell Relative Consistency Check\nChannel {channel} | Fine Cell {fine_control}")
        
        if plot_all_runs:
            
            for run in range(num_runs):
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
                std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                err = p_e[0]

                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Cells\n{sigfig.round(weighted_mean, err)} [fs]")
                ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Cells\n{sigfig.round(std_dev, err).split(' ')[0]} [fs]")
                ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Delay")
                ax.set_title(f"Fine Delay Cell Relative Consistency Check\nChannel {channel} | Run {run}")
                ax.set_ylim([-50, 600])

                if plot_temp:
                    target_temp = round(np.mean(T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp))
                    ylim = ax.get_ylim()
                    yrange = ylim[1] - ylim[0]
                    new_ylim = (target_temp-1.5, target_temp+0.5) # Use this to program new yaxis limits
                    new_yrange = new_ylim[1] - new_ylim[0]
                    
                    # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
                    # (and its inverse) for this to work correctly
                    temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
                    temp_ax.set_ylabel("Temperature [\u00b0C]")
                    temp_vals = T.query(f"(chan=={channel}) & (s4=={stage4_tune}) & (s5=={stage5_tune}) & run=={run}").temp
                    temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
                    ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")

                ax.set_xlabel("Fine Delay Step")
                ax.set_ylabel("Delay [fs]")
                ax.legend(loc="lower right")

                fig.savefig(f"{figure_save_folder}/fine_delay_relative_consistency_plots/relative_fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                plt.close(fig)


                
    if num_runs > 1:
        f.savefig(f"{figure_save_folder}/dcps3_fine_cell_relative_consistency.pdf", dpi=100, facecolor="#FFFFFF")
    plt.close()

def plot_approximate_coarse_fine_test(board_save_folder, figure_save_folder): # approximation based on seperate coarse and fine delay tests
    f = plt.figure(figsize=(6,5))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    run = 0

    def get_best_delay(delay_steps, step, step_size):
        ideal_delays = step_size*np.arange(len(delay_steps))
        delays = delay_steps.T[2]

        
        closest_delay = min(delays, key=lambda y: abs(ideal_delays[step]-y))
        i = np.where(delays==closest_delay)[0][0] # index value of closest delay value

        # if 600 <= step <= 650:
        #     print(index, abs(last_step+step_size - closest_delay)*1e3, closest_delay, delays[i])

        return int(delay_steps[i][0]), int(delay_steps[i][1])


    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 3, 1):
        channel_data = []
        fine_control = 0
        coarse_data = []
        fine_data = []

        for coarse_control in range(32):
            #print(f"Calculating coarse control: {coarse_control} channel: {channel}")
            run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
            data_save_folder = f"{board_save_folder}/N{N}_coarse"
            mean_val, std_dev, count = get_data(data_save_folder, run_name)
            coarse_data.append((coarse_control, mean_val, std_dev/np.sqrt(count)))

        coarse_control = 0
        for fine_control in range(67):
            #print(f"Calculating fine control: {fine_control} channel: {channel}")
            data_save_folder = f"{board_save_folder}/N{N}_fine"
            run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
            mean_val, std_dev, count = get_data(data_save_folder, run_name)
            fine_data.append((fine_control, mean_val, std_dev/np.sqrt(count)))
        
        coarse_data = np.asarray(coarse_data)
        fine_data = np.asarray(fine_data)

        coarse_step = coarse_data.T[0]
        coarse_delay = ((lambda channel: -1 if channel==2 else 1)(channel))*(coarse_data.T[1]+300)%3125 
        coarse_err = coarse_data.T[2]
        coarse_delay = coarse_delay - coarse_delay[0]

        fine_step = fine_data.T[0]
        fine_delay = ((lambda channel: -1 if channel==2 else 1)(channel))*(fine_data.T[1]+300)%3125 
        fine_err = fine_data.T[2]
        fine_delay = fine_delay - fine_delay[0]

        max_delay = coarse_delay[-1] + fine_delay[-1]

        popt, pcov = np.polyfit(fine_step, fine_delay, 1, cov=True, w=1/fine_err**2) # Get initial fine slope

        step_size = popt[0]
        offset = popt[1]

        all_possible_steps = []

        for cstep, cdelay in enumerate(coarse_delay):
                for fstep, fdelay in enumerate(fine_delay):
        
                    total_delay = cdelay + fdelay

                    all_possible_steps.append((cstep, fstep, total_delay))
        
        all_possible_steps = np.asarray(all_possible_steps)
        val = 0
        j = 0
        test = []
        while val < max_delay - 2*step_size:
            cstep, fstep = get_best_delay(all_possible_steps, j, step_size)

            val = coarse_delay[cstep] + fine_delay[fstep]

            if fstep == 0:
                err = coarse_err[cstep]
            else:
                err = np.sqrt(coarse_err[cstep]**2 + fine_err[fstep]**2)

            channel_data.append((cstep, fstep, val, err))

            j+=1
            




        channel_data = np.asarray(channel_data)
        test = np.asarray(test)

        x = np.asarray(range(len(channel_data.T[0])))
        x1 = channel_data.T[0] # coarse delay step
        x2 = channel_data.T[1] # fine delay step
        y = channel_data.T[2] # delay
        yerr = channel_data.T[3] # err

        ax = f.add_subplot(1, 1, channel-1)

        popt, pcov = np.polyfit(x, y, 1, cov=True, w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        divider = make_axes_locatable(ax)
        ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
        residuals = y - (popt[0]*x + popt[1])
        residuals_std_dev = weighted_std_dev(0, residuals, yerr)

        ax.grid(True, alpha=0.5)
        ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0]*1e3, p_e[0]*1e3)} [fs/step]")
        ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, errorevery=29, markevery=29, label="Total Delay")

        ax2.grid(True, alpha=0.5)
        ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
        ax2.errorbar(x, residuals*1e3, yerr=yerr*1e3, fmt='r.', ecolor="black", capsize=2, errorevery=29, markevery=29, label="Residuals")
        ax2.fill_between(x, residuals_std_dev*1e3, -residuals_std_dev*1e3, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev*1e3, p_e[0]*1e3).split(' ')[0]} [fs]")
        ax2.legend(loc="upper right", fontsize=5)
        ax2.set_ylim(-200, 200)

        ax.set_title(f"Total Coarse and Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
        ax.set_xticks(range(0, len(y), 29))
        ax2.set_xlabel("(Coarse, Fine) Step")
        ax2.set_xticks(range(0, len(y), 29))
        ax2.set_xticklabels([f"({int(x1[i])}, {int(x2[i])})" for i in range(0, len(y), 29)], rotation=45, size=5)
        ax.set_ylabel("Delay [ps]")
        ax2.set_ylabel("Residual [fs]")
        ax2.set_yticks(range(-200, 201, 100))
        ax2.set_yticklabels(range(-200, 201, 100))
        ax.legend()
        ax.set_ylim([-5, 300])

        plt.savefig(f"{figure_save_folder}/dcps3_approx_coarse_fine_test_chan{channel}.png", dpi=300, facecolor="#FFFFFF")
        plt.close()

        f, ax = plt.subplots()

        ax.hist(residuals*1e3, bins=np.arange(-202.5, 202.5, 5), label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev*1e3, p_e[0]*1e3).split(' ')[0]} [fs]")

        ax.grid(True, alpha=0.5)
        ax.set_title(f"Total Coarse and Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} Residuals")
        ax.set_xlabel("Delay Offset From Fit [fs]")
        ax.set_ylabel("Counts")
        ax.legend(loc="upper left")

        plt.savefig(f"{figure_save_folder}/dcps3_approx_coarse_fine_test_chan{channel}_residuals.png", dpi=300, facecolor="#FFFFFF")
        plt.close()

        with open("C:/Users/zache/Desktop/Work/Slides/BHM-DCPS Update 08_18_23/all_points.txt", "w") as fp:
            for cstep, fstep in zip(x1, x2):
                fp.write(f"{int(cstep)}, {int(fstep)}\n")


def plot_coarse_fine_test(data_save_folder, figure_save_folder, plot_raw=False):
    f = plt.figure(figsize=(10,4))
    f.subplots_adjust(wspace=0.3)
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    run = 0

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 4, 1):
        best_linear_data = []
        channel_data = []
        for coarse_control in range(32):
            fine_data = []
            for fine_control in range(67):
                print(f"Calculating fine control: {fine_control} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                fine_data.append((fine_control, mean_val, std_dev/np.sqrt(count)))

            fine_data = np.asarray(fine_data)
            channel_data.append((coarse_control, fine_data))
        
        raw_x = []
        raw_y = []
        raw_yerr = []

        for coarse_control, fine_data in channel_data:
            
            fine_control = fine_data.T[0]
            delay = ((lambda channel: -1 if channel==2 else 1)(channel))*(fine_data.T[1]+300)%3125 
            std_err = fine_data.T[2]

            if plot_raw:
                raw_x.extend(fine_control)
                raw_y.extend(delay)
                raw_yerr.extend(std_err)

            if coarse_control == 0:
                popt, pcov = np.polyfit(fine_control, delay, 1, cov=True, w=1/std_err**2) # get initial slope
                step_size = popt[0]

                best_linear_data.append((coarse_control, fine_control, delay, std_err))
                max_val = delay[-1]

            else:
                closest_delay = min(delay, key=lambda y: abs(max_val+step_size-y))
                i = np.where(delay==closest_delay)[0][0] # index value of closest delay value

                max_val = delay[-1]

                best_linear_data.append((coarse_control, fine_control[i], delay[i], std_err[i]))

        best_linear_data = np.asarray(best_linear_data)

        x1 = best_linear_data.T[0] # coarse step value
        x2 = best_linear_data.T[1] # minimum fine step value
        y = best_linear_data.T[2] 
        yerr = best_linear_data[3]

        y = y-y[0]

        if plot_raw:

            fig, ax = plt.subplots()

            raw_x = np.asarray(raw_x)
            raw_y = np.asarray(raw_y)
            raw_yerr = np.asarray(raw_yerr)

            raw_y = raw_y - raw_y[0]

            ax.grid(True, alpha=0.5)
            ax.errorbar(raw_x, raw_y, raw_yerr, fmt='r.', ecolor='k', capsize=2, label="Total Delay")

            ax.set_title(f"Total Coarse and Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
            ax2.set_xlabel("(Coarse, Fine) Step")
            ax.set_xticks(range(32))
            ax.set_xticklabels([f"({i//66}, {f})" for i, f in enumerate(raw_x)])
            ax.set_ylabel("Delay [ps]")
            ax2.set_ylabel("Residual [ps]")
            ax.legend()
            ax.set_ylim([-5, 300])

            fig.savefig(f"{figure_save_folder}/dcps3_coarse_fine_test_raw.png", dpi=300, facecolor="#FFFFFF")
            plt.close(fig)

        ax = f.add_subplot(1, 2, channel-1)

        popt, pcov = np.polyfit(x1, y, 1, cov=True, w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        divider = make_axes_locatable(ax)
        ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
        residuals = y - (popt[0]*x1 + popt[1])
        residuals_std_dev = weighted_std_dev(0, residuals, yerr)

        ax.grid(True, alpha=0.5)
        ax.plot(x1, popt[0]*x1+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [ps/step]")
        ax.errorbar(x1, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Total Delay")

        ax2.grid(True, alpha=0.5)
        ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
        ax2.errorbar(x1, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
        ax2.fill_between(x1, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]).split(' ')[0]} [ps]")
        ax2.legend(loc="upper right", fontsize=5)
        ax2.set_ylim(-15, 15)

        ax.set_title(f"Total Coarse and Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
        ax2.set_xlabel("(Coarse, Fine) Step")
        ax.set_xticks(range(32))
        ax.set_xticklabels([f"({c}, {f})" for c, f in zip(x1, x2)])
        ax.set_ylabel("Delay [ps]")
        ax2.set_ylabel("Residual [ps]")
        ax.legend()
        ax.set_ylim([-5, 300])

    plt.savefig(f"{figure_save_folder}/dcps3_coarse_fine_test.png", dpi=300, facecolor="#FFFFFF")
    plt.close()
        
def plot_temp_test(data_save_folder, figure_save_folder):
    data_folders = glob(f"{data_save_folder}_*C")


    coarse_data = []
    fine_data = []

    for i, data_folder in enumerate(data_folders):
        figure_folder = figure_save_folder + f"_{i*20 + 20}C"
        print(f"{data_folder} goes to {figure_folder}")
        continue
        coarse_stage_data = plot_coarse_stage_test(f"{data_folder}/N{N}_coarse_stage_test", figure_folder, plot_temp=True)
        #plot_coarse_step_relative_consistency(f"{data_folder}/N{N}_coarse_stage_test", figure_folder, plot_all_runs=True, num_runs=1, plot_temp=True)
        fine_step_data = plot_fine_consistency(f"{data_folder}/N{N}_fine", figure_folder, plot_all_runs=True, num_runs=1, plot_temp=True)
        #plot_fine_cell_relative_consistency(f"{data_folder}/N{N}_fine/", figure_folder, plot_all_runs=True, num_runs=1, plot_temp=True)

        coarse_data.extend(coarse_stage_data)
        fine_data.extend(fine_step_data)
    return
    f = plt.figure(figsize=(10, 8))
    f.subplots_adjust(wspace=0.3, hspace=0.4)

    ideal_stage4 = 2
    ideal_stage5 = 2

    for channel in [2, 3]:

        x = [vals[5] for vals in coarse_data if (vals[0] == channel and vals[1]==ideal_stage4 and vals[2]==ideal_stage5)]
        y = [vals[3] for vals in coarse_data if (vals[0] == channel and vals[1]==ideal_stage4 and vals[2]==ideal_stage5)]
        yerr = [vals[4] for vals in coarse_data if (vals[0] == channel and vals[1]==ideal_stage4 and vals[2]==ideal_stage5)]
        x = np.asarray(x)
        y = np.asarray(y)
        yerr = np.asarray(yerr)

        ax = f.add_subplot(2, 2, (channel-1))

        popt, pcov = np.polyfit(x, y, 1, cov=True, w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        ax.grid(alpha=0.5)
        ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0]*1000, p_e[0]*1000)} [(fs/step)/\u00b0C]")
        ax.errorbar(x, y, yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")
        
        ax.set_xlabel("Mean Temperature [\u00b0C]")
        ax.set_ylabel("Delay per Coarse Step [ps/step]")
        plt.xticks(np.arange(20, 100, 20))
        ax.set_title(f"Temperature Tests Coarse Delays\nChannel {channel}: {ideal_stage4} {ideal_stage5}")
        ax.legend(loc="best")

        ax = f.add_subplot(2, 2, (channel+1))

        x = [vals[5] for vals in fine_data if (vals[0] == channel)]
        y = [vals[3] for vals in fine_data if (vals[0] == channel)]
        yerr = [vals[4] for vals in fine_data if (vals[0] == channel)]
        x = np.asarray(x)
        y = np.asarray(y)
        yerr = np.asarray(yerr)

        popt, pcov = np.polyfit(x, y, 1, cov=True, w=1/yerr**2)
        p_e = np.sqrt(np.diag(pcov))

        ax.grid(alpha=0.5)
        ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [(fs/step)/\u00b0C]")
        ax.errorbar(x, y, yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")
        
        ax.set_xlabel("Mean Temperature [\u00b0C]")
        ax.set_ylabel("Delay per Fine Step [fs/step]")
        plt.xticks(np.arange(20, 100, 20))
        ax.set_title(f"Temperature Tests Fine Delays\nChannel {channel}: 0 0")
        ax.legend(loc="best")

    plt.savefig(f"{figure_save_folder}/temperature_test.png", dpi=300, facecolor="#FFFFFF")
    plt.close()


BOARD = "board1_shortcable_test"

#plot_coarse_consistency(f"./dcps3Test/data/{BOARD}/N{N}_coarse", f"./dcps3Test/figures/{BOARD}", True, False, plot_temp=True)
plot_fine_consistency(f"./dcps3Test/data/{BOARD}/N{N}_fine", f"./dcps3Test/figures/{BOARD}", True, False, num_runs=1)
# plot_coarse_cell_consistency(f"./dcps3Test/data/{BOARD}/N{N}_coarse", f"./dcps3Test/figures/{BOARD}")
# plot_fine_cell_consistency(f"./dcps3Test/data/{BOARD}/N{N}_fine_cell", f"./dcps3Test/figures/{BOARD}")
# plot_fine_cell_relative_consistency(f"./dcps3Test/data/{BOARD}/N{N}_fine/", f"./dcps3Test/figures/{BOARD}", True)
plot_coarse_stage_test(f"./dcps3Test/data/{BOARD}/N{N}_coarse_stage_test", f"./dcps3Test/figures/{BOARD}")
# plot_coarse_step_relative_consistency(f"./dcps3Test/data/{BOARD}/N{N}_coarse", f"./dcps3Test/figures/{BOARD}", True, plot_temp=True, s4=[2], s5=[2])
# plot_approximate_coarse_fine_test(f"./dcps3Test/data/{BOARD}", f"./dcps3Test/figures/{BOARD}")
# plot_temp_test(f"./dcps3Test/data/{BOARD}", f"./dcps3Test/figures/{BOARD}")