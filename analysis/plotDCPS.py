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

def format_value_err(value, err):
    """
    Outputs a formatted string to show value+/-err with proper
    significant figures.
    """
    if err == 0:
        return f"{value}+/-{err}"
    if err < 1:
        dec_digits = -int(np.log10(err)) + 2
        return f"{value:.{dec_digits}f}+/-{err:.{dec_digits}f}"
    
    elif err < 100:
        dec_digits = -int(np.log10(err)) + 1
        return f"{value:.{dec_digits}f}+/-{err:.{dec_digits}f}"
    
    else:
        err = float(f"{err:.2g}")
        err_power = int(np.log10(err))
        value = round(value, -err_power+1)
        if value != 0:
            value_power = int(np.log10(value))
            power_diff = value_power - err_power
            if power_diff == -1:
                return f"({str(value)[0]}+/-{str(err/10)[0:2]})e{value_power}"
            elif power_diff == 0:
                return f"({str(value)[0]}.{str(value)[1:-err_power-1]}+/-{str(err)[0]}.{str(err)[1]})e{value_power}"
            else:
                return f"({str(value)[0]}.{str(value)[1:-err_power-1]}+/-0.{'0'*(power_diff-1)}{str(err)[0:2]})e{value_power}"
        else:
            return f"(0+/-{str(err)[0]}.{str(err)[1]})e{err_power}"
        



def plot_coarse_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, plot_sim=False):
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
                #print(f"Calculating coarse control: {coarse_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                print(count)
                run_data.append((coarse_control, mean_val, std_dev/np.sqrt(count)))

            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+200)%3125
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

                    ax.plot(x, y00, color="orange",  marker="o", markersize=3, linestyle='--', label="Simulation | S4: 0, S5: 0")
                    ax.plot(x, y23, color="yellow",  marker="v", markersize=3, linestyle='--', label="Simulation | S4: 2, S5: 3")
                    ax.plot(x, y13, color="green",   marker="^", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 3")
                    ax.plot(x, y11, color="purple",  marker="<", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 1")
                    ax.plot(x, y12, color="magenta", marker=">", markersize=3, linestyle='--', label="Simulation | S4: 1, S5: 2")
                    ax.plot(x, y01, color="pink",    marker="s", markersize=3, linestyle='--', label="Simulation | S4: 0, S5: 1")
                
                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                residuals = y - (popt[0]*x + popt[1])
                residuals_std_dev = weighted_std_dev(0, residuals, yerr)

                ax.grid(True, alpha=0.5)
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{format_value_err(popt[0], p_e[0])} [ps/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{residuals_std_dev:4.2} [ps]")
                ax2.legend(loc="upper right", fontsize=5)
                ax2.set_ylim(-15, 15)

                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax2.set_xlabel("Coarse Step")
                ax.set_ylabel("Delay [ps]")
                ax2.set_ylabel("Residual [ps]")
                ax.legend()
                ax.set_ylim([-5, 300])

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
        std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
        err = p_e[0]


        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{format_value_err(weighted_mean, err)} [ps/step]")
        ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{std_dev:4.2} [ps/step]")
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

def plot_coarse_stage_test(data_save_folder, figure_save_folder):
    run = 0
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3

    figure_save_folder += "/coarse_stage_tests"
    print(figure_save_folder)
    no_file = False

    try:
        os.makedirs(figure_save_folder)
    except FileExistsError:
        pass

    for channel in range(2, 4, 1):
        for stage4_tune in range(2, 4, 1):
            for stage5_tune in range(2, 4, 1):
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
            
                fig, ax = plt.subplots()

                plot_data = np.asarray(plot_data)

                x = plot_data.T[0]
                y = ((lambda channel: -1 if channel==2 else 1)(channel))*(plot_data.T[1]+200)%3125
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
                ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{format_value_err(popt[0], p_e[0])} [ps/step]\nReduced \u03c7\u00B2: {reduced_chi2(residuals, ystd_dev):.3f}")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{residuals_std_dev:4.2} [ps]")
                ax2.legend(loc="upper right", fontsize=5)
                ax2.set_ylim(-15, 15)

                ax.set_title(f"Coarse Delay\nChannel {channel}: {stage4_tune} {stage5_tune}")
                ax2.set_xlabel("Coarse Step")
                ax.set_ylabel("Delay [ps]")
                ax.legend(loc="upper left")
                ax.set_ylim([-5, 300])

                plt.savefig(f"{figure_save_folder}/coarse_plot_chan{channel}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
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
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+200)%3125
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
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{format_value_err(weighted_mean, err)} [ps]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{std_dev:4.2} [ps]")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            ax.set_ylim([weighted_mean-0.4, weighted_mean+0.4])
        
            ax.set_ylabel("Delay [ps]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Coarse Delay Cell Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}\nCell {coarse_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_coarse_cell_consistency_test.png", dpi=300, facecolor="#FFFFFF")

def plot_fine_consistency(data_save_folder, figure_save_folder, plot_all_runs=False, plot_sim=False):
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
            for fine_control in range(67):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((fine_control, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)
            x = run_data.T[0]
            y = ((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+200)%3125 
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

                    ax.plot(x, y0, color="orange",   marker="o", markersize=3, linestyle='--', label="Simulation | C Step: 0")
                    ax.plot(x, y16, color="yellow",  marker="v", markersize=3, linestyle='--', label="Simulation | C Step: 16")
                    ax.plot(x, y31, color="green",   marker="^", markersize=3, linestyle='--', label="Simulation | C Step: 31")
                
                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                residuals = y - (popt[0]*x + popt[1])
                residuals_std_dev = weighted_std_dev(0, residuals, yerr)

                ax.grid(True, alpha=0.5)
                ax.plot(x, (popt[0]*x+popt[1])/1e3,color="b",linestyle='--',label=f"Channel {channel} \n{format_value_err(popt[0], p_e[0])} [fs/step]")
                ax.errorbar(x, y/1e3, yerr=yerr/1e3, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

                ax2.grid(True, alpha=0.5)
                ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                ax2.errorbar(x, residuals, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{residuals_std_dev:.1f} [fs]")
                ax2.legend(loc="upper right", fontsize=5)
                ax2.set_ylim(-300, 300)

                ax.set_title(f"Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                ax2.set_xlabel("Fine Step")
                ax.set_ylabel("Delay [ps]")
                ax2.set_ylabel("Residual [fs]")
                ax.legend()
                ax.set_ylim([-0.5, 20])

                plt.savefig(f"{figure_save_folder}/fine_consistency_plots/fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
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
        std_dev = weighted_std_dev(weighted_mean, y, 1/yerr**2)
        err = p_e[0]

        ax = f.add_subplot(int(f"12{channel-1}"))
        ax.grid(True, alpha=0.5)
        ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{format_value_err(weighted_mean, err)} [fs/step]")
        ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{std_dev:.1f} [fs/step]")
        ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

        ax.set_ylim([weighted_mean-5, weighted_mean+5])
        
        ax.set_ylabel("Delay per Fine Step [fs/step]")
        ax.set_xlabel("Run Number")
        ax.set_xticks(range(10))
        ax.set_xticklabels(range(10))
        ax.legend(loc="upper left",fontsize=8)
        ax.set_title(f"Fine Delay Consistency Check\nChannel {channel}: {stage4_tune} {stage5_tune}")
    plt.savefig(f"{figure_save_folder}/dcps3_fine_consistency_test.png", dpi=300, facecolor="#FFFFFF")
    plt.close()

def plot_fine_cell_consistency(data_save_folder, figure_save_folder):
    f = plt.figure(figsize=(10,268), dpi=100)
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
        for i, fine_control in enumerate(range(67)):
            run_data = []
            for run in range(10):
                print(f"Calculating fine control: {fine_control} run: {run} channel: {channel}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                run_data.append((run, mean_val, std_dev/np.sqrt(count)))
            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = (((lambda channel: -1 if channel==2 else 1)(channel))*(run_data.T[1]+200)%3125) * 1000 # convert to femtoseconds
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
            ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{format_value_err(weighted_mean, err)} [fs]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{std_dev:.0f} [fs]")
            ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Cell Delay")

            ax.set_ylim([weighted_mean-400, weighted_mean+400])

            ax.set_ylabel("Delay [fs]")
            ax.set_xlabel("Run Number")
            ax.set_xticks(range(10))
            ax.set_xticklabels(range(10))
            ax.legend(loc="upper left",fontsize=8)
            ax.set_title(f"Fine Delay Cell Consistency Check\nChannel {channel}: Fine Cell {fine_control}")
    plt.savefig(f"{figure_save_folder}/dcps3_fine_cell_consistency_test.pdf", dpi=100, facecolor="#FFFFFF")

def plot_fine_cell_relative_consistency(data_save_folder, figure_save_folder, plot_all_runs=False):
    f = plt.figure(figsize=(10,268), dpi=100)
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
        for i, fine_control in enumerate(range(67)):
            run_data = []
            for run in range(10):
                print(f"Calculating fine control: {fine_control} channel: {channel} run: {run}")
                run_name = f"/chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                if fine_control == 0:
                    prev_run_name = run_name
                else:
                    prev_run_name = f"chan{channel}_f{fine_control-1}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
                mean_val, std_dev, count = get_data(data_save_folder, run_name)
                prev_mean_val, prev_std_dev, prev_count = get_data(data_save_folder, prev_run_name)
                factor = ((lambda channel: -1 if channel==2 else 1)(channel))
                mean_val = ((factor*(mean_val+200)%3125)-200) - ((factor*(prev_mean_val+200)%3125)-200)
                if fine_control != 0:
                    std_err = std_dev/np.sqrt(count) + prev_std_dev/np.sqrt(prev_count)
                run_data.append((run, mean_val, std_err))

            run_data = np.asarray(run_data)

            x = run_data.T[0]
            y = run_data.T[1] * 1000 # convert to femtoseconds
            yerr = run_data.T[2] * 1000 # convert to femtoseconds

            if plot_all_runs:
                channel_data.append((fine_control, y, yerr, x))

            popt,pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
            p_e = np.sqrt(np.diag(pcov))

            weighted_mean = popt[0]
            std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
            err = p_e[0]

            ax = f.add_subplot(67, 2, channel-1 + 2*i)
            ax.grid(True, alpha=0.5)
            ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Mean Delay All Runs\n{format_value_err(weighted_mean, err)} [fs]")
            ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{std_dev:.0f} [fs]")
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
                std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                err = p_e[0]

                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Cells\n{format_value_err(weighted_mean, err)} [fs]")
                ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Cells\n{std_dev:.0f} [fs]")
                ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Delay")
                ax.set_title(f"Fine Delay Cell Relative Consistency Check\nChannel {channel} | Run {run}")
                ax.set_ylim([-50, 600])
                ax.set_xlabel("Fine Delay Step")
                ax.set_ylabel("Delay [fs]")
                ax.legend(loc="lower right")

                fig.savefig(f"{figure_save_folder}/fine_delay_relative_consistency_plots/relative_fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF")
                plt.close(fig)


                

    f.savefig(f"{figure_save_folder}/dcps3_fine_cell_relative_consistency.pdf", dpi=100, facecolor="#FFFFFF")
    plt.close()


#plot_coarse_consistency(f"./dcps3Test/data/board1/N{N}_coarse", f"./dcps3Test/figures/board1", True)
#plot_fine_consistency(f"./dcps3Test/data/board1/N{N}_fine", f"./dcps3Test/figures/board1", True)
#plot_coarse_cell_consistency(f"./dcps3Test/data/board1/N{N}_coarse", f"./dcps3Test/figures/board1")
#plot_fine_cell_consistency(f"./dcps3Test/data/board1/N{N}_fine_cell", f"./dcps3Test/figures/board1")
#plot_fine_cell_relative_consistency(f"./dcps3Test/data/board1/N{N}_fine/", f"./dcps3Test/figures/board1", True)
plot_coarse_stage_test(f"./dcps3Test/data/board1/N{N}_coarse_stage_test", f"./dcps3Test/figures/board1")