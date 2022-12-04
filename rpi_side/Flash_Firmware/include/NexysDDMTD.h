// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

//FPGA Addresses

#if !defined(NEXYSDDMTD_H)
#define NEXYSDDMTD_H 1

static const int  FIRMWARE_ADDR_MAJOR = 1;
static const int  FIRMWARE_ADDR_MINOR = 2;
static const int  DDMTD_PLL_EN_ADDR   = 3;
static const int  RESET_DDMTD         = 4;
static const int  TEST_REG            = 11;
static const int  RESET_DONE          = 12;
static const int  READ_COUNTER        = 13;
static const int  WRITE_COUNT_FIFO    = 14; 
static const int  READ_COUNT_FIFO     = 15; 
static const int  HEAT_REGISTERS      = 16;

static const int ADDR_MEM1 = 0x6;
static const int ADDR_MEM2 = 0x7;
static const int MEM_FULL  = 0x8;
static const int MEM_AFULL = 0x9;
static const int START_ACQ = 0xa;

#endif



//Talking to si5324 via spi
int set_addr(int address);
char read4addr(int address); // Need to set page, only reads 8bit address...
int write2addr(int address,int value); // Works within the page so 8 bit address
int set2page(int value); // sets the page to the 8 bit value
int spi_si5344_write(unsigned int address,unsigned char value); // Writes 8 bits into the 16 bit register
int spi_si5344_read(unsigned int address); // Writes 8 bits into the 16 bit register

//Nexys SPI
int spi_NexyDDMTD_io(int addr, int data);


//Software for New Firmware version >= 2.017
//Talk to the FPGA Logic
char send3Byte_NexysDDMTD(int addr, int val);
void checkFirmware();
void resetDDMTD();
char resetStatus();
void startAcq();
void stopAcq();
void readCounter();
void readFIFO_readCount();
void readFIFO_writeCount();
void heating_status(int i);


int spi_si5344_write_v2(unsigned int address,unsigned char value); // Writes 8 bits into the 16 bit register
int spi_si5344_read_v2(unsigned int address); // Writes 8 bits into the 16 bit register

