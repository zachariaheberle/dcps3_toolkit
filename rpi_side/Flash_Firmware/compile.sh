# Written by Rohith Saradhy
# Email -> rohithsaradhy@gmail.com
#gcc -O program_fpga.c  -l bcm2835 -o ORMFlash.exe
# gcc -O program_fpga_Nex.c  -l bcm2835 -o NexFlash.exe
# gcc -O GBT_SCA.c  spi_common.c -l bcm2835 -o GBT_SCA.exe
# gcc -O sca_blink.c spi_common.c  -l bcm2835 -o sca_blink.exe

# gcc -O ddmtd_mem.c spi_common.c NexysDDMTD.c -l bcm2835 -o ddmtd_mem.exe
# echo Done Compiling MEM

# # gcc -O data_acq_64k.c spi_common.c NexysDDMTD.c -l bcm2835 -o data_acq_64k.exe
# # echo Done Compiling data_acq_64k

gcc -Iinclude -O src/data_acq.c src/spi_common.c src/NexysDDMTD.c -l bcm2835 -o bin/data_acq.exe
echo Done Compiling data_acq


gcc -Iinclude -O src/ddmtd_pll.c src/spi_common.c src/NexysDDMTD.c -l bcm2835 -o bin/ddmtd_pll.exe
echo Done Compiling PLL

gcc -Iinclude -Isrc -O src/spi_common.c src/NexysDDMTD.c src/check_firmware.c  -l bcm2835 -o bin/check_firmware.exe
echo Done Compiling CheckFirmware
