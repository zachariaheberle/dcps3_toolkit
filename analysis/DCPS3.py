import os
import shutil
import subprocess

from tools.base import *
import tools.parser as parser
import tools.test_dcps3 as test_dcps3
import tools.plot_dcps3 as plot_dcps3
import tools.common_vars as common_vars
import time

class DCPS3_analyser():

    def __init__(self, N=100000, freq=160) -> None:
        """
        N -> Setting related to DDMTD clock offset, generally you should stick with 100k
        freq -> Frequency (in MHz) at which to run the DCPS and DDMTD clocks
        """
        self._N = N
        self._freq = freq # MHz
        self.loaded_data = dict()
        self.dcps_initialized = False
    
    @staticmethod
    def get_plot_presets():
        """
        Returns a list of all currently valid plot preset options
        """
        return list(plot_dcps3.presets.keys())

    @staticmethod
    def get_test_presets():
        """
        Returns a list of all currently valid test preset options
        """
        return list(test_dcps3.presets.keys())

    @property
    def N(self):
        return self._N
    
    @N.setter
    def N(self, new_N):
        """
        Ensure that if we change N for any reason, we reinitialize the DCPS board, else it won't work
        """
        self.dcps_initialized = False
        self._N = new_N
    
    @property
    def freq(self):
        return self._freq
    
    @freq.setter
    def freq(self, new_freq):
        """
        Ensure that if we change freq for any reason, we reinitialize the DCPS board, else it won't work
        """
        self.dcps_initialized = False
        self._freq = new_freq
    
    def load_data(self, data_folder, data_name, sep="", draw_all_points=False, force_reload=False):
        """
        Loads data from ddmtd.txt files, data comes in a data frame that is then placed in a dictionary with
        the key named data_name.

        Data is formatted as follows:
        Headers: "channel", "run", "coarse_step", "fine_step", "delay", "_std_dev", "_count", "temperature" (temperature is optional)

        channel:     PLL channel being used (1 - 3)
        run:         The run number of the data point
        coarse_step: Coarse step value of Delay Chip (0 - 1024)
        fine_step:   Fine step value of PLL delay (-32768 - 32767)
        delay:       Average time delay difference between DDMTD channels (ps) Note: All preset plots will compare these values relative to some zero-point 
                     (usually when fine_step == 0 and coarse step == 0)
        _std_dev:    Standard deviation of time delay difference between DDMTD channels (ps) Note: standard deviation is taken from a gaussian fit to
                     histogram of ddmtd values
        _count:      Number of total points for a single delay data point (total count from histogram)
        temperature: Temperature measured at data point

        """
        if not isinstance(data_name, str):
            raise TypeError("data_name must be a string")
        
        df = parser.load_files(data_folder, self.N, self.freq, sep=sep, draw=draw_all_points, force_reload=force_reload)

        self.loaded_data[data_name] = df

        #print(df.to_string())
    
    def test_dcps(self, 
                  data_folder,
                  test_preset=None, 
                  num_runs=10, 
                  channels=[2, 3], 
                  coarse_vals=range(1024), 
                  fine_vals=range(-32768, 32768),
                  dcps_file="dcps_i2c.py", 
                  measure_temp=False,
                  show_output=True,
                  **kwargs):
        """
        Handles actively testing the dcps board, requires that ssh config and keys are already set up.
        Data for the test will be saved to data_folder. kwargs are ONLY used for passing additional info 
        to preset function

        Exmaple: set fine_consistency to start at coarse control = 16...
        DCPS3_analyser.test_dcps(data_folder, test_preset='fine_consistency', coarse_control=16)
        """

        def check_connection():
            """
            Runs simple ssh command to ensure we can connect to the raspberry pi
            """
            try:
                subprocess.run(["ssh", server, "ls"], timeout=5, check=True, stdout=subprocess.DEVNULL)
            except:
                return False
            else:
                return True

        server = common_vars.server
        
        if check_connection():
            if not self.dcps_initialized:
                try:
                    test_dcps3.initialize(self.N, self.freq)
                    self.dcps_initialized = True
                except Exception as err:
                    raise Exception(f"Something went wrong with board initialization!: {err}")
     
            print("Running Sanity Checks...")
            test_dcps3.sanity_check(self.freq, self.N, test_temp=measure_temp)
            print("Sanity Checks Passed!")
            try:
                shutil.rmtree("./temporary_test")
            except (FileNotFoundError, OSError):
                print(f"Could not find directory {os.getcwd()}/temporary_test, ignoring directory deletion.")
            
            mkdir(data_folder)
            if test_preset in test_dcps3.presets and test_preset is not None:
                test_dcps3.presets[test_preset](data_folder, num_runs, show=show_output, **kwargs)

            elif test_preset is None:
                for run in range(num_runs):
                    for channel in channels:
                        for coarse_control in coarse_vals:
                            for fine_control in fine_vals:
                                test_dcps3.data_acq(fine_control, 
                                                    coarse_control, 
                                                    channel, 
                                                    run, 
                                                    data_folder, 
                                                    dcps_file, 
                                                    show_output,
                                                    measure_temp)
            else:
                raise KeyError(f"{test_preset} is not a valid test preset!\nPlease use DCPS3_analyser.get_test_presets() to get all valid test presets.")
            
        else:
            raise ConnectionError("Aborting DCPS 3 test, cannot connect to board")

    def plot(self, figure_folder, plot_preset, data_name, **kwargs):
        """
        Automatically plots data from self.loaded_data[data_name] dataframe using a predefined plot preset.

        data_name: name (key name) of dataframe in self.loaded_data that you wish to plot

        allowed kwargs:

        add_temp_vals: bool; plots temperature values in addition to delay values
        channels: ArrayLike; set which channels you'd like to plot
        runs: ArrayLike; set which runs you'd like to plot
        """

        if plot_preset in plot_dcps3.presets:
            data = self.loaded_data[data_name]
            mkdir(figure_folder)
            plot_dcps3.presets[plot_preset](data, figure_folder, **kwargs)
        else:
            raise KeyError(f"{plot_preset} is not a valid plot preset!\nPlease use DCPS3_analyser.get_plot_presets() to get all valid plot presets.")




        
        

        
