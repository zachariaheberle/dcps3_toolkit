# reset_run synth_1
# launch_runs impl_1 -to_step write_bitstream -jobs 10
write_cfgmem  -format hex -size 32 -interface SPIx1 -loadbit {up 0x00000000 "/home/rsaradhy/work/nexys_ddmtd_latest/Firmware/Nexys.runs/impl_1/main_v2.bit" } -force -file "/home/rsaradhy/work/nexys_ddmtd_latest/RPi_Side/HEX_Files/2022_12_03_v2_031.hex"

