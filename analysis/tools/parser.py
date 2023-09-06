# Written by Zachariah Eberle zachariah.eberle@gmail.com

import matplotlib.pyplot as plt
import pandas as pd
from tools.ddmtd import ddmtd
import tools.common_vars as common_vars
from glob import glob

def get_data_point(file, N, freq, sep="", draw=False):
    """
    Gets mean, std dev and number of counts from ddmtd.txt files
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
        plt.savefig(f"{common_vars.figure_folder}/data_points/{file[0:-11]}.png", dpi=300, facecolor="#FFFFFF")
        plt.close()
    return mean_val, std_dev, count

def get_temp_data(file):
    """
    Loads in temperature data file
    """
    return pd.read_csv(file, skiprows=[0], names=["chan", "f", "c", "s4", "s5", "run", "temp"])

def load_files(data_folder, N, freq, sep="", draw=False):
    files = glob(f"{data_folder}/*.txt")

    data = []

    if any(["temp_info.txt" in file for file in files]):
        temp_values = True
        T_df = get_temp_data(f"{data_folder}/temp_info.txt")
    else:
        temp_values = False

    for i, file in enumerate(files):
        # Format: type, channel, run number, coarse step, stage 4 tune, stage 5 tune, fine step, mean, std dev, count
        if "ddmtd1.txt" in file:
            mean, std_dev, count = get_data_point(file, N, freq, sep=sep, draw=draw)
            vals = file.split("_")
            run_number = int(vals[-2][3:])
            s5 = int(vals[-3][-1])
            s4 = int(vals[-4][-1])
            c = int(vals[-5][1:])
            f = int(vals[-6][1:])
            channel = int(vals[-7][-1])
            delay = ((lambda channel: -1 if channel==2 else 1)(channel))*(mean+300)%((1/freq*1e6)/2)
            if temp_values:
                t = T_df.query(f"chan=={channel} & f=={f} & c=={c} & s4=={s4} & s5=={s5} & run=={run_number}").temp.iloc[0]
                data.append((channel, run_number, c, s4, s5, f, delay, std_dev, count, t))
            else:
                data.append((channel, run_number, c, s4, s5, f, delay, std_dev, count))
            print(f"{(i+1)/len(files)*100:.3f}% Complete")
    if temp_values:
        df = pd.DataFrame(data, columns=["channel", "run", "coarse_step", "stage4_tune", "stage5_tune", "fine_step", "delay", "_std_dev", "_count", "temperature"])
    else:
        df = pd.DataFrame(data, columns=["channel", "run", "coarse_step", "stage4_tune", "stage5_tune", "fine_step", "delay", "_std_dev", "_count"])
    
    return df