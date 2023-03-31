module pTrigger(
output O,
input I,
input clk,
input reset
);


 wire FF1;
    
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


    wire FF2;
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

    assign O = (FF2 ^ (FF1))&(~FF2);



endmodule