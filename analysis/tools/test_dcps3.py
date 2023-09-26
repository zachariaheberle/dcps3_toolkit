import subprocess
from tools.base import runBash, mkdir
import tools.common_vars as common_vars
from tools.parser import get_data_point
import pyvisa

server=common_vars.server

def initialize(N, freq):
    """
    Initializes the Nexys-ddmtd-dcps boards with the correct PLL configurations
    and prepares them for taking data
    """

    ## IMPORTANT##
    ## make sure you have your ssh keys set-up properly
    ## END IMPORTANT##
    ## Contact rohith.saradhy@cern.ch for password to the RPi

    runBash(f"rsync -ra ../rpi_side/Flash_Firmware {server}:")
    runBash(f"../rpi_side/runAtNex.sh bin/check_firmware.exe 0 1 {server}") #flash the configuration file

    ddmtd_pll_config_folder="../rpi_side/PLL_Conf/ddmtd_side"
    dcps_pll_config_folder="../rpi_side/PLL_Conf/dcps_side"

    ## Configuring the PLL. This needs to be done everytime the board is restarted/ loses power.
    ##Selecting the Register File##

    ddmtd_pll_config = f"{ddmtd_pll_config_folder}/{freq}MHz_{N//1000}k.h" #Selecting the configuration according to N, freq
    dcps_pll_config = f"{dcps_pll_config_folder}/test{freq}MHz.h"

    print("Using PLL Config: \n ",ddmtd_pll_config)
    print("\n\n")
    runBash(f"scp {ddmtd_pll_config} {server}:Flash_Firmware/include/Si5344_REG.h") #Copy the config to the RPi as Si5344
    runBash(f"scp {dcps_pll_config} {server}:~/rpi_dcps/pll_config/Si5344_REG.h")
    ## Compile and Running configuration script
    runBash(f"../rpi_side/runAtNex.sh bin/ddmtd_pll.exe 1 1 {server}") #flash the configuration file and compile programs
    runBash(f"../rpi_side/flash_dcpsPLL.sh test{freq}MHz.h {server}")

    

def data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, dcps_file="dcps_i2c.py", show=True, measure_temp=False):
    """
    Function that will gather DCPS data with specified fine, coarse, stage4, stage5, channel, and dcps_file parameters.
    Will additionally transfer the data back to the local machine running this.
    """

    runBash(f"../rpi_side/runDCPS.sh ./run_dcps_control.sh {fine_control} {coarse_control} {stage4_tune} {stage5_tune} {channel} {server} {dcps_file}", show=show)
    runBash(f"../rpi_side/runAtNex.sh bin/data_acq.exe 0 1 {server}", show=show)
    # Copy over the files...
    run_name = f"chan{channel}_f{fine_control}_c{coarse_control}_s4{stage4_tune}_s5{stage5_tune}_run{run}"
    runBash(f"scp {server}:Flash_Firmware/data/ddmtd1.txt {data_save_folder}/{run_name}_ddmtd1.txt", show=show)
    runBash(f"scp {server}:Flash_Firmware/data/ddmtd2.txt {data_save_folder}/{run_name}_ddmtd2.txt", show=show)

    if measure_temp:
        temp = get_temp()

        with open(f"{data_save_folder}/temp_info.txt", "a") as fp:
            if fp.tell() == 0:
                fp.write("channel,fine_control,coarse_control,stage4_tune,stage5_tune,run,temperature\n")
            fp.write(f"{channel},{fine_control},{coarse_control},{stage4_tune},{stage5_tune},{run},{temp}\n")

def sanity_check(freq, N, test_temp=False):
    """
    Quick test to ensure that the DCPS board 
    and (if applicable) temp measurement is working properly
    """
    mkdir("./temporary_test")
    for channel in [2, 3]:
        data_acq(0, 0, 2, 2, channel, 0, "./temporary_test", measure_temp=test_temp)
        data_acq(0, 31, 2, 2, channel, 0, "./temporary_test", measure_temp=test_temp)
        data_acq(66, 0, 0, 0, channel, 0, "./temporary_test", measure_temp=test_temp)

        mean0, _, _ = get_data_point(f"./temporary_test/chan{channel}_f0_c0_s42_s52_run0", freq=freq, N=N)
        mean31, _, _ = get_data_point(f"./temporary_test/chan{channel}_f0_c31_s42_s52_run0", freq=freq, N=N)
        mean66, _, _ = get_data_point(f"./temporary_test/chan{channel}_f66_c0_s40_s50_run0", freq=freq, N=N)
        
        mean0 = (mean0+300)%((1/freq*1e6)/2)
        mean31 = (mean31+300)%((1/freq*1e6)/2)
        mean66 = (mean66+300)%((1/freq*1e6)/2)

        if abs(mean31 - mean0) < 200 or abs(mean66 - mean0) < 15:
            return False
    return True

def get_temp():
    """
    These results WILL change based on instrument used
    commands are based on Agilent 34970A using 2 wire RTD measurements
    """
    rm = pyvisa.ResourceManager()

    inst = rm.open_resource("ASRL1::INSTR")
    inst.baud_rate = 38400
    return float(inst.query("MEAS:TEMP? RTD,(@102)").decode(""))

def coarse_consistency(data_save_folder, num_runs, show, **kwargs):
    """
    Optional kwargs:
    fine_control
    stage4_tune
    stage5_tune
    """
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 2

    if "fine_control" in kwargs:
        fine_control = kwargs["fine_control"]
    if "stage4_tune" in kwargs:
        stage4_tune = kwargs["stage4_tune"]
    if "stage5_tune" in kwargs:
        stage5_tune = kwargs["stage5_tune"]

    runBash(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py") # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in [2, 3]:
            for coarse_control in range(32):
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, show=show)

def coarse_cell_consistency(data_save_folder, num_runs, show, **kwargs):
    """
    Optional kwargs:
    fine_control
    stage4_tune
    stage5_tune
    """
    fine_control = 0
    stage4_tune = 2
    stage5_tune = 2

    if "fine_control" in kwargs:
        fine_control = kwargs["fine_control"]
    if "stage4_tune" in kwargs:
        stage4_tune = kwargs["stage4_tune"]
    if "stage5_tune" in kwargs:
        stage5_tune = kwargs["stage5_tune"]

    runBash(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py") # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in [2, 3]:
            for coarse_control in [0, 1, 2, 4, 8, 16]:
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, show=show)

def fine_consistency(data_save_folder, num_runs, show, **kwargs):
    """
    Optional kwargs:
    coarse_control
    stage4_tune
    stage5_tune
    """
    coarse_control = 0
    stage4_tune = 0
    stage5_tune = 0

    if "coarse_control" in kwargs:
        coarse_control = kwargs["coarse_control"]
    if "stage4_tune" in kwargs:
        stage4_tune = kwargs["stage4_tune"]
    if "stage5_tune" in kwargs:
        stage5_tune = kwargs["stage5_tune"]

    runBash(f"rsync ../rpi_side/dcps_i2c.py {server}:/home/pi/rpi_dcps/dcps_i2c.py") # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in [2, 3]:
            for fine_control in range(67):
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, show=show)

def fine_cell_consistency(data_save_folder, num_runs, show, **kwargs):
    """
    Optional kwargs:
    coarse_control
    stage4_tune
    stage5_tune
    """
    coarse_control = kwargs.setdefault("coarse_control", 0)
    stage4_tune = 0
    stage5_tune = 0

    if "coarse_control" in kwargs:
        coarse_control = kwargs["coarse_control"]
    if "stage4_tune" in kwargs:
        stage4_tune = kwargs["stage4_tune"]
    if "stage5_tune" in kwargs:
        stage5_tune = kwargs["stage5_tune"]

    runBash(f"rsync ../rpi_side/dcps_i2c_fine_cell_test.py {server}:/home/pi/rpi_dcps/dcps_i2c_fine_cell_test.py") # Transfer dcps_i2c file

    for run in range(num_runs):
        for channel in [2, 3]:
            for fine_control in range(67):
                data_acq(fine_control, coarse_control, stage4_tune, stage5_tune, channel, run, data_save_folder, dcps_file="dcps_i2c_fine_cell_test.py", show=show)

presets = {"coarse_consistency" : coarse_consistency,
           "coarse_cell_consistency" : coarse_cell_consistency,
           "fine_consistency" : fine_consistency,
           "fine_cell_consistency" : fine_cell_consistency}
