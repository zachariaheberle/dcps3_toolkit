create_clock -period 10.000 -name sys_clk_pin -waveform {0.000 5.000} -add [get_ports clk]
create_clock -period 160.000 -name spi_sck -waveform {0.000 80.000} -add [get_ports spi_sck]


create_clock -period 5.000 -name CLK_200 -waveform {0.000 2.500} [get_ports CLK_200_P]


create_clock -period 25.000 -name CLK_P -waveform {0.000 12.500} -add [get_ports CLK_P]
set_input_delay -clock [get_clocks CLK_P] -add_delay 5.000 [get_ports {Q1A_P Q1B_P Q2A_P Q2B_P}]

# create_clock -add -name Q1B_P -period   5 -waveform {0.000 2.5} [get_ports Q1B_P]
# create_clock -add -name Q2A_P -period   5 -waveform {0.000 2.5} [get_ports Q2A_P]
# create_clock -add -name Q2B_P -period   5 -waveform {0.000 2.5} [get_ports Q2B_P]


set_input_delay -clock [get_clocks spi_sck] -clock_fall 0.000 [get_ports spi_mosi]
