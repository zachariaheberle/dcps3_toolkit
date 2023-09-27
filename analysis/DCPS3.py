import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
import time
import pandas as pd
import os
from glob import glob
import sigfig
import subprocess

from tools.base import *
from tools.ddmtd import ddmtd
import tools.parser as parser
import tools.test_dcps3 as test_dcps3
import tools.plot_dcps3 as plot_dcps3
import tools.common_vars as common_vars
from time import sleep

import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable

class DCPS3_analyser():

    def __init__(self, N=100000, freq=160) -> None:
        self._N = N
        self._freq = freq # MHz
        self.loaded_data = dict()
        self.dcps_initialized = False
    
    @property
    def N(self):
        return self._N
    
    @N.setter
    def N(self, new_N):
        self.dcps_initialized = False
        self._N = new_N
    
    @property
    def freq(self):
        return self._freq
    
    @freq.setter
    def freq(self, new_freq):
        self.dcps_initialized = False
        self._freq = new_freq
    
    def load_data(self, data_folder, data_type, sep="", draw_all_points=False, force_reload=False):
        """
        Loads data from ddmtd.txt files, data comes in a data frame that is then placed in a dictionary with
        the key named data_type 
        """
        if not isinstance(data_type, str):
            raise TypeError("data_type must be a string")
        
        df = parser.load_files(data_folder, self.N, self.freq, sep=sep, draw=draw_all_points)

        self.loaded_data[data_type] = df

        #print(df.to_string())
    
    def test_dcps(self, 
                  data_folder,
                  test_preset=None, 
                  num_runs=10, 
                  channels=[2, 3], 
                  coarse_vals=range(32), 
                  stage4_vals=[2, 3], 
                  stage5_vals=[2, 3], 
                  fine_vals=range(67),
                  dcps_file="dcps_i2c.py", 
                  measure_temp=False,
                  show_output=True,
                  **kwargs):
        """
        Handles actively testing the dcps board, requires that ssh config and keys are already set up.
        kwargs are ONLY used for passing additional info to preset function, like setting the stage4 and stage5 tunes
        for coarse_consistency or setting any coarse tunes for fine_consistency.

        Example: Say we want to set coarse_consistency stage 4 and stage 5 tunes to 2, 3, then we would call...
        DCPS3_analyser.test_dcps(data_folder, test_preset='coarse_consistency', stage4_tune=2, stage5_tune=3)

        Exmaple 2: set fine_consistency to start at coarse control = 16...
        DCPS3_analyser.test_dcps(data_folder, test_preset='fine_consistency', coarse_control=16)
        """

        def check_connection():
            try:
                subprocess.run(["ssh", server, "ls"], timeout=5, check=True, stdout=subprocess.DEVNULL)
            except:
                return False
            else:
                return True

        server = common_vars.server

        if isinstance(stage4_vals, int):
            stage4_vals = [stage4_vals] # Allows for integer inputs for stage4_vals instead of iterable
        if isinstance(stage5_vals, int):
            stage5_vals = [stage5_vals] # Allows for integer inputs for stage5_vals
        
        if check_connection():
            if not self.dcps_initialized:
                try:
                    test_dcps3.initialize(self.N, self.freq)
                    self.dcps_initialized = True
                except:
                    print("Something went wrong with board initialization!")
                    return
            mkdir(data_folder)
            if test_preset in test_dcps3.presets:
                test_dcps3.presets[test_preset](data_folder, num_runs, show=show_output, **kwargs)
            else:
                for run in range(num_runs):
                    for channel in channels:
                        for stage4_tune in stage4_vals:
                            for stage5_tune in stage5_vals:
                                for coarse_control in coarse_vals:
                                    for fine_control in fine_vals:
                                        test_dcps3.data_acq(fine_control, 
                                                            coarse_control, 
                                                            stage4_tune, 
                                                            stage5_tune, 
                                                            channel, 
                                                            run, 
                                                            data_folder, 
                                                            dcps_file, 
                                                            show_output,
                                                            measure_temp)
        else:
            print("Aborting DCPS 3 test, cannot connect to board")
            return

    def plot(self, data_type, figure_folder, x_type=None, y_type=None, plot_preset=None, **kwargs):
        """
        Documentation goes here

        data_type: key of dataframe in self.loaded_data that you wish to plot

        x_type allowed values: 'run', 'coarse_step', 'fine_step', 'temperature'
        y_type allowed values: 'delay_slope', 'delay', 'temperature'
        allowed plot_presets: coarse_delay, coarse_consistency, coarse_relative_consistency, coarse_cell_consistency
        fine_delay, fine_consistency, fine_relative_consistency, fine_cell_consistency


        allowed kwargs:
        add_temp_vals: bool; plots temperature values in addition to y_type
        channels: ArrayLike; set which channels you'd like to plot
        runs: ArrayLike; set which runs you'd like to plot
        stage4_tunes: ArrayLike; set which stage 4 tunes to use
        stage5_tunes: ArrayLike; set which stage 5 tunes to use

        xlabel: str; sets xlabel of resulting plot
        ylabel: str; sets ylabel of resulting plot

        xlim: ArrayLike; sets x-axis limits
        ylim: ArrayLike; sets y-axis limits

        xticks: ArrayLike; sets x-axis tick marks
        yticks: ArrayLike; sets y-axis tick marks

        title: str; sets the title of the resulting plot
        legend_loc: str; sets location of legend

        delay_units: str, sets delay units (ps or fs)
        residuals: bool; If true, plots residuals beneath main plot in addition
        to a histogram of the residuals (seperate plot)

        Note: presets have a significantly limited allowed kwargs values, 
        see individual preset functions for more info
        """
        x_types = ['run', 'coarse_step', 'fine_step', 'temperature']
        y_types = ['delay_slope', 'delay', 'temperature']

        if plot_preset in plot_dcps3.presets:
            data = self.loaded_data[data_type]
            mkdir(figure_folder)
            plot_dcps3.presets[plot_preset](data, figure_folder, **kwargs)
            pass
        else:
            if x_type in x_types and y_type in y_types:
                mkdir(figure_folder)
                plot_dcps3.plot_generic(data, figure_folder, x_type, y_type, **kwargs)
            else:
                raise TypeError("Invalid x_type or y_type")
    
    
            




a = DCPS3_analyser(board=1)

c_folder = "./dcps3Test/data/board1_host2_test/host2_board1_N100000_coarse"
f_folder = "./dcps3Test/data/board1_host2_test/host2_board1_N100000_fine"

#a.load_data(c_folder, data_type="coarse")
a.load_data(f_folder, data_type="fine")
# #print(a.loaded_data["coarse"])
a.plot("fine", "./dcps3Test/figures/test", plot_preset="fine_delay")
#a.plot("coarse", "./dcps3Test/figures/test", plot_preset="coarse_delay")

        
        

        
