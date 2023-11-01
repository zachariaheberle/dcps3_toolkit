# Written by Zachariah Eberle zachariah.eberle@gmail.com

import matplotlib.pyplot as plt
import pandas as pd
from tools.ddmtd import ddmtd
import tools.common_vars as common_vars
from glob import glob
import os

def get_data_point(file, N, freq, sep="", draw=False):
    """
    Gets mean, std dev and number of counts from ddmtd.txt files, not designed to be used
    outside of load_files.
    """
    df1 = pd.read_csv(f"{file}",names=['edge1','ddmtd1'])
    df2 = pd.read_csv(f"{file[0:-5]}2.txt",names=['edge2','ddmtd2'])
    df = pd.concat((df1,df2),axis=1)
    # Create a DDMTD Object for analysis of the data
    data = ddmtd(df.iloc[:,:],channel=(1,2), q=1) #creates a ddmtd object
    data.N = N
    data.INPUT_FREQ = freq*1e6 # Hz 
    data.Recalc()
    gauss_fit, _, count = data.drawTIE(sep=sep,fit=True,draw=draw)
    mean_val, std_dev = gauss_fit[1]*1000, abs(gauss_fit[2])*1000
    if draw:
        if common_vars.figure_folder:
            plt.savefig(f"{common_vars.figure_folder}/data_points/{os.path.split(file)[-1][0:-4]}.png", dpi=300, facecolor="#FFFFFF")
            plt.close()
        else:
            print("Figure folder not set, cannot draw data point.")
    return mean_val, std_dev, count

def get_temp_data(file):
    """
    Loads in temperature data file
    """
    return pd.read_csv(file, skiprows=[0], names=["chan", "f", "c", "run", "temp"])

def load_files(data_folder, N, freq, sep="", force_reload=False, draw=False):
    """
    Loads in data files from data_folder. If a cached .ddmtd dataframe file is present, it will load that instead.
    This process usually takes a *long* time uncached. Grab some water or something while you wait, I dunno.

    If for some reason your compressed_data.ddmtd cache gets corrupted or loads data in the incorrect format, you can
    pass force_reload to reload everything from scratch.
    """
    compressed_data = glob(f"{data_folder}/*.ddmtd")
    if compressed_data and not force_reload:
        df = pd.read_csv(compressed_data[0])
        return df
    files = glob(f"{data_folder}/*.txt")

    data = []

    if any(["temp_info.txt" in file for file in files]):
        temp_values = True
        T_df = get_temp_data(f"{data_folder}/temp_info.txt")
    else:
        temp_values = False

    for i, file in enumerate(files):
        # Format: type, channel, run number, coarse step, fine step, mean, std dev, count
        if "ddmtd1.txt" in file:
            mean, std_dev, count = get_data_point(file, N, freq, sep=sep, draw=draw)
            vals = file.split("_")
            run_number = int(vals[-2][3:])
            c = int(vals[-3][1:])
            f = int(vals[-4][1:])
            channel = int(vals[-5][-1])
            delay = -(mean+300)%((1/freq*1e6)/2)
            if temp_values:
                t = T_df.query(f"chan=={channel} & f=={f} & c=={c} & run=={run_number}").temp.iloc[0]
                data.append((channel, run_number, c, f, delay, std_dev, count, t))
            else:
                data.append((channel, run_number, c, f, delay, std_dev, count))
            print(f"{(i+1)/len(files)*100:.3f}% Complete")
    if temp_values:
        df = pd.DataFrame(data, columns=["channel", "run", "coarse_step", "fine_step", "delay", "_std_dev", "_count", "temperature"])
    else:
        df = pd.DataFrame(data, columns=["channel", "run", "coarse_step", "fine_step", "delay", "_std_dev", "_count"])
    
    df.to_csv(f"{data_folder}/compiled_data.ddmtd")
    
    return df