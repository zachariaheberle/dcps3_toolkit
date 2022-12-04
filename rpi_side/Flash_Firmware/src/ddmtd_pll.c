#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>


// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#define BYTES_PER_PAGE 256 // For Nexys Video
#define MAX_BYTES 32000000
#define MAX_TRIALS 3  //Changed from 5 to 2

#define CHIP_ID 0x10219 // CHIP ID for Nexys Video



#include "spi_common.h"
#include "Si5344_REG.h"






#include "NexysDDMTD.h"

// Send a 32-bit spi_write command, which writes 16 bits into the address and returns the Result



int main()
{
  // Startup the SPI interface on the Pi.


  init_spi();
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64);     // 6 MHz


  for (int i=0;i< SI5344_REVD_REG_CONFIG_NUM_REGS; i=i+1)
  {

    spi_si5344_write_v2(si5344_revd_registers[i].address,si5344_revd_registers[i].value);
    //Making sure these are written properly
    if (spi_si5344_read_v2(si5344_revd_registers[i].address) != si5344_revd_registers[i].value) printf("address = 0x%04x, value = 0x%02x ; Value returned = 0x%02x   \n",si5344_revd_registers[i].address,si5344_revd_registers[i].value ,spi_si5344_read(si5344_revd_registers[i].address) );
  }


  end_spi();


  return(0);

}// Main ends here
