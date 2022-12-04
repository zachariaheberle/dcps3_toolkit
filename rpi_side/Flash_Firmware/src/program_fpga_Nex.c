//
//	Program FPGA
//
// # Written by Rohith Saradhy
// # Email -> rohithsaradhy@gmail.com
#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#define BYTES_PER_PAGE 256 // For Nexys Video
#define MAX_BYTES 32000000
#define MAX_TRIALS 3  //Changed from 5 to 2

#define CHIP_ID 0x10219 // CHIP ID for Nexys Video

void die(const char *s);
void init_spi();
void end_spi();


int main(int argc, char *argv[]) {

    printf("\n\tFLASH MEMORY WRITE\n\n");

    // Setting up SPI
    init_spi();

    // Reading chip ID so we know everything is working OK
    bcm2835_spi_chipSelect(BCM2835_SPI_CS1);		// CS1 is the Memory Flash...


    char RDID[] = {0x9F, 0x0, 0x0, 0x0};			// RDID command w/ 3 zero bytes
    char chip_id_data[sizeof(RDID)];
    bcm2835_spi_transfernb(RDID, chip_id_data, sizeof(RDID));// Send RDID and read back into chip_id_data
    unsigned int chipID = (chip_id_data[1]<<16) + (chip_id_data[2]<<8) + chip_id_data[3];// Chip ID in decimal form
    // printf("Current Chip ID: %06x, we expect the Chip ID:  %06x \n", chipID, CHIP_ID);
    if(chipID != CHIP_ID) die("The current chip ID is incorrect!");
    printf("Current Chip ID: %06x\n\n", chipID);



    // Allocate the storage for the hex file.
    char *hex_data = malloc(sizeof(char) * MAX_BYTES); // Using malloc because gcc doesn't like big arrays
    if (hex_data == NULL) die("malloc failed");	// Using malloc because gcc doesn't like big arrays


    // Time to write to the FPGA
    // Reading file from stdin
    printf("Reading hex file:");
    fflush(stdout);
    unsigned int val, num_bytes;
    for(num_bytes=0; num_bytes<MAX_BYTES; num_bytes++) {	// Read max number of bytes from file
        if(scanf("%2x", &val) < 1) break;		// Each byte occupies two hex characters
        hex_data[num_bytes] = val;
    }

    // Die if we reached MAX_BYTES.
    if(num_bytes >= MAX_BYTES) die("num_bytes >= MAX_BYTES");
    unsigned int num_sectors = (num_bytes >> 16) + 1; 	// Add 1 because the last sector is often only partially filled

    printf("\t Success\n");

    printf("Number of Bytes: \t %i\n",num_bytes );



    // Erasing sectors
    printf("Erasing sectors:");
    fflush(stdout);
    char WEL[] = {0x06}; // Write Enable Latch
    char STATUS[] = {0x05, 0};
    char READ_STATUS[sizeof(STATUS)];

    int trial=1;
    int failed;								// Flip this if we can't verify...

    //Address related variables...
    unsigned int addr =0;
    char byte1,byte2,byte3,byte4;


    while(1) {
        //Sector ERASE for 64kB
        for(addr=0; addr < num_bytes; addr+= 64*1024) //64 kilobytes per sector...
        {
            bcm2835_spi_writenb(WEL, sizeof(WEL));		// Set Write Enable latch
            byte1 = addr & 0xFF;
            byte2 = addr >> 8 & 0xFF;
            byte3 = addr >> 16 & 0xFF;
            byte4 = addr >> 24 & 0xFF;
            char ERASE[] = {0xDC, byte4, byte3, byte2, byte1};	// Erase command followed by any address within that sector
            bcm2835_spi_writenb(ERASE, sizeof(ERASE));	// Erase the sector
            while(1)
            {   // Wait until erase complete
                bcm2835_spi_transfernb(STATUS, READ_STATUS, sizeof(STATUS));
                if(!(READ_STATUS[1] % 2)) break;	// Write in progress is last bit of status
            }
        }




        // Verifying sectors are erased
        failed=0;								// Flip this if we can't verify...
        for(addr=0; addr<num_bytes; addr+=BYTES_PER_PAGE)
        {
            byte1 = addr & 0xFF;
            byte2 = addr >> 8 & 0xFF;
            byte3 = addr >> 16 & 0xFF;
            byte4 = addr >> 24 & 0xFF;

            char READ[5 + BYTES_PER_PAGE] = {0x13,byte4,byte3,byte2,byte1};// 0x13 is read command
            char DataRead[sizeof(READ)];
            bcm2835_spi_transfernb(READ, DataRead, sizeof(READ));		// Read one page

            for(int byte = 0; byte < BYTES_PER_PAGE; byte++ )
            {
                if(DataRead[5+byte] != 0xFF)
                {
                    // printf("Failed at %i, with value %x\n",byte+addr,DataRead[byte + 5]);
                    failed = 1;
                }
            }

        }
        if(!failed) break;
        else
        {
            if(trial >= MAX_TRIALS) die("Erasing Flash Failed :(");
            trial++;
            printf("\n Erase trial %i failed, trying again...",trial-1);
            fflush(stdout);
        }
    }
    printf(" \t Success \n");



    // Writing the config data to the flash memory
    printf("Flashing memory:");
    fflush(stdout);
    unsigned int byte;
    trial=1;
    while(1) {
        // Writing the config data to the flash memory

        for(addr=0; addr<num_bytes; addr+=BYTES_PER_PAGE)
        {
            bcm2835_spi_writenb(WEL, sizeof(WEL));					// Set write enable
            byte1 = addr & 0xFF;
            byte2 = addr >> 8 & 0xFF;
            byte3 = addr >> 16 & 0xFF;
            byte4 = addr >> 24 & 0xFF;
            char WRITE[5 + BYTES_PER_PAGE] = {0x12,byte4,byte3,byte2,byte1};		// 0x02 is write command followed by 3 byte start address
            char toWrite[BYTES_PER_PAGE];
            for(byte = 0; byte <BYTES_PER_PAGE ; byte ++ )
                toWrite[byte] = hex_data[addr+byte];

            memcpy(&WRITE[5], toWrite, BYTES_PER_PAGE);
            bcm2835_spi_writenb(WRITE, sizeof(WRITE));				// Write to the page

            while(1)
            {   // Wait til write is done
                bcm2835_spi_transfernb(STATUS, READ_STATUS, sizeof(STATUS));
                if(!(READ_STATUS[1] % 2)) break;
            }

        }

        // Verifying that we read everthing correctly...
        failed=0;								// Flip this if we can't verify...
        for(addr=0; addr<num_bytes; addr+=BYTES_PER_PAGE)
        {
            byte1 = addr & 0xFF;
            byte2 = addr >> 8 & 0xFF;
            byte3 = addr >> 16 & 0xFF;
            byte4 = addr >> 24 & 0xFF;
            char READ[5 + BYTES_PER_PAGE] = {0x13,byte4,byte3,byte2,byte1};
            char DataRead[sizeof(READ)];
            bcm2835_spi_transfernb(READ, DataRead, sizeof(READ));		// Read one page

            for(byte = 0; byte < BYTES_PER_PAGE; byte++ )
            {
                if(DataRead[5+byte] != hex_data[addr + byte])
                {
                    // printf("Failed at HR:%x, R:%x \n",hex_data[addr+byte],DataRead[byte + 5]);
                    failed = 1;
                }

            }

        }


        if(!failed) break;
        else
        {
            if(trial >= MAX_TRIALS) die("Writing to memory failed :(");
            trial++;
            printf("\n Trial %i failed, trying again...",trial-1);
            fflush(stdout);

        }


    }
    printf(" \t Success \n\n");

    // Done with the write
    printf("The flash memory was successfully written.\n");
    free(hex_data);	// Again free what we got from malloc

    // Closing Connection
    end_spi();
    return 0;
}



void die(const char *s)
{
    printf("\n");
    printf(s);
    printf("\n");
    end_spi();
    exit(1);
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
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);
    //bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_256);	// 1.5625 MHz
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64);     // 6 MHz
    bcm2835_spi_chipSelect(BCM2835_SPI_CS0);			// Chip-Select 0
    bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);	// Value of CS when active
}


// Close the SPI interface.
void end_spi()
{
    bcm2835_spi_end();
    bcm2835_close();
}
