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

// Global Variables...
const int RST_DDMTD = 0x102;
const int ADDR_MEM1 = 0x106;
const int ADDR_MEM2 = 0x107;
const int MEM_FULL  = 0x108;
const int64_t MAX_CNT   = 4094967296;
int skipFirst3 = 0;

void resetDDMTD();

int memDump_DDMTD(int addr_mem,int num_words,char filename[100], int mem_no );
void mydelay (unsigned int num);

void mydelay (unsigned int num) {
clock_t goal = num+ clock();  //convert msecs to clock count  
while ( goal > clock() );               // Loop until it arrives.
}




int main(int argc, char** argv)
{
  // Startup the SPI interface on the Pi.
  init_spi();
  
  int N;
  if(argc == 2)
    N= atoi(argv[1]); 
  else
    N=1;
  remove("./ddmtd_mem_dump1.txt");
  remove("./ddmtd_mem_dump2.txt");




 int num_words = 60000; // Wont work for 10,000
//  int num_words = 96000; // Works for both 10,000 and 100,000
 int mem_full=0; //both mem full at 3(11);2(10) Mem1(1) full Mem2(0) not and so on;     

 resetDDMTD();
int N1=0,N2=0;
int max_count1,max_count2;

      while(1)
      {
          mem_full = 0;

          if ((N1 >= N) &&(N2 >= N))
          break;

          mem_full = spi_NexyDDMTD_io(MEM_FULL,0xFFFF); // 3::both, 2::Mem1, 1::Mem2 , 0 None

          
          switch (mem_full)
          {
                      case 3:
                           skipFirst3 = (N1==0)? 0:1;
                           memDump_DDMTD(ADDR_MEM1,num_words,"./ddmtd_mem_dump1.txt",0);
                           skipFirst3 = (N2==0)? 0:1;
                           memDump_DDMTD(ADDR_MEM2,num_words,"./ddmtd_mem_dump2.txt",1);
                           N1 = N1 +1;
                           N2 = N2 +1;
                          break;

                      case 1:
                          skipFirst3 = (N2==0)? 0:1;
                          memDump_DDMTD(ADDR_MEM2,num_words,"./ddmtd_mem_dump2.txt",1);
                          N2 = N2 +1;
                          break;
                      case 2:
                          skipFirst3 = (N1==0)? 0:1;
                          memDump_DDMTD(ADDR_MEM1,num_words,"./ddmtd_mem_dump1.txt",0);
                           N1 = N1 +1;
                          break;
                      
                      default:
                          break;
            }

          if (max_count1==1 || max_count2 == 1)
          {
            printf("Max count reached; terminating \n");
            break;
          }
          


          mydelay(100);// do not play with this... Critical delay!!!


      }
        
      
      // mydelay(1000000);// will fail without this

      // memDump_DDMTD(ADDR_MEM1,32000,"./ddmtd_mem_dump.txt");



    end_spi();


  return(0);

}// Main ends here



uint64_t value[2]={0,0};
uint64_t val1[2]={0,0};
uint64_t val2[2]={0,0};



int memDump_DDMTD(int addr_mem,int num_words,char filename[100], int mem_no )
{



  // const int num_Bytes = (num_words+500+2)*4; // 500 so that the last of the FIFOs is cleaned out
  const int num_Bytes = (num_words+2)*4; // 500 so that the last of the FIFOs is cleaned out
  char cmd1[num_Bytes],cmd2[num_Bytes], data1[num_Bytes],data2[num_Bytes];

  // char is 8 bits
  // int used as 32bits


  // Create the 32-bit command word.
  cmd1[0] = (addr_mem >> 8)&(0xFF);
  cmd1[1] = (addr_mem)&(0xFF);


  // cmd2[0] = (addr_mem2 >> 8)&(0xFF);
  // cmd2[1] = (addr_mem2)&(0xFF);



  bcm2835_spi_transfernb(cmd1, data1, num_Bytes);
  // usleep(100);
  // bcm2835_spi_transfernb(cmd2, data2, num_Bytes);

  // Send the command.



  FILE * fp;
  fp = fopen (filename,"a");
  // uint64_t val1=0,val2[mem_no]=0;
  
  int ign_first = 0;

  for (int i=0; i< num_Bytes; i=i+4)
  {
    // print_bits(32,data1[0+i]<<24|data1[1+i]<<16|data1[2+i]<<8|data1[3+i]);
    // print_bits(32,data2[0+i]<<24|data2[1+i]<<16|data2[2+i]<<8|data2[3+i]);
    // if (1) //first 4 is rubbish
    
    // if ((i >  4*4 )&&(i <  (num_Words+4)*4 )) //first 4 is rubbish
    if(i>4*10) skipFirst3 = 1;


    if (i>4) //Test
    {

      val1[mem_no] = (uint)(data1[0+i]<<24|data1[1+i]<<16|data1[2+i]<<8|data1[3+i]);
      if ((val1[mem_no] < val2[mem_no] )) 
      {
          if(skipFirst3 == 1)
          {
            value[mem_no] = value[mem_no] + 4294967296; 
          }
      }


      // fprintf(fp,"%" PRIu64 ", %" PRIu64 "\n",(val1[mem_no]+value[mem_no]),value[mem_no]);
      if(val1[mem_no] != val2[mem_no])
      fprintf(fp,"%" PRIu64 "\n",(val1[mem_no]+value[mem_no]));

     val2[mem_no] = val1[mem_no];
    }




    // print_bits(16,data2[0+i]<<8|data2[1+i]);
    // fprintf(stderr,"value = %06d,%06d\n",(int)(data1[0+i]<<8|data1[1+i]),(int)(data2[0+i]<<8|data2[1+i]));
    // fprintf(stderr,"value = %06d,%06d\n",(int)(data1[0+i]<<8|data1[1+i]),(int)(data2[0+i]<<8|data2[1+i]));


    // writing to file....
    // fprintf(fp,"%06d,%06d,\n",(int)(data1[0+i]<<8|data1[1+i]),(int)(data2[0+i]<<8|data2[1+i]));

  }
  // fprintf(stderr,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n");
  fprintf(fp,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n");
  fclose (fp);


}


void resetDDMTD()
{
  // init_spi();
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0); // Changing to
  spi_NexyDDMTD_io(RST_DDMTD,0x1);  //
  // end_spi();
}

