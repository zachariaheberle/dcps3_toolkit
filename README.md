# DCPS3 Toolkit
## Information
This project contains the firmware & analysis software for the Nexys-DDMTD board.

## Setup
### Required Python Packages
```bash
numpy        1.24.4
scipy        1.9.1
pandas       1.5.1
sigfig       1.3.3
matplotlib   3.5.3
```
### Physical Setup
In order for the Nexys-DDMTD-DCPS boards to work, you will need to plug in a few things:
- Nexys Carrier board power
- DCPS3 Host board power
- RP2040 connection to raspberry pi
- Ethernet
- 4 SMA Cables (Crossed)
- DCPS3 Mezzanine into DCPS3 Host board


Please contact myself at zachariah.eberle@gmail.com or eberl116@umn.edu for specifics.
### SSH Setup
In order for testing to run smoothly, you must create a passwordless ssh key to access the raspberry pi.
SSH should be setup on the raspberry pi that is connected to the Nexys board. You can connect to it on your local network by running
```bash
ssh pi@nexys-radiation.local
```
Please contact myself at zachariah.eberle@gmail.com or eberl116@umn.edu for the password to the raspberry pi.
Once you are connected, add your public ssh key to ~/.ssh/authorized_keys.

Additionally, you will need to either modify dcps3_toolkit/analysis/tools/common_vars.py and change the "server" variable to your local raspberry pi address, or, you can add this to your ssh config file and replace the HostName with the ip of the raspberry pi.
```bash
Host nexys_ddmtd_radiation
	HostName nexys-radiation.local
	User pi
```

## Data Taking
### Using the Jupyter Notebook
To make basic data measurements, simply use the final_analysis.ipynb notebook and run all relevant cells for the tests you would like to do. For more custom data taking, see "Using a Python Script".
### Using a Python Script
In order to take data using the DCPS3, you will first need to instantiate a class of ```DCPS3_analyser```.
```py
analyser = DCPS3_analyser(N=100_000, freq=160) # Frequency is in MHz, default settings are N=100_000, freq=160
```
From there, you can use the test_dcps method to begin taking data. Pass in a folder in which to save the data. From here, you can specify which settings you would like to test or pass in a test preset that you would like to use. Please see dcps3_toolkit/analysis/DCPS3.py for more details.
```py
data_save_folder = "./data"
analyser.test_dcps(data_folder=data_save_folder,
                  test_preset=None, 
                  num_runs=10, 
                  channels=[2, 3], 
                  coarse_vals=range(32), 
                  stage4_vals=[2, 3], 
                  stage5_vals=[2, 3], 
                  fine_vals=range(67),
                  dcps_file="dcps_i2c.py", 
                  measure_temp=False,
                  show_output=True,)
```
## Loading Data and Plotting
### Using the Jupyter Notebook
To load and plot collected data, simply use the final_analysis.ipynb notebook and run all relevant cells for the plots you would like to create. For more custom plotting, see "Using a Python Script".
### Using a Python Script
Once data has been collected, plotting is very simply. First, using the DCPS3_analyser class, load in the collected data from a folder using the load_dcps method. You will also need to give the data a name, this name is arbitary, and is only used to call the data later.
```py
data_save_folder = "./data"
analyser.load_data(data_folder=data_save_folder, data_name="test_data")
```
#### Data Format
When loading in the data, it is stored internally in the class as a pandas dataframe. The data is formated as follows:

- Headers: "channel", "run", "coarse_step", "stage4_tune", "stage5_tune", "fine_step", "delay", "_std_dev", "_count", "temperature" (temperature is optional)

- channel:     DCPS channel being used
- run:         The run number of the data point
- coarse_step: Coarse step value of DCPS (0 - 31)
- stage4_tune: Stage 4 tuning bit value of DCPS (0, 2, or 3)
- stage5_tune: Stage 5 tuning bit value of DCPS (0, 2, or 3)
- fine_step:   Fine step value of DCPS (0 - 66)
- delay:       Average time delay difference between DDMTD channels (ps) Note: All preset plots will compare these values relative to some zero-point 
             (usually when fine_step == 0 and coarse step == 0)
- _std_dev:    Standard deviation of time delay difference between DDMTD channels (ps) Note: standard deviation is taken from a gaussian fit to
             histogram of ddmtd values
- _count:      Number of total points for a single delay data point (total count from histogram)
- temperature: Temperature measured at data point
###
After this, you can either create your own plots by using the loaded data directly by calling
```py
data = analyser.loaded_data["DATA NAME HERE"]
# Do plotting stuff here
...
```
Or, you can use one of the many preset plots by calling the plot_dcps method
```py
analyser.plot(figure_folder="./figures", plot_preset="coarse_delay", data_name="test_data")
```
Please see dcps3_toolkit/analysis/DCPS3.py and dcps3_toolkit/analysis/tools/plot_dcps3.py for more details.
## Example Usage
### Basic Coarse Delay Test
```py
from tools.DCPS3 import DCPS3_analyser

analyser = DCPS3_analyser(N=100_000, freq=160) # Create DCPS3_analyser object

# Plots coarse values 0 - 31 with stage 4 and stage 5 tunes set to 2, 2. Uses channels 2 and 3, total of 10 runs for each channel
# A run like this typically takes ~2 hours
analyser.test_dcps(data_folder="./data/coarse_delay", test_preset="coarse_consistency")

# Loads in acquired data
analyser.load_data("./data/coarse_delay", data_name="coarse")

# Plots the average slope over multiple runs
analyser.plot(figure_folder="./figures/coarse_test", plot_preset="coarse_consistency", data_name="coarse")

# Plots the slope from each point within each run
analyser.plot(figure_folder="./figures/coarse_test", plot_preset="coarse_delay", data_name="coarse") 
```
### Custom Data Taking Test
```py
from tools.DCPS3 import DCPS3_analyser

analyser = DCPS3_analyser(N=100_000, freq=160) # Create DCPS3_analyser object

# Plots coarse values 0, 1, 2, 4, 8, 16 testing tuning values of both (2, 2) and (2, 3).
# Uses only channel 3, total of 5 runs for each permutation of settings.
analyser.test_dcps(data_folder="./data/custom_test",
                  test_preset=None, 
                  num_runs=5, 
                  channels=[3], 
                  coarse_vals=[0, 1, 2, 4, 8, 16], 
                  stage4_vals=[2], 
                  stage5_vals=[2, 3], 
                  fine_vals=[0],
                  dcps_file="dcps_i2c.py", 
                  measure_temp=False,
                  show_output=True,)

# Loads in acquired data
analyser.load_data("./data/custom_test", data_name="coarse")

# Grab loaded data
data = analyser.loaded_data["coarse"]

# Can do other stuff with data at this point
print(data)
...

```
