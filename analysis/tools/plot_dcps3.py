# Written by Zachariah Eberle zachariah.eberle@gmail.com
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import sigfig

def _parse_fstring(string, **kwargs):
    """
    Used for parsing a pseudo f-string so that users can modify titles/labels based on
    variable states:
    i.e. change title from channel 2 to channel 3 when plotting different channels
    """
    print(kwargs)
    start = False
    replace_pos = []
    for i, chr in enumerate(string):
        if chr == "{":
            l = i+1
            start = True
        elif chr == "}" and start:
            r = i
            start = False
            replace_pos.append((l, r))
    for pos in reversed(replace_pos):
        if string[pos[0]:pos[1]] in kwargs:
            string = string[0:pos[0]-1] + str(kwargs[string[pos[0]:pos[1]]]) + string[pos[1]+1:]
    return string

def weighted_std_dev(mean, values, weights):
    total = 0
    for value, weight in zip(values, weights):
        total += weight*(mean - value)**2
    return np.sqrt(total / (((len(values)-1)/len(values)) * sum(weights)))

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

def add_temp_plot(data, ax):
    target_temp = round(np.mean(data.temperature))
    mean_temp = np.mean(data.temperature)
    x = np.asarray(data.coarse_step)
    ylim = ax.get_ylim()
    yrange = ylim[1] - ylim[0]
    new_ylim = (target_temp-1, target_temp+1) # Use this to program new yaxis limits
    new_yrange = new_ylim[1] - new_ylim[0]
    
    # secondary axis is a really jank workaround because twinx doesn't work easily with a divider, so I have to set a fancy conversion function
    # (and its inverse) for this to work correctly
    temp_ax = ax.secondary_yaxis("right", functions=(lambda z: (z-ylim[0])/(yrange/new_yrange) + new_ylim[0], lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0]))
    temp_ax.set_ylabel("Temperature [\u00b0C]")
    temp_vals = data.temperature
    temp_vals = list(map(lambda w: (w-new_ylim[0])*(yrange/new_yrange)+ylim[0], temp_vals))
    ax.plot(x, temp_vals, color="green", linestyle=":", marker=".", label="Temperature")

def plot_generic():
    pass

def coarse_delay(_data, figure_folder, **kwargs):
    """
    Plots the coarse step vs the total delay for all 32 coarse steps. 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [2])
    stage5_vals = kwargs.setdefault("stage5_vals", [2])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals
    
    for run in runs:
        for stage4_tune in stage4_vals:
            for stage5_tune in stage5_vals:
                for channel in channels:
                    fig, ax = plt.subplots()
            
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("coarse_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                    x = np.asarray(data.coarse_step)
                    y = np.asarray(data.delay)
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)

                    adjusted_y = adjust_offsets(y, offset_8, offset_16, offset_24)

                    _, pcov = np.polyfit(x,adjusted_y,1,cov=True,w=1/yerr**2) # Get only error from adjusted slope
                    p_e = np.sqrt(np.diag(pcov))
                    popt, _ = np.polyfit(x,y,1,cov=True,w=1/yerr**2) # Get actual slope from raw data

                    ax.grid(True, alpha=0.5)
                    ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0], p_e[0])} [ps/step]")
                    ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                    divider = make_axes_locatable(ax)
                    ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                    residuals = y - (popt[0]*x + popt[1])
                    residuals_std_dev = weighted_std_dev(0, residuals, yerr)

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

                    if add_temp_values:
                        add_temp_plot(data, ax)
                    
                    ax.legend(loc="upper left")

                    plt.savefig(f"{figure_folder}/coarse_delay_chan{channel}_run{run}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                    plt.close()

def coarse_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of (coarse step vs the total delay) vs all runs (The delay per step over all runs). 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [2])
    stage5_vals = kwargs.setdefault("stage5_vals", [2])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals

    for stage4_tune in stage4_vals:
        for stage5_tune in stage5_vals:
            for channel in channels:
                f, ax = plt.subplots()
                channel_data = []

                for run in runs:
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("coarse_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue

                    x = np.asarray(data.coarse_step)
                    y = np.asarray(data.delay)
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    offset_8, offset_16, offset_24 = find_offsets(x, y, yerr)

                    adjusted_y = adjust_offsets(y, offset_8, offset_16, offset_24)

                    _, pcov = np.polyfit(x,adjusted_y,1,cov=True,w=1/yerr**2) # Get only error from adjusted slope
                    p_e = np.sqrt(np.diag(pcov))
                    popt, _ = np.polyfit(x,y,1,cov=True,w=1/yerr**2) # Get actual slope from raw data

                    channel_data.append((run, popt[0], p_e[0]))

                channel_data = np.asarray(channel_data)

                x = channel_data.T[0] # run number
                y = channel_data.T[1] # delay slope
                yerr = channel_data.T[2] # delay slope error

                popt, pcov = np.polyfit(x, y, 0, cov=True, w=1/yerr**2)
                p_e = np.sqrt(np.diag(pcov))

                weighted_mean = popt[0]
                std_dev = weighted_std_dev(weighted_mean, y, yerr)
                err = p_e[0]

                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{sigfig.round(weighted_mean, err)} [ps/step]")
                ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [ps/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Coarse Step")

                ax.set_xticks(runs)
                ax.set_xticklabels(runs)
                ax.set_title(f"Coarse Delay Consistency\nChannel {channel}: {stage4_tune} {stage5_tune}")
                ax.set_xlabel("Run Number")
                ax.set_ylabel("Delay per Coarse Step [ps/step]")
                ax.set_ylim([weighted_mean-0.2, weighted_mean+0.2])
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_folder}/coarse_consistency_chan{channel}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF")
                plt.close()
                    
def coarse_relative_consistency(_data, figure_folder, **kwargs): 
    """
    Plots the coarse step vs the delay relative to the cell beneath it for all 32 coarse steps. 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [2])
    stage5_vals = kwargs.setdefault("stage5_vals", [2])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals
    
    for run in runs:
        for stage4_tune in stage4_vals:
            for stage5_tune in stage5_vals:
                for channel in channels:
                    fig, ax = plt.subplots()
            
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("coarse_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                    x = np.asarray(data.coarse_step)
                    y = np.asarray([0] + [data.delay.to_numpy()[i+1] - data.delay.to_numpy()[i] for i in range(len(data.delay)-1)])
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    popt, pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                    p_e = np.sqrt(np.diag(pcov))

                    weighted_mean = popt[0]
                    std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                    err = p_e[0]

                    ax.grid(True, alpha=0.5)
                    ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Steps\n{sigfig.round(weighted_mean, err)} [ps]")
                    ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Steps\n{sigfig.round(std_dev, err).split(' ')[0]} [ps]")
                    ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Coarse Step Delay")
                    ax.set_title(f"Coarse Delay Relative Step Consistency\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                    ax.set_ylim([-.1, 15])
                    ax.set_xlabel("Coarse Delay Step")
                    ax.set_ylabel("Delay [ps]")

                    if add_temp_values:
                        add_temp_plot(data, ax)
                    
                    ax.legend(loc="lower right")

                    plt.savefig(f"{figure_folder}/coarse_relative_consistency_chan{channel}_run{run}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                    plt.close()

def coarse_cell_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of individual coarse cells vs all runs. 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [2])
    stage5_vals = kwargs.setdefault("stage5_vals", [2])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals

    for stage4_tune in stage4_vals:
        for stage5_tune in stage5_vals:
            for channel in channels:
                for coarse_step in [0, 1, 2, 4, 8, 16]:
                    data = _data.query(f"coarse_step=={coarse_step} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("run")
                    if data.empty:
                        print(f"Data not found for: coarse_step=={coarse_step} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                            

                    x = np.asarray(data.run)
                    y = np.asarray(data.delay)
                    if coarse_step == 0:
                        zero_points = y
                        y = y-y
                        continue
                    else:
                        y = y-zero_points
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    f, ax = plt.subplots()

                    popt, pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))

                    weighted_mean = popt[0]
                    std_dev = weighted_std_dev(weighted_mean, y, yerr)
                    err = p_e[0]

                    ax.grid(True, alpha=0.5)
                    ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Cell Delay All Runs\n{sigfig.round(weighted_mean, err)} [ps]")
                    ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [ps]")
                    ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Coarse Delay")

                    ax.set_xticks(runs)
                    ax.set_xticklabels(runs)
                    ax.set_title(f"Coarse Delay Cell {coarse_step} Consistency\nChannel {channel}: {stage4_tune} {stage5_tune}")
                    ax.set_xlabel("Run Number")
                    ax.set_ylabel("Delay [ps]")
                    ax.set_ylim([weighted_mean-0.4, weighted_mean+0.4])
                    ax.legend(loc="upper left")

                    plt.savefig(f"{figure_folder}/coarse_cell{coarse_step}_consistency_chan{channel}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF")
                    plt.close()

def fine_delay(_data, figure_folder, **kwargs):
    """
    Plots the fine step vs the total delay for all 67 coarse steps. 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [0])
    stage5_vals = kwargs.setdefault("stage5_vals", [0])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals
    
    for run in runs:
        for stage4_tune in stage4_vals:
            for stage5_tune in stage5_vals:
                for channel in channels:
                    fig, ax = plt.subplots()
            
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("fine_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                    x = np.asarray(data.fine_step)
                    y = np.asarray(data.delay)
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))

                    ax.grid(True, alpha=0.5)
                    ax.plot(x, popt[0]*x+popt[1],color="b",linestyle='--',label=f"Channel {channel} \n{sigfig.round(popt[0]*1e3, p_e[0]*1e3)} [fs/step]")
                    ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

                    divider = make_axes_locatable(ax)
                    ax2 = divider.append_axes("bottom", size="40%", pad=0.1)
                    residuals = (y - (popt[0]*x + popt[1]))*1e3 # convert to fs
                    residuals_std_dev = weighted_std_dev(0, residuals, yerr*1e3)

                    ax2.grid(True, alpha=0.5)
                    ax2.axhline(y=0, color='blue',linewidth=1, linestyle='-.', label="Fit")
                    ax2.errorbar(x, residuals, yerr=yerr*1e3, fmt='r.', ecolor="black", capsize=2, label="Residuals")
                    ax2.fill_between(x, residuals_std_dev, -residuals_std_dev, color='orange', alpha=.5, label=f"Residual \u03c3\n{sigfig.round(residuals_std_dev, p_e[0]*1e3).split(' ')[0]} [fs]")
                    ax2.legend(loc="upper right", fontsize=5)
                    ax2.set_ylim(-300, 300)

                    ax.set_title(f"Fine Delay\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                    ax2.set_xlabel("Fine Step")
                    ax.set_ylabel("Delay [ps]")
                    ax2.set_ylabel("Residual [fs]")
                    ax.set_ylim([-0.5, 25])

                    if add_temp_values:
                        add_temp_plot(data, ax)
                    
                    ax.legend(loc="upper left")

                    plt.savefig(f"{figure_folder}/fine_delay_chan{channel}_run{run}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                    plt.close()

def fine_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of (fine step vs the total delay) vs all runs (The delay per step over all runs). 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [0])
    stage5_vals = kwargs.setdefault("stage5_vals", [0])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals

    for stage4_tune in stage4_vals:
        for stage5_tune in stage5_vals:
            for channel in channels:
                f, ax = plt.subplots()
                channel_data = []

                for run in runs:
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("fine_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue

                    x = np.asarray(data.fine_step)
                    y = np.asarray(data.delay)*1e3
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))*1e3

                    popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))

                    channel_data.append((run, popt[0], p_e[0]))

                channel_data = np.asarray(channel_data)

                x = channel_data.T[0] # run number
                y = channel_data.T[1] # delay slope
                yerr = channel_data.T[2] # delay slope error

                popt, pcov = np.polyfit(x, y, 0, cov=True, w=1/yerr**2)
                p_e = np.sqrt(np.diag(pcov))

                weighted_mean = popt[0]
                std_dev = weighted_std_dev(weighted_mean, y, yerr)
                err = p_e[0]

                ax.grid(True, alpha=0.5)
                ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Delay Slope All Runs\n{sigfig.round(weighted_mean, err)} [fs/step]")
                ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [fs/step]")
                ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Delay per Fine Step")

                ax.set_xticks(runs)
                ax.set_xticklabels(runs)
                ax.set_title(f"Fine Delay Consistency\nChannel {channel}: {stage4_tune} {stage5_tune}")
                ax.set_xlabel("Run Number")
                ax.set_ylabel("Delay per Fine Step [fs/step]")
                ax.set_ylim([weighted_mean-5, weighted_mean+5])
                ax.legend(loc="upper left")

                plt.savefig(f"{figure_folder}/dcps3_fine_consistency_chan{channel}_run{run}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF")
                plt.close()

def fine_relative_consistency(_data, figure_folder, **kwargs):
    """
    Plots the fine step vs the delay relative to the cell beneath it for all 67 coarse steps.

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [0])
    stage5_vals = kwargs.setdefault("stage5_vals", [0])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals
    
    for run in runs:
        for stage4_tune in stage4_vals:
            for stage5_tune in stage5_vals:
                for channel in channels:
                    fig, ax = plt.subplots()
            
                    data = _data.query(f"run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("fine_step")
                    if data.empty:
                        print(f"Data not found for: run=={run} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                    x = np.asarray(data.fine_step)
                    y = np.asarray([0] + [data.delay.to_numpy()[i+1] - data.delay.to_numpy()[i] for i in range(len(data.delay)-1)])*1e3
                    y = y-y[0]
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    popt, pcov = np.polyfit(x[1:],y[1:],0,cov=True,w=1/yerr[1:]**2)
                    p_e = np.sqrt(np.diag(pcov))

                    weighted_mean = popt[0]
                    std_dev = weighted_std_dev(weighted_mean, y[1:], 1/yerr[1:]**2)
                    err = p_e[0]

                    ax.grid(True, alpha=0.5)
                    ax.axhline(y=weighted_mean, color='black', linewidth=1, linestyle='-.',label=f"Relative Mean Delay All Steps\n{sigfig.round(weighted_mean, err)} [fs]")
                    ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Steps\n{sigfig.round(std_dev, err).split(' ')[0]} [fs]")
                    ax.errorbar(x, y, yerr, fmt='r.', ecolor='k', capsize=2, label="Relative Fine Step Delay")
                    ax.set_title(f"Fine Delay Relative Step Consistency\nChannel {channel}: {stage4_tune} {stage5_tune} | Run {run}")
                    ax.set_ylim([-50, 600])
                    ax.set_xlabel("Fine Delay Step")
                    ax.set_ylabel("Delay [fs]")

                    if add_temp_values:
                        add_temp_plot(data, ax)
                    
                    ax.legend(loc="lower right")

                    plt.savefig(f"{figure_folder}/fine_relative_consistency_chan{channel}_run{run}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
                    plt.close()

def fine_cell_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of individual fine cells vs all runs. 

    Valid kwargs: add_temp_values, channels, stage4_vals, stage5_vals
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [2, 3])
    runs = kwargs.setdefault("runs", "all")
    stage4_vals = kwargs.setdefault("stage4_vals", [0])
    stage5_vals = kwargs.setdefault("stage5_vals", [0])

    if runs == "all":
        runs = np.unique(_data.run)

    if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
    if isinstance(stage5_vals, int):
        stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals

    for stage4_tune in stage4_vals:
        for stage5_tune in stage5_vals:
            for channel in channels:
                for fine_step in range(67):
                    data = _data.query(f"fine_step=={fine_step} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}").sort_values("run")
                    if data.empty:
                        print(f"Data not found for: fine_step=={fine_step} & channel=={channel} & stage4_tune=={stage4_tune} & stage5_tune=={stage5_tune}")
                        continue
                            

                    x = np.asarray(data.run)
                    y = np.asarray(data.delay)*1e3
                    if fine_step == 0:
                        zero_points = y
                        y = y-y
                        continue
                    else:
                        y = y-zero_points
                    yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

                    f, ax = plt.subplots()

                    popt, pcov = np.polyfit(x,y,0,cov=True,w=1/yerr**2)
                    p_e = np.sqrt(np.diag(pcov))

                    weighted_mean = popt[0]
                    std_dev = weighted_std_dev(weighted_mean, y, yerr)
                    err = p_e[0]

                    ax.grid(True, alpha=0.5)
                    ax.axhline(y=weighted_mean, color='black',linewidth=1, linestyle='-.',label=f"Mean Cell Delay All Runs\n{sigfig.round(weighted_mean, err)} [fs]")
                    ax.fill_between(x, weighted_mean+std_dev, weighted_mean-std_dev, color='orange', alpha=.5, label=f"\u03c3 All Runs\n{sigfig.round(std_dev, err).split(' ')[0]} [fs]")
                    ax.errorbar(x, y, yerr=yerr, fmt='r.', ecolor="black", capsize=2, label=f"Fine Delay")

                    ax.set_xticks(runs)
                    ax.set_xticklabels(runs)
                    ax.set_title(f"Fine Delay Cell {fine_step} Consistency\nChannel {channel}: {stage4_tune} {stage5_tune}")
                    ax.set_xlabel("Run Number")
                    ax.set_ylabel("Delay [fs]")
                    ax.set_ylim([weighted_mean-400, weighted_mean+400])
                    ax.legend(loc="upper left")

                    plt.savefig(f"{figure_folder}/fine_cell{fine_step}_consistency_chan{channel}_s4{stage4_tune}_s5{stage5_tune}.png", dpi=300, facecolor="#FFFFFF")
                    plt.close()

presets = {"coarse_delay" : coarse_delay,
           "coarse_consistency" : coarse_consistency,
           "coarse_relative_consistency" : coarse_relative_consistency,
           "coarse_cell_consistency" : coarse_cell_consistency,
           "fine_delay" : fine_delay,
           "fine_consistency" : fine_consistency,
           "fine_relative_consistency" : fine_relative_consistency,
           "fine_cell_consistency" : fine_cell_consistency}