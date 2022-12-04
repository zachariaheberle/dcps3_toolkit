// Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2019.2 (lin64) Build 2708876 Wed Nov  6 21:39:14 MST 2019
// Date        : Sun Dec  4 00:05:03 2022
// Host        : ubuntu running 64-bit Ubuntu 18.04.6 LTS
// Command     : write_verilog -force -mode funcsim -rename_top binary_counter -prefix
//               binary_counter_ binary_counter_sim_netlist.v
// Design      : binary_counter
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a200tsbg484-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "binary_counter,c_counter_binary_v12_0_14,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "c_counter_binary_v12_0_14,Vivado 2019.2" *) 
(* NotValidForBitStream *)
module binary_counter
   (CLK,
    CE,
    SCLR,
    Q);
  (* x_interface_info = "xilinx.com:signal:clock:1.0 clk_intf CLK" *) (* x_interface_parameter = "XIL_INTERFACENAME clk_intf, ASSOCIATED_BUSIF q_intf:thresh0_intf:l_intf:load_intf:up_intf:sinit_intf:sset_intf, ASSOCIATED_RESET SCLR, ASSOCIATED_CLKEN CE, FREQ_HZ 10000000, PHASE 0.000, INSERT_VIP 0" *) input CLK;
  (* x_interface_info = "xilinx.com:signal:clockenable:1.0 ce_intf CE" *) (* x_interface_parameter = "XIL_INTERFACENAME ce_intf, POLARITY ACTIVE_HIGH" *) input CE;
  (* x_interface_info = "xilinx.com:signal:reset:1.0 sclr_intf RST" *) (* x_interface_parameter = "XIL_INTERFACENAME sclr_intf, POLARITY ACTIVE_HIGH, INSERT_VIP 0" *) input SCLR;
  (* x_interface_info = "xilinx.com:signal:data:1.0 q_intf DATA" *) (* x_interface_parameter = "XIL_INTERFACENAME q_intf, LAYERED_METADATA undef" *) output [31:0]Q;

  wire CE;
  wire CLK;
  wire [31:0]Q;
  wire SCLR;
  wire NLW_U0_THRESH0_UNCONNECTED;

  (* C_AINIT_VAL = "0" *) 
  (* C_CE_OVERRIDES_SYNC = "0" *) 
  (* C_COUNT_BY = "1" *) 
  (* C_COUNT_MODE = "0" *) 
  (* C_COUNT_TO = "1" *) 
  (* C_FB_LATENCY = "0" *) 
  (* C_HAS_CE = "1" *) 
  (* C_HAS_LOAD = "0" *) 
  (* C_HAS_SCLR = "1" *) 
  (* C_HAS_SINIT = "0" *) 
  (* C_HAS_SSET = "0" *) 
  (* C_HAS_THRESH0 = "0" *) 
  (* C_IMPLEMENTATION = "1" *) 
  (* C_LATENCY = "1" *) 
  (* C_LOAD_LOW = "0" *) 
  (* C_RESTRICT_COUNT = "0" *) 
  (* C_SCLR_OVERRIDES_SSET = "1" *) 
  (* C_SINIT_VAL = "0" *) 
  (* C_THRESH0_VALUE = "1" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_WIDTH = "32" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  binary_counter_c_counter_binary_v12_0_14 U0
       (.CE(CE),
        .CLK(CLK),
        .L({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .LOAD(1'b0),
        .Q(Q),
        .SCLR(SCLR),
        .SINIT(1'b0),
        .SSET(1'b0),
        .THRESH0(NLW_U0_THRESH0_UNCONNECTED),
        .UP(1'b1));
endmodule

(* C_AINIT_VAL = "0" *) (* C_CE_OVERRIDES_SYNC = "0" *) (* C_COUNT_BY = "1" *) 
(* C_COUNT_MODE = "0" *) (* C_COUNT_TO = "1" *) (* C_FB_LATENCY = "0" *) 
(* C_HAS_CE = "1" *) (* C_HAS_LOAD = "0" *) (* C_HAS_SCLR = "1" *) 
(* C_HAS_SINIT = "0" *) (* C_HAS_SSET = "0" *) (* C_HAS_THRESH0 = "0" *) 
(* C_IMPLEMENTATION = "1" *) (* C_LATENCY = "1" *) (* C_LOAD_LOW = "0" *) 
(* C_RESTRICT_COUNT = "0" *) (* C_SCLR_OVERRIDES_SSET = "1" *) (* C_SINIT_VAL = "0" *) 
(* C_THRESH0_VALUE = "1" *) (* C_VERBOSITY = "0" *) (* C_WIDTH = "32" *) 
(* C_XDEVICEFAMILY = "artix7" *) (* downgradeipidentifiedwarnings = "yes" *) 
module binary_counter_c_counter_binary_v12_0_14
   (CLK,
    CE,
    SCLR,
    SSET,
    SINIT,
    UP,
    LOAD,
    L,
    THRESH0,
    Q);
  input CLK;
  input CE;
  input SCLR;
  input SSET;
  input SINIT;
  input UP;
  input LOAD;
  input [31:0]L;
  output THRESH0;
  output [31:0]Q;

  wire \<const1> ;
  wire CE;
  wire CLK;
  wire [31:0]L;
  wire [31:0]Q;
  wire SCLR;
  wire NLW_i_synth_THRESH0_UNCONNECTED;

  assign THRESH0 = \<const1> ;
  VCC VCC
       (.P(\<const1> ));
  (* C_AINIT_VAL = "0" *) 
  (* C_CE_OVERRIDES_SYNC = "0" *) 
  (* C_COUNT_BY = "1" *) 
  (* C_COUNT_MODE = "0" *) 
  (* C_COUNT_TO = "1" *) 
  (* C_FB_LATENCY = "0" *) 
  (* C_HAS_CE = "1" *) 
  (* C_HAS_LOAD = "0" *) 
  (* C_HAS_SCLR = "1" *) 
  (* C_HAS_SINIT = "0" *) 
  (* C_HAS_SSET = "0" *) 
  (* C_HAS_THRESH0 = "0" *) 
  (* C_IMPLEMENTATION = "1" *) 
  (* C_LATENCY = "1" *) 
  (* C_LOAD_LOW = "0" *) 
  (* C_RESTRICT_COUNT = "0" *) 
  (* C_SCLR_OVERRIDES_SSET = "1" *) 
  (* C_SINIT_VAL = "0" *) 
  (* C_THRESH0_VALUE = "1" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_WIDTH = "32" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  binary_counter_c_counter_binary_v12_0_14_viv i_synth
       (.CE(CE),
        .CLK(CLK),
        .L(L),
        .LOAD(1'b0),
        .Q(Q),
        .SCLR(SCLR),
        .SINIT(1'b0),
        .SSET(1'b0),
        .THRESH0(NLW_i_synth_THRESH0_UNCONNECTED),
        .UP(1'b0));
endmodule
`pragma protect begin_protected
`pragma protect version = 1
`pragma protect encrypt_agent = "XILINX"
`pragma protect encrypt_agent_info = "Xilinx Encryption Tool 2019.1"
`pragma protect key_keyowner="Cadence Design Systems.", key_keyname="cds_rsa_key", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=64)
`pragma protect key_block
mZM+QkmBmYCY7NPgF4QadIitw8Eo+SIwG/ZLPzQSVo/+iaeH+D5UcymUJegYkWcUJho8I/Ca6tC9
BcrWLzqiSg==

`pragma protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
m+fC7UnOc3lEJdF6HAD+AO/yeZSz11oLyDHA0Df3kGgHhj+RwbK/SnWf9v1KZrS0pMJJUO6XV6v4
HlgXy4/LyWr9xInVKpipB37EutWXywoqz+1z6QQnBeEc/bFgaYnjfNVfmCe7b/uvzsznRxv4g49x
IbbwmYVPlJlM7RiIIUw=

`pragma protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
rDbHS5sy994Wefoo6l/eUEpHx+Zo4hK7RxI32sncxdT1Bdk5aKjGY4UEdTJnrzZnlUNeiA7lqAY4
kbOZOXFRZQqL/9cE+Eexju7i3W9oXfaETCK004ve+Hh7ccj0BXqFm2Y4k07Ne/CtUJNcyH0Yqqti
gCrOLCDDO0bLrxPHhJABOIcLDs6XdASBzfQSOIX13iKktynuDQy9P0UWcx60e6rMtbpwLXUBSYUv
U+Hu1UEMOHnc/WTTxxmY85cP1KeGPYOpLlkIokpXZ8YevtDSE+cd5cn78Pj1A84QhZfP0eyUXT58
QBazbLlAIfh5YqSZshCArhNLzWy46i+D9nhtnA==

`pragma protect key_keyowner="ATRENTA", key_keyname="ATR-SG-2015-RSA-3", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
kDAueH+1IfJtZIC4dXJ0KOFeEyMeE64ROjlOQFn0YA50L5K3mjbOqsUNUOYQ3AQv/MDoPnhQAw24
ncqGrSzr22Eo3qkCBevBDcKaOXbJKeuuWwa2BL9gVLd8x1CGNKRCY9HgRWTaFP3bFE8IC6Wb1MQM
lh1aab6Hc1hCVUoaMZovDfA7pahwN+Ofes0F7tNeWWHBJ9HqmXjdNSIc0fhiL4oCkFYFKxAj7VYV
fvJk1Lt8t3eAqqFmX1wv/GZUSXH/T4wH/dtyGB4+Z9HiVEhbPwshofy5qPAJ1GyWuU9knKZ7oXwF
y0rW1H9CueC082UO0KJfTB5adMlR6IAxdDst6A==

`pragma protect key_keyowner="Xilinx", key_keyname="xilinxt_2019_02", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
Fc/3ZbRoeSBESwxq84FLKKHw5JiDREh8UGnn2Rzjhu2zXqMwcnjmmkcDnHaxqko+FpcFl3MSrQyA
N7dj5tbbO6LV2Gvp9gQHdOMqgogI5ZSA2MrQM1xkEs7og+WXFDOW2DzaoVNBBPY30Fxo2z2EdGkK
82BQlO03GRrZB8bBN/1ndJVAqKmb6I2LgcJOsV4HvHc5rgPq6Q89NS7JvmN3YI/cw4uWXXLkso+g
80AfqZjAXMw5OY4cWZscectXNx5vGHWy9fcKNH0p3fS7FRh1M2zsRrVvSEP/ygtXR3Jrf+/xqhv1
fZSqKqzI0Q17bh68ZGd39RDw/TGEUIOZg8lY1w==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
K3Ao/bH4OtPU9lcf8MKmR5SH3AU/XNzFMyvYN1Cvi8TkAqVSjsRpmiA6psdHUxQ6ChxDL+ifIZmx
XmGdelYbBZX2cseyC7F4SArU6gFMESx2kqccYUXXKgud9VEcW/cLeAiU54NEeoRjHzxfyykkXDVi
5FoCcUIuf1d/5LfCh6E=

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
g8trO3AM2GKk54eXi8fG+FquVAmu50gIUwVjw4ul+0+xnhvRbginNickq5wikk4ZtP1HiuGxz/PB
o3q4N1Lj+w+QS4/JvRo4wuezx5vzkWzfGJh4N4eME2ziyNHCuxLEobWs8KEG+ilhltk1c2hvgkMz
JXhUTpJ6l1apI5+sSCHAcYvC7VVjjiCJQhk8YXIbnWX5GNaeHmM9sXw6q6MXafVhmkI7KkLrNLFO
9p/t2fdUw33+h4NQB/TdcR/Eksd0542M6+Y06QqjDbTR7KIjnhxELKh1JRW3t+rXEJOoLqsFjP7I
26tNqlayy5YjSzF90FiIpUUwtrOsZ1lXamVFzQ==

`pragma protect key_keyowner="Real Intent", key_keyname="RI-RSA-KEY-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
QwE2AalCFRTpm3aOoXgseW8MLMWLVbSa89zNSHS9I26fnur8dp1ecu4nBhbmdCiT6xN9K+Y9LOqy
eZa8uQGcMgejXddOOIOoRBcM4/c8NEJcAIpN5sedKHupwvRA+1Ok8SjcQdRLHuJbTnYBRLvaK5QS
6SSXFkiXv2R3xlZ4ji1w0O9Ta+AzNh+ntvJ1Hd68xxmunKOL1y/YY43obHssJp/KBybMaCqwZpej
yYEz8Lz8oeoYFaK3poBxJSPhygpk0gKOHf5FNHmJu4tB4+EqhHpANOMIxzKELrB4cS1HL/3VPJv/
uryTtzko/3vhXdbwZl23slwjYt2mW1vcnIXTyQ==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-PREC-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
qpMclxj9E69LeL5M8OxOOpVj3licOa5kBTCn+yGUdJVyc46oQvsoGv0EZrkAZ5aIlQl6aBlH8pzB
mcXaHsQDHt4ymtVk27vvSBMdQbDEsafNMBO/oT0ne8G60vjYfDfKzqvVUdFSNnVEBUROFqCe4qNq
6NxfFEj5Wx+ZyECHbGPrhAYP/QtqGP+wjxQESAe22S2nmyt5FFJKuH8axzAbpukOC7ILtEgyY6Pg
BksJNSIigiysSaJKOB3yuLPdpFuyLNTpdacVX30sdedab+LY22FyCIGTw2ciLbyR4dn7ceXwLn/J
KtuJh6+W0447XWjmjhp62z82tc5ucPF+xe1VlQ==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
BkRAf7OElti+a5GZR0Us5wSDSwvHXzfslpQiyS8XwU/EareFDAlDHy3zDej0rGVvW7Vi9PvlWL/a
WgxRhr/DK44h24qiyFSZKMKhhlynLtrTw4O6KdXyDF53BvQosZR5+KQQ4h/APRDhlBjfvmDZ5y3e
2RPufLaVs5/riIvpPihCLI1+npWzIFAjxPryYNlx8oIa1crY9Y0yyAfYCg51F11PULeYywoL5i8o
T/SU21Fj6pSdTB2kzgcod2hC6yMNCYCOM4YuqpeUco/YJ9dbSJpoiWzsVBt4HMwSzvRPIQAfD2ru
9lb8TDsLOmVczFunCP2HhFKtFf+HaZsbpQt13w==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 10800)
`pragma protect data_block
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
/5f+kH8E5GlCGSCtP+hESmFSPkFddQ==
`pragma protect end_protected
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

endmodule
`endif
