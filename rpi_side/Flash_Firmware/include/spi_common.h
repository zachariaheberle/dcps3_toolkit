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



// Initialize the SPI interface.
void init_spi(void);

// Close the SPI interface.
void end_spi(void);

// Send a 32-bit spi_read command, and keep the 16 bits that are returned.
int spi_get_16bits(int addr);

// Send a 32-bit spi_write command, which writes 16 bits into the address.
int spi_put_16bits(int addr, int value);

// printing bits...
void print_bits(int size,int64_t Data);

int write_toFiles(FILE* fp1,FILE* fp2,  void* virtual_address, int byte_count);

int print_nWords(void* virtual_address, int byte_count, int mod_num) ;

