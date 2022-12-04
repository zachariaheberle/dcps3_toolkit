`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/14/2020 04:12:03 AM
// Design Name: 
// Module Name: main_v2
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module main_v2(
    input clk,
    output[0:7] led,
    output [0:3] led_fmc,
    output[0:1] set_vadj,
    output vadj_en,
    input spi_mosi,
    spi_sck,
    spi_cs0,
    spi_cs1,
    output spi_miso,
    output FCS_B,         // FLASH CS
    output DQ0,           // FPGA2MEM
    input DQ1,            // MEM2FPGA
    output jb1,
    input PLL_MISO,
    output PLL_MOSI,
    PLL_SS,
    PLL_SCK,              // PLL Controls
    output PLL_EQ_OK,
    PLL_RESET_B,
    PLL_SEL0,
    PLL_SEL1,             // PLL Controls
    input CLK_P,
    CLK_N,
    CLK_A_P,
    CLK_A_N,
    CLK_B_P,
    CLK_B_N,
    Q1A_P,
    Q1A_N,
    Q2A_P,
    Q2A_N,
    Q1B_P,
    Q1B_N,
    Q2B_P,
    Q2B_N,
    input CLK_200_P,CLK_200_N,
    output HEAT_1,HEAT_2
    );

//----------------------------------------------------------------------
// PERIPHERAL ADDRESS SPACE
//----------------------------------------------------------------------    
    parameter FIRMWARE_VERSION = 16'd2034;
    parameter FIRMWARE_VERSION_MAJOR = FIRMWARE_VERSION[15:8];
    parameter FIRMWARE_VERSION_MINOR = FIRMWARE_VERSION[ 7:0];

    parameter FIRMWARE_ADDR_MAJOR = 1;
    parameter FIRMWARE_ADDR_MINOR = 2;
    parameter DDMTD_PLL_EN_ADDR   = 3;
    parameter m_reset_LOC         = 4;
    parameter REC_DATA            = 5;
    parameter MEM1_LOC            = 6;
    parameter MEM2_LOC            = 7;
    parameter MEM_FULL            = 8;
    parameter MEM_AFULL           = 9;
    parameter START_ACQ           = 10;
    parameter TEST_REG            = 11;
    parameter RESET_DONE          = 12; // Not working at the moment be SPI doesn't work during reset
    parameter READ_COUNTER        = 13; 
    parameter WRITE_COUNT_FIFO    = 14; 
    parameter READ_COUNT_FIFO     = 15;
    parameter HEAT_REGISTERS      = 16; 
    parameter END_TRANSACTION     = 17'hED;

//----------------------------------------------------------------------
// HEATING ELEMENT
//----------------------------------------------------------------------    
    reg heat1_reg=0;
    reg heat2_reg=0;

    assign HEAT_1 = heat1_reg;
    assign HEAT_2 = heat2_reg;

//----------------------------------------------------------------------
// Clocking Inputs
//----------------------------------------------------------------------    
        
    wire Q1A_temp,Q2A_temp,Q1B_temp,Q2B_temp;
    wire Q1A,Q2A,Q1B,Q2B;
    wire Q1An,Q2An,Q1Bn,Q2Bn;
    wire clk_ref;
    wire clk_ref_temp;

    IBUFGDS IBUFGDS_clkpll(.O(clk_ref),.I(CLK_P),.IB(CLK_N));
    IBUFGDS IBUFGDS_clk200(.O(clk_200),.I(CLK_200_P),.IB(CLK_200_N));
    BUF beatBuf1 (.I(clk_ref),.O(clk_ref_temp));
    assign clk_refn = ~clk_ref_temp;

    IBUFGDS IBUFGDS_Q1A (.O(Q1A_temp), .I(Q1A_P), .IB(Q1A_N)); //good
    IBUFGDS IBUFGDS_Q2A (.O(Q2A_temp), .I(Q2A_P), .IB(Q2A_N)); 
    IBUFGDS IBUFGDS_Q1B (.O(Q1B_temp), .I(Q1B_P), .IB(Q1B_N));//good
    IBUFGDS IBUFGDS_Q2B (.O(Q2B_temp), .I(Q2B_P), .IB(Q2B_N));

    // sync_ddr sync_Q1A(.clk(clk_ref),.D(Q1A_temp),.Q(Q1A),.Q2(Q1An));
    // sync_ddr sync_Q2A(.clk(clk_ref),.D(Q2A_temp),.Q(Q2A),.Q2(Q2An));
    // sync_ddr sync_Q1B(.clk(clk_ref),.D(Q1B_temp),.Q(Q1B),.Q2(Q1Bn));
    // sync_ddr sync_Q2B(.clk(clk_ref),.D(Q2B_temp),.Q(Q2B),.Q2(Q2Bn));


    //Connections to the sampling logic: reference --> (* ASYNC_REG = "TRUE" *) 
    wire   sampling_logic_clock;
    wire   ddmtd1_beat_clock;
    wire   ddmtd2_beat_clock;

    assign sampling_logic_clock = clk_ref; // Clock that is used to sample...
    assign ddmtd1_beat_clock    = Q1A_temp;
    assign ddmtd2_beat_clock    = Q1B_temp;
    // assign sampling_logic_clock = clk_200; // Clock that is used to sample...
    // assign ddmtd1_beat_clock    = beat_0_q1; //Fake Clock
    // assign ddmtd2_beat_clock    = beat_1_q1; //Fake Clock




// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// RESET LOGIC 
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
    wire [31:0] reset_count;
    reg reset_count_rst;
    reg m_reset              = 1'b1;
    reg mem_reset            = 1'b1;
    reg trim_reset           = 1'b0; // restart the counter

    COUNTER_TC_MACRO#(
        .COUNT_BY(48'h000000000001),//Countbyvalue
        .DEVICE("7SERIES"),//TargetDevice:"7SERIES"
        .DIRECTION("UP"),//Counterdirection,"UP"or"DOWN"
        .RESET_UPON_TC("FALSE"),//Reset counter upon terminal count,"TRUE"or"FALSE"
        .TC_VALUE(32'h000000000000),//Terminalcount value
        .WIDTH_DATA(32)//Counteroutputbuswidth,1-48
      ) reset_counter(
             .Q(reset_count),//Counteroutputbus,widthdeterminedbyWIDTH_DATAparameter
//             .TC(TC),//1-bitterminalcountoutput,high=terminalcountisreached
             .CLK(clk),//1-bitpositiveedgeclockinput
             .CE(1'b1),//1-bit active high clock enable input
             .RST(reset_count_rst)//1-bitactivehighsynchronousreset
        );
    reg enable_sampling_logic = 0 ;
    always @(negedge clk)
    begin
        reset_count_rst <=    1'b0;
        if (mem_reset)
        begin
            if (reset_count >= 32'd100000) 
                mem_reset <= 1'b0; 
        end
        else if(m_reset)
        begin
            if (reset_count >= 32'd200000000) 
            begin
                m_reset <= 1'b0;
            end     
        end
        else if(trim_reset)
        begin
            reset_count_rst <=    1'b1;
            m_reset       <=    1'b1;
            mem_reset     <=    1'b1;
            enable_sampling_logic <= 1'b0 ;
        end
        else
        begin
            if (reset_count >= 32'd400000000) 
                enable_sampling_logic <= 1'b1 ;
        end    
   
    end  



// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// Tri-state the SPI output.
// The SPI interfaces will fail without this.
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
   
    wire spi_miso0,spi_miso1,spi_miso2;//spi_miso0->FPGA,spi_miso1-> MEM ; spi_miso2 -> PLL
    wire tmp_miso, enable_miso;
    wire pll_cs; // active low for PLL; active high for MEM
    reg PLL_SPI        = 1'b0;
    assign pll_cs      = ~PLL_SPI;
    assign tmp_miso    = ((~spi_cs0) & spi_miso0) | (~spi_cs1)&(((pll_cs) & spi_miso1) |  ((~pll_cs) & spi_miso2))  ;
    assign enable_miso = ~((~spi_cs0) | (~spi_cs1));
    OBUFT OBUFT_i (.O(spi_miso), .I(tmp_miso), .T(enable_miso));
       
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// Reprogram the PLL via SPI interface using CS1 and PLL_SPI register
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 

    wire rx_byte_done;
    reg tx_byte_done=0;
    reg prev_rx_byte_done;
    wire [7:0] rx_byte;
    wire [7:0] tx_byte;
    wire spi_clk;
    reg spi_reset = 1;
    BUFG buf_spi_clk (.I(spi_sck),.O(spi_clk));
    wire spi_clk_synced; 
    wire spi_cs0_synced;
    //Syncing spi_clk & cs to clk




    
    SPI_slave spiInterface_i(
        .i_Rst_L(spi_reset),        // FPGA Reset, active low
        .i_Clk(clk),                // FPGA Clock
        .o_RX_DV(rx_byte_done),     // Data Valid pulse (1 clock cycle)
        .o_RX_Byte(rx_byte),        // Byte received on MOSI
        .i_TX_DV(tx_byte_done),     // Data Valid pulse to register i_TX_Byte
        .i_TX_Byte(tx_byte),        // Byte to serialize to MISO.
        .i_SPI_Clk(spi_clk),
        .o_SPI_MISO(spi_miso0),
        .i_SPI_MOSI(spi_mosi),
        .i_SPI_CS_n(spi_cs0)  
    );

    // Getting the address and subsequent data
    integer data_counter = 0;
    reg [7:0] addr_byte  = 0;
    reg [7:0] data_byte  = 0;
    reg mem1_active,mem2_active,mem_full,mem_afull,firmware_addr_major,firmware_addr_minor;
    reg start_acq = 1'b0;


    // Transmission part
    reg [2:0] idx = 0;
    reg [7:0] TDATA=0;
    reg [7:0] read_counter=0;
    wire [31:0] tdata1;
    wire [31:0] tdata2;
    reg read_en = 0;
    reg test_reg = 0;
    reg all_set_to_decode = 0;


    //FIFO filling status...
    wire full_1,prog_full_1;
    wire full_2,prog_full_2;

    wire [7:0] read_count_fifo1;
    wire [7:0] write_count_fifo1;
    always@(negedge clk)
    begin

        if (spi_cs0)
        begin
            //once transaction is done, we reset everything
            firmware_addr_major     <= 0;
            firmware_addr_minor     <= 0;
            mem1_active             <= 0;
            mem2_active             <= 0;
            mem_full                <= 0;
            mem_afull               <= 0;
            data_counter            <= 0;
            trim_reset              <= 0;
            idx                     <= 0;
            all_set_to_decode       <= 0;
            TDATA                   <= 0;
            tx_byte_done            <= 0;
            spi_reset               <= 0; //resets the SPI every time the cs goes low...
        end
        else if(m_reset) //Resetting all the registers
        begin
            mem1_active         <= 1'b0;
            firmware_addr_major <= 1'b0;
            firmware_addr_minor <= 1'b0;
            mem2_active         <= 1'b0;
            mem_full            <= 1'b0;
            mem_afull           <= 1'b0;
            start_acq           <= 1'b0;
            read_en             <= 1'b0;
            prev_rx_byte_done   <= 1'b0;
            data_counter        <= 1'b0;
            all_set_to_decode   <= 1'b0;
            TDATA               <= 8'b0;
            tx_byte_done        <= 1'b0;
            spi_reset           <= 1'b0;
            test_reg            <= 1'b0;
            trim_reset          <= 1'b0;
            read_counter        <= 1'b0;
        end
        else 
        begin
            spi_reset           <= 1'b1;
             //Receiving Part...
            if ((rx_byte_done)) // set the addr_byte & data_byte
            begin
                if (data_counter == 0) //set the address
                    addr_byte <= rx_byte;
                if (data_counter == 1) //set the first data_byte
                begin
                    data_byte           <= rx_byte;
                    all_set_to_decode   <= 1;
                end
                data_counter        <= data_counter + 1;
            end //rest of the receive decoding happens at pos edge of clock


            if (all_set_to_decode == 1)
            begin 
                //Case statements to switch between registers
                case (addr_byte)
                        DDMTD_PLL_EN_ADDR       : PLL_SPI                   <= data_byte[0]; // Sets the location to flash stuff to; default is to flash the memory with 0
                        m_reset_LOC             : trim_reset                <= 1'b1; // triggers the reset action for 1000 cycles
                        MEM1_LOC                : mem1_active               <= 1'b1;
                        MEM2_LOC                : mem2_active               <= 1'b1;
                        MEM_FULL                : mem_full                  <= 1'b1;
                        MEM_AFULL               : mem_afull                 <= 1'b1;
                        FIRMWARE_ADDR_MAJOR     : firmware_addr_major       <= 1'b1;
                        FIRMWARE_ADDR_MINOR     : firmware_addr_minor       <= 1'b1;
                        START_ACQ               : start_acq                 <= data_byte[0];
                        TEST_REG                : test_reg                  <= data_byte[0];
                        HEAT_REGISTERS:
                        begin
                            heat1_reg <= data_byte[0];
                            heat2_reg <= data_byte[1];
                        end
                        default:
                        begin
                            firmware_addr_major     <= 1'b0;
                            firmware_addr_minor     <= 1'b0;
                            mem1_active             <= 1'b0;
                            mem2_active             <= 1'b0;
                            mem_full                <= 1'b0;
                            mem_afull               <= 1'b0;
                        end
                endcase
                all_set_to_decode <=0;
            end

            prev_rx_byte_done <= rx_byte_done;


            //Transmission Part
            
            if ((data_counter>=1) && (rx_byte_done))
            begin
                case (addr_byte)
                    MEM1_LOC:
                        begin
                            case(idx)
                                3'b000:TDATA <= tdata1[7:0]; 
                                3'b001:TDATA <= tdata1[15:8];
                                3'b010:TDATA <= tdata1[23:16]; 
                                3'b011:TDATA <= tdata1[31:24];
                                3'b100:TDATA <= tdata2[7:0]; 
                                3'b101:TDATA <= tdata2[15:8];
                                3'b110:TDATA <= tdata2[23:16]; 
                                3'b111:TDATA <= tdata2[31:24];
                            endcase
                            if ((idx == 03'b111) && (data_counter>1)) //read stuff when 8 bytes are done...
                            begin
                                read_en <= 1;
                                read_counter <= read_counter + 1; // for debugging how many words are read...
                            end

                                
                            idx <= idx +1;
                        end
                    FIRMWARE_ADDR_MAJOR: TDATA<=FIRMWARE_VERSION_MAJOR;
                    FIRMWARE_ADDR_MINOR: TDATA<=FIRMWARE_VERSION_MINOR;
                    MEM_FULL           : TDATA<={6'b0,full_1,full_2};
                    MEM_AFULL          : TDATA<={6'b0,prog_full_1,prog_full_2};
                    RESET_DONE         : TDATA<={7'b0,~m_reset};
                    READ_COUNTER       : TDATA<= read_counter;
                    WRITE_COUNT_FIFO   : TDATA<= write_count_fifo1;
                    READ_COUNT_FIFO    : TDATA<= read_count_fifo1;
                    HEAT_REGISTERS     : TDATA<= {6'b0,heat2_reg,heat1_reg};

                    
                    default            : TDATA <= addr_byte; // send addr_byte...
                endcase
                tx_byte_done <= 1;
            end
            else
            begin
                tx_byte_done <= 0;
                read_en <= 0;
                TDATA <= 0;
            end       
        end
    end



    assign tx_byte =   TDATA;
    //Legacy Logic
    // assign tx_byte =    (mem1_active)?TDATA:
    //                 (mem_full)?{6'b0,full_1,full_2}:
    //                 (mem_afull)?{6'b0,prog_full_1,prog_full_2}:
    //                 (firmware_addr_major)?FIRMWARE_VERSION_MAJOR: //Else send in the firmware version...
    //                 (firmware_addr_minor)?FIRMWARE_VERSION_MINOR: //Else send in the firmware version...
    //                 addr_byte;



// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// Sampling Logic for the beat clocks from the DDMTD...
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 

    // Fake beat clocks used for debugging...
    reg beat_0_q1=0;
    reg beat_1_q1=0;
    integer counter_clkbeat=0;
    integer dummy_counter =0;
    reg odd=0;
    always @(posedge sampling_logic_clock)
    begin
        if (m_reset)
        begin
            counter_clkbeat <=0;
            dummy_counter <=0;
        end
        else
            dummy_counter <= dummy_counter +1;
        if(counter_clkbeat == 5)
        begin
            beat_0_q1<=~beat_0_q1;
            beat_1_q1<=~beat_1_q1;
            counter_clkbeat <=0;
        end
        else
        begin
            counter_clkbeat<=counter_clkbeat+1;
        end
    end

    








    
    //Legacy for reference
    // wire ddmtd_beatclk1,ddmtd_beatclk2;
    // BUF beatBuf2 (.I(Q1B),.O(ddmtd_beatclk2));
    // wire sync_beat1;
    // wire sync_beat2;
    // SYNC SYNC1(
    // .I(ddmtd_beatclk1),
    // .O(sync_beat1),
    // .clk(clk_ref),
    // .reset(m_reset)
    // );
    // SYNC SYNC2(
    // .I(ddmtd_beatclk2),
    // .O(sync_beat2),
    // .clk(clk_ref),
    // .reset(m_reset)
    // );



    // wire enable_sampling_logic_synced;
    // SYNC en_sample_logic(.I(enable_sampling_logic),.O(enable_sampling_logic_synced),clk(clk_ref));
    // wire clk_buffed;
    // BUF clkBuf1 (.I(sampling_logic_clock),.O(clk_buffed));
    // wire ddmtd1_beat_clock_buff;
    // BUF ddmtd1clkBuf1 (.I(ddmtd1_beat_clock),.O(ddmtd1_beat_clock_buff));
    // wire ddmtd2_beat_clock_buff;
    // BUF ddmtd2clkBuf1 (.I(ddmtd2_beat_clock),.O(ddmtd2_beat_clock_buff));


    wire rd_clk_buff;
    BUF readclkBuf1 (.I(clk),.O(rd_clk_buff));
    wire read_en_buff;
    BUF read_enBuf1 (.I(read_en),.O(read_en_buff));




    wire [31:0] external_counter;
    binary_counter bc1(
    .Q(external_counter),
    .CLK(sampling_logic_clock),
    .CE(start_acq),
    .SCLR(~start_acq | m_reset)
    );



    DDMTD_Sampler
    #(.DATA_WIDTH(32))
    DDMTD1(
        // Inputs for the sampling logic
        .WR_CLK(sampling_logic_clock),
        .BEAT_CLK(ddmtd1_beat_clock),
        .en_SAMPLING_LOGIC(start_acq), //Active High
        .EXTERNAL_COUNTER(external_counter),
        .RST(m_reset),
        //Inputs for readout
        .RD_CLK(rd_clk_buff),
        .R_TDATA(tdata1),  
        .READ_EN(read_en_buff),
        //  .PROG_FULL(prog_full_1),
        //  .PROG_EMPTY(TREADY),
        // .EMPTY(),
        .FULL(full_1),
        .R_LOGIC_EN(1),
        .WRITE_COUNT(write_count_fifo1),
        .READ_COUNT(read_count_fifo1)
    );



    DDMTD_Sampler
    #(.DATA_WIDTH(32))
    DDMTD2(
        // Inputs for the sampling logic
        .WR_CLK(sampling_logic_clock),
        .BEAT_CLK(ddmtd2_beat_clock),
        .en_SAMPLING_LOGIC(start_acq), //Active High
        .EXTERNAL_COUNTER(external_counter),
        .RST(m_reset),
        //Inputs for readout
        .RD_CLK(rd_clk_buff),
        .R_TDATA(tdata2),  
        .READ_EN(read_en_buff),
        //  .PROG_FULL(prog_full_1),
        //  .PROG_EMPTY(TREADY),
        // .EMPTY(),
        .FULL(full_2),
        .R_LOGIC_EN(1)
        // .WRITE_COUNT(write_count_fifo2),
        // .READ_COUNT(read_count_fifo2)
    );








// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// LED BLINKERS FOR STATUS REPORT
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
    
    //To visualize the beat clocks, we implement counters and attach it to leds
    integer ref_clk_testCounter=0;
    reg ref_clk_led=0;
    always@(posedge clk_ref)
        begin
        ref_clk_testCounter<=ref_clk_testCounter+1;
        if(ref_clk_testCounter == 100000000)
            begin
                ref_clk_testCounter <=0;
                ref_clk_led <=~ref_clk_led;
            end
        end

    integer test_counter;
    always@(posedge Q1A)
        begin
            test_counter <= test_counter +1;
        end


    assign led[0]     = ~PLL_SPI;
    assign led[1]     = spi_cs0;
    assign led[2]     = start_acq;
    assign led[3]     = prog_full_1;
    assign led[4]     = prog_full_2;
    assign led[5]     = test_counter[6];
    assign led[6]     = m_reset;
    assign led[7]     = enable_sampling_logic;

    assign led_fmc[0] = PLL_SPI;
    assign led_fmc[1] = full_1;
    assign led_fmc[2] = full_2;
    assign led_fmc[3] = ref_clk_led; //This should blink if PLL is generating pulse at 2.5s for 40MHz, and 0.625s for 160MHz





// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// Reprogram the FLASH via SPI interface using CS1
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 

    wire spi_gclk,cclk_in,cclk_cs;
    BUFG buf_sck (.I(spi_sck),.O(spi_gclk));
    assign FCS_B     = ~pll_cs |  spi_cs1; // FLASH CS
    assign DQ0       = spi_mosi;  // FPGA2MEM
    assign spi_miso1 = DQ1; // MEM2FPGA
    assign cclk_in   = spi_gclk;
    assign cclk_cs   = spi_cs1;

    STARTUPE2 STARTUPE2_i
    (
    //        .CFGMCLK(),
    .CLK(zero),
    .GSR(zero),
    .GTS(zero),
    .KEYCLEARB(zero),
    .PACK(zero),
    .USRCCLKO(cclk_in),
    .USRCCLKTS(cclk_cs),
    .USRDONEO(one),
    .USRDONETS(one));


// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// Reprogram the PLL via SPI interface using CS1 and PLL_SPI register
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
    wire pll_spiclk ;
    BUFG buf_sck_pll (.I(spi_sck),.O(pll_spiclk));
    assign PLL_SS    = pll_cs  |  spi_cs1; // PLL CS active low
    assign PLL_MOSI  = spi_mosi;  // RPI2PLL
    assign spi_miso2 = PLL_MISO; // PLL2RPI
    assign PLL_SCK   = pll_spiclk;



// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// VOLTAGE SETTINGS
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
    
    assign set_vadj[0] = 1'b0;
    assign set_vadj[1] = 1'b1;
    assign vadj_en     = 1'b1;

// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  == 
// END OF MODULE
// ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==  ==   
endmodule
