# reset_run synth_1
# launch_runs impl_1 -to_step write_bitstream -jobs 10
# write_cfgmem  -format hex -size 32 -interface SPIx1 -loadbit {up 0x00000000 "/home/rsaradhy/work/nexys_ddmtd_latest/Firmware/Nexys.runs/impl_1/main_v2.bit" } -force -file "/home/rsaradhy/work/nexys_ddmtd_latest/rpi_side/HEX_Files/2022_12_03_v2_032.hex"

# S25FL256S

write_cfgmem  -format hex -size 32 -interface SPIx1 -loadbit {up 0x00000000 "/home/rsaradhy/work/nexys_ddmtd_github/firmware/project_folder/project_folder.runs/impl_1/main_v2.bit" } -force -file "/home/rsaradhy/work/nexys_ddmtd_github/rpi_side/HEX_Files/40MHz_6.25Delay_MAIN_v2_042.hex"
