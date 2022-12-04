// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>
#include <inttypes.h>
#include "spi_common.h"
#include "NexysDDMTD.h"



int main(int argc, char** argv)
{
  // Startup the SPI interface on the Pi.
  init_spi();
  
  resetDDMTD();
  int reset_status = 1;
  int reset_iteration  = 0 ;
  char output;
  while (1)
  {
    output =resetStatus();
    reset_status = (uint)(output);
    // printf("%u \n",reset_status);
    if (reset_status==1) break;
  }
  printf("RESET DONE \n");

  heating_status(0); //0--> both off; 1--> heat ddmtd1; 2--> head ddmtd2; 
  checkFirmware();
  //End SPI
  end_spi();
}