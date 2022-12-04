// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include "spi_common.h"
#include "NexysDDMTD.h"




int set_addr(int address) {
  char cmd[2],data[2];  // two Bytes
  cmd[0] = 0b00000000; //Command to set address
  cmd[1] = address; // Page Address Location
  bcm2835_spi_transfernb(cmd, data, 2);

}

char read4addr(int address) // Need to set page, only reads 8bit address...
{
  char cmd[2],data[2];  // two Bytes
  set_addr(address&0xFF); //8 bits only
  cmd[0] = 0b10000000; //Command to Read Data
  bcm2835_spi_transfernb(cmd, data, 2);
  // print_bits(8,data[1]);
  return data[1];
}


int write2addr(int address,int value){ // Works within the page so 8 bit address
  char cmd[2],data[2];  // two Bytes
  //set_addr
  set_addr(address&0xFF); //8 bits only
  // Write the page address
  cmd[0] = 0b01000000; //Command to Write Data
  cmd[1] = value&0xFF; // Write the page address
  bcm2835_spi_transfernb(cmd, data, 2);

}

int set2page(int value) {
    write2addr(0x1,value&0xFF);
}


int spi_si5344_write(unsigned int address,unsigned char value) // Writes 8 bits into the 16 bit register
{
  spi_NexyDDMTD_io(0x101,0x1);
  bcm2835_spi_chipSelect(BCM2835_SPI_CS1); // Changing to
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW);	// Value of CS when active



  char cmd[2],data[2];  // two Bytes

  //Changing page address
  unsigned int page;
  page = (address>>8)&(0xFF);
  set2page(page); //write to page register the page you want to go to.
  // if ((int)read4addr(0x1) == page) printf("Success at setting the page to 0x%04x\n",(int)read4addr(0x1) );
  // else printf("Oh No...... Page not set to 0x%04x, the read value is 0x%04x! \n",page,(int)read4addr(0x1));
  write2addr((address&0xFF),value);
  // if ((int)read4addr(address&0xFF) == (int)value) printf("Success at writing  to 0x%04x with the value 0x%02x \n",(int)read4addr(0x1)<<8|address&0xFF,value );
  // else printf("Oh No...... Page not set to 0x%02x, the read value is 0x%02x! \n",(int)value,(int)read4addr(0x1));

  // bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Talking to FPGA
  // spi_NexyDDMTD_io(0x101,0x0000); // Making the FPGA connect MEM to RPi from RPi
}


int spi_si5344_read(unsigned int address) // Writes 8 bits into the 16 bit register
{
  spi_NexyDDMTD_io(0x101,0x1);
  bcm2835_spi_chipSelect(BCM2835_SPI_CS1); // Changing to
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW);	// Value of CS when active
  char cmd[2],data[2];  // two Bytes

  //Changing page address
  unsigned int page;
  page = (address>>8)&(0xFF);
  set2page(page); //write to page register the page you want to go to.
  // if ((int)read4addr(0x1) == page) printf("Success at setting the page to 0x%04x\n",(int)read4addr(0x1) );
  // else printf("Oh No...... Page not set to 0x%04x, the read value is 0x%04x! \n",page,(int)read4addr(0x1));
  int value = read4addr((address&0xFF));

  bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Talking to FPGA
  spi_NexyDDMTD_io(0x101,0x0000); // Making the FPGA connect MEM to RPi from RPi
  return value;
}



int spi_NexyDDMTD_io(int addr, int value) //Transfers 32bits of data

{
  const int num_Bytes = 8; 
  char cmd[num_Bytes], data[num_Bytes];
  // int result;

  // char is 8 bits
  // int used as 32bits

  int spi_read, spi_auto_inc, spi_addr, spi_command;

  // Create the 32-bit command word.
  spi_command = (addr<<16)|(value & 0xFFFF);
  cmd[0] = (spi_command >> 24)&(0xFF);
  cmd[1] = (spi_command >> 16)&(0xFF);
  cmd[2] = (spi_command >>  8)&(0xFF);
  cmd[3] = (spi_command      )&(0xFF);


  // Send the command.

  bcm2835_spi_transfernb(cmd, data, num_Bytes);


  int output;
  output = data[4]<<24|data[5]<<16|data[6]<<8|data[7];
    // print_bits(32,output);
  // fprintf(stderr,"value = %04d\n",output);
  return output;
}






//Software for New Firmware version >= 2.017

char send3Byte_NexysDDMTD(int addr, int val) //Send three byte with version >= 2.017
{
  char cmd[3];
  char data[3];
  cmd[0] = addr & 0xFF; //Address
  cmd[1] = val  & 0xFF; // Value to set if applicable
  cmd[2] = 0    & 0xFF; // Information is send back in this byte

  data[0] = 0;
  data[1] = 0;
  data[2] = 0;

  bcm2835_spi_transfernb(cmd, data, 3);

  return data[2];
};

void checkFirmware()
{
  char firmware_major,firmware_minor;
  uint output;
  firmware_major = send3Byte_NexysDDMTD(FIRMWARE_ADDR_MAJOR,0);
  firmware_minor = send3Byte_NexysDDMTD(FIRMWARE_ADDR_MINOR,0);
  output = (uint)((firmware_major<<8)|(firmware_minor));
  printf("Firmware Version: %0.3f \n",(float)(output)/1000);

};

void resetDDMTD()
{
  send3Byte_NexysDDMTD(RESET_DDMTD,0x1);
}

char resetStatus()
{
  return send3Byte_NexysDDMTD(RESET_DONE,0x0);
}

void startAcq()
{
  send3Byte_NexysDDMTD(START_ACQ,0x1);
}
void stopAcq()
{
  send3Byte_NexysDDMTD(START_ACQ,0x0);
}

void readCounter()
{
  char output;
  output=send3Byte_NexysDDMTD(READ_COUNTER,0x0);
  printf("Read Counter: %u\n",(uint)(output));
}

void readFIFO_readCount(){
  char output;
  output=send3Byte_NexysDDMTD(READ_COUNT_FIFO,0x0);
  printf("FIFO READ COUNT: %u\n",(uint)(output));
};
void readFIFO_writeCount(){
  char output;
  output=send3Byte_NexysDDMTD(WRITE_COUNT_FIFO,0x0);
  printf("FIFO WRITE COUNT: %u\n",(uint)(output));
};


void heating_status(int i){
  char output;
  output=send3Byte_NexysDDMTD(HEAT_REGISTERS,i&0b11);
  printf("HEATING 1 STATUS: %u\n",(uint)(output&0b1));
  printf("HEATING 2 STATUS: %u\n",(uint)((output>>1)&0b1));

}

int spi_si5344_write_v2(unsigned int address,unsigned char value) // Writes 8 bits into the 16 bit register
{
  send3Byte_NexysDDMTD(DDMTD_PLL_EN_ADDR,0x1); // Point to PLL from FPGA

  bcm2835_spi_chipSelect(BCM2835_SPI_CS1); // Changing to
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW);	// Value of CS when active



  char cmd[2],data[2];  // two Bytes

  //Changing page address
  unsigned int page;
  page = (address>>8)&(0xFF);
  set2page(page); //write to page register the page you want to go to.
  // if ((int)read4addr(0x1) == page) printf("Success at setting the page to 0x%04x\n",(int)read4addr(0x1) );
  // else printf("Oh No...... Page not set to 0x%04x, the read value is 0x%04x! \n",page,(int)read4addr(0x1));
  write2addr((address&0xFF),value);
  // if ((int)read4addr(address&0xFF) == (int)value) printf("Success at writing  to 0x%04x with the value 0x%02x \n",(int)read4addr(0x1)<<8|address&0xFF,value );
  // else printf("Oh No...... Page not set to 0x%02x, the read value is 0x%02x! \n",(int)value,(int)read4addr(0x1));

  // bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Talking to FPGA
  // spi_NexyDDMTD_io(0x101,0x0000); // Making the FPGA connect MEM to RPi from RPi
}


int spi_si5344_read_v2(unsigned int address) // Writes 8 bits into the 16 bit register
{
  send3Byte_NexysDDMTD(DDMTD_PLL_EN_ADDR,0x1); // Point to PLL from FPGA

  bcm2835_spi_chipSelect(BCM2835_SPI_CS1); // Changing to
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW);	// Value of CS when active
  char cmd[2],data[2];  // two Bytes

  //Changing page address
  unsigned int page;
  page = (address>>8)&(0xFF);
  set2page(page); //write to page register the page you want to go to.
  // if ((int)read4addr(0x1) == page) printf("Success at setting the page to 0x%04x\n",(int)read4addr(0x1) );
  // else printf("Oh No...... Page not set to 0x%04x, the read value is 0x%04x! \n",page,(int)read4addr(0x1));
  int value = read4addr((address&0xFF));

  bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Talking to FPGA
  send3Byte_NexysDDMTD(DDMTD_PLL_EN_ADDR,0x0); // Point to FLASH from FPGA
  return value;
}

