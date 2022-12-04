`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/09/2019 11:11:17 AM
// Design Name: 
// Module Name: SYNC
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


module SYNC(
output O,
input I,
input clk,
input reset
    );
    
    
      (* ASYNC_REG = "TRUE" *) wire FF1;
    
             FDRE
        #(
            .INIT(1'b0)//Initialvalueofregister(1'b0or1'b1)
         )
        FDRE_inst(
        .Q(FF1),//1-bit Data output
        .C(clk),//1-bit Clock input
        .CE(1'b1), //1-bit Clock enable input
        .R(reset),//1- bit Synchronous reset input
        .D(I)//1 -bit Data input
        );
        
        
                     FDRE
        #(
            .INIT(1'b0)//Initialvalueofregister(1'b0or1'b1)
         )
        FDRE_inst1(
        .Q(O),//1-bit Data output
        .C(clk),//1-bit Clock input
        .CE(1'b1), //1-bit Clock enable input
        .R(reset),//1- bit Synchronous reset input
        .D(FF1)//1 -bit Data input
        );
        
        
        
        
endmodule
