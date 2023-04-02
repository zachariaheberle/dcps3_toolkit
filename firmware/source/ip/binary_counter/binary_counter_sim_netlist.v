// Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2019.2 (lin64) Build 2708876 Wed Nov  6 21:39:14 MST 2019
// Date        : Sat Apr  1 17:40:32 2023
// Host        : ubuntu running 64-bit Ubuntu 18.04.6 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/rsaradhy/work/nexys_ddmtd_github/firmware/source/ip/binary_counter/binary_counter_sim_netlist.v
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
  (* C_FB_LATENCY = "0" *) 
  (* C_HAS_CE = "1" *) 
  (* C_HAS_SCLR = "1" *) 
  (* C_HAS_SINIT = "0" *) 
  (* C_HAS_SSET = "0" *) 
  (* C_IMPLEMENTATION = "0" *) 
  (* C_SCLR_OVERRIDES_SSET = "1" *) 
  (* C_SINIT_VAL = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_WIDTH = "32" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* c_count_by = "1" *) 
  (* c_count_mode = "0" *) 
  (* c_count_to = "1" *) 
  (* c_has_load = "0" *) 
  (* c_has_thresh0 = "0" *) 
  (* c_latency = "1" *) 
  (* c_load_low = "0" *) 
  (* c_restrict_count = "0" *) 
  (* c_thresh0_value = "1" *) 
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
(* C_IMPLEMENTATION = "0" *) (* C_LATENCY = "1" *) (* C_LOAD_LOW = "0" *) 
(* C_RESTRICT_COUNT = "0" *) (* C_SCLR_OVERRIDES_SSET = "1" *) (* C_SINIT_VAL = "0" *) 
(* C_THRESH0_VALUE = "1" *) (* C_VERBOSITY = "0" *) (* C_WIDTH = "32" *) 
(* C_XDEVICEFAMILY = "artix7" *) (* ORIG_REF_NAME = "c_counter_binary_v12_0_14" *) (* downgradeipidentifiedwarnings = "yes" *) 
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
  wire [31:0]Q;
  wire SCLR;
  wire NLW_i_synth_THRESH0_UNCONNECTED;

  assign THRESH0 = \<const1> ;
  VCC VCC
       (.P(\<const1> ));
  (* C_AINIT_VAL = "0" *) 
  (* C_CE_OVERRIDES_SYNC = "0" *) 
  (* C_FB_LATENCY = "0" *) 
  (* C_HAS_CE = "1" *) 
  (* C_HAS_SCLR = "1" *) 
  (* C_HAS_SINIT = "0" *) 
  (* C_HAS_SSET = "0" *) 
  (* C_IMPLEMENTATION = "0" *) 
  (* C_SCLR_OVERRIDES_SSET = "1" *) 
  (* C_SINIT_VAL = "0" *) 
  (* C_VERBOSITY = "0" *) 
  (* C_WIDTH = "32" *) 
  (* C_XDEVICEFAMILY = "artix7" *) 
  (* c_count_by = "1" *) 
  (* c_count_mode = "0" *) 
  (* c_count_to = "1" *) 
  (* c_has_load = "0" *) 
  (* c_has_thresh0 = "0" *) 
  (* c_latency = "1" *) 
  (* c_load_low = "0" *) 
  (* c_restrict_count = "0" *) 
  (* c_thresh0_value = "1" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  binary_counter_c_counter_binary_v12_0_14_viv i_synth
       (.CE(CE),
        .CLK(CLK),
        .L({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
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
dmmXCzwxW2FLu/vVGpJzoQ/uTl0t/oirVzDN8rGCQ/cshHIr5KZa8hMP1zjDcrW6js/9tSBuCaB1
Ioj63zjqZA==

`pragma protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
N9Ijk+dhcsedFOz7GhClRR68iRquy2ZzjVLVhi5GByFuPpr/oGFn021AFcKE54GT1hqizIMvWGS0
qRbWSO/aiWGT8c930WMeayc4xm2b65tzi7UyXSjcZqyZqk5spgPewfSuL0LKD5R4+zccn3yeTyAR
Cpi6LZ2KmpRW5biXvss=

`pragma protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
M8NGALCMec7MmW5uPCxfU8HATjWU2XqyPU8phSDe3mtyor4pgfPtg5TJdKOytKhxa+fQwJxytwzI
KPxtYmaRH/KFiGrOvm7jO78NIlt31qN95S7sMYrLxORaZ4bbNMg4RfwEB0haV15qORczgxWEpvBX
6Qukl64ihp4NiBjXt4YYGoDiNMSczgOe3tLn7UWjfPQnsJ8aMxugelO5AciSBxAdohgLMRE3cu6p
gwakO6ytq1vAR8bqHLT8g/Kdsxn72SBHYdpkba0NfEvzzheOlZY7fNuWD48V6QefMjsX1taMkmQH
m38VdXlC6Ocia7H3zT8LvNLtxrpG8zyD+UI+sg==

`pragma protect key_keyowner="ATRENTA", key_keyname="ATR-SG-2015-RSA-3", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
I1BukTJgP0oEpI/mdw6jwrYhUTr7MTzY5G/EvfuPKQfGzYRI1qLG+aEQeclA1P65+tkbstBEIIg8
ZhiouPVaom8KwKZHBX7eLpxvNBcYVFfnJb1ES5wdcph3sgGtaYKSpspp51oYPM6ZD7DmMGdoc/Wg
JVIUuIfRpo8AnEMfkayPkbwuB0VUKpz5BXS50B+5jvgK7cFe2gUp2ckThqzKUjViVB56Swsz+IQe
l7GvtTbuNcSwapfPtNHH0bWSQStfIzPZZm1A2IZ2WCYafRPkj7uibtKNgnKgIZs1197qomgXbb+b
fDx1iikgF8snJsPchukmgxkMSQtLntwbLs6H+w==

`pragma protect key_keyowner="Xilinx", key_keyname="xilinxt_2019_02", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
UNzBll4hVdQjkp7KJChMHZ9agdKjtTu8+3O75Phz7SpwUZ73Z533+9pCfaH7QI/cwqaVREb20HXT
ji2kU1DV7+Cwbshd08hvUBl23F60ITYS+3rluBLIFX3pzXhjjSu8HQpnxXppbCODvCiWrDLqRU/y
lcFf7B+yp5jK6vEY5xuh8is/oxSPNFwip6GSMqDnE45GU6kU+6n8FTk8pAZUNKnh3j0t6YzcwS3J
wYUhnJpEQYd7+0D/NPjEz0YFqzB8WCh70MxBRJzwdXpuRLiFzplysvw+eHjMPVeU/UPKJWuwWuwc
Bfxw0ThSXZit/SSD+BGhxjbEI9T6rh66FpqbTg==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
F7AZy6dB5VKzcudhyRSKWKUbVrSs4vS9jtgDkM6KrVPs3ghP3AF2TeIDyl03EesBxeIQxHqq8thx
uVIGQN5wt92jkzGo61VyUoF2dYHY2dkK9PY4bicayI6rppCS18HnyCC5ODrTMKgOpoj+PEmghCZl
j8+i3NFWPAo6M/MAtVI=

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
NQpRHEO/CEh2TWVl2zAKLb4TTDP4G4mQHrGzJeErDNbJ2L2B4iz3unsCjzHkoDagHoU9jeHYNzw1
EdgeGwokAwsWnHc0V18iEu5CZPPLrncpORhuc7qe0zJvoIFW4tgNZuIjFZI6bkrWzgxNYlkitGJ7
wQxgR+6ZenldybAjVF7d1R8FQmrEKWQ9ztmGHKMd9PfWD1VsbOoxbNA1tkQ3Suq2M9HDzUONaPQq
yMnGxLE4+4xTZZFVVFZeizNxqQcM1Y6s2MEUyS89U6rdAH95x9zDN8PGrif1SUWhpoz33cYp/IL8
acGyIWDbmuS0X+xsLC8cWcrO/MxKDk8bj12S7g==

`pragma protect key_keyowner="Real Intent", key_keyname="RI-RSA-KEY-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
W2ZLxVMM2bO/6hqe8KRsBOYby+akb1JiKHhCv9fhS2DK483JVHKKDFtV5ZylpQSPfpmWVI6nDnNm
XtxOYqhOdd9wAHIVXly/nJQ3BORIgR42ZfKk3tkiYQd75XwTJmWjvIda5LTjKISy58Rg+7/yc6kX
SAKkQWzcaHy0VIrsbeLAK7Rz2vPrBQAwZijqUO1uD9pTa1ID2lBqRKOaN/lex50cPJ7PNmyesOUe
aisZi7+ubKWoKmZJmdUy4nKUk4a0FLkIqdFpmX+Bu5UVgWOF47nrEwh3c1MVRxWa1uvngQGGl026
FTa0G+nc1Q9KslAvMQ+fMbz+FbnTF3u/A9gizA==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-PREC-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
K8WeCvaUyCtfRDzLHxXS/YbxJLrAmJV8PN6cddh25VoXHU4pxJxpsw6gXHaFmM0AyU+REQIdfSUe
3Es6J0SMqo/HEEQEoCF7jqrO94wHD4Nc+tM5fYNsTsDFw0a0iq1CAWlNyTIXSRn4KDISkHKWsEUA
lf5M5KuzXpiDwkWOXD0MMwwKiVl1KAbSRomujL6ODXnD7kcvSxjTg/h3xYY1QfDXcwqizNpwY/00
cGqyGDepimbRQ6UeyP2g7YkVeaLKck0GaCnxioVWwwoVtwKXvhxHJhF0Xfiu+mHmdOBpXU6M1Vzz
bLiP1Rm56BOHFh8gBu+SMJI2fU1U8WxDXTpXqw==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
mQmQK2XG5whjis1t+m9wiMSynMO8Q3mBPgoOqD3U0wNO2eykLqpIozMX4jjGSNn+vP8Wxq+/YkuV
48z9N7DeWS9QpHrFIOPEoK6mnUCm4OK20uiIDXr7jxfWred6kN3HFdb8E4Ku63/ngwpMyZ+axfMg
44ILDe7h5rWNsmf2X+/9cmuszR30ei03RR1XnZ11HSJsvUHTNfgjw5pSaOOfiF9FFU3gi0sdcVJa
unhSO9UJBmN+iymzRKOZ7O4BH6whNbiw9VkOL5nZqulCLXLQMyDAlopMPKeydpQ8T1M22i6yG7R5
6DA5KaoUSsPuRJhh29WpfJDdASSeX8giNqPMQA==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 17920)
`pragma protect data_block
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
h4/cCPIS03Ew3iOB10kA9wd3f137CQ==
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
