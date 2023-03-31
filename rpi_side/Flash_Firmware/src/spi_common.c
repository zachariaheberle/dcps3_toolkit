// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com

#include <stdlib.h>
#include <stdio.h>
#include "spi_common.h"
#include <stdint.h>






//Printing 16 bits...
void print_bits(int size,int64_t Data)
{
  char Result[size];
  for(int i=0; i< size;i++)
  {
    Result[i] = (Data >>i ) & 1; //Take the Least Significant Bit after shifting
  }

  for(int i=1;i<=size;i++ )
  {
    printf("%i",(int)Result[size-i]);
    if((i % 4 == 0 ) && (i != 0 ))printf(" ");
    // if((i % 8 == 0 ) && (i != 0 ))printf("\n");
  }
  printf("\n");


}




// Send a 32-bit spi_read command, and keep the 16 bits that are returned.
int spi_get_16bits(int addr)
{
  char cmd[4], data[4];
  unsigned spi_read, spi_auto_inc, spi_addr, spi_command;
  int result;

  // Create the 32-bit command word.
  spi_read = 1;
  spi_auto_inc = 0;
  spi_addr = addr & 0x3FF; //Taking the 0b1111111111 of the address
  spi_command = (spi_read<<31)|(spi_auto_inc<<30)|(spi_addr<<20); //Constructing the command...
  cmd[0] = spi_command >> 24;//Taking the first 8 bits
  cmd[1] = spi_command >> 16;//Taking the next 8 bits
  cmd[2] = spi_command >> 8;//Taking the next 8 bits
  cmd[3] = spi_command >> 0;//Taking the next 8 bits

  // Send the command.
  bcm2835_spi_transfernb(cmd, data, 4); // input buffer, output buffer, and length of input and output buffer....

  result = (data[2]<<8) | data[3];
  return (result);
}

// Send a 32-bit spi_write command, which writes 16 bits into the address.
int spi_put_16bits(int addr, int value)
{
  char cmd[4], data[4];
  unsigned spi_read, spi_auto_inc, spi_addr, spi_command;

  // Create the 32-bit command word.
  spi_read = 0;
  spi_auto_inc = 0;
  spi_addr = addr & 0x3FF;
  spi_command = (spi_read<<31)|(spi_auto_inc<<30)|(spi_addr<<20)|
    (value & 0xFFFF);
  cmd[0] = spi_command >> 24;
  cmd[1] = spi_command >> 16;
  cmd[2] = spi_command >> 8;
  cmd[3] = spi_command >> 0;

  // Send the command.
  bcm2835_spi_transfernb(cmd, data, 4);
  return (0);
}




// Initialize the SPI interface.
void init_spi()
{
  if(!bcm2835_init())
  {
    printf("bcm2825_init failed. You most likely are not running as root.\n");
    exit(1);
  }

  if(!bcm2835_spi_begin())
  {
    printf("bcm2825_spi_begin failed. You most likely are not running as root.\n");
    exit(1);
  }

  bcm2835_spi_begin();
  bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);
  // bcm2835_spi_setDataMode(BCM2835_SPI_MODE3);
  bcm2835_spi_setDataMode(BCM2835_SPI_MODE0); 
  // bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_65536);	//kHz
  // bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_);	// 50MHz
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_32);     // 6 MHz
  // bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64);
  // bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_128);     // 6 MHz
       // 6 MHz
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0);			// Chip-Select 0
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);	// Value of CS when active
}


// Close the SPI interface.
void end_spi()
{
  bcm2835_spi_end();
  bcm2835_close();
}




uint64_t cycles1=0;
uint64_t cycles2=0;
int write_toFiles(FILE* fp1,FILE* fp2,  void* virtual_address, int byte_count) 
{ 
    int offset;
    uint val1,val2;
    uint64_t val1_disp,val2_disp;
    uint val1_bit,val2_bit;
    uint val1_val,val2_val;
    uint val1_prev=0;
    uint val2_prev=0;


    char *p = virtual_address;
    int mod_num = 2; //number of channels
    int word_byte = 4; //bytes per word
    int skip_words =2; //skip just the first word

    int count1, count2;
    count1 = 0;
    count2 = 0;
    
    for (offset = 0; offset < byte_count; offset=offset+mod_num*word_byte){

        val1 = (uint)(0xffffffff&(p[0+offset]|p[1+offset]<<8|p[2+offset]<<16|p[3+offset]<<24));
        val2 = (uint)(0xffffffff&(p[0+offset+word_byte]|p[1+offset+word_byte]<<8|p[2+offset+word_byte]<<16|p[3+offset+word_byte]<<24));
        // printf("0x%02hX \t 0x%02hX \t 0x%02hX \t 0x%02hX \t $$$$$$$$$$ \t",(uint)(p[3+offset]),(uint)(p[2+offset]),(uint)(p[1+offset]),(uint)(p[0+offset]));
        // printf("0x%02hX \t 0x%02hX \t 0x%02hX \t 0x%02hX \n",(uint)(p[3+offset+word_byte]),(uint)(p[2+offset+word_byte]),(uint)(p[1+offset+word_byte]),(uint)(p[0+offset+word_byte]));

        // printf("%u \n", (uint)(val1 & 0x7fff));
        val1_val = (val1&0x7fffffff);
        val1_bit = (val1>>31 & 0x1);
        val2_val = (val2&0x7fffffff);
        val2_bit = (val2>>31 & 0x1);
        // printf("%10u,%10u \t",(val1>>31 & 0x1),(val1 & 0x7fffffff));
        // printf("%10u,%10u \n",(val2>>31 & 0x1),(val2 & 0x7fffffff));
        // printf("%10u,%10u \t", (val1>>31 & 0x1),(val1 & 0x7fffffff));


          if( (val1_val!=val1_prev) | (val1_val == 0) )
          {
              // printf("%u,%u \n ", (uint)(val1>>31 & 0x1),(uint)(val1 & 0x7fffffff));
              if(val1_val < val1_prev) cycles1= cycles1 + 1;
              // if(val1_prev - val1_val > (0x7fffffff>>1) ) cycles1= cycles1 + 1; // if previous value is greater by 1/2 of 0x7fffffff
              val1_disp =  (uint64_t)(val1_val) + (cycles1)*2147483648;
              fprintf(fp1,"%u,",(uint)(val1>>31 & 0x1));
              // fprintf(fp1,"%u\n",(uint)(val1 & 0x7fffffff));
              fprintf(fp1,"%"PRIu64" \n",val1_disp);
              count1=count1+1;
          }
          if( (val2_val!=val2_prev) | (val2_val == 0) )
          {
              // printf("%u,%u \n ", (uint)(val2>>31 & 0x1),(uint)(val2 & 0x7fffffff));
              // if(val2_prev - val2_val > (0x7fffffff>>1)) cycles2= cycles2 + 1; // if previous value is greater by 1/2 of 0x7fffffff
              val2_disp =  (uint64_t)val2_val + (cycles2)*2147483648;
              fprintf(fp2,"%u,",(uint)(val2>>31 & 0x1));
              fprintf(fp2,"%"PRIu64" \n",val2_disp);
              // fprintf(fp2,"%u\n",(uint)(val2 & 0x7fffffff));
              count2=count2+1;

          }
          
          val1_prev = val1_val;
          val2_prev = val2_val;

        }
        fprintf(fp1,"\n\n");
        fprintf(fp2,"\n\n");
        printf("Counts Recorded for DDMTD1: %u \n",count1);
        printf("Counts Recorded for DDMTD2: %u \n",count2);
        printf("Efficiency for DDMTD1: %f \% \n",(float)(count1)*100/offset);
        printf("Efficiency for DDMTD2: %f \% \n",(float)(count2)*100/offset);


        // printf("%"PRIu64"\n",cycles1);
        // printf("%"PRIu64"\n",cycles2);




    return 0;
}


int print_nWords(void* virtual_address, int byte_count, int mod_num)  
{
    // int mod_num = 8;
    int word_byte = 4;
    char *p = virtual_address;
    int offset;
    printf("\n");
    uint64_t val1;

    for (offset = 0; offset < byte_count; offset=offset+word_byte) {
        val1 = (uint64_t)(0xffffffff&((p[0+offset]&0b01111111)<<24|p[1+offset]<<16|p[2+offset]<<8|p[3+offset]));
        
        if(offset % (4*mod_num) == 0 & (offset != 0) ) {/*if(val1!=0x7fffffff)*/  printf("\n",offset);} //

        // if(1)
        // if(val1!=0x7fffffff)
        {
        printf("%1u--",(int)(p[0+offset]>>7& 0x1));  
        printf("%012" PRIu64,val1);
        // printf("%x",(int)val1);

        // printf("%02x%02x%02x%02x",p[offset+3],p[offset+2], p[offset+1],p[offset]);

        printf(" ");

        }
        // printf("%x" PRIu64,p[3+offset]<<24|p[2+offset]<<16|p[1+offset]<<8|p[0+offset]);

    }
    printf("\n");
    return 0;
}
