
####### DCPS3 Instantiation and Setup #######
import tools.common_vars as common_vars

common_vars.server = "pi@nexys_ddmtd_dcps3" # Change this to whatever you setup the pi's host name as in your ssh config

from tools.DCPS3 import DCPS3_analyser

# Keep these values the same
N = 100_000
freq = 160 # MHz

analyser = DCPS3_analyser(N=N, freq=freq)

data_save_folder_name = "test"

####### DCPS3 Fine Delay Test #######
fine_data_folder = f"./data/{data_save_folder_name}/N{N}_fine"

analyser.test_dcps(fine_data_folder, "fine_consistency", num_runs=1)


####### DCPS3 Coarse Delay Test #######
coarse_data_folder = f"./data/{data_save_folder_name}/N{N}_coarse"

analyser.test_dcps(coarse_data_folder, "coarse_consistency", num_runs=1)


####### Coarse Delay Plotting #######
figure_folder = f"./figures/{data_save_folder_name}"

analyser.load_data(coarse_data_folder, "coarse")

analyser.plot(figure_folder, "coarse_delay", "coarse")
analyser.plot(figure_folder, "coarse_consistency", "coarse")


####### Fine Delay Plotting #######
figure_folder = f"./figures/{data_save_folder_name}"

analyser.load_data(fine_data_folder, "fine")

analyser.plot(figure_folder, "fine_delay", "fine")
analyser.plot(figure_folder, "fine_consistency", "fine")