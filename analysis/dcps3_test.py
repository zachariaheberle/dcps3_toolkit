import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
import time
import pandas as pd
import subprocess

from tools.base import *
from tools.ddmtd import ddmtd
from time import sleep

def data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, dcps_file="dcps_i2c.py", quiet=True):
    """
    Function that will gather DCPS data with specified fine, coarse, stage4, stage5, channel, and dcps_file parameters.
    Will additionally transfer the data back to the local machine running this.
    """
    if quiet:
        stdout = subprocess.DEVNULL
    else:
        stdout = None

    subprocess.run(f"../rpi_side/runDCPS.sh ./run_dcps_control.sh {fine_control} {coarse_control} {stage4_tune} {stage5_tune} {channel} {server} {dcps_file}", shell=True, stdout=stdout)
    subprocess.run(f"../rpi_side/runAtNex.sh bin/data_acq.exe 0 1 {server}", shell=True, stdout=stdout)
    # Copy over the files...
    run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
    subprocess.run(f"scp {server}:Flash_Firmware/data/ddmtd1.txt {data_save_folder+run_name}_ddmtd1.txt", shell=True, stdout=stdout)
    subprocess.run(f"scp {server}:Flash_Firmware/data/ddmtd2.txt {data_save_folder+run_name}_ddmtd2.txt", shell=True, stdout=stdout)

def run_coarse_stage_test(data_save_folder, num_runs=1, stage4_tunes=[2, 3], stage5_tunes=[2, 3], channels=[2, 3], track_completion = True):
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    total_loops = num_runs * len(channels) * len(stage4_tunes) * len(stage5_tunes) * len(range(32))
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py", shell=True) # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in channels:
            for stage4_tune in stage4_tunes:
                for stage5_tune in stage5_tunes:
                    for coarse_control in range(0,32,1):
                        data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder)
                        if track_completion:
                            completed_loops += 1
                            print(f"run_coarse_stage_test: {(completed_loops/total_loops)*100:.3f}% complete")
    return 0

def run_coarse_delay_consistency_test(data_save_folder, num_runs=10, channels=[2, 3], track_completion=True):
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    total_loops = num_runs * len(channels) * len(range(32))
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py", shell=True) # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in channels:
            for coarse_control in range(0,32,1):
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder)
                if track_completion:
                    completed_loops += 1
                    print(f"run_coarse_delay_consistency_test: {(completed_loops/total_loops)*100:.3f}% complete")
    return 0

def run_coarse_delay_cell_consistency_test(data_save_folder, num_runs=10, channels=[2, 3], track_completion=True):
    coarse_control = 0
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    total_loops = num_runs * len(channels) * len([0, 1, 2, 4, 8, 16])
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py", shell=True) # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in channels:
            for coarse_control in [0, 1, 2, 4, 8, 16]:
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder)
                if track_completion:
                    completed_loops += 1
                    print(f"run_coarse_delay_cell_consistency_test: {(completed_loops/total_loops)*100:.3f}% complete")
    return 0


def run_fine_delay_consistency_test(data_save_folder, num_runs=10, channels=[2, 3], track_completion=True):
    coarse_control = 0
    fine_control = 0 
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    total_loops = num_runs * len(channels) * len(range(67))
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py", shell=True) # Transfer dcps_i2c file
    
    for run in range(num_runs):
        for channel in channels:
            for fine_control in range(0,67,1): 
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder)
                if track_completion:
                    completed_loops += 1
                    print(f"run_fine_delay_consistency_test: {(completed_loops/total_loops)*100:.3f}% complete")
    return 0


def run_fine_delay_cell_consistency_test(data_save_folder, num_runs=10, channels=[2, 3], track_completion=True):
    coarse_control = 0
    fine_control = 0 
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    dcps_file = "dcps_i2c_fine_cell_test.py"
    total_loops = num_runs * len(channels) * len(range(67))
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c_fine_cell_test.py {server}:/home/pi/rpi_dcps/dcps_i2c_fine_cell_test.py", shell=True) # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in channels:
            for fine_control in range(0,67,1): 
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, dcps_file=dcps_file)
                if track_completion:
                    completed_loops += 1
                    print(f"run_fine_delay_cell_consistency_test: {(completed_loops/total_loops)*100:.3f}% complete")
    return 0

def run_fine_delay_cell_set_consistency_test(data_save_folder, num_runs=10, channels=[2, 3], track_completion=True):
    coarse_control = 0
    fine_control = 0 
    stage4_tune = 2
    stage5_tune = 3
    channel = 2
    dcps_file = "dcps_i2c_fine_cell_set_test.py"
    total_loops = num_runs * len(channels) * len(range(12))
    completed_loops = 0

    subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
    subprocess.run(f"rsync ../rpi_side/dcps_i2c_fine_cell_set_test.py {server}:/home/pi/rpi_dcps/dcps_i2c_fine_cell_set_test.py", shell=True) # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in channels:
            for fine_control in range(12): # eleven sets with 6 cells in each
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, dcps_file=dcps_file)
                if track_completion:
                    completed_loops += 1
                    print(f"run_fine_delay_cell_set_consistency_test: {(completed_loops/total_loops)*100:.3f}% complete")
                    
    return 0






server="pi@nexys_ddmtd_dcps3" # your ip address might be different

## IMPORTANT##
## make sure you have your ssh keys set-up properly
## END IMPORTANT##
## Contact rohith.saradhy@cern.ch for password to the RPi

subprocess.run(f"rsync -ra ../rpi_side/Flash_Firmware {server}:", shell=True)

subprocess.run(f"rsync -ra ../rpi_side/Flash_Firmware {server}:", shell=True)
subprocess.run(f"../rpi_side/runAtNex.sh bin/check_firmware.exe 0 1 {server}", shell=True) #flash the configuration file

N=100000  #Setting the DDMTD N
freq="160"#in MHz #Setting the input clock frequency
pll_config_folder="../rpi_side/PLL_Conf/"
fig_save_folder = f"./dcps3Test/figures/N{N}/"
data_save_folder = f"./dcps3Test/data/N{N}/"
subprocess.run(f"mkdir -p {fig_save_folder}", shell=True) #create those directories
subprocess.run(f"mkdir -p {data_save_folder}", shell=True) #create those directories
run_number = 1
run_name   = f"dcps3TestRun{run_number}"

## Configuring the PLL. This needs to be done everytime the board is restarted/ loses power.
##Selecting the Register File##

# pll_config = f"{pll_config_folder}/bcp_configs/bcp_nexys_{100000+1}_{160}MHz.h" #Selecting the configuration according to N, freq
pll_config = f"{pll_config_folder}160MHz_100k.h" #Selecting the configuration according to N, freq

print("Using PLL Config: \n ",pll_config)
print("\n\n")
subprocess.run(f"scp {pll_config} {server}:Flash_Firmware/include/Si5344_REG.h", shell=True) #Copy the config to the RPi as Si5344
## Compile and Running configuration script
subprocess.run(f"../rpi_side/runAtNex.sh bin/ddmtd_pll.exe 1 1 {server}", shell=True) #flash the configuration file
#The output should look like the following::
# Done Compiling MEM
# Done Compiling PLL
# address = 0x0514, value = 0x01 ; Value returned = 0x00   
# address = 0x001c, value = 0x01 ; Value returned = 0x00 

# After configuration, D304 will blink every 500 cycles of the beat clock


# MAKE SURE TO COMPILE THIS

subprocess.run(f"../rpi_side/runAtNex.sh bin/data_acq.exe 1 1 {server}", shell=True) # 0 no compile, 1 compile (second arg, ignore third arg)
# Copy over the files...
subprocess.run(f"scp {server}:Flash_Firmware/data/ddmtd1.txt {data_save_folder+run_name}_ddmtd1.txt", shell=True)
subprocess.run(f"scp {server}:Flash_Firmware/data/ddmtd2.txt {data_save_folder+run_name}_ddmtd2.txt", shell=True) 

#run_coarse_stage_test(f"./dcps3Test/data/N{N}_coarse_stage_test/", stage4_tunes=[2], stage5_tunes=[2, 3], track_completion=True)
#run_coarse_delay_consistency_test(f"./dcps3Test/data/N{N}_coarse/")
#run_fine_delay_consistency_test(f"./dcps3Test/data/N{N}_fine/")
#run_coarse_delay_cell_consistency_test(f"./dcps3Test/data/N{N}_coarse_cell/")
#run_fine_delay_cell_consistency_test(f"./dcps3Test/data/N{N}_fine_cell/")
#run_fine_delay_cell_set_consistency_test(f"./dcps3Test/data/N{N}_fine_cell_set/")