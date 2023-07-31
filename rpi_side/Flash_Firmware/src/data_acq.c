// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include "spi_common.h"
#include "NexysDDMTD.h"



const int64_t MAX_CNT   = 4094967296;
int skipFirst3 = 0;


int memDump_DDMTD(int addr_mem,int num_words,char filename[100], int mem_no );



int main(int argc, char** argv)
{
  // Startup the SPI interface on the Pi.
  init_spi();
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64); 
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0);

  //Switch Off Heating...
  heating_status(0); //0--> both off; 1--> heat ddmtd1; 2--> head ddmtd2; 

  int N;
  if(argc == 2)
    N= atoi(argv[1]); 
  else
    N=1;


  char filename1[100] = "./data/ddmtd1.txt";
  char filename2[100] = "./data/ddmtd2.txt";

  remove(filename1);
  remove(filename2);

  FILE *fp1 = fopen(filename1,"w");
  FILE *fp2 = fopen(filename2,"w");

  int mem_full=0; 
  int num_of_words = 2*25000; 
  int addr_mem     = ADDR_MEM1;

  int num_Bytes = 4*num_of_words+2; // Cause each word is 32 bits so 4 bytes per word and +2 because the first two bytes are for sending command
  char* data_buf = malloc(num_Bytes);
  char*  cmd_buf = malloc(num_Bytes);
  char* total_data_buf =  malloc(N*num_Bytes);


  printf("Data_Allocated: 2*%f MB \n",((float)(num_Bytes)/1000000));

  memset(data_buf, 0xff,num_Bytes );
  memset(cmd_buf, 0xff, num_Bytes );
// print_nWords(cmd_buf,num_Bytes,2) ; //Test to see if the memory buffer has been initialized.

  cmd_buf[0] = ADDR_MEM1 & 0xFF;
  cmd_buf[1] = 0;

  int N_count =0;
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
  // usleep(1000000);


  int numBytesRead =0; //Number of bytes read
  int i = 0;
  // //Debug Tools...
  readCounter();
  readFIFO_readCount();
  readFIFO_writeCount();
  // // END Debug Tools...

  
  //Clear out the FIFO
  bcm2835_spi_transfernb(cmd_buf, data_buf, num_Bytes); 
  bcm2835_spi_transfernb(cmd_buf, data_buf, num_Bytes); 
  memset(data_buf, 0xff,num_Bytes );


  startAcq();
  // usleep(1000000);
  // stopAcq();   
  
  
  // readCounter();
  // readFIFO_readCount();
  // readFIFO_writeCount();

  //continuous acquisition
  // while(1){ // waiting for memoryFull with SPI command is too slow....
  //     mem_full = send3Byte_NexysDDMTD(MEM_FULL,0x0); // 3::both, 2::Mem1, 1::Mem2 , 0 None
  //     if(mem_full>0) break;
  // }
  // int offset = 0 ;//64*100; // 100 words are removed...  
  // bcm2835_spi_transfernb(cmd_buf, data_buf, num_Bytes+2); // +2 because the first two bytes are empty
  // memcpy(total_data_buf+numBytesRead,data_buf+2+offset,num_Bytes-offset);
  // numBytesRead = numBytesRead + num_Bytes-2;
  // memset(data_buf, 0xff,num_Bytes ); //cleaning data 
  // END continuous acquisition
  // readFIFO_readCount();
  // readFIFO_writeCount();

  // usleep(10000000);

  // Offset parameter
  uint num_of_words_toRemove = 1; // 1word from both ddmtd1 & ddmtd2
  uint offset_bytes = num_of_words_toRemove*2*4 + 2; //2 since ddmtd1 & ddmtd2; 4 is the number of bytes per word; +2 for the ignoring the returned command.

  while(i < 100000000)
  {
      if (N_count>=N) break;
      mem_full = send3Byte_NexysDDMTD(MEM_FULL,0x0); // 3::both, 2::Mem1, 1::Mem2 , 0 None
      if(mem_full>0)
      {
          N_count = N_count + 1;
          bcm2835_spi_transfernb(cmd_buf, data_buf, num_Bytes);
          
            memcpy(total_data_buf+numBytesRead,data_buf+offset_bytes,num_Bytes-offset_bytes);
            numBytesRead = numBytesRead + num_Bytes - offset_bytes;
            // write_toFiles(fp1,fp2,data_buf+2, num_Bytes -2);
            // printf("$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n");
            memset(data_buf, 0xff,num_Bytes ); //cleaning data
      }
      // usleep(100);
      i=i+1;
  }
  stopAcq();   

  
  
  write_toFiles(fp1,fp2,total_data_buf, numBytesRead);

  fclose(fp1);
  fclose(fp2);

  free(data_buf);
  free(cmd_buf);
  free(total_data_buf);




  end_spi();
  return 0;
}




//Legacy Code for reference
// if (i==0){}
// else{
//   memcpy(total_data_buf+numBytesRead,data_buf+2,num_Bytes-2); //+2 
//   numBytesRead = numBytesRead + num_Bytes  -2; // 2 is to offset by the command bits...
//   write_toFiles(fp1,fp2,data_buf+2, num_Bytes -2); // remove two words as it will be repetition...
//   printf("$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n");
//   memset(data_buf, 0xff,num_Bytes );
// }