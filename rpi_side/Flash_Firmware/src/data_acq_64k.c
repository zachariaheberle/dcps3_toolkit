// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include "spi_common.h"
#include "NexysDDMTD.h"



const int RST_DDMTD = 0x102;
const int ADDR_MEM1 = 0x106;
const int ADDR_MEM2 = 0x107;
const int MEM_FULL  = 0x108;
const int MEM_AFULL = 0x109;

const int64_t MAX_CNT   = 4094967296;
int skipFirst3 = 0;



int memDump_DDMTD(int addr_mem,int num_words,char filename[100], int mem_no );


void resetDDMTD()
{
  // init_spi();
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Changing to
  spi_NexyDDMTD_io(RST_DDMTD,0x1);  //
  // end_spi();
}



int main(int argc, char** argv)
{
  // Startup the SPI interface on the Pi.
  init_spi();
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64); 
  
  int N;
  if(argc == 2)
    N= atoi(argv[1]); 
  else
    N=1;



char filename1[100] = "./ddmtd1.txt";
char filename2[100] = "./ddmtd2.txt";

remove(filename1);
remove(filename2);

FILE *fp1 = fopen(filename1,"a");
FILE *fp2 = fopen(filename2,"a");

 


 

int mem_full=0; 
int num_of_words = 2*64000; 
int addr_mem     = 0x106;
int num_Bytes = 4*num_of_words; // Cause each word is 32 bits so 4 bytes per word
char* data_buf = malloc(num_Bytes);
char*  cmd_buf = malloc(num_Bytes);


char* total_data_buf =  malloc(N*num_Bytes);



memset(data_buf, 0xff,num_Bytes );
memset(cmd_buf, 0xff, num_Bytes );
// print_nWords(cmd_buf,num_Bytes,2) ; //Test to see if the memory buffer has been initialized.

cmd_buf[0] = (addr_mem >> 8)&(0xFF);
cmd_buf[1] = (addr_mem)&(0xFF);

int N_count =0;
int numBytesRead =0; //Number of bytes read
while(1)
{
    if (N_count>=N) break;
    resetDDMTD();
    for (int i=0; i< 1;)
    {
        mem_full = spi_NexyDDMTD_io(MEM_AFULL,0xFFFF); // 3::both, 2::Mem1, 1::Mem2 , 0 None
        if(mem_full==3)
        {

            N_count = N_count + 1;
            bcm2835_spi_transfernb(cmd_buf, data_buf, num_Bytes);
            memcpy(total_data_buf+numBytesRead,data_buf+2*4,num_Bytes-2*4);
            numBytesRead = numBytesRead + num_Bytes-2*4;
            memset(data_buf, 0xff,num_Bytes ); //cleaning data
            i=1;
        }
        usleep(100);
    }
}

write_toFiles(fp1,fp2,total_data_buf+2*4, numBytesRead-2*4);



fclose(fp1);
fclose(fp2);

free(data_buf);
free(cmd_buf);
free(total_data_buf);




end_spi();
return 0;
}




