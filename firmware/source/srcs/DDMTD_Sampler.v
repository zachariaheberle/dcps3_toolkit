`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Rohith 
// 
// Create Date: 08/12/2020 08:00:43 AM
// Design Name: 
// Module Name: DDMTD_Sampler
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


module DDMTD_Sampler
#(
    parameter integer DATA_WIDTH = 32
 )
 (
    // Inputs for the sampling logic
    input WR_CLK, // should be synchronous with BEAT_CLK
    input BEAT_CLK,
    input [DATA_WIDTH-1:0] EXTERNAL_COUNTER,
    input RST,
    input en_SAMPLING_LOGIC, // Active high
    input wire  RD_CLK,
    output wire [DATA_WIDTH-1 : 0] R_TDATA,
    input wire  READ_EN,
    input wire R_LOGIC_EN,
    output wire PROG_FULL,
    output wire PROG_EMPTY,
    output wire EMPTY,
    output wire FULL,
    output wire [7:0] WRITE_COUNT,
    output wire [7:0] READ_COUNT





 );


// Internal Counter if needed...
// wire [31:0] internal_counter;
// binary_counter bc1(
// .Q(internal_counter),
// .CLK(WR_CLK),
// .CE(en_SAMPLING_LOGIC),
// .SCLR(~en_SAMPLING_LOGIC | RST)
// );


// (* ASYNC_REG = "TRUE" *) wire BEAT_CLK_synced;
// SYNC beat_sync(
//     .I(BEAT_CLK),
//     .O(BEAT_CLK_synced),
//     .clk(WR_CLK),
//     .reset(RST)
// );

reg [31:0] DATA_IN;
reg temp_mem=0;
reg WRITE_EN=0;
integer test_counter = 0;
always @(negedge WR_CLK) 
begin
    test_counter <= test_counter + 1;
    if(temp_mem !=  BEAT_CLK && en_SAMPLING_LOGIC) begin
        temp_mem <= BEAT_CLK;
        WRITE_EN <= 1;
        DATA_IN  <={BEAT_CLK,EXTERNAL_COUNTER[30:0]};
        // DATA_IN  <={clk_beat,internal_counter[30:0]};
        // DATA_IN  <={BEAT_CLK,test_counter[30:0]};
        // DATA_IN  <=test_counter[30:0];
    end
    else begin
        WRITE_EN <=0;
    end
    if (RST|~en_SAMPLING_LOGIC)
        test_counter <= 0 ;
end




//SYNC WRITE_EN & DATA_IN
reg write_en_sync_pos;
reg [31:0] data_in_sync_pos;
always @(posedge WR_CLK ) begin
    write_en_sync_pos <= WRITE_EN;
    data_in_sync_pos <= DATA_IN;
end


reg write_en_sync_neg;
reg [31:0] data_in_sync_neg;
always @(negedge WR_CLK ) begin
    write_en_sync_neg <= write_en_sync_pos;
    data_in_sync_neg <= data_in_sync_pos;
end





 


//DEBUGGING CODE
//Code for Generating Fake events at every posedge of the clock
// reg write_en;
// integer reset_counter=0;
// always@(negedge WR_CLK)
// begin
//     if (RST)
//         reset_counter <=0;
//     else if (reset_counter < 300) 
//         reset_counter <= reset_counter +1;


//     if ((data_in_temperory < 1000)&&(reset_counter > 100))
//         write_en <=  en_SAMPLING_LOGIC;
//     else
//         write_en <=0;
// end

// reg [31:0] data_in_temperory;
// always@(negedge clk_ref)
// begin
//     if ((en_SAMPLING_LOGIC)&&(reset_counter > 100))
//         data_in_temperory <= data_in_temperory+1;
//     else
//         data_in_temperory <=0;
// end



FIFO_Array FIFO_Array_inst (
    .rst(RST),
    .wr_clk(WR_CLK),
    .rd_clk(RD_CLK), //Done to flush out the data
    .din(data_in_sync_neg),
    .wr_en(write_en_sync_neg),
    .rd_en(READ_EN),
    .dout(R_TDATA),
    .full(FULL),
    .empty(EMPTY)
    //,.rd_data_count(READ_COUNT), if you are using Block RAM FIFO
    //.wr_data_count(WRITE_COUNT), if you are using Block RAM FIFO
    //.prog_empty(PROG_EMPTY),
    //.prog_full(PROG_FULL)
    //.wr_rst_busy,
    //.rd_rst_busy
    );


// FIFO TEST MACRO
// FIFO36E1: 36Kb FIFO (First-In-First-Out) Block RAM Memory
// 7 Series
// Xilinx HDL Language Template, version 2021.1
// FIFO36E1 #(
//  .ALMOST_EMPTY_OFFSET(13'h0080), // Sets the almost empty threshold
//  .ALMOST_FULL_OFFSET(13'h0080), // Sets almost full threshold
//  .DATA_WIDTH(36), // Sets data width to 4-72
//  .DO_REG(1), // Enable output register (1-0) Must be 1 if EN_SYN = FALSE
//  .EN_ECC_READ("FALSE"), // Enable ECC decoder, FALSE, TRUE
//  .EN_ECC_WRITE("FALSE"), // Enable ECC encoder, FALSE, TRUE
//  .EN_SYN("FALSE"), // Specifies FIFO as Asynchronous (FALSE) or Synchronous (TRUE)
//  .FIFO_MODE("FIFO36"), // Sets mode to "FIFO36" or "FIFO36_72"
//  .FIRST_WORD_FALL_THROUGH("FALSE"), // Sets the FIFO FWFT to FALSE, TRUE
//  .INIT(72'h000000000000000000), // Initial values on output port
//  .SIM_DEVICE("7SERIES"), // Must be set to "7SERIES" for simulation behavior
//  .SRVAL(72'h000000000000000000) // Set/Reset value for output port
// )
// FIFO36E1_inst (
//  // ECC Signals: 1-bit (each) output: Error Correction Circuitry ports
// //  .DBITERR(DBITERR), // 1-bit output: Double bit error status
// //  .ECCPARITY(ECCPARITY), // 8-bit output: Generated error correction parity
// //  .SBITERR(SBITERR), // 1-bit output: Single bit error status
//  // Read Data: 64-bit (each) output: Read output data
//  .DO(R_TDATA), // 64-bit output: Data output
// //  .DOP(DOP), // 8-bit output: Parity data output
//  // Status: 1-bit (each) output: Flags and other FIFO status outputs
// //  .ALMOSTEMPTY(ALMOSTEMPTY), // 1-bit output: Almost empty flag
// //  .ALMOSTFULL(ALMOSTFULL), // 1-bit output: Almost full flag
//  .EMPTY(EMPTY), // 1-bit output: Empty flag
//  .FULL(FULL), // 1-bit output: Full flag
//  .RDCOUNT(READ_COUNT), // 13-bit output: Read count
// //  .RDERR(RDERR), // 1-bit output: Read error
//  .WRCOUNT(WRITE_COUNT), // 13-bit output: Write count
// //  .WRERR(WRERR), // 1-bit output: Write error
//  // ECC Signals: 1-bit (each) input: Error Correction Circuitry ports
// //  .INJECTDBITERR(INJECTDBITERR), // 1-bit input: Inject a double bit error input
// //  .INJECTSBITERR(INJECTSBITERR),
//  // Read Control Signals: 1-bit (each) input: Read clock, enable and reset input signals
//  .RDCLK(R_CLK), // 1-bit input: Read clock
//  .RDEN(READ_EN), // 1-bit input: Read enable
//  .REGCE(1'b1), // 1-bit input: Clock enable
//  .RST(RST), // 1-bit input: Reset
// //  .RSTREG(RSTREG), // 1-bit input: Output register set/reset
//  // Write Control Signals: 1-bit (each) input: Write clock and enable input signals
//  .WRCLK(WR_CLK), // 1-bit input: Rising edge write clock.
//  .WREN(WRITE_EN), // 1-bit input: Write enable
//  // Write Data: 64-bit (each) input: Write input data
//  .DI(DATA_IN) // 64-bit input: Data input
// //  .DIP(DIP) // 8-bit input: Parity input
// );
// // End of FIFO36E1_inst instantiation
    
endmodule