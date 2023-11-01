# Written by Zachariah Eberle zachariah.eberle@gmail.com
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import sigfig

def weighted_std_dev(mean, values, weights):
    """
    Calculate weighted standard deviation
    """
    total = 0
    for value, weight in zip(values, weights):
        total += weight*(mean - value)**2
    return np.sqrt(total / (((len(values)-1)/len(values)) * sum(weights)))

def add_temp_plot(data, ax):
    """
    Creates a second temperature plot on the same axes as ax and adds another ylabel on the right hand side of graph
    """
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

def coarse_delay(_data, figure_folder, **kwargs):
    """
    Plots the coarse step vs the total delay for all 32 coarse steps. 

    Valid kwargs: add_temp_values, channels, ylim, residual_ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    ylim = kwargs.setdefault("ylim", (-10, 500)) # In ps
    residual_ylim = kwargs.setdefault("residual_ylim", (-3, 3)) # In ps

    if runs == "all":
        runs = np.unique(_data.run)
    
    for run in runs:
        for channel in channels:
            fig, ax = plt.subplots()
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("coarse_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
                continue
            x = np.asarray(data.coarse_step)
            y = np.asarray(data.delay)
            y = y-y[0]
            yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

            popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

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
            ax2.set_ylim(residual_ylim)

            ax.set_title(f"Coarse Delay\nChannel {channel} | Run {run}")
            ax2.set_xlabel("Coarse Step")
            ax.set_ylabel("Delay [ps]")
            ax2.set_ylabel("Residual [ps]")
            ax.set_ylim(ylim)

            if add_temp_values:
                add_temp_plot(data, ax)
            
            ax.legend(loc="upper left")

            plt.savefig(f"{figure_folder}/coarse_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
            plt.close()

def coarse_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of (coarse step vs the total delay) vs all runs (The delay per step over all runs). 

    Valid kwargs: add_temp_values, channels, relative_ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    relative_ylim = kwargs.setdefault("relative_ylim", (-0.2, 0.2)) # ylim relative to the mean delay slope for all included runs, 
    # must be array-like of size (2,), values in ps

    if runs == "all":
        runs = np.unique(_data.run)

    for channel in channels:
        channel_data = []

        for run in runs:
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("coarse_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
                continue

            x = np.asarray(data.coarse_step)
            y = np.asarray(data.delay)
            y = y-y[0]
            yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))

            popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            channel_data.append((run, popt[0], p_e[0]))

        channel_data = np.asarray(channel_data)

        if len(channel_data) == 0:
            print(f"No data found for channel {channel}")
            continue

        f, ax = plt.subplots()

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
        ax.set_title(f"Coarse Delay Consistency\nChannel {channel}")
        ax.set_xlabel("Run Number")
        ax.set_ylabel("Delay per Coarse Step [ps/step]")
        ax.set_ylim([weighted_mean+relative_ylim[0], weighted_mean+relative_ylim[1]])
        ax.legend(loc="upper left")

        plt.savefig(f"{figure_folder}/coarse_consistency_chan{channel}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
        plt.close()
                    
def coarse_relative_consistency(_data, figure_folder, **kwargs): 
    """
    Plots the coarse step vs the delay relative to the cell beneath it for all 32 coarse steps. 

    Valid kwargs: add_temp_values, channels, ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    ylim = kwargs.setdefault("ylim", (-.1, 15)) # In ps

    if runs == "all":
        runs = np.unique(_data.run)
    
    for run in runs:
        for channel in channels:
            fig, ax = plt.subplots()
    
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("coarse_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
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
            ax.set_title(f"Coarse Delay Relative Step Consistency\nChannel {channel} | Run {run}")
            ax.set_ylim(ylim)
            ax.set_xlabel("Coarse Delay Step")
            ax.set_ylabel("Delay [ps]")

            if add_temp_values:
                add_temp_plot(data, ax)
            
            ax.legend(loc="lower right")

            plt.savefig(f"{figure_folder}/coarse_relative_consistency_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
            plt.close()

def coarse_cell_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of individual coarse cells vs all runs. 

    Valid kwargs: add_temp_values, channels, relative_ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    relative_ylim = kwargs.setdefault("relative_ylim", (-0.4, 0.4)) # ylim relative to the mean delay slope for all included runs, 
    # must be array-like of size (2,), values in ps

    if runs == "all":
        runs = np.unique(_data.run)

    
    for channel in channels:
        for coarse_step in [0] + [2**i for i in range(10)]:
            data = _data.query(f"coarse_step=={coarse_step} & channel=={channel}").sort_values("run")
            if data.empty:
                print(f"Data not found for: coarse_step=={coarse_step} & channel=={channel}")
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
            ax.set_title(f"Coarse Delay Cell {coarse_step} Consistency\nChannel {channel}")
            ax.set_xlabel("Run Number")
            ax.set_ylabel("Delay [ps]")
            ax.set_ylim([weighted_mean+relative_ylim[0], weighted_mean+relative_ylim[1]])
            ax.legend(loc="upper left")

            plt.savefig(f"{figure_folder}/coarse_cell{coarse_step}_consistency_chan{channel}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
            plt.close()

def fine_delay(_data, figure_folder, **kwargs):
    """
    Plots the fine step vs the total delay for all 67 coarse steps. 

    Valid kwargs: add_temp_values, channels, ylim, residual_ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    ylim = kwargs.setdefault("ylim", (-500, 25000)) # In fs
    residual_ylim = kwargs.setdefault("residual_ylim", (-300, 300)) # In fs

    if runs == "all":
        runs = np.unique(_data.run)
    
    for run in runs:
        for channel in channels:
            fig, ax = plt.subplots()
    
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("fine_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
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
            ax2.set_ylim(residual_ylim)

            ax.set_title(f"Fine Delay\nChannel {channel} | Run {run}")
            ax2.set_xlabel("Fine Step")
            ax.set_ylabel("Delay [ps]")
            ax2.set_ylabel("Residual [fs]")
            ax.set_ylim(ylim[0]/1000, ylim[1]/1000)

            if add_temp_values:
                add_temp_plot(data, ax)
            
            ax.legend(loc="upper left")

            plt.savefig(f"{figure_folder}/fine_delay_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
            plt.close()

def fine_consistency(_data, figure_folder, **kwargs):
    """
    Plots the consistency of (fine step vs the total delay) vs all runs (The delay per step over all runs). 

    Valid kwargs: add_temp_values, channels, relative_ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    relative_ylim = kwargs.setdefault("relative_ylim", (-5, 5)) # ylim relative to the mean delay slope for all included runs, 
    # must be array-like of size (2,), values in fs

    if runs == "all":
        runs = np.unique(_data.run)

    for channel in channels:
        channel_data = []

        for run in runs:
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("fine_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
                continue

            x = np.asarray(data.fine_step)
            y = np.asarray(data.delay)*1e3
            y = y-y[0]
            yerr = np.asarray(data._std_dev) / np.sqrt(np.asarray(data._count))*1e3

            popt, pcov = np.polyfit(x,y,1,cov=True,w=1/yerr**2)
            p_e = np.sqrt(np.diag(pcov))

            channel_data.append((run, popt[0], p_e[0]))

        channel_data = np.asarray(channel_data)

        if len(channel_data) == 0:
            print(f"No data found for channel {channel}")
            continue

        f, ax = plt.subplots()

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
        ax.set_title(f"Fine Delay Consistency\nChannel {channel}")
        ax.set_xlabel("Run Number")
        ax.set_ylabel("Delay per Fine Step [fs/step]")
        ax.set_ylim([weighted_mean+relative_ylim[0], weighted_mean+relative_ylim[1]])
        ax.legend(loc="upper left")

        plt.savefig(f"{figure_folder}/dcps3_fine_consistency_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
        plt.close()

def fine_relative_consistency(_data, figure_folder, **kwargs):
    """
    Plots the fine step vs the delay relative to the cell beneath it for all 67 coarse steps.

    Valid kwargs: add_temp_values, channels, ylim
    """
    add_temp_values = kwargs.setdefault("add_temp_values", False)
    channels = kwargs.setdefault("channels", [3])
    runs = kwargs.setdefault("runs", "all")
    ylim = kwargs.setdefault("ylim", (50, 600)) # In fs

    if runs == "all":
        runs = np.unique(_data.run)

    for run in runs:
        for channel in channels:
            fig, ax = plt.subplots()
    
            data = _data.query(f"run=={run} & channel=={channel}").sort_values("fine_step")
            if data.empty:
                print(f"Data not found for: run=={run} & channel=={channel}")
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
            ax.set_title(f"Fine Delay Relative Step Consistency\nChannel {channel} | Run {run}")
            ax.set_ylim(ylim)
            ax.set_xlabel("Fine Delay Step")
            ax.set_ylabel("Delay [fs]")

            if add_temp_values:
                add_temp_plot(data, ax)
            
            ax.legend(loc="lower right")

            plt.savefig(f"{figure_folder}/fine_relative_consistency_chan{channel}_run{run}.png", dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
            plt.close()

presets = {"coarse_delay" : coarse_delay,
           "coarse_consistency" : coarse_consistency,
           "coarse_relative_consistency" : coarse_relative_consistency,
           "coarse_cell_consistency" : coarse_cell_consistency,
           "fine_delay" : fine_delay,
           "fine_consistency" : fine_consistency,
           "fine_relative_consistency" : fine_relative_consistency}