create_clock -add -name sys_clk_pin -period 10.00   -waveform {0 5}          [get_ports clk]
create_clock -add -name spi_sck     -period 160.000 -waveform {0.000 80.000} [get_ports spi_sck]

create_clock -add -name CLK_P -period  25 -waveform  {0.000 12.5} [get_ports CLK_P]
# create_clock -add -name Q1A_P -period   5 -waveform {0.000 2.5} [get_ports Q1A_P]
# create_clock -add -name Q1B_P -period   5 -waveform {0.000 2.5} [get_ports Q1B_P]
# create_clock -add -name Q2A_P -period   5 -waveform {0.000 2.5} [get_ports Q2A_P]
# create_clock -add -name Q2B_P -period   5 -waveform {0.000 2.5} [get_ports Q2B_P]

